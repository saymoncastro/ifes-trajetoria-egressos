"""Contribuição do egresso (026 US1, US2; T007, T009, T012, T017)."""

import re
import uuid
from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from tests.declaracao import construcao as cd
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from tests.portal import construcao_contribuicao as cc
from trajetoria.portal import mensagens as m_portal
from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.regras import ManifestacaoRejeitada, Motivo
from trajetoria.portal.models import Manifestacao

pytestmark = pytest.mark.django_db

LICENCIATURA = "Licenciatura em Química"


def _principal(resposta) -> str:
    html = resposta.content.decode()
    return html[html.index("<main"): html.index("</main>")]


def _texto(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


# --- Operações (T007) ------------------------------------------------------------------------

def test_registrar_grava_versao_momento_e_unidade_copiada(cenario):
    diego = cenario.pessoa("SIM-P-0004")
    conclusao = cc.conclusao(diego, LICENCIATURA)
    manifestacao = cc.registrar(diego, conclusao, email=" Diego@Exemplo.TEST ")
    linha = Manifestacao.objects.get()
    assert linha.pk == manifestacao.pk
    assert (linha.pessoa_id, linha.conclusao_id) == (diego.pk, conclusao.pk)
    assert linha.unidade == "Vila Velha" and linha.forma == "experiencia"
    assert linha.versao_da_ciencia == m.VERSAO_DA_CIENCIA  # SC-002
    assert linha.registrada_em == c.NO_PERIODO
    assert linha.email == "Diego@exemplo.test"
    assert linha.retirada_em is None and linha.contato_registrado_em is None


def test_conclusao_de_outra_pessoa_e_recusada(cenario):
    diego, maria = cenario.pessoa("SIM-P-0004"), cenario.pessoa("SIM-P-0003")
    with pytest.raises(ManifestacaoRejeitada) as erro:
        cc.registrar(diego, maria.conclusoes.first())
    assert Motivo.FORMACAO in erro.value.motivos
    with pytest.raises(ManifestacaoRejeitada):
        operacoes.registrar(diego, conclusao_id=uuid.uuid4(), forma="mentoria", mensagem="",
                            email=cc.EMAIL, versao_da_ciencia=m.VERSAO_DA_CIENCIA,
                            agora=c.NO_PERIODO)
    assert not Manifestacao.objects.exists()


def test_formacao_declarada_nao_serve(cenario):
    """D-2603: a Formação Declarada (019) não é Conclusão: seu id é recusado."""
    declarada = cd.declaracao_concluida(cenario.campanha)
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.registrar(cenario.pessoa("SIM-P-0004"), conclusao_id=declarada.pk,
                            forma="mentoria", mensagem="", email=cc.EMAIL,
                            versao_da_ciencia=m.VERSAO_DA_CIENCIA, agora=c.NO_PERIODO)
    assert Motivo.FORMACAO in erro.value.motivos


def test_versao_que_nao_e_a_vigente_e_recusada(cenario):
    diego = cenario.pessoa("SIM-P-0004")
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.registrar(diego, conclusao_id=diego.conclusoes.first().pk, forma="mentoria",
                            mensagem="", email=cc.EMAIL, versao_da_ciencia="antiga",
                            agora=c.NO_PERIODO)
    assert erro.value.motivos == (Motivo.CIENCIA,)


def test_uma_ativa_por_forma_e_formacao(cenario):
    """FR-006: a segunda é recusada; outra forma, outra formação ou depois da retirada,
    não."""
    diego = cenario.pessoa("SIM-P-0004")
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    primeira = cc.registrar(diego, licenciatura)
    with pytest.raises(ManifestacaoRejeitada) as erro:
        cc.registrar(diego, licenciatura)
    assert erro.value.motivos == (Motivo.DUPLICADA,)
    cc.registrar(diego, licenciatura, forma="mentoria")
    cc.registrar(diego, cc.conclusao(diego, "Técnico em Química"))
    operacoes.retirar(diego, primeira.pk, agora=c.NO_PERIODO)
    cc.registrar(diego, licenciatura)  # US2.3: nova, sem desfazer a retirada
    assert Manifestacao.objects.count() == 4
    assert Manifestacao.objects.get(pk=primeira.pk).retirada_em == c.NO_PERIODO


def test_unicidade_no_banco_mesmo_sem_a_verificacao(cenario):
    """R6: dois envios simultâneos esbarram na restrição parcial do banco."""
    diego = cenario.pessoa("SIM-P-0004")
    existente = cc.registrar(diego)
    with pytest.raises(IntegrityError), transaction.atomic():
        Manifestacao.objects.create(
            pessoa_id=diego.pk, conclusao_id=existente.conclusao_id, unidade="Vila Velha",
            forma=existente.forma, email=cc.EMAIL, versao_da_ciencia="x",
            registrada_em=c.NO_PERIODO,
        )


def test_corrida_vira_recusa_e_nao_erro(cenario, monkeypatch):
    diego = cenario.pessoa("SIM-P-0004")
    cc.registrar(diego)
    monkeypatch.setattr("django.db.models.query.QuerySet.exists", lambda self: False)
    with pytest.raises(ManifestacaoRejeitada) as erro:
        cc.registrar(diego)
    assert erro.value.motivos == (Motivo.DUPLICADA,)


def test_retirar_so_a_propria_e_uma_vez(cenario):
    diego, maria = cenario.pessoa("SIM-P-0004"), cenario.pessoa("SIM-P-0003")
    manifestacao = cc.registrar(diego)
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.retirar(maria, manifestacao.pk, agora=c.NO_PERIODO)
    assert erro.value.motivos == (Motivo.FORA_DO_ESCOPO,)
    depois = c.NO_PERIODO + timedelta(days=1)
    operacoes.retirar(diego, manifestacao.pk, agora=depois)
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.retirar(diego, manifestacao.pk, agora=depois)
    assert erro.value.motivos == (Motivo.ESTADO,)
    assert Manifestacao.objects.get().retirada_em == depois


def test_conclusao_sem_unidade_fica_com_o_ifes(cenario):
    diego = cenario.pessoa("SIM-P-0004")
    conclusao = diego.conclusoes.first()
    type(conclusao).objects.filter(pk=conclusao.pk).update(unidade=None)
    assert cc.registrar(diego, conclusao).unidade == ""


# --- Fluxo em três telas (T009; SC-001) ------------------------------------------------------

def _entrar(client, cenario, id_externo="SIM-P-0004"):
    pessoa = cenario.pessoa(id_externo)
    cp.entrar(client, pessoa)
    return pessoa


def test_escolha_mostra_formas_e_as_proprias_formacoes(client, cenario):
    diego = _entrar(client, cenario)
    resposta = client.get("/contribuir/")
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    html = _principal(resposta)
    assert html.count("<h1") == 1 and m.TITULO in html
    assert html.count('name="forma"') == 6 and html.count('name="formacao"') == 3
    for conclusao in diego.conclusoes.all():
        assert f'value="{conclusao.pk}"' in html and conclusao.curso in html
    assert " checked" not in html  # três formações: nenhuma pré-selecionada
    assert m.DICA_MENSAGEM in html and 'maxlength="500"' in html
    assert "<script" not in resposta.content.decode()


def test_formacao_unica_vem_marcada(client, cenario):
    ana = _entrar(client, cenario, "SIM-P-0001")
    html = _principal(client.get("/contribuir/"))
    assert re.search(rf'value="{ana.conclusoes.get().pk}" checked', html)


def test_escolha_valida_mostra_a_confirmacao(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    resposta = client.post("/contribuir/", cc.escolha(licenciatura))
    html = _principal(resposta)
    assert resposta.status_code == 200 and m.CONFIRMAR_TITULO in html
    texto = _texto(html)
    assert "Compartilhar experiência" in texto
    assert "Licenciatura em Química · Vila Velha · 2017" in texto
    assert "A unidade Vila Velha" in texto
    for frase in m.ciencia("Vila Velha"):
        assert frase in texto
    assert m.VERSAO_TEXTO.format(versao=m.VERSAO_DA_CIENCIA) in texto
    # US1.3: e-mail obrigatório, vazio, sem pré-preenchimento (D-2602).
    assert re.search(r'<input type="email" id="email" name="email" value=""', html)
    assert not Manifestacao.objects.exists()


def test_escolha_invalida_mostra_os_erros_sem_gravar(client, cenario):
    diego = _entrar(client, cenario)
    resposta = client.post("/contribuir/", {"forma": "outra", "formacao": "x",
                                            "mensagem": "a" * 501})
    html = _principal(resposta)
    assert resposta.status_code == 422
    assert 'class="resumo-erros"' in html
    for chave in ("forma", "formacao", "mensagem"):
        assert m.ERROS[chave] in html
    assert "a" * 501 in html  # a mensagem volta para ser corrigida
    assert html.count(" autofocus") == 1
    assert not Manifestacao.objects.exists()
    maria = cenario.pessoa("SIM-P-0003")  # formação de outra Pessoa num POST forjado
    resposta = client.post("/contribuir/", cc.escolha(maria.conclusoes.first()))
    assert resposta.status_code == 422 and m.ERROS["formacao"] in _principal(resposta)
    assert diego.conclusoes.count() == 3


def test_confirmar_grava_e_leva_ao_resultado(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    resposta = client.post("/contribuir/confirmar/", cc.confirmacao(licenciatura))
    manifestacao = Manifestacao.objects.get()
    assert resposta.status_code == 303
    assert resposta["Location"] == f"/contribuicoes/{manifestacao.pk}/?aviso=enviada"
    assert manifestacao.mensagem == cc.MENSAGEM and manifestacao.email == cc.EMAIL
    html = _principal(client.get(resposta["Location"]))
    texto = _texto(html)
    assert m.AVISOS["enviada"] in texto and m.DETALHE_TITULO in texto
    assert "A unidade Vila Velha" in texto  # US1.4: para quem
    data = timezone.localtime(manifestacao.registrada_em).strftime("%d/%m/%Y")
    assert m.SITUACAO_ENVIADA.format(data=data) in texto
    assert f'href="/contribuicoes/{manifestacao.pk}/retirar/"' in html


def test_mensagem_com_quebras_de_linha_atravessa_as_telas(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    mensagem = "Primeira linha.\r\nSegunda linha."
    html = _principal(client.post("/contribuir/", cc.escolha(licenciatura, mensagem=mensagem)))
    oculta = re.search(r'<textarea name="mensagem" hidden>(.*?)</textarea>', html, re.S).group(1)
    client.post("/contribuir/confirmar/", cc.confirmacao(licenciatura, mensagem=oculta))
    assert Manifestacao.objects.get().mensagem == "Primeira linha.\nSegunda linha."


def test_erro_de_email_mantem_as_escolhas(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    resposta = client.post("/contribuir/confirmar/",
                           cc.confirmacao(licenciatura, email="diego@"))
    html = _principal(resposta)
    assert resposta.status_code == 422 and m.ERROS["email"] in html
    assert 'value="diego@"' in html and 'aria-invalid="true"' in html
    assert f'name="formacao" value="{licenciatura.pk}"' in html
    assert 'name="forma" value="experiencia"' in html
    assert not Manifestacao.objects.exists()


def test_voltar_e_alterar_mantem_as_escolhas(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    resposta = client.post("/contribuir/", {**cc.confirmacao(licenciatura), "voltar": "1"})
    html = _principal(resposta)
    assert resposta.status_code == 200 and m.TITULO in html
    assert re.search(r'value="experiencia" checked', html)
    assert re.search(rf'value="{licenciatura.pk}" checked', html)
    assert cc.MENSAGEM in html and 'class="resumo-erros"' not in html


def test_ciencia_atualizada_pede_nova_conferencia(client, cenario):
    diego = _entrar(client, cenario)
    resposta = client.post("/contribuir/confirmar/",
                           cc.confirmacao(diego.conclusoes.first(), versao="antiga"))
    html = _principal(resposta)
    assert resposta.status_code == 409 and m.ERROS["ciencia"] in html
    assert f'name="versao" value="{m.VERSAO_DA_CIENCIA}"' in html
    assert not Manifestacao.objects.exists()


def test_mesma_contribuicao_ativa_nao_duplica(client, cenario):
    diego = _entrar(client, cenario)
    licenciatura = cc.conclusao(diego, LICENCIATURA)
    cc.registrar(diego, licenciatura)
    for url, dados in (("/contribuir/", cc.escolha(licenciatura)),
                       ("/contribuir/confirmar/", cc.confirmacao(licenciatura))):
        resposta = client.post(url, dados)
        html = _principal(resposta)
        assert resposta.status_code in (409, 422), url
        assert m.ERROS["duplicada"] in html and 'href="/contribuicoes/"' in html
    assert Manifestacao.objects.count() == 1


def test_sem_sessao_vai_para_a_entrada(client, cenario):
    for url in ("/contribuir/", "/contribuicoes/"):
        assert client.get(url)["Location"] == "/entrar/"
    assert client.post("/contribuir/confirmar/", {})["Location"] == "/entrar/"
    assert not Manifestacao.objects.exists()


def test_declarante_vai_para_a_declaracao(client, cenario):
    cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
    assert client.get("/contribuir/")["Location"] == "/declaracao/"


def test_sem_conclusao_a_contribuicao_nao_existe(client, cenario):
    cp.entrar(client, cp.pessoa_sem_conclusao())
    for url in ("/contribuir/", "/contribuicoes/"):
        assert client.get(url).status_code == 404, url
    assert client.post("/contribuir/confirmar/", {}).status_code == 404


def test_confirmar_so_por_post(client, cenario):
    _entrar(client, cenario)
    assert client.get("/contribuir/confirmar/").status_code == 405


# --- Ver e retirar (T012; US2) -----------------------------------------------------------------

def test_suas_contribuicoes_com_situacao(client, cenario):
    diego = _entrar(client, cenario)
    enviada = cc.registrar(diego, cc.conclusao(diego, LICENCIATURA))
    com_contato = cc.registrar(diego, cc.conclusao(diego, "Técnico em Química"),
                               forma="mentoria")
    retirada = cc.registrar(diego, cc.conclusao(diego, "Mestrado Profissional em Química"),
                            forma="parceria")
    dia = c.NO_PERIODO + timedelta(days=3)
    operacoes.registrar_contato(com_contato.pk, operador=cc.OPERADOR_A, escopo=cc.ESCOPO_A,
                                agora=dia)
    operacoes.retirar(diego, retirada.pk, agora=dia)
    html = _principal(client.get("/contribuicoes/"))
    texto = _texto(html)
    data = timezone.localtime(dia).strftime("%d/%m/%Y")
    data_envio = timezone.localtime(c.NO_PERIODO).strftime("%d/%m/%Y")
    assert "A unidade Vila Velha registrou contato em " + data in texto  # FR-005a
    assert m.SITUACAO_RETIRADA.format(data=data) in texto
    assert m.SITUACAO_ENVIADA_NA_LISTA in texto
    assert f"Técnico em Química · Unidade Vila Velha · enviada em {data_envio}" in texto
    assert f'/contribuicoes/{enviada.pk}/retirar/' in html
    assert f'/contribuicoes/{com_contato.pk}/retirar/' in html
    assert f'/contribuicoes/{retirada.pk}/retirar/' not in html
    assert html.count("<h1") == 1


def test_lista_vazia_convida_a_contribuir(client, cenario):
    _entrar(client, cenario)
    html = _principal(client.get("/contribuicoes/"))
    assert m.LISTA_VAZIA in html and f'href="/contribuir/">{m.INICIO_ACAO}<' in html


def test_manifestacao_de_outra_pessoa_e_404(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    dela = cc.registrar(maria)
    _entrar(client, cenario)
    for url in (f"/contribuicoes/{dela.pk}/", f"/contribuicoes/{dela.pk}/retirar/"):
        assert client.get(url).status_code == 404, url
    assert client.post(f"/contribuicoes/{dela.pk}/retirar/").status_code == 404
    assert Manifestacao.objects.get().retirada_em is None


def test_retirada_com_confirmacao(client, cenario):
    diego = _entrar(client, cenario)
    manifestacao = cc.registrar(diego)
    pagina = client.get(f"/contribuicoes/{manifestacao.pk}/retirar/")
    html = _principal(pagina)
    assert pagina.status_code == 200 and m.RETIRAR_TITULO in html
    assert m.RETIRAR_TEXTO.format(da_unidade="da unidade Vila Velha") in _texto(html)
    assert Manifestacao.objects.get().retirada_em is None  # GET não grava
    resposta = client.post(f"/contribuicoes/{manifestacao.pk}/retirar/")
    assert resposta["Location"] == "/contribuicoes/?aviso=retirada"
    assert Manifestacao.objects.get().retirada_em == c.NO_PERIODO
    assert m.AVISOS["retirada"] in _principal(client.get(resposta["Location"]))
    # Já retirada: volta ao detalhe, que não oferece retirar de novo.
    de_novo = client.post(f"/contribuicoes/{manifestacao.pk}/retirar/")
    assert de_novo["Location"] == f"/contribuicoes/{manifestacao.pk}/"
    assert "/retirar/" not in _principal(client.get(de_novo["Location"]))


# --- Início e navegação (T017; FR-011) ---------------------------------------------------------

def test_bloco_depois_de_oportunidades_e_antes_do_convite(client, cenario):
    from tests.portal import construcao_oportunidades as co

    co.publicada("Para todos")
    ana = _entrar(client, cenario, "SIM-P-0001")
    html = _principal(client.get("/inicio/"))
    posicoes = [html.index(marca) for marca in (
        m_portal.TITULO_ACOES, 'class="inicio-oportunidades', 'class="inicio-contribuir"',
        'class="inicio-convite"',
    )]
    assert posicoes == sorted(posicoes)
    bloco = html[html.index('class="inicio-contribuir"'):html.index('class="inicio-convite"')]
    assert m.INICIO_TEXTO in bloco and f'href="/contribuir/">{m.INICIO_ACAO}<' in bloco
    assert "/contribuicoes/" not in bloco
    cc.registrar(ana)
    html = _principal(client.get("/inicio/"))
    assert f'href="/contribuicoes/">{m.INICIO_SUAS}<' in html


def test_sem_conclusao_sem_bloco(client, cenario):
    cp.entrar(client, cp.pessoa_sem_conclusao())
    assert 'class="inicio-contribuir"' not in client.get("/inicio/").content.decode()


def test_navegacao_marca_contribuir_nas_telas_da_contribuicao(client, cenario):
    diego = _entrar(client, cenario)
    manifestacao = cc.registrar(diego)
    for url in ("/contribuir/", "/contribuicoes/", f"/contribuicoes/{manifestacao.pk}/",
                f"/contribuicoes/{manifestacao.pk}/retirar/"):
        html = client.get(url).content.decode()
        nav = re.search(r'<nav class="navegacao".*?</nav>', html, re.S).group(0)
        assert re.findall(r'href="([^"]+)"[^>]*aria-current="page"', nav) == ["/contribuir/"], url
        assert 'action="/sair/"' in html and "--portal-profundo:" in html, url

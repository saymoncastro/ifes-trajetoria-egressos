"""Rodapé da Seção (014 US2, US3; FR-008 a FR-017; SC-002 a SC-005, SC-015).

Quatro ações: "Salvar e continuar" (principal), "Salvar e sair" (secundária), "Voltar à
seção anterior" e "Sair sem salvar esta seção" (terciárias). Os testes cobrem a Matriz de
comportamento do rodapé da spec, comparando o que está gravado antes e depois
(`c.retrato`), e a regra de verdade das mensagens de salvamento. Os testes conhecem Q1…Q54
pela `Baseline`; a interface não.
"""

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def _url(pk, posicao, consulta=""):
    return f"/participacoes/{pk}/secoes/{posicao}/{consulta}"


def _secao(client, pk, posicao, dados, *, sair=False):
    """POST na Seção; `sair=True` é o botão "Salvar e sair"."""
    dados = {k: v for k, v in dados.items() if v is not None}
    if sair:
        dados["depois"] = "sair"
    return client.post(_url(pk, posicao), dados)


def _ana_na_secao(client, cenario, posicao, escolhas=None):
    """Ana entra, inicia e tem as Seções anteriores do percurso respondidas, de modo que a
    Seção `posicao` é a atual. Devolve a Participação."""
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    participacao = Participacao.objects.get(pk=ci.participacao_de(resposta))
    escolhas = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim", **(escolhas or {})}
    percurso = c.secoes_esperadas(escolhas["Q1"], escolhas["Q14"], escolhas["Q33"], escolhas["Q46"])
    anteriores = [p for p in percurso if p < posicao]
    if anteriores:
        c.preencher(participacao, cenario.base, anteriores, escolhas)
    return participacao


def _completa(cenario, posicao, escolhas=None):
    return ci.dados_validos(
        ci.secao_do_conteudo(cenario.base.versao, posicao),
        ci.escolhas_por_id(cenario.base, escolhas or {}),
    )


def _parcial(cenario, posicao, quantas):
    dados = _completa(cenario, posicao)
    return {k: dados[k] for k in sorted(dados, key=lambda campo: int(campo[1:]))[:quantas]}


def _trajetoria(aviso):
    return f"/formacoes/?aviso={aviso}"


# --- Matriz de comportamento do rodapé (spec; contracts/rodape-secao.md) --------------------


def test_envio_completo(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    antes = len(c.retrato(ana)["respostas"])
    continuar = _secao(client, ana.pk, 2, _completa(cenario, 2))
    assert continuar.status_code == 302 and continuar["Location"] == _url(ana.pk, 3)
    assert len(c.retrato(ana)["respostas"]) > antes


def test_envio_completo_salvar_e_sair(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    antes = len(c.retrato(ana)["respostas"])
    resposta = _secao(client, ana.pk, 2, _completa(cenario, 2), sair=True)
    assert resposta.status_code == 302 and resposta["Location"] == _trajetoria("salvo")
    assert len(c.retrato(ana)["respostas"]) > antes


def test_envio_incompleto_salvar_e_sair_grava_e_diz_que_salvou(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    antes = len(c.retrato(ana)["respostas"])
    resposta = _secao(client, ana.pk, 2, _parcial(cenario, 2, 3), sair=True)
    assert resposta["Location"] == _trajetoria("salvo")
    assert len(c.retrato(ana)["respostas"]) == antes + 3
    texto = ci.texto_visivel(client.get(resposta["Location"]))
    assert "O que você respondeu nesta seção está salvo." in texto


def test_envio_sem_nenhuma_resposta_salvar_e_sair_nao_afirma_salvamento(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    antes = c.retrato(ana)
    resposta = _secao(client, ana.pk, 2, {}, sair=True)
    assert resposta.status_code == 302 and resposta["Location"] == _trajetoria("saida")
    assert c.retrato(ana) == antes
    texto = ci.texto_visivel(client.get(resposta["Location"]))
    assert "Você pode continuar a pesquisa quando quiser." in texto
    assert "salvo" not in texto


def test_respostas_removidas_salvar_e_sair_e_neutro(client, cenario):
    from trajetoria.participacao import operacoes as op

    escolhas = {"Q33": "Não", "Q46": "Não"}
    ana = _ana_na_secao(client, cenario, 11, escolhas)
    op.responder_escala(ana, cenario.base.q(48), 3)  # única Resposta da Seção 11 (opcional)
    resposta = _secao(client, ana.pk, 11, {"p3-remover": "1"}, sair=True)
    assert resposta["Location"] == _trajetoria("saida")
    assert cenario.base.q(48).id not in {r["pergunta_id"] for r in c.retrato(ana)["respostas"]}


def test_secao_so_opcional_vazia(client, db):
    from tests.participacao import construcao_entrada as ce
    from trajetoria.fonte_academica.simulada import FonteSimulada

    ce.incorporar(FonteSimulada(), "SIM-P-0001")
    inst = c.instrumento()
    c.campanha_aberta(inst.versao)
    pk = ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte("SIM-P-0001")))
    c.preencher_instrumento(Participacao.objects.get(pk=pk), inst)
    continuar = _secao(client, pk, 2, {})
    assert continuar["Location"] == f"/participacoes/{pk}/concluir/"
    sair = _secao(client, pk, 2, {}, sair=True)
    assert sair["Location"] == _trajetoria("saida")


@pytest.mark.parametrize("sair", [False, True])
def test_erro_de_forma_nada_gravado_e_saida_sem_salvar_disponivel(client, cenario, sair):
    ana = _ana_na_secao(client, cenario, 8)
    antes = c.retrato(ana)
    dados = _completa(cenario, 8)
    dados["p7"] = []
    dados["p7-complemento"] = "Texto fictício"
    resposta = _secao(client, ana.pk, 8, dados, sair=sair)
    assert resposta.status_code == 200 and c.retrato(ana) == antes
    html, texto = resposta.content.decode(), ci.texto_visivel(resposta)
    assert "Há problemas nesta seção" in texto
    assert '<a href="/formacoes/">Sair sem salvar esta seção</a>' in html
    assert f'<a href="{_url(ana.pk, 6)}">Voltar à seção anterior</a>' in html  # Graduação: S6


@pytest.mark.parametrize("sair", [False, True])
def test_secao_fora_do_percurso(client, cenario, sair):
    ana = _ana_na_secao(client, cenario, 2)
    antes = c.retrato(ana)
    resposta = _secao(client, ana.pk, 8, _completa(cenario, 8), sair=sair)
    assert resposta.status_code == 302
    assert resposta["Location"] == _url(ana.pk, 2, "?aviso=percurso")
    assert c.retrato(ana) == antes


@pytest.mark.parametrize("sair", [False, True])
def test_coleta_encerrada(client, cenario, relogio, sair):
    ana = _ana_na_secao(client, cenario, 2)
    antes = c.retrato(ana)
    relogio.agora = c.DEPOIS_DO_FIM
    ci.entrar_como(client, ana.conclusao.pessoa)
    resposta = _secao(client, ana.pk, 2, _completa(cenario, 2), sair=sair)
    assert resposta.status_code == 200 and c.retrato(ana) == antes
    assert "O período de resposta desta pesquisa foi encerrado." in ci.texto_visivel(resposta)


@pytest.mark.parametrize("sair", [False, True])
def test_participacao_concluida(client, cenario, sair):
    from trajetoria.participacao.operacoes import concluir

    ana = _ana_na_secao(client, cenario, 1)
    c.preencher(ana, cenario.base, [1], {"Q1": "Não"})
    concluir(ana)
    antes = c.retrato(ana)
    resposta = _secao(client, ana.pk, 1, _completa(cenario, 1, {"Q1": "Sim"}), sair=sair)
    assert resposta.status_code == 200 and c.retrato(ana) == antes
    assert "Esta pesquisa já foi respondida." in ci.texto_visivel(resposta)


def test_reenvio_repetido_de_salvar_e_sair(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    dados = _parcial(cenario, 2, 3)
    primeiro = _secao(client, ana.pk, 2, dados, sair=True)
    depois_do_primeiro = c.retrato(ana)
    segundo = _secao(client, ana.pk, 2, dados, sair=True)
    assert primeiro["Location"] == segundo["Location"] == _trajetoria("salvo")
    assert c.retrato(ana) == depois_do_primeiro


def test_salvar_e_sair_com_destino_de_finalizacao(client, cenario):
    ana = _ana_na_secao(client, cenario, 1)
    resposta = _secao(client, ana.pk, 1, _completa(cenario, 1, {"Q1": "Não"}), sair=True)
    assert resposta["Location"] == _trajetoria("salvo")
    assert client.get(f"/participacoes/{ana.pk}/")["Location"] == (
        f"/participacoes/{ana.pk}/concluir/"
    )


def test_valor_desconhecido_de_depois_equivale_a_continuar(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    dados = {**_completa(cenario, 2), "depois": "x"}
    assert client.post(_url(ana.pk, 2), dados)["Location"] == _url(ana.pk, 3)


def test_salvar_e_sair_e_retomar_vai_a_secao_atual(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    _secao(client, ana.pk, 2, _parcial(cenario, 2, 3), sair=True)
    retomada = client.post("/formacoes/entrar/")
    assert client.get(retomada["Location"])["Location"] == _url(ana.pk, 2)


# --- Tela do rodapé (FR-009, FR-013, FR-014) -----------------------------------------------


def test_quatro_acoes_na_ordem_e_com_hierarquia(client, cenario):
    ana = _ana_na_secao(client, cenario, 2)
    html = client.get(_url(ana.pk, 2)).content.decode()
    continuar = html.index('<button type="submit" class="primario">Salvar e continuar</button>')
    sair = html.index(
        '<button type="submit" name="depois" value="sair" class="secundario">Salvar e sair</button>'
    )
    saidas = html.index('<div class="saidas">')
    voltar = html.index(f'<a href="{_url(ana.pk, 1)}">Voltar à seção anterior</a>')
    sem_salvar = html.index('<a href="/formacoes/">Sair sem salvar esta seção</a>')
    assert continuar < sair < html.index("</form>", sair) < saidas < voltar < sem_salvar
    texto = ci.texto_visivel(client.get(_url(ana.pk, 2)))
    assert "O que já foi salvo antes continua guardado." in texto
    assert "Alterações não salvas nesta página serão descartadas." in texto
    assert "Sair e continuar depois" not in texto


def test_primeira_secao_sem_voltar(client, cenario):
    ana = _ana_na_secao(client, cenario, 1)
    html = client.get(_url(ana.pk, 1)).content.decode()
    assert "Voltar à seção anterior" not in html
    assert '<a href="/formacoes/">Sair sem salvar esta seção</a>' in html


# --- Enter/"Ir" não envia (014 US3; FR-016, FR-017) ----------------------------------------


def _botoes_de_envio(html: str) -> list[str]:
    """Os `<button>` e `<input type="submit">` do formulário da Seção, em ordem."""
    import re

    inicio = html.index('<form method="post" action="/participacoes/')
    formulario = html[inicio : html.index("</form>", inicio)]
    return re.findall(r'<button[^>]*>|<input[^>]*type="submit"[^>]*>', formulario)


@pytest.mark.parametrize("com_erro", [False, True])
def test_primeiro_botao_de_envio_bloqueia_o_envio_implicito(client, cenario, com_erro):
    """O botão padrão do formulário (o primeiro de envio) está desabilitado e oculto: Enter/
    "Ir" depois de digitar num campo de digitação não envia a Seção (FR-016; research R2,
    verificado no Chromium para texto curto e "Outro"). Os botões visíveis seguem ativos."""
    ana = _ana_na_secao(client, cenario, 3)
    if com_erro:
        html = _secao(client, ana.pk, 3, {"p2": "999"}).content.decode()
    else:
        html = client.get(_url(ana.pk, 3)).content.decode()
    assert 'type="text"' in html  # Seção com campo de texto (o ano)
    botoes = _botoes_de_envio(html)
    assert botoes[0].startswith("<button") and 'type="submit"' in botoes[0]
    assert " disabled" in botoes[0] and " hidden" in botoes[0]
    visiveis = botoes[1:]
    assert len(visiveis) == 2 and all("disabled" not in b and "hidden" not in b for b in visiveis)

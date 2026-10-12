"""Retorno à conclusão depois de revisar (Feature 033; spec FR-001 a FR-012).

Por requisição, sem navegador. Ana chega à conclusão pelo percurso "trabalha e estuda" da
baseline (9 partes). As Versões de teste cobrem o que a baseline não tem: Seção só de
opcionais num ramo e duas Seções novas em sequência.
"""

import re
from datetime import timedelta
from urllib.parse import urlsplit

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.interface import mensagens
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db

ANA = "SIM-P-0001"
_ESCOLHAS = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim"}
PERCURSO = c.secoes_esperadas("Sim", "Graduação", "Sim", "Sim")  # [1, 2, 3, 6, 8, 9, 11, 12, 13]
CAMINHO = mensagens.AVISOS["caminho"]
SALVA = mensagens.AVISOS["revisada"]


def _url(pk, sufixo=""):
    return f"/participacoes/{pk}/{sufixo}"


def _dados(cenario, posicao, escolhas=None, **extra):
    escolhas = {**_ESCOLHAS, **(escolhas or {})}
    secao = ci.secao_do_conteudo(cenario.base.versao, posicao)
    dados = ci.dados_validos(secao, ci.escolhas_por_id(cenario.base, escolhas))
    return {**dados, **extra}


def _em_revisao(client, cenario, pk, posicao, escolhas=None, **extra):
    """Envio da Seção aberta pela revisão (o formulário leva `revisao=1`)."""
    return client.post(
        _url(pk, f"secoes/{posicao}/"), _dados(cenario, posicao, escolhas, revisao="1", **extra)
    )


def _destino(resposta) -> str:
    assert resposta.status_code == 302, resposta.status_code
    return resposta["Location"]


def _links_da_revisao(html: str) -> list[str]:
    return re.findall(r'href="([^"]*\?revisao=1)"', html)


@pytest.fixture
def ana(client, cenario):
    """Ana na conclusão, pelo percurso "trabalha e estuda"."""
    participacao = Participacao.objects.get(
        pk=ci.participacao_de(ci.iniciar(client, cenario.pessoa(ANA)))
    )
    apresentadas, url = ci.percorrer_pela_interface(
        client, participacao.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, _ESCOLHAS)
    )
    assert apresentadas == PERCURSO and url == _url(participacao.pk, "concluir/")
    return participacao


# --- US1: corrigir e voltar à conclusão -------------------------------------------------------


def test_lista_da_revisao_abre_cada_parte_em_revisao(client, cenario, ana):
    html = client.get(_url(ana.pk, "concluir/")).content.decode()
    assert _links_da_revisao(html) == [
        _url(ana.pk, f"secoes/{p}/?revisao=1") for p in PERCURSO
    ]


def test_parte_aberta_pela_revisao(client, cenario, ana):
    resposta = client.get(_url(ana.pk, "secoes/2/?revisao=1"))
    html, texto = resposta.content.decode(), ci.texto_visivel(resposta)
    assert '<input type="hidden" name="revisao" value="1">' in html
    assert mensagens.SALVAR_E_VOLTAR in texto and "Salvar e continuar" not in texto
    assert "Parte 2 · revisando suas respostas" in texto and "faltam no máximo" not in texto
    assert "Salvar e sair" in texto  # FR-002d
    assert f'href="{_url(ana.pk, "secoes/1/?revisao=1")}"' in html  # anterior em revisão
    assert ci.TEXTO_FICTICIO in html  # as Respostas gravadas aparecem preenchidas
    assert CAMINHO not in texto


def test_sem_marcador_a_secao_e_a_de_hoje(client, cenario, ana):
    hoje = client.get(_url(ana.pk, "secoes/2/"))
    html, texto = hoje.content.decode(), ci.texto_visivel(hoje)
    assert 'name="revisao"' not in html
    assert "Salvar e continuar" in texto and mensagens.SALVAR_E_VOLTAR not in texto
    assert "faltam no máximo" in texto and "revisando" not in texto
    assert f'href="{_url(ana.pk, "secoes/1/")}"' in html
    # Valor diferente de "1" é ignorado: a mesma tela, inclusive o aviso de lista fechada.
    outro = client.get(_url(ana.pk, "secoes/2/?revisao=sim&aviso=caminho"))
    assert ci.texto_visivel(outro) == texto
    assert 'name="revisao"' not in outro.content.decode()


def test_corrigir_uma_resposta_volta_a_conclusao(client, cenario, ana):
    secao = ci.secao_do_conteudo(cenario.base.versao, 2)
    texto_curto = next(p for p in secao.perguntas if p.obrigatoria and p.tipo == "TEXTO_CURTO")
    resposta = _em_revisao(
        client, cenario, ana.pk, 2, **{f"p{texto_curto.posicao}": "valor corrigido"}
    )
    assert _destino(resposta) == _url(ana.pk, "concluir/?aviso=revisada&secao=2")
    gravada = Resposta.objects.get(participacao=ana, pergunta_id=texto_curto.id)
    assert gravada.texto == "valor corrigido"
    texto = ci.texto_visivel(client.get(resposta["Location"]))
    assert SALVA in texto and "Concluir pesquisa" in texto


def test_salvar_sem_mudar_volta_a_conclusao(client, cenario, ana):
    assert _destino(_em_revisao(client, cenario, ana.pk, 2)).startswith(_url(ana.pk, "concluir/"))


@pytest.mark.parametrize("posicao", PERCURSO)
def test_qualquer_parte_custa_um_envio(client, cenario, ana, posicao):
    """SC-001: sem mudar o caminho, 1 envio a partir da conclusão, em qualquer parte."""
    destino = _destino(_em_revisao(client, cenario, ana.pk, posicao))
    assert destino == _url(ana.pk, f"concluir/?aviso=revisada&secao={posicao}")


def test_deixar_de_estudar_tira_a_parte_e_volta_direto(client, cenario, ana):
    destino = _destino(_em_revisao(client, cenario, ana.pk, 11, {"Q46": "Não"}))
    assert destino.startswith(_url(ana.pk, "concluir/"))
    links = _links_da_revisao(client.get(destino).content.decode())
    assert len(links) == 8 and _url(ana.pk, "secoes/12/?revisao=1") not in links


# --- US2: alteração que muda o caminho ------------------------------------------------------


def test_parar_de_trabalhar_passa_pela_parte_nova(client, cenario, ana):
    destino = _destino(_em_revisao(client, cenario, ana.pk, 8, {"Q33": "Não"}))
    assert destino == _url(ana.pk, "secoes/10/?revisao=1&aviso=caminho")
    tela = client.get(destino)
    html, texto = tela.content.decode(), ci.texto_visivel(tela)
    assert CAMINHO in texto and 'name="revisao" value="1"' in html
    # SC-002: a parte nova e, depois, a conclusão — 2 envios, sem refazer Estudo e seguintes.
    assert _destino(_em_revisao(client, cenario, ana.pk, 10)) == _url(
        ana.pk, "concluir/?aviso=revisada&secao=10"
    )


def test_parte_que_volta_com_respostas_antigas_nao_e_reapresentada(client, cenario, ana):
    _em_revisao(client, cenario, ana.pk, 8, {"Q33": "Não"})
    _em_revisao(client, cenario, ana.pk, 10)
    # De novo "Sim": "Egresso que trabalha" volta com as Respostas antigas (inativas até agora).
    destino = _destino(_em_revisao(client, cenario, ana.pk, 8, {"Q33": "Sim"}))
    assert destino == _url(ana.pk, "concluir/?aviso=revisada&secao=8")


def _participacao_com(client, *secoes):
    ce.incorporar(FonteSimulada(), ANA)
    versao = c.versao_publicada_de(*secoes)
    c.campanha_aberta(versao)
    return ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte(ANA)))


def test_parte_nova_so_de_opcionais_aparece_antes_da_conclusao(client, db):
    # S1 decide: "Sim" → S2 (só opcional), "Não" → S3.
    pk = _participacao_com(
        client,
        secao_mem(pergunta_mem(regras={"Sim": 2, "Não": 3})),
        secao_mem(pergunta_mem(obrigatoria=False)),
        secao_mem(pergunta_mem()),
    )
    destino = _destino(client.post(_url(pk, "secoes/1/"), {"p1": "2"}))
    assert destino == _url(pk, "secoes/3/?aviso=anterior")
    assert _destino(client.post(_url(pk, "secoes/3/"), {"p1": "1"})) == _url(pk, "concluir/")
    # Revisão: "Sim" faz entrar S2, satisfeita (só opcional) e nunca respondida.
    destino = _destino(client.post(_url(pk, "secoes/1/"), {"p1": "1", "revisao": "1"}))
    assert destino == _url(pk, "secoes/2/?revisao=1&aviso=caminho")
    # Salva em branco: segue adiante, sem voltar para a mesma parte (US2.4).
    destino = _destino(client.post(_url(pk, "secoes/2/"), {"revisao": "1"}))
    assert destino == _url(pk, "concluir/?aviso=revisada&secao=2")
    # Nada foi gravado em S2: "Parte salva." não aparece (FR-007; 014 FR-008).
    assert SALVA not in ci.texto_visivel(client.get(destino))


def test_varias_partes_novas_em_ordem(client, db):
    # S1 decide: "Sim" → S2, S3 e S4; "Não" → S4.
    pk = _participacao_com(
        client,
        secao_mem(pergunta_mem(regras={"Sim": 2, "Não": 4})),
        secao_mem(pergunta_mem()),
        secao_mem(pergunta_mem()),
        secao_mem(pergunta_mem()),
    )
    client.post(_url(pk, "secoes/1/"), {"p1": "2"})
    assert _destino(client.post(_url(pk, "secoes/4/"), {"p1": "1"})) == _url(pk, "concluir/")
    destinos = [
        _destino(client.post(_url(pk, f"secoes/{n}/"), {"p1": "1", "revisao": "1"}))
        for n in (1, 2, 3)
    ]
    assert destinos == [
        _url(pk, "secoes/2/?revisao=1&aviso=caminho"),
        _url(pk, "secoes/3/?revisao=1&aviso=caminho"),
        _url(pk, "concluir/?aviso=revisada&secao=3"),
    ]


# --- US3: erros, sessão vencida e saídas ------------------------------------------------------


def test_erro_de_forma_continua_em_revisao(client, cenario, ana):
    antes = Resposta.objects.filter(participacao=ana).count()
    resposta = client.post(_url(ana.pk, "secoes/11/"), {"p1": "99", "revisao": "1"})
    assert resposta.status_code == 200
    html, texto = resposta.content.decode(), ci.texto_visivel(resposta)
    assert '<div class="resumo-erros' in html and 'name="revisao" value="1"' in html
    assert mensagens.SALVAR_E_VOLTAR in texto
    assert Resposta.objects.filter(participacao=ana).count() == antes


def test_pendencia_continua_em_revisao_e_nao_chega_a_conclusao(client, cenario, ana):
    q46 = cenario.base.q(46)
    resposta = client.post(_url(ana.pk, "secoes/11/"), {"p1-remover": "1", "revisao": "1"})
    assert not Resposta.objects.filter(participacao=ana, pergunta=q46).exists()
    assert _destino(resposta) == _url(ana.pk, "secoes/11/?pendencias=1&revisao=1")
    tela = client.get(resposta["Location"])
    assert 'name="revisao" value="1"' in tela.content.decode()
    assert client.get(_url(ana.pk, "concluir/"))["Location"] == _url(ana.pk, "secoes/11/")


def test_envio_pendente_restaurado_continua_em_revisao(client, cenario, ana, settings, relogio):
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=1)
    relogio.agora += timedelta(seconds=61)
    assert _destino(_em_revisao(client, cenario, ana.pk, 2)) == "/acesso/?aviso=sessao"
    ci.entrar_como(client, cenario.pessoa(ANA))
    tela = client.get(_url(ana.pk, "secoes/2/"))
    assert mensagens.RECUPERADO in ci.texto_visivel(tela)
    assert 'name="revisao" value="1"' in tela.content.decode()
    assert _destino(_em_revisao(client, cenario, ana.pk, 2)).startswith(_url(ana.pk, "concluir/"))


def test_salvar_e_sair_em_revisao_e_o_de_hoje(client, cenario, ana):
    resposta = _em_revisao(client, cenario, ana.pk, 2, depois="sair")
    assert _destino(resposta) == "/formacoes/?aviso=salvo"


# --- US4: fronteiras ---------------------------------------------------------------------------


def test_marcador_forjado_no_primeiro_preenchimento_nao_pula_nada(client, cenario):
    pk = ci.participacao_de(ci.iniciar(client, cenario.pessoa(ANA)))
    url, apresentadas = _url(pk, "secoes/1/"), []
    for _ in range(len(PERCURSO) + 1):
        posicao = ci.posicao_da_url(url)
        if posicao is None:
            break
        apresentadas.append(posicao)
        url = _destino(_em_revisao(client, cenario, pk, posicao))
    assert apresentadas == PERCURSO
    assert urlsplit(url).path == _url(pk, "concluir/")


def test_marcador_nao_abre_secao_fora_do_percurso(client, cenario, ana):
    resposta = client.get(_url(ana.pk, "secoes/10/?revisao=1"))
    assert resposta["Location"] == _url(ana.pk, "concluir/?aviso=percurso")


def test_marcador_depois_de_concluida_e_com_coleta_encerrada(client, cenario, ana, relogio):
    relogio.agora = c.DEPOIS_DO_FIM
    ci.entrar_como(client, cenario.pessoa(ANA))
    texto = ci.texto_visivel(_em_revisao(client, cenario, ana.pk, 2))
    assert mensagens.PERIODO_ENCERRADO[0] in texto
    relogio.agora = c.NO_PERIODO
    ci.entrar_como(client, cenario.pessoa(ANA))
    assert client.post(_url(ana.pk, "concluir/"))["Location"] == _url(ana.pk, "concluida/")
    texto = ci.texto_visivel(_em_revisao(client, cenario, ana.pk, 2))
    assert mensagens.JA_RESPONDIDA[0] in texto


@pytest.mark.parametrize("secao", ["99", "10", "abc", ""])
def test_parte_salva_nunca_pela_simples_presenca_do_codigo(client, cenario, ana, secao):
    texto = ci.texto_visivel(client.get(_url(ana.pk, f"concluir/?aviso=revisada&secao={secao}")))
    assert SALVA not in texto

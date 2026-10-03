"""Avanço segundo a 006 (008 US5, US7; FR-050 a FR-055; SC-004, SC-005).

A interface nunca calcula destino: segue `situacao_da_jornada` da 006. Os testes conhecem
Q1…Q54 pela `Baseline`; a interface não.
"""

import re

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def ana(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


def _url(participacao, posicao, consulta=""):
    return f"/participacoes/{participacao.pk}/secoes/{posicao}/{consulta}"


def _enviar(client, participacao, base, posicao, escolhas=None, **trocas):
    dados = ci.dados_validos(
        ci.secao_do_conteudo(base.versao, posicao), ci.escolhas_por_id(base, escolhas or {})
    )
    dados.update(trocas)
    dados = {k: v for k, v in dados.items() if v is not None}
    return client.post(_url(participacao, posicao), dados)


def _pendencias_na_tela(html: str) -> set[str]:
    """Ids das Perguntas que mostram "Esta pergunta é obrigatória."."""
    ids = set()
    for bloco in re.finditer(r'id="(p\d+)"(.*?)(?=class="pergunta|</form>)', html, re.S):
        if "Esta pergunta é obrigatória." in bloco.group(2):
            ids.add(bloco.group(1))
    return ids


def test_s1_sim_vai_para_s2_e_seguir_nao_regrava(client, cenario, ana):
    resposta = _enviar(client, ana, cenario.base, 1, {"Q1": "Sim"})
    assert resposta.status_code == 302 and resposta["Location"] == _url(ana, 2)
    antes = c.retrato(ana)
    assert client.get(resposta["Location"]).status_code == 200
    assert c.retrato(ana) == antes


def test_obrigatoria_em_branco_volta_com_a_pendencia_da_006(client, cenario, ana):
    b = cenario.base
    _enviar(client, ana, b, 1, {"Q1": "Sim"})
    resposta = _enviar(client, ana, b, 2, p2=None)  # Q3 (texto) em branco
    assert resposta["Location"] == _url(ana, 2, "?pendencias=1")
    pendentes = situacao_da_jornada(ana).passagens[-1].pendentes
    esperadas = {
        f"p{p.posicao}" for p in ci.secao_do_conteudo(b.versao, 2).perguntas if p.id in pendentes
    }
    tela = client.get(resposta["Location"])
    html = tela.content.decode()
    assert _pendencias_na_tela(html) == esperadas == {"p2"}
    assert "<title>Faltam respostas: " in html  # pendência não é erro (014 FR-007)
    assert "O que você respondeu nesta seção está salvo." in ci.texto_visivel(tela)
    assert b.q(2).id in situacao_da_jornada(ana).respostas  # demais respostas gravadas


def test_pendencias_so_na_secao_atual_nao_satisfeita(client, cenario, ana):
    b = cenario.base
    _enviar(client, ana, b, 1, {"Q1": "Sim"})
    html = client.get(_url(ana, 1, "?pendencias=1")).content.decode()
    assert _pendencias_na_tela(html) == set() and "<title>Erro: " not in html
    html = client.get(_url(ana, 2)).content.decode()  # primeira visita: sem pendências
    assert _pendencias_na_tela(html) == set()


def test_destino_e_o_da_006_inclusive_encaminhamento(client, cenario, ana):
    b = cenario.base
    escolhas = {"Q1": "Sim", "Q14": "Graduação"}
    for posicao, destino in ((1, 2), (2, 3), (3, 6), (6, 8)):
        resposta = _enviar(client, ana, b, posicao, escolhas)
        passagem = next(
            p for p in situacao_da_jornada(ana).passagens if p.secao.posicao == posicao
        )
        secoes = conteudo_da_versao(b.versao).secoes
        destino_006 = next(s.posicao for s in secoes if s.id == passagem.destino)
        assert destino_006 == destino
        assert resposta["Location"] == _url(ana, destino)


def test_ultima_secao_leva_a_conclusao(client, cenario, ana):
    resposta = _enviar(client, ana, cenario.base, 1, {"Q1": "Não"})
    assert resposta["Location"] == f"/participacoes/{ana.pk}/concluir/"


# --- Ramos reais da baseline e Versão diferente (US7) ---------------------------------------


@pytest.mark.parametrize("q1, q14, q33, q46", list(c.combinacoes_baseline()))
def test_17_percursos_pela_interface(client, cenario, ana, q1, q14, q33, q46):
    escolhas = c.escolhas_baseline(q1, q14, q33, q46)
    apresentadas, fim = ci.percorrer_pela_interface(
        client, ana.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, escolhas)
    )
    assert apresentadas == c.secoes_esperadas(q1, q14, q33, q46)
    assert fim == f"/participacoes/{ana.pk}/concluir/"


def test_versao_de_estrutura_diferente_e_seguida_sem_mudar_a_interface(client):
    inst = c.instrumento()  # 2 Seções; "Não" na primeira Pergunta finaliza
    c.campanha_aberta(inst.versao)
    ce.incorporar(FonteSimulada(), "SIM-P-0001", "SIM-P-0005")
    for id_externo, resposta, esperado in (
        ("SIM-P-0001", "Sim", [1, 2]),
        ("SIM-P-0005", "Não", [1]),
    ):
        participacao = ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte(id_externo)))
        apresentadas, fim = ci.percorrer_pela_interface(
            client, participacao, inst.versao, {inst.unica.id: resposta}
        )
        assert apresentadas == esperado and fim.endswith("/concluir/")
        jornada = situacao_da_jornada(Participacao.objects.get(pk=participacao))
        assert [p.secao.posicao for p in jornada.passagens] == esperado and jornada.finalizada


def test_revisitar_s3_e_trocar_o_ramo(client, cenario, ana):
    b = cenario.base
    escolhas = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Não"}
    for posicao in (1, 2, 3, 6, 8, 9, 11):
        _enviar(client, ana, b, posicao, escolhas)
    resposta = _enviar(client, ana, b, 3, {**escolhas, "Q14": "Pós-Graduação"})
    assert resposta["Location"] == _url(ana, 7)
    assert client.get(_url(ana, 6))["Location"].startswith(_url(ana, 7))  # S6 fora do percurso
    assert "Você é egresso(a) de qual Curso?" in ci.texto_visivel(client.get(_url(ana, 7)))


def test_voltar_a_secao_anterior_do_percurso(client, cenario, ana):
    b = cenario.base
    escolhas = {"Q1": "Sim", "Q14": "Graduação"}
    for posicao in (1, 2, 3, 6):
        _enviar(client, ana, b, posicao, escolhas)
    html = client.get(_url(ana, 8)).content.decode()
    assert f'href="{_url(ana, 6)}">Voltar à seção anterior' in html  # anterior no percurso
    assert "Alterações não salvas nesta página serão descartadas." in html
    assert "Voltar à seção anterior" not in client.get(_url(ana, 1)).content.decode()
    antes = c.retrato(ana)
    client.get(_url(ana, 6))
    assert c.retrato(ana) == antes


def test_mensagem_de_salvo_so_depois_de_gravar(client, cenario, ana):
    b = cenario.base
    _enviar(client, ana, b, 1, {"Q1": "Sim"})
    texto = ci.texto_visivel(client.get(_url(ana, 2, "?pendencias=1")))
    assert "Esta pergunta é obrigatória." in texto
    assert "nesta seção está salvo" not in texto  # nada gravado na Seção 2 ainda (014 FR-008)
    destino = _enviar(client, ana, b, 2, p2=None)["Location"]
    assert "O que você respondeu nesta seção está salvo." in ci.texto_visivel(
        client.get(destino)
    )


def test_formulario_envia_sem_a_query_string(client, cenario, ana):
    _enviar(client, ana, cenario.base, 1, {"Q1": "Sim"})
    html = client.get(_url(ana, 2, "?aviso=percurso&pendencias=1")).content.decode()
    assert f'<form method="post" action="{_url(ana, 2)}"' in html
    texto = ci.texto_visivel(client.post(_url(ana, 2), {"p1": "99"}))
    assert "mudaram o caminho" not in texto and "Selecione uma das opções" in texto


def test_destino_e_a_passagem_seguinte_do_percurso(client, cenario, ana):
    b = cenario.base
    escolhas = {"Q1": "Sim", "Q14": "Pós-Graduação"}
    for posicao in (1, 2):
        _enviar(client, ana, b, posicao, escolhas)
    assert _enviar(client, ana, b, 3, escolhas)["Location"] == _url(ana, 7)
    assert _enviar(client, ana, b, 7, escolhas)["Location"] == _url(ana, 8)  # encaminhamento

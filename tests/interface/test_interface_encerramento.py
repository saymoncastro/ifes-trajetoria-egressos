"""Encerramento da Campanha durante o preenchimento — E2E-4 (008 US13; FR-065, FR-066).

A interface não avalia período: traduz as rejeições da 005/006 e o `admite_escrita` da
jornada. O tempo é controlado pela fixture `relogio`.
"""

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.campanha.operacoes import encerrar
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

ENCERRADO = "O período de resposta desta pesquisa foi encerrado."
PRESERVADAS = "As respostas salvas anteriormente foram preservadas."


@pytest.fixture
def ana(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


def _url(participacao, sufixo=""):
    return f"/participacoes/{participacao.pk}/{sufixo}"


def _dados_s1(cenario, texto):
    secao = ci.secao_do_conteudo(cenario.base.versao, 1)
    return ci.dados_validos(secao, ci.escolhas_por_id(cenario.base, {"Q1": texto}))


@pytest.mark.parametrize("forma", ["por_data", "explicita"])
def test_envio_depois_do_encerramento(client, cenario, ana, relogio, forma):
    c.preencher(ana, cenario.base, [1], {"Q1": "Sim"})
    assert client.get(_url(ana, "secoes/2/")).status_code == 200
    if forma == "por_data":
        relogio.agora = c.DEPOIS_DO_FIM
    else:
        encerrar(cenario.campanha, agora=c.momento(2027, 5, 2))
        relogio.agora = c.momento(2027, 5, 3)
    # 018: o salto de dias exige uma nova sessão para testar somente o período.
    ci.entrar_como(client, ana.conclusao.pessoa)
    antes = c.retrato(ana)
    dados = ci.dados_validos(ci.secao_do_conteudo(cenario.base.versao, 2))
    resposta = client.post(_url(ana, "secoes/2/"), dados)
    texto = ci.texto_visivel(resposta)
    assert resposta.status_code == 200 and ENCERRADO in texto and PRESERVADAS in texto
    assert 'action="/participacoes/' not in resposta.content.decode()
    assert c.retrato(ana) == antes
    for sufixo in ("", "secoes/2/", "concluir/"):
        assert ENCERRADO in ci.texto_visivel(client.get(_url(ana, sufixo)))
    assert ENCERRADO in ci.texto_visivel(client.post(_url(ana, "concluir/")))
    ana.refresh_from_db()
    assert ana.concluida_em is None and c.retrato(ana) == antes
    formacoes = ci.texto_visivel(client.get("/formacoes/"))
    # 014 FR-036: a situação geral aparece uma vez; "sem pesquisa" não se repete por formação.
    assert "No momento, não há pesquisa disponível para as suas formações." in formacoes
    assert "Sem pesquisa disponível no momento." not in formacoes
    assert "prazo" not in formacoes.lower()


def test_conclusao_finalizada_depois_do_fim(client, cenario, ana, relogio):
    client.post(_url(ana, "secoes/1/"), _dados_s1(cenario, "Não"))
    relogio.agora = c.DEPOIS_DO_FIM
    ci.entrar_como(client, ana.conclusao.pessoa)
    assert ENCERRADO in ci.texto_visivel(client.post(_url(ana, "concluir/")))
    ana.refresh_from_db()
    assert ana.concluida_em is None


def test_ultimo_dia_ainda_aceita(client, cenario, ana, relogio):
    relogio.agora = c.ULTIMO_DIA
    ci.entrar_como(client, ana.conclusao.pessoa)
    resposta = client.post(_url(ana, "secoes/1/"), _dados_s1(cenario, "Não"))
    assert resposta["Location"] == _url(ana, "concluir/")
    assert client.post(_url(ana, "concluir/"))["Location"] == _url(ana, "concluida/")

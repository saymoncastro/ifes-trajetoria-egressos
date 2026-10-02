"""Cenário fictício da exportação: o mesmo de referência da 012 (spec 012, "Dados de
referência"), montado por `tests/analitico/construcao.cenario_de_referencia`, e uma chave de
pseudonimização fictícia (nunca real; DP-1301)."""

import pytest

from tests.analitico import construcao as c
from tests.participacao.construcao import instrumento

CHAVE_FICTICIA = "chave-ficticia-de-teste-da-exportacao-0000000001"


@pytest.fixture(autouse=True)
def chave_ficticia(settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = CHAVE_FICTICIA
    return CHAVE_FICTICIA


@pytest.fixture
def inst():
    return instrumento()


@pytest.fixture
def cenario(inst) -> c.Cenario:
    return c.cenario_de_referencia(inst)


@pytest.fixture
def snapshot(cenario):
    from trajetoria.analitico.operacoes import capturar_snapshot

    return capturar_snapshot(cenario.campanha)

"""Fixtures dos testes de Participação. `fonte_simulada` vem de `tests/conftest.py`."""

import pytest

from tests.participacao import construcao as c


@pytest.fixture
def inst():
    return c.instrumento()


@pytest.fixture
def campanha(inst):
    return c.campanha_aberta(inst.versao, ano_minimo=2020)


@pytest.fixture
def conclusao():
    return c.conclusao(ano=2022)


@pytest.fixture
def participacao(campanha, conclusao):
    # Import tardio: `operacoes.py` só existe a partir de T010 (tasks, F1).
    from trajetoria.participacao.operacoes import iniciar_participacao

    return iniciar_participacao(campanha, conclusao, agora=c.NO_PERIODO).participacao

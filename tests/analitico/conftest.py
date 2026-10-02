"""Cenário de referência fictício do snapshot analítico (spec, "Dados de referência").

Campanha E: critério de unidades {Serra, Vitória}, aberta no passado e já ENCERRADA pelo fim
do período. Universo esperado: as cinco Conclusões de Serra e Vitória (elegíveis); Cefor e
"sem unidade" ficam fora (não elegíveis e sem Participação).
"""

import pytest

from tests.analitico import construcao as c
from tests.participacao.construcao import instrumento


@pytest.fixture
def inst():
    return instrumento()


@pytest.fixture
def cenario(inst) -> c.Cenario:
    return c.cenario_de_referencia(inst)


@pytest.fixture
def campanha_v(inst):
    """Encerrada, sem Participações, com elegíveis."""
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Cefor"])
    c.conclusao(unidade="Cefor", ano=2020)
    c.conclusao(unidade="Cefor", ano=2021)
    return campanha


@pytest.fixture
def campanha_c(inst):
    return c.campanha_em_coleta(inst.versao)


@pytest.fixture
def campanha_p(inst):
    return c.campanha_nunca_aberta(inst.versao)


@pytest.fixture
def campanha_x(inst):
    return c.campanha_nunca_aberta(inst.versao, expirada=True)

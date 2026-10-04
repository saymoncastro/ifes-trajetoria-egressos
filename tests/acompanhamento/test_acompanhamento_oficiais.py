import pytest

from tests.declaracao.construcao import declaracao_concluida, validar
from tests.participacao import construcao as c
from trajetoria.acompanhamento.consultas import Recorte, _linhas, indicadores_da_campanha
from trajetoria.governanca.regras import EscopoDeAcompanhamento

pytestmark = pytest.mark.django_db


def test_oficiais_e_escopo():
    campanha = c.campanha_aberta(c.instrumento().versao)
    x = c.conclusao(unidade="Vitória")
    f = declaracao_concluida(campanha, unidade="Serra")
    escopo = EscopoDeAcompanhamento(False, frozenset({"Vitória"}))
    assert indicadores_da_campanha(campanha, escopo).iniciadas == 0
    validar(f, x)
    i = indicadores_da_campanha(campanha, escopo)
    assert (i.elegiveis, i.iniciadas, i.concluidas) == (1, 1, 1)
    assert _linhas(campanha, escopo, Recorte.UNIDADE)[0].chave == ("Vitória",)

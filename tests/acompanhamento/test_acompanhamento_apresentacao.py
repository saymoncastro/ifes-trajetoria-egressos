"""Apresentação pura do acompanhamento (Feature 011; research R8, R9, R10; spec FR-034 a
FR-038, FR-056). Sem banco."""

from decimal import Decimal

import pytest

from trajetoria.acompanhamento.apresentacao import (
    Indicadores,
    chave_de_ordem,
    percentual,
    rotulo_nao_concluidas,
)
from trajetoria.campanha.consultas import EstadoCampanha


def test_nao_concluidas_e_iniciadas_menos_concluidas():
    assert Indicadores(10, 4, 1).nao_concluidas == 3


@pytest.mark.parametrize(
    ("numerador", "denominador", "esperado"),
    [(1, 8, "12.5"), (1, 3, "33.3"), (2, 3, "66.7"), (9, 8, "112.5"), (0, 5, "0.0")],
)
def test_taxas_decimal_uma_casa_arredondamento_para_cima_no_meio(numerador, denominador, esperado):
    indicadores = Indicadores(denominador, numerador, numerador)
    assert indicadores.taxa_inicio == Decimal(esperado)
    assert indicadores.taxa_conclusao == Decimal(esperado)


def test_meio_arredonda_para_cima():
    # 1/16 = 6,25% → 6,3% (não arredondamento bancário).
    assert Indicadores(16, 1, 0).taxa_inicio == Decimal("6.3")


def test_denominador_zero_nao_se_aplica():
    indicadores = Indicadores(0, 2, 1)
    assert indicadores.taxa_inicio is None
    assert indicadores.taxa_conclusao is None


def test_sem_teto_de_cem_por_cento():
    assert Indicadores(1, 2, 2).taxa_conclusao == Decimal("200.0")


def test_soma():
    assert Indicadores(3, 2, 1) + Indicadores(4, 1, 0) == Indicadores(7, 3, 1)


def test_percentual():
    assert percentual(None) is None
    assert percentual(Decimal("30.0")) == "30,0%"
    assert percentual(Decimal("112.5")) == "112,5%"


def test_ordem_textual_com_nao_informado_por_ultimo_sem_fundir():
    chaves = [("Viana",), (None,), ("Águia Branca",), ("alegre",), ("Alegre",)]
    ordenadas = sorted(chaves, key=chave_de_ordem)
    assert ordenadas == [("Águia Branca",), ("Alegre",), ("alegre",), ("Viana",), (None,)]


def test_ordem_de_ano_crescente():
    assert sorted([(2024,), (None,), (2019,)], key=chave_de_ordem) == [(2019,), (2024,), (None,)]


def test_ordem_de_chave_composta():
    chaves = [("Vitória", "B"), (None, "A"), ("Serra", None), ("Serra", "A")]
    assert sorted(chaves, key=chave_de_ordem) == [
        ("Serra", "A"),
        ("Serra", None),
        ("Vitória", "B"),
        (None, "A"),
    ]


def test_rotulo_nao_concluidas():
    assert rotulo_nao_concluidas(EstadoCampanha.EM_COLETA) == "Em andamento"
    for estado in (EstadoCampanha.EM_PREPARACAO, EstadoCampanha.ENCERRADA):
        assert rotulo_nao_concluidas(estado) == "Iniciadas e não concluídas"

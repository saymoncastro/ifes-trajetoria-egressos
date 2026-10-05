"""Contrato da capacidade de contexto da trajetória (021 P2; data-model §1;
contracts/contexto-da-trajetoria.md). Separada da `FonteAcademica` (FR-071)."""

from datetime import date
from pathlib import Path

import pytest

from trajetoria.fonte_academica import contexto_da_trajetoria as ct

APURACAO = date(2026, 1, 31)


def _agregado(**campos):
    base = dict(
        metrica=ct.MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO,
        unidade="Serra", ano=2022, valor=27, apurado_em=APURACAO, curso="TADS",
    )
    return ct.AgregadoNaFonte(**(base | campos))


def test_complemento_valido_e_invalidos():
    assert ct.ComplementoNaFonte("SIM-C-0001", 2019).data_ingresso is None
    with pytest.raises(ValueError):
        ct.ComplementoNaFonte("", 2019)
    with pytest.raises(ValueError):
        ct.ComplementoNaFonte("SIM-C-0001", 2019, date(2018, 2, 1))


def test_curso_conforme_a_metrica():
    assert _agregado().curso == "TADS"
    with pytest.raises(ValueError):
        _agregado(curso=None)
    unidade = _agregado(metrica=ct.MetricaAgregada.CONCLUSOES_UNIDADE_ANO, curso=None)
    assert unidade.curso is None
    with pytest.raises(ValueError):
        _agregado(metrica=ct.MetricaAgregada.CONCLUSOES_UNIDADE_ANO)


@pytest.mark.parametrize("campos", [{"valor": -1}, {"unidade": ""}, {"curso": ""}])
def test_agregado_invalido(campos):
    with pytest.raises(ValueError):
        _agregado(**campos)


def test_resposta_sem_repeticao():
    with pytest.raises(ValueError):
        ct.ContextoDaTrajetoriaNaFonte(
            (ct.ComplementoNaFonte("SIM-C-0001", 2019), ct.ComplementoNaFonte("SIM-C-0001", 2018)),
            (),
        )
    with pytest.raises(ValueError):
        ct.ContextoDaTrajetoriaNaFonte((), (_agregado(), _agregado(valor=28)))
    with pytest.raises(TypeError):
        ct.ContextoDaTrajetoriaNaFonte([], ())


def test_duas_metricas_fechadas():
    assert [m.value for m in ct.MetricaAgregada] == [
        "conclusoes_curso_unidade_ano", "conclusoes_unidade_ano",
    ]


def test_valores_iguais_aos_da_narrativa():
    from trajetoria.narrativa import contrato

    assert ct.MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO.value == (
        contrato.METRICA_CURSO_UNIDADE_ANO
    )
    assert ct.MetricaAgregada.CONCLUSOES_UNIDADE_ANO.value == contrato.METRICA_UNIDADE_ANO


def test_python_puro_e_contrato_fundamental_intocado():
    fonte = Path(ct.__file__).read_text(encoding="utf-8")
    assert "django" not in fonte
    contrato = Path("trajetoria/fonte_academica/contrato.py").read_text(encoding="utf-8")
    for nome in ("ComplementoNaFonte", "AgregadoNaFonte", "MetricaAgregada",
                 "ContextoDaTrajetoria", "ingresso"):
        assert nome not in contrato, nome

"""Fonte simulada de contexto da trajetória (021 R18; FR-063, FR-064)."""

from collections import Counter
from datetime import date

import pytest

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contexto_da_trajetoria import ContextoIndisponivel, MetricaAgregada
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado

APURACAO = date(2026, 1, 31)
M1, M2 = MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO, MetricaAgregada.CONCLUSOES_UNIDADE_ANO


def _resumo(contexto):
    return [(a.metrica, a.curso, a.unidade, a.ano, a.valor, a.apurado_em)
            for a in contexto.agregados]


def test_codigo_igual_ao_da_fonte_academica():
    assert ContextoSimulado().codigo == "simulada"


def test_ana_com_ingresso_e_dois_agregados():
    contexto = ContextoSimulado().obter_contexto(("SIM-C-0001",))
    assert [(c.id_externo_conclusao, c.ano_ingresso) for c in contexto.complementos] == [
        ("SIM-C-0001", 2019)
    ]
    assert _resumo(contexto) == [
        (M1, cenarios.TADS, "Serra", 2022, 27, APURACAO),
        (M2, None, "Serra", 2022, 812, APURACAO),
    ]


def test_maria_sem_complemento_e_nada_para_o_cefor():
    contexto = ContextoSimulado().obter_contexto(("SIM-C-0004", "SIM-C-0005"))
    assert contexto.complementos == ()
    assert [a.unidade for a in contexto.agregados] == ["Serra", "Serra"]


def test_diego_nada():
    contexto = ContextoSimulado().obter_contexto(("SIM-C-0006", "SIM-C-0007", "SIM-C-0008"))
    assert contexto.complementos == () and contexto.agregados == ()


def test_so_ids_pedidos_e_reconhecidos():
    assert ContextoSimulado().obter_contexto(("SIM-C-0004",)).complementos == ()
    assert ContextoSimulado().obter_contexto(("SIM-C-0901",)).agregados == ()  # matrícula


def test_indisponivel():
    with pytest.raises(ContextoIndisponivel):
        ContextoSimulado(indisponivel=True).obter_contexto(("SIM-C-0001",))


def test_deterministico():
    ids = ("SIM-C-0004", "SIM-C-0001")
    assert ContextoSimulado().obter_contexto(ids) == ContextoSimulado().obter_contexto(ids)


def test_agregados_coerentes_com_as_conclusoes_simuladas():
    concluidas = [r for r in cenarios.REGISTROS if r.situacao == cenarios.CONCLUIDA]
    por_curso = Counter((r.curso, r.unidade, r.ano_conclusao) for r in concluidas)
    por_unidade = Counter((r.unidade, r.ano_conclusao) for r in concluidas)
    for metrica, curso, unidade, ano, valor, _ in cenarios.AGREGADOS:
        local = por_curso[(curso, unidade, ano)] if curso else por_unidade[(unidade, ano)]
        assert valor >= local, (metrica, curso, unidade, ano)

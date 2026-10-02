"""Contexto acadêmico congelado (US4; spec FR-040 a FR-047; casos H, I)."""

from datetime import date

import pytest

from tests.analitico import construcao as c
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO

pytestmark = pytest.mark.django_db


@pytest.fixture
def campanha(inst):
    """População ampla: inclui Conclusões sem unidade (caso H)."""
    return c.campanha_aberta_no_passado(inst.versao)


def _registro(campanha, conclusao):
    return capturar_snapshot(campanha).registros.get(conclusao=conclusao)


def test_sete_atributos_copiados(campanha):
    conclusao = c.conclusao(
        unidade="Serra",
        curso="Técnico em Informática",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Subsequente",
        ano=2022,
        data=date(2022, 12, 15),
    )
    registro = _registro(campanha, conclusao)
    for campo in CAMPOS_DE_CONTEXTO:
        assert getattr(registro, campo) == getattr(conclusao, campo), campo


def test_atributos_ausentes_sao_preservados(campanha):
    conclusao = c.conclusao(curso="Engenharia", ano=2020)
    registro = _registro(campanha, conclusao)
    assert registro.unidade is None
    assert registro.forma_oferta is None
    assert registro.nivel is None and registro.modalidade is None
    assert registro.curso == "Engenharia"


def test_ano_sem_data(campanha):
    registro = _registro(campanha, c.conclusao(unidade="Serra", ano=2019))
    assert registro.ano_conclusao == 2019
    assert registro.data_conclusao is None


def test_ano_e_data(campanha):
    registro = _registro(campanha, c.conclusao(ano=2021, data=date(2021, 7, 30)))
    assert registro.ano_conclusao == 2021
    assert registro.data_conclusao == date(2021, 7, 30)


def test_grafia_como_registrada(campanha):
    conclusao = c.conclusao(unidade=" Serra ", curso="técnico em INFORMÁTICA")
    registro = _registro(campanha, conclusao)
    assert registro.unidade == " Serra "
    assert registro.curso == "técnico em INFORMÁTICA"


def test_cursos_homonimos_em_unidades_diferentes(campanha):
    serra = c.conclusao(unidade="Serra", curso="Técnico em Informática")
    vitoria = c.conclusao(unidade="Vitória", curso="Técnico em Informática")
    snapshot = capturar_snapshot(campanha)
    registros = {r.conclusao_id: r for r in snapshot.registros.all()}
    assert registros[serra.pk].curso == registros[vitoria.pk].curso
    assert (registros[serra.pk].unidade, registros[vitoria.pk].unidade) == ("Serra", "Vitória")


def test_correcao_posterior_nao_altera_o_registro(campanha):
    conclusao = c.conclusao(
        unidade="Serra",
        curso="Técnico",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Subsequente",
        ano=2022,
        data=date(2022, 3, 1),
    )
    snapshot = capturar_snapshot(campanha)
    antes = c.retrato(snapshot)
    c.simular_correcao(  # simula 001/DP-005
        conclusao,
        unidade="Vitória",
        curso="Outro",
        nivel="Graduação",
        modalidade="A distância",
        forma_oferta="Integrado",
        ano_conclusao=2023,
        data_conclusao=date(2023, 1, 1),
    )
    assert c.retrato(snapshot) == antes

"""Universo e elegibilidade no snapshot (US3, US5; spec FR-020 a FR-034; casos F, G)."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.analitico import construcao as c
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.analitico.models import RegistroDoSnapshot
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha.consultas import avaliar, populacao_no_momento
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def _elegiveis(snapshot):
    return set(
        snapshot.registros.filter(elegivel_no_snapshot=True).values_list("conclusao_id", flat=True)
    )


# --- US3: população congelada ------------------------------------------------------------------


def test_elegiveis_do_snapshot_sao_a_populacao_da_004(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    populacao = set(populacao_no_momento(cenario.campanha).values_list("pk", flat=True))
    assert _elegiveis(snapshot) == populacao == cenario.elegiveis
    assert len(_elegiveis(snapshot)) == populacao_no_momento(cenario.campanha).count()


def test_elegibilidade_de_cada_registro_equivale_a_avaliacao_da_004(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    for registro in snapshot.registros.select_related("conclusao"):
        assert registro.elegivel_no_snapshot == (
            avaliar(cenario.campanha, registro.conclusao).elegivel
        )


def test_elegivel_sem_participacao_tem_registro_elegivel(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    registro = snapshot.registros.get(conclusao=cenario.vitoria_sem_atributos)
    assert registro.elegivel_no_snapshot is True
    assert not Participacao.objects.filter(conclusao=cenario.vitoria_sem_atributos).exists()


def test_populacao_ampla_inclui_todas_as_conclusoes(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao)
    c.conclusao(unidade="Serra")
    c.conclusao()
    snapshot = capturar_snapshot(campanha)
    assert _elegiveis(snapshot) == set(ConclusaoAcademica.objects.values_list("pk", flat=True))
    assert not snapshot.registros.filter(elegivel_no_snapshot=False).exists()


def test_conclusoes_da_mesma_pessoa_sao_registros_distintos(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    primeira = c.conclusao(unidade="Serra", curso="Técnico")
    segunda = c.conclusao(unidade="Serra", curso="Graduação", pessoa=primeira.pessoa)
    snapshot = capturar_snapshot(campanha)
    assert _elegiveis(snapshot) == {primeira.pk, segunda.pk}


def test_conclusao_incorporada_depois_do_encerramento_e_elegivel(cenario):
    tardia = c.conclusao(unidade="Serra", ano=2023)
    snapshot = capturar_snapshot(cenario.campanha)
    assert snapshot.registros.get(conclusao=tardia).elegivel_no_snapshot is True


def test_incorporacao_depois_da_captura_nao_muda_o_snapshot(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = c.retrato(snapshot)
    c.conclusao(unidade="Serra")
    c.conclusao(unidade="Vitória")
    assert c.retrato(snapshot) == antes
    assert populacao_no_momento(cenario.campanha).count() == len(antes) + 2


def _consultas_da_captura(inst, n):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=[f"Unidade {n}"])
    for _ in range(n):
        c.conclusao(unidade=f"Unidade {n}")
    with CaptureQueriesContext(connection) as consultas:
        capturar_snapshot(campanha)
    return len(consultas)


def test_captura_sem_consulta_por_conclusao(inst):
    assert _consultas_da_captura(inst, 3) == _consultas_da_captura(inst, 30)


# --- US5: Participações fora da população congelada -------------------------------------------


def test_universo_e_elegiveis_uniao_participantes(cenario):
    c.simular_correcao(cenario.serra_info, unidade="Cefor")  # simula 001/DP-005
    snapshot = capturar_snapshot(cenario.campanha)
    participantes = set(
        Participacao.objects.filter(campanha=cenario.campanha).values_list(
            "conclusao_id", flat=True
        )
    )
    populacao = set(populacao_no_momento(cenario.campanha).values_list("pk", flat=True))
    universo = set(snapshot.registros.values_list("conclusao_id", flat=True))
    assert universo == populacao | participantes
    assert cenario.cefor.pk not in universo and cenario.sem_unidade.pk not in universo


def test_participacao_de_conclusao_que_deixou_de_ser_elegivel(cenario):
    c.simular_correcao(cenario.serra_info, unidade="Cefor")  # simula 001/DP-005
    antes = list(Participacao.objects.filter(pk=cenario.concluida.pk).values())
    snapshot = capturar_snapshot(cenario.campanha)
    registro = snapshot.registros.get(conclusao=cenario.serra_info)
    assert registro.elegivel_no_snapshot is False
    assert registro.unidade == "Cefor"  # o contexto lido na captura
    assert registro.curso == "Técnico em Informática"
    assert list(Participacao.objects.filter(pk=cenario.concluida.pk).values()) == antes


def test_conclusao_elegivel_com_participacao_tem_um_so_registro(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    registros = snapshot.registros.filter(conclusao=cenario.serra_info)
    assert registros.count() == 1
    assert registros.get().elegivel_no_snapshot is True


def test_toda_participacao_da_campanha_tem_registro(cenario):
    c.simular_correcao(cenario.vitoria_info, unidade=None)  # simula 001/DP-005
    snapshot = capturar_snapshot(cenario.campanha)
    sem_registro = Participacao.objects.filter(campanha=cenario.campanha).exclude(
        conclusao_id__in=RegistroDoSnapshot.objects.filter(snapshot=snapshot).values("conclusao_id")
    )
    assert not sem_registro.exists()


def _leituras_da_001(campanha) -> int:
    tabela = ConclusaoAcademica._meta.db_table
    with CaptureQueriesContext(connection) as consultas:
        capturar_snapshot(campanha)
    return sum(f'FROM "{tabela}"' in q["sql"] for q in consultas.captured_queries)


def test_contexto_de_participante_elegivel_nao_e_relido(cenario):
    assert _leituras_da_001(cenario.campanha) == 1  # só a população da 004


def test_contexto_de_participante_fora_da_populacao_e_lido_a_parte(cenario):
    c.simular_correcao(cenario.serra_info, unidade="Cefor")  # simula 001/DP-005
    assert _leituras_da_001(cenario.campanha) == 2

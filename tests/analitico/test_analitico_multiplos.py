"""Vários snapshots e concorrência (US11, US13; spec FR-060 a FR-064; caso N)."""

import threading

import pytest
from django.db import connection

from tests.analitico import construcao as c
from trajetoria.analitico import consultas, operacoes
from trajetoria.analitico.consultas import indicadores_do_snapshot, snapshots_da_campanha
from trajetoria.analitico.models import SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha.consultas import encerramento

pytestmark = pytest.mark.django_db

CONTRATO_DE_CONSULTAS = {
    "ContextoCongelado",
    "IndicadoresDoSnapshot",
    "LinhaDoDataset",
    "LinhaDoRecorte",
    "ParticipacaoNoDataset",
    "RecorteDoSnapshot",
    "RespostaNoDataset",
    "indicadores_do_snapshot",
    "linhas_do_dataset",
    "recorte_do_snapshot",
    "snapshots_da_campanha",
}


def test_novo_snapshot_reflete_o_novo_estado_e_o_anterior_nao_muda(cenario):
    a = capturar_snapshot(cenario.campanha)
    retrato_a = c.retrato(a)
    c.simular_correcao(cenario.serra_info, unidade="Cefor")  # simula 001/DP-005
    b = capturar_snapshot(cenario.campanha)
    assert c.retrato(a) == retrato_a
    retrato_b = c.retrato(b)
    assert retrato_b[cenario.serra_info.pk][0] is False  # não elegível em B
    assert retrato_b[cenario.serra_info.pk][2] == "Cefor"  # unidade corrigida em B
    assert retrato_a[cenario.serra_info.pk][0] is True


def test_a_e_b_coexistem_com_registros_independentes(cenario):
    a = capturar_snapshot(cenario.campanha)
    b = capturar_snapshot(cenario.campanha)
    assert a.pk != b.pk
    ids_a = set(a.registros.values_list("id", flat=True))
    ids_b = set(b.registros.values_list("id", flat=True))
    assert ids_a and ids_b and not ids_a & ids_b


def test_snapshots_da_campanha_lista_todos_em_ordem_administrativa(cenario, campanha_v):
    a = capturar_snapshot(cenario.campanha)
    capturar_snapshot(campanha_v)
    b = capturar_snapshot(cenario.campanha)
    lista = list(snapshots_da_campanha(cenario.campanha))
    assert [s.pk for s in lista] == [a.pk, b.pk]
    assert lista == sorted(lista, key=lambda s: (s.capturado_em, s.pk))


def test_capturas_repetidas_nao_sao_deduplicadas(cenario):
    a = capturar_snapshot(cenario.campanha)
    b = capturar_snapshot(cenario.campanha)
    assert c.retrato(a) == c.retrato(b)
    assert SnapshotAnalitico.objects.filter(campanha=cenario.campanha).count() == 2


def test_contratos_publicos_nao_escolhem_snapshot():
    # Prova estrutural de que não existe "snapshot atual/vigente/último" (DP-1201).
    assert set(consultas.__all__) == CONTRATO_DE_CONSULTAS
    assert set(operacoes.__all__) == {"capturar_snapshot"}


def test_captura_durante_outra_captura_gera_dois_snapshots_completos(cenario, monkeypatch):
    # Concorrência determinística (caso N): uma captura completa ocorre no meio de outra.
    original = operacoes._universo
    internas = []

    def com_captura_no_meio(campanha):
        universo = original(campanha)
        if not internas:
            internas.append(None)  # só a primeira chamada dispara a captura interna
            internas[0] = capturar_snapshot(campanha)
        return universo

    monkeypatch.setattr(operacoes, "_universo", com_captura_no_meio)
    externa = capturar_snapshot(cenario.campanha)
    (interna,) = internas
    assert externa.pk != interna.pk
    for snapshot in (externa, interna):
        assert snapshot.registros.count() == len(cenario.elegiveis)
    assert c.retrato(externa) == c.retrato(interna)


@pytest.mark.django_db(transaction=True)
def test_capturas_simultaneas_em_threads(cenario):
    # Opcional, como na 005: prova com transações reais; o teste determinístico acima é a
    # proteção principal. Remover se ficar instável no CI.
    barreira = threading.Barrier(2)
    resultados, erros = [], []

    def capturar():
        try:
            barreira.wait(timeout=10)
            resultados.append(capturar_snapshot(cenario.campanha))
        except Exception as erro:  # noqa: BLE001 — o teste exibe qualquer falha da thread
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=capturar) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not erros
    assert len(resultados) == 2
    for snapshot in resultados:
        assert snapshot.registros.count() == len(cenario.elegiveis)


# --- US13: metadados mínimos -------------------------------------------------------------------


def test_metadados_por_composicao_sem_dado_individual(cenario):
    capturar_snapshot(cenario.campanha)
    capturar_snapshot(cenario.campanha)
    forma, momento_do_encerramento = encerramento(cenario.campanha)
    for snapshot in snapshots_da_campanha(cenario.campanha):
        ind = indicadores_do_snapshot(snapshot)
        assert snapshot.campanha_id == cenario.campanha.pk
        assert snapshot.capturado_em > momento_do_encerramento
        assert ind.registros == snapshot.registros.count() == 5
        assert (ind.elegiveis, ind.iniciadas, ind.concluidas) == (5, 3, 2)
        valores = vars(ind).values()
        assert all(isinstance(v, int) for v in valores)  # só contagens

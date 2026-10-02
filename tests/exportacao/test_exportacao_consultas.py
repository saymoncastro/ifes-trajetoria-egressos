"""Proporcionalidade e ausência de escrita (spec FR-005, FR-114, FR-133)."""

import logging
import tempfile

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.analitico import construcao as c
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import exportar_csv, exportar_xlsx

pytestmark = pytest.mark.django_db


def _consultas(inst, n: int) -> int:
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    for _ in range(n):
        conclusao = c.conclusao(unidade="Serra")
        c.concluida(campanha, conclusao, inst)
    snapshot = capturar_snapshot(campanha)
    with CaptureQueriesContext(connection) as consultas:
        dataset_exportado(snapshot)
    return len(consultas.captured_queries)


def test_consultas_independem_do_numero_de_registros(inst):
    assert _consultas(inst, 3) == _consultas(inst, 30)


def test_nenhuma_escrita_no_banco(snapshot):
    antes = c.contagens()
    with CaptureQueriesContext(connection) as consultas:
        exportar_csv(snapshot)
        exportar_xlsx(snapshot)
    escritas = [
        q["sql"]
        for q in consultas.captured_queries
        if q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
    ]
    assert escritas == []
    assert c.contagens() == antes


def test_nada_em_disco_nem_em_log(snapshot, cenario, monkeypatch, tmp_path, caplog, chave_ficticia):
    def proibido(*args, **kwargs):
        raise AssertionError("a exportação não pode criar arquivo temporário")

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    for nome in ("mkstemp", "mkdtemp", "NamedTemporaryFile", "TemporaryFile"):
        monkeypatch.setattr(tempfile, nome, proibido)
    with caplog.at_level(logging.DEBUG):
        exportar_csv(snapshot)
        exportar_xlsx(snapshot)
    assert list(tmp_path.iterdir()) == []
    registrado = "\n".join(r.getMessage() for r in caplog.records)
    assert chave_ficticia not in registrado
    for valor in ("Campus Serra", "Técnico em Informática", "comentário fictício", "27"):
        assert valor not in registrado

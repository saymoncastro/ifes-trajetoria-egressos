"""Lote confirmado é imutável (020 FR-022; T017)."""

import ast
from pathlib import Path

import pytest

from tests.editor.construcao_editor import A
from trajetoria.mobilizacao.operacoes import confirmar_lote

pytestmark = pytest.mark.django_db
OPERACOES = Path(__file__).resolve().parents[2] / "trajetoria" / "mobilizacao" / "operacoes.py"


def test_sem_rota_de_edicao_ou_remocao(ampla, clientes):
    lote = confirmar_lote(ampla.pk, A, "Lote", {"unidades": ["Vitória"]})
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/"
    for sufixo in ("editar/", "remover/", "excluir/"):
        assert clientes[A].post(base + sufixo).status_code == 404
    assert clientes[A].post(base).status_code == 405
    assert clientes[A].delete(base).status_code == 405


def test_operacoes_nao_alteram_lote_nem_identidade_de_membros():
    texto = OPERACOES.read_text()
    arvore = ast.parse(texto)
    chamadas = {
        no.func.attr for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
    }
    assert not {"delete", "bulk_update"} & chamadas
    # O único `update` permitido é o de situação e instantes do membro (envio).
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call) and getattr(no.func, "attr", None) == "update":
            assert {k.arg for k in no.keywords} <= {
                "situacao", "tentativa_iniciada_em", "resultado_em",
            }

"""Fronteiras da 020: 011, 012, 013 e 017 intocados; controle C1; dependências entre apps
(020 FR-039, FR-040, FR-044, SC-008; research R9 C1, C4, C5; T056–T058)."""

import ast
from pathlib import Path

import pytest

from tests.contato.conftest import contato
from tests.editor.construcao_editor import A
from tests.mobilizacao.conftest import pessoa
from trajetoria.acompanhamento.gestao.formularios import CampanhaForm
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.contato.models import Origem
from trajetoria.exportacao.contrato import COLUNAS_BASE
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"
TERMOS = ("email", "e_mail", "contato", "lote", "membro", "mobiliza", "telefone")


def _importados(arquivo):
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module:
            yield no.module
        elif isinstance(no, ast.Import):
            yield from (a.name for a in no.names)


def _modulos(pasta):
    for arquivo in (RAIZ / pasta).rglob("*.py"):
        yield arquivo, set(_importados(arquivo))


def test_dependencias_entre_apps():
    for arquivo, importados in _modulos("contato"):
        assert not [m for m in importados if m.startswith("trajetoria.mobilizacao")], arquivo
    for arquivo, importados in _modulos("comunicacao"):
        assert not [
            m for m in importados
            if m.startswith(("trajetoria.campanha", "trajetoria.acompanhamento",
                             "trajetoria.mobilizacao"))
        ], arquivo
    for pasta in ("narrativa", "video", "contexto_trajetoria"):
        for arquivo, importados in _modulos(pasta):
            assert not [
                m for m in importados
                if m.startswith(("trajetoria.contato", "trajetoria.mobilizacao"))
            ], arquivo


def test_controle_c1_leitura_do_endereco():
    """Fora de `contato/` e de `mobilizacao/operacoes.py`, ninguém lê `.valor` de contato."""
    permitidos = {RAIZ / "mobilizacao" / "operacoes.py"}
    for arquivo in RAIZ.rglob("*.py"):
        if "contato" in arquivo.relative_to(RAIZ).parts[:1] or arquivo in permitidos:
            continue
        if "migrations" in arquivo.parts:
            continue
        arvore = ast.parse(arquivo.read_text())
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute) and no.attr == "valor":
                origem = ast.unparse(no.value)
                assert "contato" not in origem.lower(), f"{arquivo}: {ast.unparse(no)}"
    for template in RAIZ.rglob("*.html"):
        assert "contato.valor" not in template.read_text(), template


def test_formulario_da_campanha_sem_mobilizacao():
    campos = " ".join(CampanhaForm([]).fields).lower()
    for termo in (*TERMOS, "publico", "foco", "curso", "campus", "unidade"):
        assert termo not in campos, termo


def test_colunas_de_exportacao_sem_contato_nem_lote():
    nomes = " ".join(c.nome for c in COLUNAS_BASE).lower()
    for termo in TERMOS:
        assert termo not in nomes


@pytest.mark.django_db
def test_snapshot_identico_depois_de_lotes(ampla, em_preparacao, settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "chave-ficticia-de-teste-020-000000000000001"
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    enviar_lote(lote.pk, A)
    op_campanha.encerrar(ampla)
    snapshot = capturar_snapshot(ampla)

    def retrato():
        registros = sorted(
            map(repr, RegistroDoSnapshot.objects.filter(snapshot=snapshot).values())
        )
        dados = dataset_exportado(snapshot).dados
        return (list(SnapshotAnalitico.objects.values()), registros, repr(dados))

    antes = retrato()
    texto = antes[2].lower()
    assert "example.invalid" not in texto and "lote" not in texto
    contato(pessoa("SIM-P-0001"), "novo@example.invalid", Origem.EGRESSO)
    confirmar_lote(em_preparacao.pk, A, "Outra", {"unidades": ["Serra"]})
    assert retrato() == antes


@pytest.mark.django_db
def test_indicadores_do_acompanhamento_inalterados(ampla, clientes):
    url = f"/acompanhamento/campanhas/{ampla.pk}/"
    antes = clientes[A].get(url).context["resumo"]
    enviar_lote(confirmar_lote(ampla.pk, A, "Todos", {}, True).pk, A)
    depois = clientes[A].get(url)
    assert depois.context["resumo"] == antes
    html = depois.content.decode().lower()
    for termo in ("convidad", "example.invalid", "conversão", "alcance"):
        assert termo not in html

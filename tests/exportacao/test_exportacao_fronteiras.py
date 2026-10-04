"""Fronteiras e neutralidade do contrato (US11; spec FR-026, FR-100 a FR-123, FR-130).
Verificações estruturais por AST e sobre os arquivos produzidos, sem procurar palavras soltas
em comentários."""

import ast
import importlib.util
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.urls import get_resolver

import trajetoria.exportacao
from tests.exportacao import leitura
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.analitico.consultas import indicadores_do_snapshot
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import exportar_csv, exportar_xlsx
from trajetoria.governanca import regras as governanca
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

RAIZ = Path(trajetoria.exportacao.__file__).parent
MODULOS = sorted(RAIZ.glob("*.py"))
PERMITIDOS = ("trajetoria.exportacao", "trajetoria.analitico", "trajetoria.instrumento")
DOWNSTREAM = ("looker", "google", "bigquery", "datastudio", "sheets", "dashboard")


def _importados(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
        elif isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
    return nomes


def _identificadores(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, (ast.FunctionDef, ast.ClassDef)):
            nomes.add(no.name)
        elif isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
        elif isinstance(no, ast.arg):
            nomes.add(no.arg)
    return nomes


# --- Nomes de coluna ---------------------------------------------------------------------------


def test_nomes_de_coluna_validos_para_ferramentas_tabulares(snapshot):
    for nome in dataset_exportado(snapshot).dados.cabecalho:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", nome), nome
        assert len(nome) <= 81, nome


# --- Código ------------------------------------------------------------------------------------


def test_imports_so_do_permitido():
    assert MODULOS
    for arquivo in MODULOS:
        for nome in _importados(arquivo):
            raiz = nome.split(".")[0]
            if raiz == "trajetoria":
                assert nome.startswith(PERMITIDOS), (arquivo.name, nome)
            else:
                assert raiz in sys.stdlib_module_names or raiz in ("django", "xlsxwriter"), (
                    arquivo.name,
                    nome,
                )


def test_nenhum_identificador_de_ferramenta_a_jusante():
    for arquivo in MODULOS:
        for nome in _identificadores(arquivo):
            assert not any(p in nome.lower() for p in DOWNSTREAM), (arquivo.name, nome)


def test_pacote_nao_e_app_nem_tem_interface():
    assert "trajetoria.exportacao" not in settings.INSTALLED_APPS
    assert "exportacao" not in {a.label for a in apps.get_app_configs()}
    for nome in ("apps.py", "models.py", "views.py", "urls.py", "admin.py", "forms.py"):
        assert not (RAIZ / nome).exists(), nome
    for pasta in ("migrations", "management", "templates"):
        assert not (RAIZ / pasta).exists(), pasta
    for sufixo in ("views", "urls", "api", "serializers"):
        assert importlib.util.find_spec(f"trajetoria.exportacao.{sufixo}") is None


def test_nenhuma_rota_leva_a_exportacao():
    def modulos(padroes):
        for padrao in padroes:
            if hasattr(padrao, "url_patterns"):
                yield from modulos(padrao.url_patterns)
            else:
                yield padrao.callback.__module__

    assert not [m for m in modulos(get_resolver().url_patterns) if "exportacao" in m]


def test_nenhuma_regra_de_governanca_nova():
    assert set(governanca.__all__) == {
        "EscopoDeAcompanhamento",
        "escopo_de_acompanhamento",
        "pode_acompanhar_coleta",
        "pode_consultar_publicado",
        "pode_consultar_rascunho",
        "pode_elaborar_instrumento",
        "pode_simular_comunicacao",  # capacidade administrativa introduzida pela 016
        "pode_gerir_campanha",  # gestão na demonstração introduzida pela 017
    }


def test_sem_migration_nova():
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


# --- Conteúdo dos arquivos ------------------------------------------------------------------------


def _textos(snapshot) -> str:
    csv = leitura.ler_csv(exportar_csv(snapshot))
    xlsx = leitura.ler_xlsx(exportar_xlsx(snapshot))
    return "\n".join(
        str(v) for tabelas in (csv, xlsx) for t in tabelas.values() for linha in t for v in linha
    )


def test_arquivos_sem_identificador_interno_nem_pii(snapshot, cenario, chave_ficticia):
    texto = _textos(snapshot).lower()
    conclusoes = ConclusaoAcademica.objects.filter(pk__in=snapshot.registros.values("conclusao_id"))
    internos = [
        *conclusoes.values_list("pk", flat=True),
        *Pessoa.objects.filter(conclusoes__in=conclusoes).values_list("pk", flat=True),
        *Participacao.objects.filter(campanha=cenario.campanha).values_list("pk", flat=True),
        *snapshot.registros.values_list("pk", flat=True),
    ]
    for uuid in internos:
        assert str(uuid) not in texto and uuid.hex not in texto
    for externo, nome in Pessoa.objects.filter(conclusoes__in=conclusoes).values_list(
        "id_externo", "nome"
    ):
        assert externo.lower() not in texto and nome.lower() not in texto
    for externo in conclusoes.values_list("id_externo", flat=True):
        assert externo.lower() not in texto
    assert chave_ficticia.lower() not in texto


def test_taxas_reconstruidas_so_com_o_pacote_csv(snapshot):
    cabecalho, linhas = leitura.normalizar_csv(leitura.ler_csv(exportar_csv(snapshot)))["dados"]
    linhas = [dict(zip(cabecalho, linha, strict=True)) for linha in linhas]
    elegiveis = sum(1 for x in linhas if x["elegivel_no_snapshot"])
    iniciadas = sum(1 for x in linhas if x["possui_participacao"])
    concluidas = sum(1 for x in linhas if x["participacao_concluida"])
    indicadores = indicadores_do_snapshot(snapshot)
    assert Decimal(iniciadas) / Decimal(elegiveis) == indicadores.taxa_inicio
    assert Decimal(concluidas) / Decimal(elegiveis) == indicadores.taxa_conclusao

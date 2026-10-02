"""Fronteiras da governança (Feature 010; plan, "Sinais de over engineering"; SC-004, SC-006
a SC-008).

Um modelo, cinco campos, dois papéis, três regras; nada de autenticação, privilégio técnico,
modo de demonstração, publicação, aprovação ou papel genérico. Os nomes são verificados pelo
que o app **define** (funções, classes, membros de enum), não pelo texto livre das
docstrings, que fala de "registro administrativo" e de "Versões publicadas".
"""

import ast
from pathlib import Path

import pytest
from django.apps import apps
from django.core.management import call_command

from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.operacoes import Motivo

RAIZ = Path(__file__).resolve().parents[2]
GOVERNANCA = RAIZ / "trajetoria" / "governanca"
ACESSO = RAIZ / "trajetoria" / "editor" / "acesso.py"
FONTES = [p for p in GOVERNANCA.rglob("*.py") if "migrations" not in p.parts]


def test_um_modelo_cinco_campos_dois_papeis():
    assert list(apps.get_app_config("governanca").get_models()) == [VinculoDeGovernanca]
    campos = {c.name for c in VinculoDeGovernanca._meta.get_fields()}
    assert campos == {"id", "identificador_operador", "papel", "unidade", "ativo"}
    assert VinculoDeGovernanca._meta.get_field("unidade").null is False
    assert {p.value for p in Papel} == {"CPAEG", "CSAEG"}


def test_sem_superficie_nem_dependencia_indevida():
    for nome in ("urls.py", "views.py", "admin.py", "forms.py", "middleware.py"):
        assert not (GOVERNANCA / nome).exists(), nome
    for pasta in ("management", "templates"):
        assert not (GOVERNANCA / pasta).exists(), pasta
    proibidos = (
        "django.contrib.auth", "trajetoria.editor", "trajetoria.demonstracao",
        "trajetoria.interface", "trajetoria.instrumento", "trajetoria.campanha",
        "trajetoria.participacao",
    )  # fmt: skip
    for arquivo in FONTES:
        for no in ast.walk(ast.parse(arquivo.read_text())):
            modulos = []
            if isinstance(no, ast.ImportFrom) and no.module:
                modulos = [no.module]
            elif isinstance(no, ast.Import):
                modulos = [a.name for a in no.names]
            assert not [m for m in modulos if m.startswith(proibidos)], (arquivo.name, modulos)


def _nomes_definidos():
    for arquivo in FONTES:
        for no in ast.walk(ast.parse(arquivo.read_text())):
            if isinstance(no, ast.FunctionDef | ast.ClassDef):
                yield no.name
            elif isinstance(no, ast.Assign):
                yield from (t.id for t in no.targets if isinstance(t, ast.Name))


def test_nenhum_nome_de_publicacao_privilegio_ou_papel_generico():
    proibidos = ("publicar", "aprov", "homolog", "admin", "superuser", "permission", "policy")
    proibidos += ("capab", "publicador", "editor", "viewer", "leitor", "gestor", "manager")
    nomes = [n.lower() for n in _nomes_definidos()]
    assert not [n for n in nomes if any(p in n for p in proibidos)]
    assert {m.name for m in Motivo} == {
        "IDENTIFICADOR_INVALIDO", "PAPEL_INVALIDO", "UNIDADE_PROIBIDA", "UNIDADE_EXIGIDA",
        "UNIDADE_INVALIDA", "JA_ATIVO", "JA_INATIVO",
    }  # fmt: skip


def test_autorizacao_nao_consulta_privilegio_tecnico_nem_modo_de_demonstracao():
    proibidos = ("is_staff", "is_superuser", "request.user", "TRAJETORIA_DEMONSTRACAO")
    for arquivo in (*FONTES, ACESSO):
        texto = arquivo.read_text()
        assert not [p for p in proibidos if p in texto], arquivo.name


@pytest.mark.django_db
def test_sem_migracao_pendente():
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)

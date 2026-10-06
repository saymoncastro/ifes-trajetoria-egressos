import ast
import tomllib
from pathlib import Path

import pytest
from django.core.management import call_command

from tests.dependencias import DEPENDENCIAS_APROVADAS
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.acesso.models import MaterialDeVerificacao

RAIZ = Path(__file__).resolve().parents[2]


def test_dependencia_unidirecional_e_material_fora_de_operador():
    pastas = (
        "academico",
        "fonte_academica",
        "participacao",
        "campanha",
        "instrumento",
        "interface",
        "exportacao",
        "analitico",
        "acompanhamento",
        "comunicacao",
        "editor",
        "contato",
        "mobilizacao",
    )
    for pasta in pastas:
        for p in (RAIZ / "trajetoria" / pasta).rglob("*.py"):
            for no in ast.walk(ast.parse(p.read_text())):
                if (
                    isinstance(no, ast.ImportFrom)
                    and no.module
                    and no.module.startswith("trajetoria.acesso")
                ):
                    # 020: a página "Meu e-mail" usa a mesma sessão de Pessoa (FR-011).
                    # 023: o destino da entrada com aviso (FR-001) e, só nas telas de Seção,
                    # o envio pendente (FR-002 a FR-009), cujo conteúdo é opaco para a 018.
                    assert pasta in ("interface", "contato") and p.name == "views.py"
                    if no.module == "trajetoria.acesso":
                        assert pasta == "interface"
                        assert {a.name for a in no.names} == {"pendente"}
                        continue
                    assert no.module == "trajetoria.acesso.sessao"
                    assert {a.name for a in no.names} <= {"pessoa_em_uso", "destino_da_entrada"}
                if isinstance(no, ast.Import):
                    assert not any(a.name.startswith("trajetoria.acesso") for a in no.names)
        if pasta in ("exportacao", "analitico", "acompanhamento", "comunicacao", "editor",
                     "mobilizacao"):
            assert all(
                "MaterialDeVerificacao" not in p.read_text()
                for p in (RAIZ / "trajetoria" / pasta).rglob("*.html")
            )
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text())
    assert projeto["project"]["dependencies"] == DEPENDENCIAS_APROVADAS


def test_modelos_antigos_e_material_separado():
    assert {f.name for f in Pessoa._meta.fields} == {
        "id",
        "fonte",
        "id_externo",
        "nome",
        "incorporado_em",
    }
    assert "cpf" not in {f.name for f in ConclusaoAcademica._meta.fields}
    assert "data_nascimento" not in {f.name for f in ConclusaoAcademica._meta.fields}
    assert MaterialDeVerificacao._meta.get_field("pessoa").remote_field.related_name == "+"
    assert not MaterialDeVerificacao._meta.get_field("identificador_cpf").unique
    assert MaterialDeVerificacao._meta.get_field("identificador_cpf").db_index


@pytest.mark.django_db
def test_sem_migracoes_pendentes():
    call_command("makemigrations", check=True, dry_run=True, verbosity=0)


def test_sem_import_privado_de_outro_app_nem_estilo_proprio():
    """Revisão 018: `acesso` usa só nomes públicos de outros apps; estilos ficam no shell."""
    for arquivo in (RAIZ / "trajetoria/acesso").glob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.ImportFrom) and (no.module or "").startswith("trajetoria."):
                if not no.module.startswith("trajetoria.acesso"):
                    privados = [n.name for n in no.names if n.name.startswith("_")]
                    assert not privados, (arquivo.name, privados)
    for template in (RAIZ / "trajetoria/acesso/templates").rglob("*.html"):
        assert "<style" not in template.read_text(encoding="utf-8"), template.name

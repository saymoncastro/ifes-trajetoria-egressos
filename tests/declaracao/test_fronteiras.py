import ast
from pathlib import Path

import pytest
from django.core.management import call_command

from tests.declaracao.construcao import declaracao_concluida
from tests.participacao import construcao as c

RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "trajetoria/declaracao"
PERMITIDOS = {
    "academico",
    "acesso",
    "campanha",
    "declaracao",
    "participacao",
    "governanca",
    "fonte_academica",
    "demonstracao",
    "acompanhamento",
    "interface",
}


def test_dependencias_e_criptografia_restrita():
    for p in APP.glob("*.py"):
        arvore = ast.parse(p.read_text())
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and (no.module or "").startswith("trajetoria."):
                assert no.module.split(".")[1] in PERMITIDOS
            if (
                isinstance(no, ast.Call)
                and isinstance(no.func, ast.Name)
                and no.func.id == "abrir_consulta"
            ):
                assert p.name == "operacoes.py"
                funcoes = [
                    fn
                    for fn in ast.walk(arvore)
                    if isinstance(fn, ast.FunctionDef) and no in ast.walk(fn)
                ]
                assert [fn.name for fn in funcoes] == ["revelar_dados"]
    # A 018 não depende da 019 (T047; FR-119): o selo transitório é da 018 (`acesso.transito`)
    # e a 019 o consome. Nenhum módulo de `acesso` importa `declaracao`, nem pelo registro de
    # apps.
    for p in (RAIZ / "trajetoria/acesso").glob("*.py"):
        for no in ast.walk(ast.parse(p.read_text())):
            if isinstance(no, ast.ImportFrom | ast.Import):
                nomes = [no.module or ""] if isinstance(no, ast.ImportFrom) else [
                    a.name for a in no.names
                ]
                assert not any(n.startswith("trajetoria.declaracao") for n in nomes), p.name


@pytest.mark.django_db
def test_modelos_sem_valores_sensiveis_em_repr():
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    for obj in (f, f.dados_consulta):
        texto = str(obj) + repr(obj)
        assert f.identificador_cpf not in texto and f.verificador not in texto
        assert f.dados_consulta.selado not in texto


@pytest.mark.django_db
def test_migracoes_e_barreira(client, settings):
    call_command("makemigrations", check=True, dry_run=True, verbosity=0)
    settings.TRAJETORIA_DEMONSTRACAO = False
    for url in (
        "/declaracao/",
        "/declaracao/nova/",
        "/declaracao/comecar/",
        "/validacoes-formacao/",
    ):
        assert client.get(url).status_code == 404
        assert client.post(url).status_code == 404


def test_criacao_de_participacao_restrita_a_operacao_de_inicio():
    mutacoes = {"create", "get_or_create", "update_or_create", "bulk_create", "update", "delete"}
    for caminho in (RAIZ / "trajetoria").rglob("*.py"):
        if "migrations" in caminho.parts:
            continue
        arvore = ast.parse(caminho.read_text())
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call) or not isinstance(no.func, ast.Attribute):
                continue
            if no.func.attr not in mutacoes or not ast.unparse(no.func).startswith(
                "Participacao.objects"
            ):
                continue
            if caminho == RAIZ / "trajetoria/participacao/operacoes.py":
                continue
            assert caminho == APP / "operacoes.py"
            funcoes = [
                fn
                for fn in ast.walk(arvore)
                if isinstance(fn, ast.FunctionDef) and no in ast.walk(fn)
            ]
            assert [fn.name for fn in funcoes] == ["iniciar_participacao_declarada"]

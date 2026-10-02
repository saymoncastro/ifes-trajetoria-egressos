"""Fronteiras e invariantes estruturais do editor (FR-021, FR-022, FR-076, FR-098, FR-104 a
FR-109; SC-007, SC-010; plan "Desenho → Camadas").

Verificações baratas de importação, escrita, publicação, modelos, migrações, scripts, CSRF e
rotas. A prova principal de comportamento está nos demais testes do editor.
"""

import ast
import re
import tomllib
from pathlib import Path

import pytest
from django.apps import apps
from django.core.management import call_command
from django.test import Client

from tests.editor import construcao_editor as ce
from trajetoria.editor import urls

RAIZ = Path(__file__).resolve().parents[2]
EDITOR = RAIZ / "trajetoria" / "editor"
ESCRITAS_PERMITIDAS = {
    "criar_pesquisa", "criar_versao", "criar_versao_a_partir_de", "alterar_versao",
    "adicionar_secao", "alterar_secao", "definir_encaminhamento", "reordenar_secoes",
    "remover_secao", "adicionar_pergunta", "alterar_pergunta", "mover_pergunta",
    "reordenar_perguntas", "remover_pergunta", "adicionar_opcao", "alterar_opcao",
    "reordenar_opcoes", "remover_opcao", "definir_regra", "remover_regra", "FINALIZAR",
}  # fmt: skip
# Módulo → nomes que o editor pode importar dele (None = qualquer nome).
PERMITIDOS = {
    "trajetoria.instrumento.conteudo": None,
    "trajetoria.instrumento.regras": {"Motivo", "OperacaoRejeitada", "verificar_completude"},
    "trajetoria.instrumento.models": {
        "EstadoVersao",
        "Pesquisa",
        "Versao",
        "Secao",
        "Pergunta",
        "Opcao",
        "TipoPergunta",
    },  # fmt: skip
    "trajetoria.participacao.percurso": {"secoes_nao_suportadas"},
    "trajetoria.participacao.regras": {"Motivo"},
    "trajetoria.interface.formularios": {"FormularioDaSecao"},
    # 010: identificação (só em acesso.py) e as três regras; nunca operações de vínculo.
    "trajetoria.demonstracao.operador": {"operador_em_uso"},
    "trajetoria.governanca.consultas": {"vinculos_ativos"},
    "trajetoria.governanca.regras": {
        "pode_consultar_publicado",
        "pode_consultar_rascunho",
        "pode_elaborar_instrumento",
    },
}


def _importacoes(arquivo: Path):
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module and no.module.startswith("trajetoria"):
            for alias in no.names:
                yield no.module, alias.name
        elif isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.startswith("trajetoria"):
                    yield alias.name, None


def _fontes(sufixos):
    return [p for p in EDITOR.rglob("*") if p.suffix in sufixos]


def test_importacoes_permitidas():
    for arquivo in _fontes((".py",)):
        for modulo, nome in _importacoes(arquivo):
            if modulo.startswith("trajetoria.editor"):
                continue
            if modulo == "trajetoria.instrumento" and nome == "operacoes":
                continue  # `from trajetoria.instrumento import operacoes as op`
            assert modulo in PERMITIDOS, (arquivo.name, modulo)
            assert PERMITIDOS[modulo] is None or nome in PERMITIDOS[modulo], (arquivo.name, nome)


def test_identificacao_so_em_acesso_e_nenhuma_escrita_de_vinculo():
    for arquivo in _fontes((".py",)):
        for modulo, _nome in _importacoes(arquivo):
            if modulo == "trajetoria.demonstracao.operador":
                assert arquivo.name == "acesso.py", arquivo.name
            assert modulo not in ("trajetoria.governanca.operacoes", "trajetoria.governanca.models")


def test_so_operacoes_da_002_e_nunca_publicar():
    for arquivo in _fontes((".py",)):
        conteudo = arquivo.read_text()
        usadas = set(re.findall(r"\bop\.(\w+)", conteudo))
        assert usadas <= ESCRITAS_PERMITIDAS, (arquivo.name, usadas - ESCRITAS_PERMITIDAS)
        assert not re.search(r"\bpublicar\s*\(|\bpublicar\b,|renomear_pesquisa", conteudo), (
            arquivo.name
        )
        assert not re.search(r"\.(save|create|update|delete|bulk_\w+)\(", conteudo), arquivo.name
        assert not re.search(r"forms\.ModelForm|django\.views\.generic", conteudo), arquivo.name


def test_sem_modelos_nem_migracoes(db):
    assert not (EDITOR / "models.py").exists() and not (EDITOR / "migrations").exists()
    assert list(apps.get_app_config("editor").get_models()) == []
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


def test_sem_script_recurso_externo_nem_dependencia_nova():
    for arquivo in _fontes((".html", ".css")):
        conteudo = arquivo.read_text()
        assert "<script" not in conteudo and not re.search(r'(src|href)="https?://', conteudo)
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text())["project"]
    assert projeto["dependencies"] == ["Django>=5.2,<5.3", "psycopg[binary]>=3.2,<3.4"]


def test_rotas_sem_publicacao_exclusao_api_ou_campanha():
    rotas = [str(p.pattern) for p in urls.urlpatterns]
    proibidas = r"publicar|aprovar|homologar|api|exportar|importar|campanha|excluir|apagar"
    assert not [r for r in rotas if re.search(proibidas, r)]
    assert not [
        r for r in rotas if r.startswith(("pesquisas/<", "versoes/<")) and r.endswith("remover/")
    ]
    assert not [r for r in rotas if r.startswith("pesquisas/<") and re.search("editar|renomear", r)]


@pytest.mark.django_db
def test_csrf_em_toda_familia_de_escrita(copia):
    secao, pergunta = ce.secao(copia, 1), ce.pergunta(copia, 1, 1)
    opcao = pergunta.opcoes.first()
    sem_token = Client(enforce_csrf_checks=True)
    for rota in (
        "/editor/pesquisas/nova/",
        f"/editor/versoes/{copia.pk}/nova-a-partir/",
        f"/editor/versoes/{copia.pk}/dados/",
        f"/editor/secoes/{secao.pk}/mover/",
        f"/editor/perguntas/{pergunta.pk}/editar/",
        f"/editor/opcoes/{opcao.pk}/",
        f"/editor/opcoes/{opcao.pk}/remover/",
    ):
        assert sem_token.post(rota).status_code == 403, rota

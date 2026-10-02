"""Fronteiras do acompanhamento da coleta (Feature 011; plan, "Sinais de over engineering";
spec FR-100, FR-101, FR-110, FR-125, FR-130, FR-131; SC-007).

Nada persistido, nada escrito, nenhuma Resposta, nenhuma infraestrutura analítica. Os nomes
são verificados pelo que o app **define**, não pelo texto livre das docstrings.
"""

import ast
from io import StringIO
from pathlib import Path

from django.apps import apps
from django.core.management import call_command

RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "trajetoria" / "acompanhamento"
FONTES = list(APP.rglob("*.py"))


def test_app_sem_modelos_nem_migrations(db):
    assert list(apps.get_app_config("acompanhamento").get_models()) == []
    assert not (APP / "migrations").exists()
    assert not (APP / "models.py").exists()
    saida = StringIO()
    call_command("makemigrations", "--check", "--dry-run", stdout=saida)
    assert "No changes detected" in saida.getvalue()


def _arvores():
    for arquivo in FONTES:
        yield arquivo, ast.parse(arquivo.read_text())


def test_nao_importa_pessoa_resposta_nem_operacoes_de_escrita():
    for arquivo, arvore in _arvores():
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module:
                nomes = {a.name for a in no.names}
                assert not nomes & {"Pessoa", "Resposta", "RespostaOpcao"}, arquivo.name
                assert not no.module.endswith("operacoes"), (arquivo.name, no.module)
            elif isinstance(no, ast.Import):
                assert not [a.name for a in no.names if a.name.endswith("operacoes")]


def test_nenhum_nome_de_infraestrutura_analitica():
    proibidos = (
        "metric", "dimension", "dashboard", "widget", "snapshot", "cache", "ranking",
        "permission", "policy", "capab", "export",
    )  # fmt: skip
    nomes = []
    for _, arvore in _arvores():
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef | ast.ClassDef):
                nomes.append(no.name.lower())
            elif isinstance(no, ast.Assign):
                nomes += [t.id.lower() for t in no.targets if isinstance(t, ast.Name)]
    assert not [n for n in nomes if any(p in n for p in proibidos)]


def test_gate_usa_a_regra_explicita_e_a_identificacao_compartilhada():
    """Regressão do code review: o acesso decide por `pode_acompanhar_coleta` (CPAEG/CSAEG
    nomeados) e identifica o operador pelo mesmo ponto único do editor."""
    nomes = set()
    for no in ast.walk(ast.parse((APP / "acesso.py").read_text())):
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            nomes.add(no.func.id)
    assert {"pode_acompanhar_coleta", "vinculos_do_operador_em_uso"} <= nomes
    assert "operador_em_uso" not in nomes and "vinculos_ativos" not in nomes


def test_elegibilidade_da_004_inalterada():
    """O contrato é `populacao_no_momento`; `_filtro` continua privado (research R4)."""
    from trajetoria.campanha import consultas

    assert "populacao_no_momento" in consultas.__all__
    assert "_filtro" not in consultas.__all__
    publicas = {n for n in vars(consultas) if not n.startswith("_")}
    assert "criterio_de_populacao" not in publicas
    for arquivo, arvore in _arvores():
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module == "trajetoria.campanha.consultas":
                assert "_filtro" not in {a.name for a in no.names}, arquivo.name


def test_nenhuma_acao_de_gestao_comunicacao_ou_exportacao(client, db, settings):
    """Somente leitura (FR-100, FR-101, FR-131): sem formulário de escrita nem ação de gestão,
    comunicação ou exportação."""
    from tests.acompanhamento import construcao as k
    from tests.campanha.construcao import versao_publicada
    from trajetoria.governanca.models import Papel
    from trajetoria.governanca.operacoes import registrar_vinculo

    settings.TRAJETORIA_DEMONSTRACAO = True
    registrar_vinculo(k.A, Papel.CPAEG)
    cliente = k.atuar_como(client, k.A)
    campanha = k.campanha(versao_publicada())
    proibidos = (
        "Criar Campanha", "Abrir", "Encerrar", "Reabrir", "Excluir", "Convite", "Lembrete",
        "E-mail", "WhatsApp", "não respondentes", "Exportar", "CSV", "XLSX",
    )  # fmt: skip
    from tests.editor.construcao_editor import texto_visivel

    for resposta in (cliente.get("/acompanhamento/"), k.detalhe(cliente, campanha)):
        html = resposta.content.decode()
        assert 'method="post"' not in html.lower()
        texto = texto_visivel(resposta)
        for termo in proibidos:
            assert termo not in texto, termo

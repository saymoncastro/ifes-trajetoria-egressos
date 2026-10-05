"""Fronteiras da 021 com 001, 012, 013, 018 e 019 (FR-042 a FR-045, FR-071)."""

import ast
import logging
from dataclasses import fields
from pathlib import Path

import pytest

from tests.narrativa import construcao as cn
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO, PessoaEncontrada

RAIZ = Path("trajetoria")
CAPACIDADES_DA_021 = (
    "trajetoria.narrativa",
    "trajetoria.contexto_trajetoria",
    "trajetoria.fonte_academica.contexto_da_trajetoria",
    "trajetoria.fonte_academica.contexto_simulado",
)


def _importacoes(arquivo: Path):
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            yield from (a.name for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            yield no.module
            yield from (f"{no.module}.{a.name}" for a in no.names)


def _modulos(pasta: str):
    return [a for a in (RAIZ / pasta).rglob("*.py") if "migrations" not in a.parts]


def test_contexto_fundamental_inalterado():
    assert CAMPOS_DE_CONTEXTO == (
        "curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao",
        "data_conclusao",
    )
    assert tuple(f.name for f in fields(PessoaEncontrada)) == (
        "id_externo", "nome", "conclusoes", "cpf", "data_nascimento",
    )


def test_snapshot_da_012_inalterado():
    from trajetoria.analitico.models import RegistroDoSnapshot

    assert [f.name for f in RegistroDoSnapshot._meta.get_fields() if f.concrete] == [
        "id", "snapshot", "conclusao", "participacao", "origem_formacao", "elegivel_no_snapshot",
        "curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao",
        "data_conclusao",
    ]


def test_exportacao_da_013_inalterada():
    from trajetoria.exportacao import contrato

    assert contrato.VERSAO_CONTRATO == 2
    assert [c.nome for c in contrato.COLUNAS_BASE] == [
        "conclusao_analitica_id", "pessoa_analitica_id", "elegivel_no_snapshot", "unidade",
        "curso", "nivel", "modalidade", "forma_oferta", "ano_conclusao", "data_conclusao",
        "possui_participacao", "participacao_concluida", "participacao_iniciada_em",
        "participacao_concluida_em", "origem_formacao",
    ]


def test_narrativa_nao_le_analitico_acompanhamento_nem_respostas():
    for arquivo in _modulos("narrativa"):
        for modulo in _importacoes(arquivo):
            assert not modulo.startswith(
                ("trajetoria.analitico", "trajetoria.acompanhamento", "trajetoria.exportacao")
            ), (arquivo, modulo)
        nomes = {
            getattr(no, "id", None) or getattr(no, "attr", None)
            for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8")))
            if isinstance(no, ast.Name | ast.Attribute)
        }
        assert not nomes & {"Resposta", "RespostaOpcao", "respostas"}, arquivo


@pytest.mark.parametrize("pasta", ["acesso", "declaracao", "academico"])
def test_001_018_019_nao_conhecem_a_021(pasta):
    for arquivo in _modulos(pasta):
        for modulo in _importacoes(arquivo):
            assert not modulo.startswith(CAPACIDADES_DA_021), (arquivo, modulo)


def test_so_a_rasterizacao_importa_resvg():
    for arquivo in RAIZ.rglob("*.py"):
        if any(m.split(".")[0] == "resvg_py" for m in _importacoes(arquivo)):
            assert arquivo == RAIZ / "narrativa" / "rasterizacao.py", arquivo


@pytest.mark.parametrize("pasta", ["acesso", "declaracao", "academico", "analitico",
                                   "exportacao", "acompanhamento"])
def test_001_018_019_e_analiticos_nao_conhecem_a_022(pasta):
    """O vídeo (022) é derivado opcional: nem identidade nem snapshot/exportação o veem."""
    for arquivo in _modulos(pasta):
        for modulo in _importacoes(arquivo):
            assert not modulo.startswith("trajetoria.video"), (arquivo, modulo)


def test_so_o_renderizador_chama_processos_externos():
    for arquivo in RAIZ.rglob("*.py"):
        if any(m.split(".")[0] == "subprocess" for m in _importacoes(arquivo)):
            assert arquivo == RAIZ / "video" / "renderizador.py", arquivo


@pytest.mark.django_db
def test_logs_sem_dados_pessoais(client, cenario, caplog):
    caplog.set_level(logging.DEBUG)
    maria = cenario.pessoa("SIM-P-0003")
    cenario.concluir(maria.conclusoes.first())
    cn.entrar(client, maria)
    for rota in ("/minha-trajetoria/", "/minha-trajetoria/card.png?nome=1",
                 "/minha-trajetoria/card.svg?nome=1"):
        client.get(rota)
    for registro in caplog.records:
        mensagem = registro.getMessage()
        assert "Maria Exemplo" not in mensagem
        assert "Tecnologia em Análise" not in mensagem
        assert "00000000272" not in mensagem

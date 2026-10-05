"""Isolamento dos contatos (020 FR-005, FR-006; research R9 C5, R14; T039).

Identidade (018), incorporação (001), declaração (019), narrativa (021) e vídeo (022) não
dependem da capacidade de contatos, e o contrato acadêmico não muda.
"""

import ast
import dataclasses
from pathlib import Path

import pytest

from tests.acesso.construcao import ANA
from trajetoria.academico.incorporacao import incorporar_pessoa
from trajetoria.contato.models import ContatoDaPessoa
from trajetoria.demonstracao.cenario import preparar
from trajetoria.fonte_academica import contrato
from trajetoria.fonte_academica.contatos_simulados import ContatosSimulados
from trajetoria.fonte_academica.simulada import FonteSimulada

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"
PROIBIDOS = ("trajetoria.contato", "trajetoria.mobilizacao", "trajetoria.fonte_academica.contatos")
ISOLADOS = (
    "academico", "acesso", "declaracao", "narrativa", "video", "contexto_trajetoria",
    "participacao", "analitico", "exportacao", "instrumento", "campanha", "governanca",
)


def _importados(arquivo):
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module:
            yield no.module
        elif isinstance(no, ast.Import):
            yield from (a.name for a in no.names)


def test_apps_isolados_nao_importam_contatos_nem_lotes():
    arquivos = [p for pasta in ISOLADOS for p in (RAIZ / pasta).rglob("*.py")]
    arquivos += [RAIZ / "fonte_academica" / n for n in ("contrato.py", "simulada.py")]
    for arquivo in arquivos:
        for modulo in _importados(arquivo):
            assert not modulo.startswith(PROIBIDOS), f"{arquivo}: {modulo}"


def test_contrato_academico_inalterado():
    assert [f.name for f in dataclasses.fields(contrato.PessoaEncontrada)] == [
        "id_externo", "nome", "conclusoes", "cpf", "data_nascimento",
    ]
    assert "email" not in contrato.CAMPOS_DE_CONTEXTO


@pytest.mark.django_db
def test_incorporacao_nao_consulta_contatos(monkeypatch):
    def proibido(*_):
        raise AssertionError("a incorporação não conhece a capacidade de contatos")

    monkeypatch.setattr(ContatosSimulados, "obter_emails", proibido)
    incorporar_pessoa(FonteSimulada(), "SIM-P-0001")
    assert not ContatoDaPessoa.objects.exists()


@pytest.mark.django_db
def test_acesso_funciona_com_fonte_de_contatos_indisponivel(client, settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar(fonte_de_contatos=ContatosSimulados(indisponivel=True))
    assert not ContatoDaPessoa.objects.exists()
    resposta = client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento})
    assert resposta.status_code == 303
    assert resposta["Location"] == "/formacoes/"

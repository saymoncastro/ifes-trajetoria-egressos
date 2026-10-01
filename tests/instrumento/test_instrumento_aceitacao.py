"""Aceitação da Feature 002: SC-001, SC-006 e SC-007."""

import ast
from pathlib import Path

import pytest
from django.apps import apps

from tests.instrumento.construcao import RAMOS, percursos_de_secoes, versao_de_demonstracao
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import EstadoVersao, TipoPergunta

pytestmark = pytest.mark.django_db

APP = Path(__file__).resolve().parents[2] / "trajetoria" / "instrumento"


def test_sc001_versao_de_demonstracao_publicavel_e_percursos_esperados():
    versao = versao_de_demonstracao()
    assert op.publicar(versao) == op.SituacaoPublicacao.PUBLICADA
    conteudo = conteudo_da_versao(versao)
    comum = ("Avaliação",)
    esperados = {("Termos", "FIM")}
    for ramo in RAMOS:
        inicio = ("Termos", "Pessoais", "Curso", ramo, *comum)
        esperados.add((*inicio, "Trabalha", "#11", "FIM"))
        esperados.add((*inicio, "Não trabalha", "#11", "FIM"))
    assert percursos_de_secoes(conteudo) == esperados

    perguntas = [p for s in conteudo.secoes for p in s.perguntas]
    assert {p.tipo for p in perguntas} == set(TipoPergunta)
    assert any(o.complemento_textual for p in perguntas for o in p.opcoes)
    assert any(p.texto_explicativo for p in perguntas)
    assert any(not p.obrigatoria for p in perguntas)
    assert any(p.escala and p.escala.rotulo_fim for p in perguntas)
    assert any(s.titulo is None for s in conteudo.secoes)
    assert conteudo.titulo and conteudo.texto_abertura and conteudo.texto_encerramento


def _importacoes(arquivo: Path) -> set[str]:
    modulos = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module)
    return modulos


def test_sc006_instrumento_independente_do_nucleo_academico():
    for arquivo in APP.rglob("*.py"):
        for modulo in _importacoes(arquivo):
            assert not modulo.startswith(
                ("trajetoria.academico", "trajetoria.fonte_academica")
            ), (arquivo, modulo)
    for modelo in apps.get_app_config("instrumento").get_models():
        for campo in modelo._meta.get_fields():
            if campo.is_relation and campo.related_model is not None:
                assert campo.related_model._meta.app_label == "instrumento", (modelo, campo)


def test_sc007_quatro_tipos_dois_estados_cinco_modelos():
    assert len(TipoPergunta) == 4
    assert len(EstadoVersao) == 2
    nomes = {m.__name__ for m in apps.get_app_config("instrumento").get_models()}
    # A igualdade também garante FR-066: a 002 não cria Campanha, Participação nem
    # Resposta (esses conceitos pertencem às features seguintes).
    assert nomes == {"Pesquisa", "Versao", "Secao", "Pergunta", "Opcao"}

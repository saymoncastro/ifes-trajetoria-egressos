"""Fronteiras e invariantes estruturais da interface (008 SC-006, SC-007, SC-012, SC-013,
SC-016, SC-017; FR-005, FR-069, FR-079 a FR-096).

Complementa os testes de comportamento: a prova principal de que a navegação é da 006 é a
Versão de estrutura diferente (test_interface_navegacao); aqui ficam as verificações
baratas de importação, escrita, textos, métodos, CSRF, rastros e páginas de erro.
"""

import ast
import logging
import re
import tomllib
from pathlib import Path
from uuid import uuid4

import pytest
from django.apps import apps
from django.test import Client, RequestFactory
from django.views import defaults

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.formulario_2024 import declaracao
from trajetoria.participacao.models import Participacao

RAIZ = Path(__file__).resolve().parents[2]
INTERFACE = RAIZ / "trajetoria" / "interface"
DEMONSTRACAO = RAIZ / "trajetoria" / "demonstracao"

# Módulo de domínio → nomes que a interface pode importar dele (None = qualquer nome).
PERMITIDOS_NA_INTERFACE = {
    "trajetoria.participacao.entrada": None,
    "trajetoria.participacao.operacoes": {
        "responder_escolha_unica",
        "responder_escolha_multipla",
        "responder_texto",
        "responder_escala",
        "remover_resposta",
        "concluir",
    },
    "trajetoria.participacao.consultas": {"situacao_da_jornada"},
    "trajetoria.participacao.percurso": {"Saida"},
    "trajetoria.participacao.regras": {"Motivo", "ParticipacaoRejeitada"},
    "trajetoria.participacao.models": {"Participacao"},
    "trajetoria.instrumento.conteudo": None,
    "trajetoria.instrumento.models": {"Pergunta", "Opcao", "TipoPergunta"},
    "trajetoria.academico.models": {"ConclusaoAcademica", "Pessoa"},
    "trajetoria.demonstracao.entrada": {"pessoa_em_uso"},  # FR-005: só a Pessoa resolvida
}
SO_NO_CENARIO = (
    "trajetoria.campanha",
    "trajetoria.instrumento.operacoes",
    "trajetoria.formulario_2024",
    "trajetoria.academico.incorporacao",
    "trajetoria.fonte_academica.cenarios",
    "trajetoria.participacao.entrada",
)


def _importacoes(arquivo: Path):
    """(módulo, nome) de cada importação de `trajetoria.*`."""
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module and no.module.startswith("trajetoria"):
            for alias in no.names:
                yield no.module, alias.name
        elif isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.startswith("trajetoria"):
                    yield alias.name, None


def _fontes(*pastas, sufixos=(".py", ".html", ".css")):
    return [p for pasta in pastas for p in pasta.rglob("*") if p.suffix in sufixos]


def test_interface_so_importa_o_permitido_do_dominio():
    for arquivo in INTERFACE.rglob("*.py"):
        for modulo, nome in _importacoes(arquivo):
            if modulo.startswith("trajetoria.interface"):
                continue
            assert modulo in PERMITIDOS_NA_INTERFACE, (arquivo.name, modulo)
            permitidos = PERMITIDOS_NA_INTERFACE[modulo]
            assert permitidos is None or nome in permitidos, (arquivo.name, modulo, nome)


def test_demonstracao_isolada():
    for arquivo in DEMONSTRACAO.rglob("*.py"):
        relativo = arquivo.relative_to(DEMONSTRACAO).as_posix()
        for modulo, _nome in _importacoes(arquivo):
            if modulo.startswith("trajetoria.interface"):
                assert relativo == "views.py", relativo
                assert modulo == "trajetoria.interface.apresentacao", modulo
            if modulo.startswith(SO_NO_CENARIO):
                assert relativo == "cenario.py", (relativo, modulo)


def test_nenhuma_regra_por_pergunta_nos_fontes():
    textos = {
        t
        for s in declaracao.SECOES
        for p in s.perguntas
        for t in (p.texto, *p.opcoes)
        if len(t) >= 12
    }
    for arquivo in _fontes(INTERFACE, DEMONSTRACAO):
        conteudo = arquivo.read_text()
        assert not re.search(r"\bQ\d{1,2}\b", conteudo), arquivo.name
        if arquivo.name == "cenario.py":
            continue  # critérios de Campanha usam valores institucionais (ex.: nível)
        assert not [t for t in textos if t in conteudo], arquivo.name


def test_nenhuma_escrita_direta_nem_modelo():
    for arquivo in _fontes(INTERFACE, DEMONSTRACAO, sufixos=(".py",)):
        conteudo = arquivo.read_text()
        assert not re.search(r"\.(save|create|update|delete|bulk_\w+)\(", conteudo), arquivo
    assert not (INTERFACE / "models.py").exists() and not (DEMONSTRACAO / "models.py").exists()
    for app in ("interface", "demonstracao"):
        assert list(apps.get_app_config(app).get_models()) == []


def test_sem_dependencia_nova_nem_script():
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text())["project"]
    assert projeto["dependencies"] == ["Django>=5.2,<5.3", "psycopg[binary]>=3.2,<3.4"]
    for arquivo in _fontes(INTERFACE, DEMONSTRACAO, sufixos=(".html",)):
        conteudo = arquivo.read_text()
        assert "<script" not in conteudo and not re.search(r'(src|href)="https?://', conteudo)


# --- HTTP ----------------------------------------------------------------------------------


@pytest.fixture
def ana(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


@pytest.mark.django_db
def test_csrf_em_toda_escrita(cenario, ana):
    sem_token = Client(enforce_csrf_checks=True)
    base = f"/participacoes/{ana.pk}/"
    for rota in (
        "/demonstracao/escolher/",
        "/demonstracao/encerrar/",
        "/formacoes/entrar/",
        base + "secoes/1/",
        base + "concluir/",
    ):
        assert sem_token.post(rota).status_code == 403, rota


@pytest.mark.django_db
def test_metodos(client, cenario, ana):
    base = f"/participacoes/{ana.pk}/"
    for rota in ("/demonstracao/escolher/", "/demonstracao/encerrar/", "/formacoes/entrar/"):
        assert client.get(rota).status_code == 405, rota
    for rota in ("/", "/demonstracao/", "/formacoes/", base, base + "concluida/"):
        assert client.post(rota).status_code == 405, rota
    for rota in (base + "secoes/1/", base + "concluir/"):
        assert client.put(rota).status_code == 405 and client.delete(rota).status_code == 405


@pytest.mark.django_db
def test_rastros_e_telas_sem_dados_declarados_nem_tecnicos(client, cenario, caplog):
    caplog.set_level(logging.DEBUG)
    pessoa = cenario.pessoa("SIM-P-0001")
    curso = pessoa.conclusoes.get().curso
    declarado = f"Texto declarado {uuid4().hex[:8]}"
    respostas = [client.get("/demonstracao/")]
    ci.entrar_como(client, pessoa)
    respostas.append(client.get("/formacoes/"))
    entrada = client.post("/formacoes/entrar/")
    participacao = Participacao.objects.get(pk=ci.participacao_de(entrada))
    base = f"/participacoes/{participacao.pk}/"
    respostas.append(client.get(base + "secoes/1/"))
    redirecionamentos = [entrada, client.post(base + "secoes/1/", {"p1": "1"})]
    respostas.append(client.post(base + "secoes/2/", {"p1": "99", "p2": declarado}))
    redirecionamentos.append(client.post(base + "secoes/2/", {"p2": declarado}))
    respostas.append(client.get(redirecionamentos[-1]["Location"]))
    respostas.append(client.get("/nao-existe/"))
    for valor in (declarado, pessoa.nome, curso):
        assert valor not in caplog.text
        for r in redirecionamentos + respostas:
            assert valor not in r.get("Location", "")
            assert valor not in r.wsgi_request.get_full_path()
    for r in respostas:
        texto = ci.texto_visivel(r)
        assert ci.tecnicos_em(texto) == [], r.wsgi_request.path
        assert "progresso" not in texto.lower() and not re.search(r"\d+\s*%", texto)
        assert not re.search(r"etapa \d+ de \d+", texto.lower())


# --- Páginas de erro (FR-001, FR-068, FR-069) -----------------------------------------------

TECNICO = re.compile(r"Traceback|Exception|Error|RuntimeError|\.py\b|/Users/|Participacao")


def test_pagina_500_generica():
    resposta = defaults.server_error(RequestFactory().get("/"))
    texto = resposta.content.decode()
    assert resposta.status_code == 500
    assert "Não foi possível concluir a operação. Tente novamente." in texto
    assert 'href="/"' in texto and not TECNICO.search(texto)
    assert "Ambiente de demonstração" not in texto


@pytest.mark.django_db
def test_pagina_404_autonoma():
    resposta = defaults.page_not_found(RequestFactory().get("/x/"), Exception("x"))
    texto = resposta.content.decode()
    assert "Página não encontrada." in texto and "Ambiente de demonstração" not in texto
    assert "Trocar de pessoa" not in texto


@pytest.mark.django_db
@pytest.mark.urls("tests.interface.urls_falha")
def test_falha_inesperada_mostra_pagina_generica_e_registra(caplog):
    caplog.set_level(logging.ERROR, logger="django.request")
    resposta = Client(raise_request_exception=False).get("/falha-de-teste/")
    texto = resposta.content.decode()
    assert resposta.status_code == 500
    assert "Não foi possível concluir a operação. Tente novamente." in texto
    assert not TECNICO.search(texto)
    assert "Internal Server Error: /falha-de-teste/" in caplog.text


def test_tempo_padrao_dos_testes_e_controlado(relogio):
    from django.utils import timezone

    assert timezone.now() == c.NO_PERIODO

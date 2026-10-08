"""Início do Portal (024 US1; FR-015 a FR-021, FR-031; contracts/inicio.md)."""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from trajetoria.interface import mensagens as estados
from trajetoria.portal import mensagens

pytestmark = pytest.mark.django_db

VEDADOS = ("minuto", "%", "turma", "geração", "conectad", "Olá", "Oportunidade",
           "Volte ao Ifes", "comunidade")


def _inicio(client, pessoa):
    cp.entrar(client, pessoa)
    resposta = client.get("/inicio/")
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    return resposta


def _principal(resposta) -> str:
    html = resposta.content.decode()
    return html[html.index("<main"): html.index("</main>")]


def test_ordem_reconhecimento_proveniencia_acoes_convite(client, cenario):
    resposta = _inicio(client, cenario.pessoa("SIM-P-0003"))
    html = _principal(resposta)
    posicoes = [
        html.index("<figure"),
        html.index("<h1>"),
        html.index("O Ifes registra 2 formações concluídas por você."),
        html.index("Tecnologia em Análise e Desenvolvimento de Sistemas"),
        html.index(mensagens.PROVENIENCIA),
        html.index(mensagens.TITULO_ACOES),
        html.index(mensagens.TITULO_CONVITE),
    ]
    assert posicoes == sorted(posicoes)
    assert html.count("<h1") == 1


def test_cada_frase_de_formacao_tem_a_origem(client, cenario):
    html = _principal(_inicio(client, cenario.pessoa("SIM-P-0003")))
    itens = re.findall(r"<li>(.*?)</li>", html[html.index('class="inicio-formacoes"'):], re.S)
    formacoes = [i for i in itens if "<p" in i]
    assert len(formacoes) == 2
    for item in formacoes:
        primeira = re.search(r"<p>(.*?)</p>", item, re.S).group(1)
        assert mensagens.REGISTRO_DO_IFES in primeira


def test_todas_as_conclusoes_na_ordem_da_007(client, cenario):
    diego = cenario.pessoa("SIM-P-0004")
    texto = ci.texto_visivel(_inicio(client, diego))
    cursos = [k.curso for k in diego.conclusoes.all()]
    assert len(cursos) == 3
    assert [texto.index(curso) for curso in cursos] == sorted(texto.index(k) for k in cursos)


def test_sem_nome_e_sem_vocabulario_vedado(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    principal = _principal(_inicio(client, maria))
    texto = re.sub(r"<[^>]+>", " ", principal)
    assert maria.nome not in texto  # FR-019: o Início não exibe o nome
    for vedado in VEDADOS:
        assert vedado.lower() not in texto.lower(), vedado


def test_pesquisa_so_no_convite(client, cenario):
    principal = _principal(_inicio(client, cenario.pessoa("SIM-P-0003")))
    antes_do_convite = principal[: principal.index('class="inicio-convite"')]
    assert "pesquisa" not in re.sub(r"<[^>]+>", " ", antes_do_convite).lower()


def test_todo_endereco_do_inicio_responde(client, cenario):
    html = _inicio(client, cenario.pessoa("SIM-P-0003")).content.decode()
    enderecos = set(re.findall(r'href="(/[^"#]*)', html))
    assert {"/minha-trajetoria/", "/meu-email/", "/formacoes/", "/inicio/"} <= enderecos
    for endereco in enderecos:
        assert client.get(endereco).status_code in (200, 302), endereco


def test_nao_le_resposta_nem_contato(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    with CaptureQueriesContext(connection) as consultas:
        assert client.get("/inicio/").status_code == 200
    tabelas = " ".join(q["sql"] for q in consultas.captured_queries)
    assert "participacao_resposta" not in tabelas
    assert "contato_contatodapessoa" not in tabelas


# --- Convite por situação (FR-020) ---------------------------------------------------------


def _convite(resposta) -> str:
    html = _principal(resposta)
    return html[html.index('class="inicio-convite"'):]


def test_convite_para_iniciar(client, cenario):
    convite = _convite(_inicio(client, cenario.pessoa("SIM-P-0001")))
    assert "Tecnologia em Análise e Desenvolvimento de Sistemas" in convite
    assert f'href="/formacoes/">{mensagens.ACAO_RESPONDER}<' in convite


def test_convite_para_retomar(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    ci.iniciar(client, ana)
    convite = _convite(client.get("/inicio/"))
    assert f'href="/formacoes/">{mensagens.ACAO_CONTINUAR}<' in convite


def test_convite_com_varias_formacoes(client, cenario):
    convite = _convite(_inicio(client, cenario.pessoa("SIM-P-0003")))
    assert mensagens.CONVITE_VARIAS.format(n=2) in convite
    assert f'href="/formacoes/">{mensagens.ACAO_ESCOLHER}<' in convite


def test_convite_sem_pendencia_e_sem_pesquisa(client, cenario, relogio):
    ana = cenario.pessoa("SIM-P-0001")
    cenario.concluir(ana.conclusoes.first())
    convite = _convite(_inicio(client, ana))
    assert estados.SEM_ENTRADA_PENDENTE in convite and "<a" not in convite
    relogio.agora = c.DEPOIS_DO_FIM
    convite = _convite(_inicio(client, ana))  # nova sessão: a anterior expirou
    assert estados.SEM_PESQUISA in convite and "<a" not in convite


# --- Casos de borda ------------------------------------------------------------------------


def test_pessoa_sem_conclusao(client, cenario):
    resposta = _inicio(client, cp.pessoa_sem_conclusao())
    principal = _principal(resposta)
    assert estados.SEM_FORMACAO in principal
    assert "inicio-convite" not in principal and "/minha-trajetoria/" not in principal
    assert re.findall(r'<li><a href="([^"]+)"', principal) == ["/meu-email/"]


def test_falha_da_narrativa_omite_o_reconhecimento(client, cenario, monkeypatch, caplog):
    maria = cenario.pessoa("SIM-P-0003")

    def falha(entrada):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr("trajetoria.portal.inicio.montar", falha)
    principal = _principal(_inicio(client, maria))
    assert "<figure" not in principal and "inicio-formacoes" not in principal
    assert mensagens.TITULO_ACOES in principal and mensagens.TITULO_CONVITE in principal
    registro = " ".join(r.getMessage() for r in caplog.records)
    assert "portal: falha ao montar o reconhecimento" in registro
    assert maria.nome not in registro


def test_atalho_do_video_so_com_renderizador(client, cenario, monkeypatch):
    maria = cenario.pessoa("SIM-P-0003")
    assert "#video" not in _principal(_inicio(client, maria))
    monkeypatch.setattr("trajetoria.video.renderizador.disponivel", lambda: True)
    assert 'href="/minha-trajetoria/#video"' in _principal(client.get("/inicio/"))

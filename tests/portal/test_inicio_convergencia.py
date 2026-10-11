"""Início e Participação na convergência C (032 FR-008 a FR-012; US2, US3)."""

import re
from datetime import timedelta

import pytest

from tests.declaracao import construcao as cd
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from tests.portal import construcao_contribuicao as cc
from tests.portal import construcao_oportunidades as co
from trajetoria.portal import mensagens as m
from trajetoria.portal.contribuicao import mensagens as m_contribuicao
from trajetoria.portal.contribuicao import operacoes

pytestmark = pytest.mark.django_db

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"


def _principal(client, url="/inicio/") -> str:
    resposta = client.get(url)
    assert resposta.status_code == 200, url
    html = resposta.content.decode()
    return html[html.index("<main"):html.index("</main>")]


def _texto(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _li(principal: str, classe: str) -> str | None:
    achado = re.search(rf'<li class="{classe}">(.*?)</li>', principal, re.S)
    return achado.group(1) if achado else None


# --- Hoje e Adiante (FR-009) -------------------------------------------------------------------

def test_hoje_sem_oportunidade_diz_que_nao_ha_e_nao_tem_secao(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client)
    hoje = _li(principal, "inicio-linha-hoje")
    assert m.HOJE_NENHUMA in hoje and "<a" not in hoje
    assert 'id="oportunidades"' not in principal and "inicio-encontros" not in principal


def test_hoje_conta_as_oportunidades_e_leva_a_secao(client, cenario):
    co.publicada("Para todos")
    co.publicada("Outra para todos")
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client)
    assert f'<a href="#oportunidades">{m.HOJE_VARIAS.format(n=2)}</a>' in _li(
        principal, "inicio-linha-hoje")
    assert 'id="oportunidades"' in principal


def test_adiante_convida_ou_conta_as_enviadas(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    cp.entrar(client, ana)
    adiante = _li(_principal(client), "inicio-linha-adiante")
    assert f'href="/contribuir/">{m_contribuicao.INICIO_TITULO}<' in adiante
    enviada = cc.registrar(ana)
    adiante = _li(_principal(client), "inicio-linha-adiante")
    assert f'href="/contribuicoes/">{m_contribuicao.ADIANTE_UMA}<' in adiante
    operacoes.retirar(ana, enviada.pk, agora=c.NO_PERIODO)  # retirada não conta
    assert m_contribuicao.INICIO_TITULO in _li(_principal(client), "inicio-linha-adiante")
    assert "andamento" not in _principal(client)


# --- Encontros e oportunidades (FR-008, FR-012) --------------------------------------------------

def test_encontro_pertinente_tem_secao_propria_e_nao_repete_no_destaque(client, cenario):
    co.publicada("Encontro de egressos de TI", categoria="eventos")
    co.publicada("Curso para todos")
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client)
    encontros = re.search(r'<section class="inicio-encontros.*?</section>', principal,
                          re.S).group(0)
    assert m.TITULO_ENCONTROS in encontros and "Encontro de egressos de TI" in encontros
    oportunidades = re.search(r'<section class="inicio-oportunidades.*?</section>', principal,
                              re.S).group(0)
    assert "Curso para todos" in oportunidades and "Encontro de egressos" not in oportunidades
    assert posicao(principal, "inicio-encontros") < posicao(principal, "inicio-oportunidades")


def posicao(html: str, classe: str) -> int:
    return html.index(f'class="{classe}')


def test_so_o_encontro_sem_secao_de_oportunidades(client, cenario):
    co.publicada("Único encontro", categoria="eventos")
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client)
    assert "inicio-encontros" in principal and 'class="inicio-oportunidades' not in principal
    # Code review: sem a seção, o "Hoje" leva à página de Oportunidades, não a uma âncora vazia.
    assert f'<a href="/oportunidades/">{m.HOJE_UMA}</a>' in _li(principal, "inicio-linha-hoje")
    assert 'href="#oportunidades"' not in principal


def test_ponte_diz_por_que_ou_para_quem(client, cenario):
    co.publicada("Para TADS", publico_cursos=[TADS], unidade_responsavel="Serra")
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    texto = _texto(_principal(client))
    assert f"{m.PORQUE_CONCLUIU} {TADS} · 2022" in texto
    assert m.SEM_INSCRICAO in texto


# --- Participação (FR-008, FR-011) --------------------------------------------------------------

def test_participacao_contribuicao_canal_e_convite_por_ultimo(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    manifestacao = cc.registrar(ana)
    operacoes.registrar_contato(manifestacao.pk, operador=cc.OPERADOR_A, escopo=cc.ESCOPO_A,
                                agora=c.NO_PERIODO + timedelta(days=2))
    cp.entrar(client, ana)
    principal = _principal(client)
    ordem = [principal.index(x) for x in ('inicio-contribuir"', 'participacao-canal"',
                                          'inicio-convite"')]
    assert ordem == sorted(ordem)
    texto = _texto(principal)
    assert m_contribuicao.TITULO_SUA in texto
    assert "Compartilhar experiência · Unidade Serra" in texto
    assert m_contribuicao.MARCO_ENVIADA in texto and "A unidade Serra registrou contato" in texto
    assert m.CANAL_TEXTO in texto and 'href="/meu-email/">Informar e-mail<' in principal
    for retirado in ("Não informado", "remover", "Que bom ver", "Compartilhar<", "continua."):
        assert retirado not in principal, retirado


def test_pagina_participacao(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client, "/participacao/")
    assert principal.count("<h1") == 1 and m.TITULO_PARTICIPACAO in principal
    for destino in ("/contribuir/", "/meu-email/", "/formacoes/"):
        assert f'href="{destino}"' in principal, destino
    assert "inicio-formacoes" not in principal and "<form" not in principal


def test_participacao_sem_conclusao_so_canal(client, cenario):
    cp.entrar(client, cp.pessoa_sem_conclusao())
    principal = _principal(client, "/participacao/")
    assert "inicio-contribuir" not in principal and 'href="/meu-email/"' in principal
    # Code review: sem o item "Pesquisa" na navegação, a escolha de formações continua aqui.
    assert f'href="/formacoes/">{m.VER_FORMACOES}<' in principal


def test_participacao_sem_sessao_e_declarante(client, cenario):
    assert client.get("/participacao/")["Location"] == "/entrar/"
    cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
    assert client.get("/participacao/")["Location"] == "/declaracao/"


@pytest.mark.urls("tests.portal.urls_sem_portal")
def test_sem_o_portal_participacao_nao_existe(client, cenario, settings):
    settings.TRAJETORIA_PORTAL = False
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    assert client.get("/participacao/").status_code == 404


# --- Ações do card -------------------------------------------------------------------------------

def test_uma_leitura_das_manifestacoes_no_inicio(client, cenario):
    """Code review: existência, contagem e a mais recente saem de uma consulta só."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    ana = cenario.pessoa("SIM-P-0001")
    cc.registrar(ana)
    cp.entrar(client, ana)
    with CaptureQueriesContext(connection) as consultas:
        assert client.get("/inicio/").status_code == 200
    leituras = [q for q in consultas.captured_queries if "portal_manifestacao" in q["sql"]]
    assert len(leituras) == 1


def test_baixar_meu_card_baixa_o_arquivo(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    principal = _principal(client)
    achado = re.search(r'<a href="(/minha-trajetoria/card\.(png|svg))" download="([^"]+)"'
                       r' class="portal-botao">Baixar meu card</a>', principal)
    assert achado and achado.group(3) == f"minha-trajetoria-ifes.{achado.group(2)}"
    assert client.get(achado.group(1)).status_code == 200

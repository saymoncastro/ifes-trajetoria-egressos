"""Acesso à página "Minha trajetória no Ifes" (021 US1; FR-001, FR-002, FR-010, FR-016,
FR-069; SC-002, SC-012)."""

from datetime import timedelta

import pytest
from django.conf import settings

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn

pytestmark = pytest.mark.django_db

URL = "/minha-trajetoria/"


def _maria_concluida(cenario):
    maria = cenario.pessoa("SIM-P-0003")
    cenario.concluir(maria.conclusoes.first())
    return maria


def test_maria_depois_de_concluir_ve_as_duas_formacoes(client, cenario):
    cn.entrar(client, _maria_concluida(cenario))
    resposta = client.get(URL)
    assert resposta.status_code == 200
    texto = ci.texto_visivel(resposta)
    assert "O Ifes registra 2 formações concluídas por você." in texto
    assert "Tecnologia em Análise e Desenvolvimento de Sistemas" in texto
    assert "Especialização em Informática na Educação" in texto


def test_sem_participacao_concluida_vai_para_formacoes(client, cenario):
    cn.entrar(client, cenario.pessoa("SIM-P-0003"))
    resposta = client.get(URL)
    assert resposta.status_code == 302 and resposta["Location"] == "/formacoes/"


def test_sem_sessao_vai_para_acesso(client, cenario):
    resposta = client.get(URL)
    assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"


def test_sessao_de_declarante_vai_para_acesso(client, cenario):
    from tests.declaracao import construcao as cd
    from tests.participacao import construcao as c

    formacao = cd.declaracao_concluida(cenario.campanha)
    sessao = client.session
    sessao.update({
        "declaracao.formacoes": [str(formacao.pk)],
        "declaracao.confirmada_em": c.NO_PERIODO.isoformat(),
        "declaracao.ultimo_uso": c.NO_PERIODO.isoformat(),
    })
    sessao.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key
    resposta = client.get(URL)
    assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"


def test_sessao_expirada_nao_mostra_nada(client, cenario, relogio):
    cn.entrar(client, _maria_concluida(cenario))
    relogio.agora += settings.TRAJETORIA_SESSAO_INATIVIDADE + timedelta(minutes=1)
    resposta = client.get(URL)
    assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"


def test_sem_cache(client, cenario):
    cn.entrar(client, _maria_concluida(cenario))
    assert "no-store" in client.get(URL)["Cache-Control"]


def test_modo_demonstracao_desligado_404(client, cenario, settings):
    cn.entrar(client, _maria_concluida(cenario))
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert client.get(URL).status_code == 404


def test_uma_narrativa_por_pessoa(client, cenario):
    maria = _maria_concluida(cenario)
    cn.entrar(client, maria)
    antes = ci.texto_visivel(client.get(URL))
    cenario.concluir(maria.conclusoes.last())
    assert ci.texto_visivel(client.get(URL)) == antes


def test_diego_em_ordem_e_ana_sem_outras(client, cenario):
    diego = cenario.pessoa("SIM-P-0004")
    cenario.concluir(diego.conclusoes.first())
    cn.entrar(client, diego)
    texto = ci.texto_visivel(client.get(URL))
    assert texto.index("Técnico em Química") < texto.index("Licenciatura em Química") < (
        texto.index("Mestrado Profissional em Química")
    )
    ana = cenario.pessoa("SIM-P-0001")
    cenario.concluir(ana.conclusoes.get())
    cn.entrar(client, ana)
    assert "Outras formações no Ifes" not in ci.texto_visivel(client.get(URL))

"""Trajetória Ifes com o Portal desligado (024 US5; FR-027; SC-005; ADR 0008)."""

import pytest
from django.urls import URLResolver

from tests.interface import construcao_interface as ci
from tests.portal import construcao as cp

pytestmark = [pytest.mark.django_db, pytest.mark.urls("tests.portal.urls_sem_portal")]


@pytest.fixture(autouse=True)
def portal_desligado(settings):
    settings.TRAJETORIA_PORTAL = False


def test_raiz_volta_a_ser_a_da_008(client, cenario):
    from tests.declaracao import construcao as cd

    assert client.get("/")["Location"] == "/acesso/"
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    assert client.get("/")["Location"] == "/formacoes/"
    declarante = client.__class__()
    cp.sessao_de_declarante(declarante, cd.declaracao_concluida(cenario.campanha))
    assert declarante.get("/")["Location"] == "/declaracao/"


def test_rotas_do_portal_nao_existem(client, cenario):
    for url in ("/entrar/", "/inicio/"):
        assert client.get(url).status_code == 404
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    for url in ("/entrar/", "/inicio/"):
        assert client.get(url).status_code == 404


def test_nenhuma_tela_tem_navegacao(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    for url in ("/formacoes/", "/minha-trajetoria/", "/meu-email/"):
        resposta = client.get(url)
        assert resposta.status_code == 200, url
        assert "<nav" not in resposta.content.decode(), url


def test_shell_saida_e_retorno_de_hoje(client, cenario):
    """Revisão de 2026-10-08: sem o Portal, nome, "Sair" e links de fim de página são os de
    antes da revisão."""
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    for url in ("/formacoes/", "/minha-trajetoria/", "/meu-email/"):
        html = client.get(url).content.decode()
        assert '<span class="nome">Trajetória Ifes</span>' in html, url
        assert 'action="/acesso/sair/"' in html and 'action="/sair/"' not in html, url
        assert 'href="/inicio/"' not in html, url
    assert "Voltar às suas formações" in client.get("/minha-trajetoria/").content.decode()
    assert "Ver suas formações no Ifes" in client.get("/meu-email/").content.decode()
    assert client.post("/sair/").status_code == 404


def test_caminho_do_convite_completo(client, cenario):
    cp.com_material("SIM-P-0003")
    assert cp.entrar_pelo_convite(client, "SIM-P-0003")["Location"] == "/formacoes/"
    ana = cenario.pessoa("SIM-P-0001")
    participacao = cenario.concluir(ana.conclusoes.first())
    cp.entrar(client, ana)
    concluida = client.get(f"/participacoes/{participacao.pk}/concluida/")
    assert concluida.status_code == 200
    assert "Ver minha trajetória no Ifes" in ci.texto_visivel(concluida)


def test_trajetoria_antes_da_pesquisa_independe_do_portal(client, cenario):
    """FR-009 é regra da trajetória, não do Portal."""
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    assert client.get("/minha-trajetoria/").status_code == 200


def test_rotas_sem_o_portal():
    from config.rotas import rotas

    def modulos(padroes):
        for padrao in padroes:
            if isinstance(padrao, URLResolver):
                yield getattr(padrao.urlconf_module, "__name__", str(padrao.urlconf_module))

    assert "trajetoria.portal.urls" not in set(modulos(rotas(False)))
    assert "trajetoria.portal.urls" in set(modulos(rotas(True)))

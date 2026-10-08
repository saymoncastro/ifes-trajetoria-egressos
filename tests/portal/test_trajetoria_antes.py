"""Trajetória, card e vídeo antes de responder (024 US2; FR-009 a FR-012; SC-006)."""

import pytest

from tests.declaracao import construcao as cd
from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def test_pagina_card_e_svg_sem_participacao_sem_gravar(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    assert not Participacao.objects.filter(conclusao__pessoa=maria).exists()
    cp.entrar(client, maria)
    antes = cp.contagens()
    assert client.get("/minha-trajetoria/").status_code == 200
    assert client.get("/minha-trajetoria/card.svg").status_code == 200
    png = client.get("/minha-trajetoria/card.png")
    assert png.status_code in (200, 404)  # 404 só sem rasterização no ambiente (021)
    assert cp.contagens() == antes


def test_pedido_de_video_so_grava_o_pedido(client, cenario, monkeypatch):
    monkeypatch.setattr("trajetoria.video.renderizador.disponivel", lambda: True)
    monkeypatch.setattr("trajetoria.video.renderizador.renderizar", lambda composicao: b"")
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    antes = cp.contagens()
    client.post("/minha-trajetoria/video/")
    depois = cp.contagens()
    assert depois.pop("video.GeracaoDeVideo") == antes.pop("video.GeracaoDeVideo") + 1
    assert depois == antes


def test_rascunho_nao_muda(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    participacao = Participacao.objects.get(pk=ci.participacao_de(ci.iniciar(client, ana)))
    retrato = c.retrato(participacao)
    assert client.get("/minha-trajetoria/").status_code == 200
    assert client.get("/inicio/").status_code == 200
    participacao.refresh_from_db()
    assert c.retrato(participacao) == retrato and participacao.concluida_em is None


def test_formacao_declarada_continua_sem_narrativa(client, cenario):
    """FR-012 (021 FR-007): Formação Declarada não é Conclusão."""
    cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
    assert client.get("/minha-trajetoria/")["Location"] == "/acesso/"

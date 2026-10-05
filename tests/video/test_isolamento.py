"""Espera e falha não atrapalham (022 US4; FR-033, FR-037; SC-005)."""

import logging
from datetime import timedelta

import pytest
from django.apps import apps
from django.core.management import call_command

from tests.narrativa import construcao as cn
from trajetoria.narrativa import composicao as modulo_composicao
from trajetoria.video import operacoes, renderizador
from trajetoria.video.models import GeracaoDeVideo as G

pytestmark = pytest.mark.django_db
PAGINA, PEDIR = "/minha-trajetoria/", "/minha-trajetoria/video/"


def _contagens():
    return {
        modelo._meta.label: modelo.objects.count()
        for modelo in apps.get_models()
        if modelo._meta.app_label not in ("sessions", "video")
    }


@pytest.fixture
def maria(client, cenario):
    pessoa = cenario.pessoa("SIM-P-0003")
    cenario.concluir(pessoa.conclusoes.first())
    cn.entrar(client, pessoa)
    return pessoa


@pytest.mark.parametrize("cenario_do_render", ["pronto", "falha"])
def test_dominio_inalterado(client, maria, cenario_do_render, renderizador_falso, monkeypatch):
    if cenario_do_render == "falha":
        def falhar(composicao):
            raise renderizador.FalhaDeRenderizacao("codigo_1")

        monkeypatch.setattr(renderizador, "renderizar", falhar)
    antes = _contagens()
    client.post(PEDIR)
    call_command("processar_videos", "--uma-vez")
    client.get(PAGINA)
    client.get("/minha-trajetoria/video.mp4")
    assert _contagens() == antes


def test_dominio_inalterado_sem_renderizador(client, maria, monkeypatch):
    monkeypatch.setattr(renderizador, "disponivel", lambda: False)
    antes = _contagens()
    assert client.post(PEDIR).status_code == 303
    assert not G.objects.exists()
    assert _contagens() == antes


def test_pagina_e_card_funcionam_com_falha(client, maria, renderizador_com_falha):
    client.post(PEDIR)
    call_command("processar_videos", "--uma-vez")
    pagina = client.get(PAGINA)
    assert pagina.status_code == 200
    html = pagina.content.decode()
    assert "Não foi possível preparar o vídeo agora" in html and "Tentar novamente" in html
    assert client.get("/minha-trajetoria/card.svg").status_code == 200


def test_tentar_novamente(client, maria, renderizador_com_falha, renderizador_falso):
    G.objects.all().delete()
    client.post(PEDIR)
    G.objects.update(estado=G.FALHOU, motivo="codigo_1", composicao=None)
    client.post(PEDIR)
    assert G.objects.get().estado == G.SOLICITADO


def test_sem_renderizador_a_pagina_e_a_da_021(client, maria, monkeypatch):
    monkeypatch.setattr(renderizador, "disponivel", lambda: False)
    html = client.get(PAGINA).content.decode()
    assert 'id="video"' not in html and "Gerar vídeo" not in html
    assert 'id="card"' in html and "Baixar imagem" in html


def test_sem_processador_vira_falha(client, maria, renderizador_falso, relogio):
    client.post(PEDIR)
    relogio.agora += timedelta(minutes=11)
    assert "Não foi possível preparar o vídeo agora" in client.get(PAGINA).content.decode()


def test_erro_inesperado_no_bloco_nao_derruba_a_pagina(client, maria, renderizador_falso,
                                                       monkeypatch, caplog):
    def quebrar(*args, **kwargs):
        raise RuntimeError("Maria Exemplo")

    monkeypatch.setattr(operacoes, "bloco", quebrar)
    resposta = client.get(PAGINA)
    assert resposta.status_code == 200
    assert 'id="video"' not in resposta.content.decode()
    assert any(r.getMessage() == "video: falha ao montar o bloco" for r in caplog.records)


def test_composicao_impossivel_esconde_o_video(client, maria, renderizador_falso, monkeypatch):
    def impossivel(*args, **kwargs):
        raise modulo_composicao.ComposicaoImpossivel

    monkeypatch.setattr("trajetoria.narrativa.views.composicao_visual", impossivel)
    resposta = client.get(PAGINA)
    assert resposta.status_code == 200 and 'id="video"' not in resposta.content.decode()
    assert client.get("/minha-trajetoria/video.mp4").status_code == 404


def test_logs_sem_dados_pessoais(client, maria, renderizador_com_falha, caplog):
    caplog.set_level(logging.DEBUG)
    client.post(PEDIR, {"nome": "1"})
    call_command("processar_videos", "--uma-vez")
    for rota in (PAGINA + "?nome=1", "/minha-trajetoria/video/estado?nome=1",
                 "/minha-trajetoria/video.mp4?nome=1"):
        client.get(rota)
    for registro in caplog.records:
        mensagem = registro.getMessage()
        assert "Maria Exemplo" not in mensagem
        assert "Tecnologia em Análise" not in mensagem
        assert "00000000272" not in mensagem

"""Rotas e bloco do vídeo na página (022 US1; contracts/rotas.md; FR-001 a FR-003, FR-021,
FR-025, FR-026, FR-034 a FR-036; analyze C1, C2)."""

import re

import pytest
from django.core.management import call_command
from django.test import Client

from tests.narrativa import construcao as cn
from tests.video.conftest import MP4_FALSO
from trajetoria.narrativa import card
from trajetoria.video.models import GeracaoDeVideo as G

pytestmark = pytest.mark.django_db
PAGINA = "/minha-trajetoria/"
PEDIR = "/minha-trajetoria/video/"
ARQUIVO = "/minha-trajetoria/video.mp4"
ESTADO = "/minha-trajetoria/video/estado"


@pytest.fixture
def maria(cenario):
    pessoa = cenario.pessoa("SIM-P-0003")
    cenario.concluir(pessoa.conclusoes.first())
    return pessoa


@pytest.fixture
def cliente(client, maria, renderizador_falso):
    cn.entrar(client, maria)
    return client


def _bloco(resposta) -> str:
    html = resposta.content.decode()
    inicio = html.index('id="video"')
    return html[inicio:html.index("</div><!-- #video -->", inicio)]


def _pronto(cliente, nome=False):
    cliente.post(PEDIR, {"nome": "1"} if nome else {})
    call_command("processar_videos", "--uma-vez")


def test_abrir_a_pagina_nao_gera_video(cliente):
    bloco = _bloco(cliente.get(PAGINA))
    assert "Gerar vídeo" in bloco
    assert not G.objects.exists()


def test_pedido_exige_csrf(maria, renderizador_falso):
    cliente = Client(enforce_csrf_checks=True)
    cn.entrar(cliente, maria)
    assert cliente.post(PEDIR).status_code == 403
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',
                      _bloco(cliente.get(PAGINA))).group(1)
    resposta = cliente.post(PEDIR, {"csrfmiddlewaretoken": token})
    assert resposta.status_code == 303
    assert resposta["Location"] == "/minha-trajetoria/#video"
    assert G.objects.get().estado == G.SOLICITADO


def test_pedido_com_nome_e_outra_composicao(cliente):
    resposta = cliente.post(PEDIR, {"nome": "1"})
    assert resposta["Location"] == "/minha-trajetoria/?nome=1#video"
    cliente.post(PEDIR)
    assert G.objects.count() == 2
    com_nome = [g for g in G.objects.all() if "Maria Exemplo" in str(g.composicao)]
    assert len(com_nome) == 1


def test_preparo_e_pronto(cliente):
    cliente.post(PEDIR)
    assert "Estamos preparando seu vídeo…" in _bloco(cliente.get(PAGINA))
    call_command("processar_videos", "--uma-vez")
    bloco = _bloco(cliente.get(PAGINA))
    video = re.search(r"<video [^>]*>", bloco).group(0)
    assert "controls" in video and "playsinline" in video and 'preload="metadata"' in video
    assert "autoplay" not in video
    assert 'poster="/minha-trajetoria/card.png"' in video
    assert 'download="minha-trajetoria-ifes.mp4"' in bloco and "Baixar vídeo (MP4)" in bloco
    assert f'href="{ARQUIVO}"' in bloco


def test_arquivo_inteiro(cliente):
    _pronto(cliente)
    resposta = cliente.get(ARQUIVO)
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "video/mp4"
    assert resposta["Accept-Ranges"] == "bytes"
    assert resposta["Content-Disposition"] == 'inline; filename="minha-trajetoria-ifes.mp4"'
    assert "no-store" in resposta["Cache-Control"]
    assert resposta.content == MP4_FALSO


@pytest.mark.parametrize(("pedido", "inicio", "fim"), [
    ("bytes=0-1", 0, 1), ("bytes=10-", 10, len(MP4_FALSO) - 1),
    ("bytes=-5", len(MP4_FALSO) - 5, len(MP4_FALSO) - 1),
    ("bytes=4-999999", 4, len(MP4_FALSO) - 1),
])
def test_intervalo(cliente, pedido, inicio, fim):
    _pronto(cliente)
    resposta = cliente.get(ARQUIVO, HTTP_RANGE=pedido)
    assert resposta.status_code == 206
    assert resposta["Content-Range"] == f"bytes {inicio}-{fim}/{len(MP4_FALSO)}"
    assert resposta.content == MP4_FALSO[inicio:fim + 1]
    assert resposta["Content-Length"] == str(fim - inicio + 1)


@pytest.mark.parametrize("pedido", ["bytes=999999-", "bytes=5-2"])
def test_intervalo_invalido(cliente, pedido):
    _pronto(cliente)
    resposta = cliente.get(ARQUIVO, HTTP_RANGE=pedido)
    assert resposta.status_code == 416
    assert resposta["Content-Range"] == f"bytes */{len(MP4_FALSO)}"


@pytest.mark.parametrize("pedido", ["bytes=0-1,4-5", "linhas=0-1", "bytes=x-y"])
def test_intervalo_nao_suportado_devolve_inteiro(cliente, pedido):
    _pronto(cliente)
    resposta = cliente.get(ARQUIVO, HTTP_RANGE=pedido)
    assert resposta.status_code == 200 and resposta.content == MP4_FALSO


def test_sem_pronto_404(cliente):
    assert cliente.get(ARQUIVO).status_code == 404
    cliente.post(PEDIR)
    assert cliente.get(ARQUIVO).status_code == 404


def test_cada_escolha_de_nome_tem_seu_video(cliente):
    _pronto(cliente)
    assert cliente.get(ARQUIVO).status_code == 200
    assert cliente.get(ARQUIVO + "?nome=1").status_code == 404


def test_sem_sessao_vai_para_acesso(maria, renderizador_falso, client):
    for metodo, rota in (("post", PEDIR), ("get", ARQUIVO), ("get", ESTADO)):
        resposta = getattr(client, metodo)(rota)
        assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"


def test_outra_pessoa_nao_recebe_o_video(cliente, cenario, client):
    _pronto(cliente)
    diego = cenario.pessoa("SIM-P-0004")
    cenario.concluir(diego.conclusoes.first())
    outro = Client()
    cn.entrar(outro, diego)
    assert outro.get(ARQUIVO).status_code == 404
    assert outro.get(ESTADO).json() == {"estado": "nenhum"}


def test_estado_json(cliente):
    assert cliente.get(ESTADO).json() == {"estado": "nenhum"}
    cliente.post(PEDIR)
    assert cliente.get(ESTADO).json() == {"estado": "preparando"}
    call_command("processar_videos", "--uma-vez")
    assert cliente.get(ESTADO).json() == {"estado": "pronto"}


def test_estado_falhou(client, maria, renderizador_com_falha):
    cn.entrar(client, maria)
    client.post(PEDIR)
    call_command("processar_videos", "--uma-vez")
    assert client.get(ESTADO).json() == {"estado": "falhou"}
    bloco = _bloco(client.get(PAGINA))
    assert "Não foi possível preparar o vídeo agora" in bloco and "Tentar novamente" in bloco


def test_nome_so_com_nome_na_fonte(cenario, renderizador_falso, client):
    sem_nome = cenario.pessoa("SIM-P-0009")
    cenario.concluir(sem_nome.conclusoes.first())
    cn.entrar(client, sem_nome)
    resposta = client.post(PEDIR, {"nome": "1"})
    assert resposta["Location"] == "/minha-trajetoria/#video"
    assert 'name="nome"' not in _bloco(client.get(PAGINA))


def test_modo_demonstracao_desligado(cliente, settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    for metodo, rota in (("post", PEDIR), ("get", ARQUIVO), ("get", ESTADO)):
        assert getattr(cliente, metodo)(rota).status_code == 404
    assert not G.objects.exists()


def test_acessibilidade_do_bloco(cliente, maria):
    _pronto(cliente)
    resposta = cliente.get(PAGINA)
    html = resposta.content.decode()
    bloco = _bloco(resposta)
    assert re.search(r'id="video"[^>]*aria-live="polite"', html)
    video = re.search(r"<video [^>]*>", bloco).group(0)
    alvo = re.search(r'aria-describedby="([^"]+)"', video).group(1)
    descricao = re.search(rf'id="{alvo}"[^>]*>([^<]+)<', bloco).group(1)
    esperado = card.descricao(cn.caso_maria(), None, True)
    assert descricao.strip().startswith("Minha trajetória no Ifes.")
    assert "Tecnologia em Análise e Desenvolvimento de Sistemas" in descricao
    assert esperado.split(".")[0] in descricao
    assert "autoplay" not in html and 'http-equiv="refresh"' not in html
    assert re.search(r'<button[^>]*id="compartilhar-video"[^>]*hidden', bloco)
    assert "tabindex" not in bloco


def test_fluxo_sem_javascript(cliente):
    """Pedir, acompanhar, baixar: tudo por formulário, link e recarga (FR-035)."""
    bloco = _bloco(cliente.get(PAGINA))
    assert re.search(r'<form method="post" action="/minha-trajetoria/video/"', bloco)
    cliente.post(PEDIR)
    bloco = _bloco(cliente.get(PAGINA))
    assert 'href="/minha-trajetoria/#video"' in bloco  # Atualizar
    call_command("processar_videos", "--uma-vez")
    assert cliente.get(ARQUIVO).status_code == 200


def test_scripts_so_inline_sem_recurso_externo(cliente):
    _pronto(cliente)
    html = cliente.get(PAGINA).content.decode()
    scripts = re.findall(r"<script[^>]*>", html)
    assert scripts and all(s == "<script>" for s in scripts)
    bloco = _bloco(cliente.get(PAGINA))
    assert "http" not in bloco.split("<script>")[1]

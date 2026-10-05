"""Seção "Seu card": prévia, nome, baixar e compartilhar (021 FR-031, FR-034, FR-039,
FR-073; SC-004; contracts/rotas.md)."""

import re
import struct

import pytest

from tests.narrativa import construcao as cn
from trajetoria.narrativa import rasterizacao

pytestmark = pytest.mark.django_db
URL = "/minha-trajetoria/"


@pytest.fixture
def maria(client, cenario):
    pessoa = cenario.pessoa("SIM-P-0003")
    cenario.concluir(pessoa.conclusoes.first())
    cn.entrar(client, pessoa)
    return pessoa


def _secao_card(resposta):
    html = resposta.content.decode()
    return html[html.index('id="card"'):].split("</section>")[0]


def test_previa_e_a_propria_png(client, maria):
    secao = _secao_card(client.get(URL))
    img = re.search(r"<img [^>]*>", secao).group(0)
    assert 'src="/minha-trajetoria/card.png"' in img
    assert 'width="270" height="480"' in img  # 9:16
    alt = re.search(r'alt="([^"]+)"', img).group(1)
    assert "Minha trajetória no Ifes" in alt and "Maria Exemplo" not in alt


def test_nome_desmarcado_por_padrao_e_atualizacao_sem_js(client, maria):
    secao = _secao_card(client.get(URL))
    assert 'method="get"' in secao and 'name="nome" value="1"' in secao
    assert "checked" not in secao
    assert "Atualizar prévia" in secao
    com_nome = _secao_card(client.get(URL + "?nome=1"))
    assert 'src="/minha-trajetoria/card.png?nome=1"' in com_nome
    baixar = 'href="/minha-trajetoria/card.png?nome=1" download="minha-trajetoria-ifes.png"'
    assert baixar in com_nome
    assert "checked" in com_nome


def test_baixar_com_atributo_download(client, maria):
    secao = _secao_card(client.get(URL))
    assert re.search(
        r'<a class="botao" href="/minha-trajetoria/card.png" download="minha-trajetoria-ifes.png">'
        r"Baixar imagem \(PNG\)</a>",
        secao,
    )


def test_compartilhar_oculto_e_script_inline_sem_recurso_externo(client, maria):
    resposta = client.get(URL)
    secao = _secao_card(resposta)
    assert re.search(r'<button [^>]*id="compartilhar"[^>]*hidden', secao)
    scripts = re.findall(r"<script[^>]*>", resposta.content.decode())
    assert scripts == ["<script>"]
    assert "http" not in secao.split("<script>")[1]


def test_nenhum_script_nas_outras_telas(client, maria):
    assert "<script" not in client.get("/formacoes/").content.decode()


def test_sem_nome_na_fonte_nao_ha_opcao(client, cenario):
    sem_nome = cenario.pessoa("SIM-P-0009")
    cenario.concluir(sem_nome.conclusoes.get())
    cn.entrar(client, sem_nome)
    secao = _secao_card(client.get(URL + "?nome=1"))
    assert 'name="nome"' not in secao
    assert "card.png?nome=1" not in secao


def test_png_da_rota(client, maria):
    resposta = client.get("/minha-trajetoria/card.png")
    assert resposta["Content-Type"] == "image/png"
    assert resposta["Content-Disposition"] == 'inline; filename="minha-trajetoria-ifes.png"'
    assert "no-store" in resposta["Cache-Control"]
    assert struct.unpack(">II", resposta.content[16:24]) == (1080, 1920)


def test_svg_da_rota_com_e_sem_nome(client, maria):
    sem = client.get("/minha-trajetoria/card.svg")
    assert sem["Content-Disposition"] == 'attachment; filename="minha-trajetoria-ifes.svg"'
    assert "Maria Exemplo" not in sem.content.decode()
    com = client.get("/minha-trajetoria/card.svg?nome=1").content.decode()
    assert ">Maria Exemplo</text>" in com
    assert "Maria Exemplo" not in client.get("/minha-trajetoria/card.svg?nome=sim").content.decode()


def test_fallback_svg_sem_rasterizacao(client, maria, monkeypatch):
    monkeypatch.setattr(rasterizacao, "rasterizacao_disponivel", lambda: False)
    monkeypatch.setattr(rasterizacao, "png_de", lambda svg: None)
    secao = _secao_card(client.get(URL))
    assert "<svg" in secao and "<img" not in secao
    assert 'download="minha-trajetoria-ifes.svg">Baixar imagem (SVG)</a>' in secao
    assert 'id="compartilhar"' not in secao and "<script" not in secao
    assert client.get("/minha-trajetoria/card.png").status_code == 404

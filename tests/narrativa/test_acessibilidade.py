"""Acessibilidade da página e do card (021 FR-066 a FR-068; Const. XX)."""

import re

import pytest

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn
from trajetoria.narrativa import card as k
from trajetoria.narrativa import consultas
from trajetoria.narrativa.montagem import montar

pytestmark = pytest.mark.django_db


@pytest.fixture
def pagina(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    cenario.concluir(maria.conclusoes.first())
    cn.entrar(client, maria)
    return maria, client.get("/minha-trajetoria/")


def test_caixa_do_nome_tem_rotulo(pagina):
    html = pagina[1].content.decode()
    assert re.search(r'<input type="checkbox" id="incluir-nome"', html)
    assert '<label for="incluir-nome">Incluir meu nome no card</label>' in html


def test_acoes_com_nome_que_indica_o_formato(pagina):
    texto = ci.texto_visivel(pagina[1])
    assert "Baixar imagem (PNG)" in texto and "Compartilhar imagem" in texto


def test_previa_com_alt_nao_vazio(pagina):
    alt = re.search(r'<img [^>]*alt="([^"]*)"', pagina[1].content.decode()).group(1)
    assert alt.strip()


def test_texto_do_card_tambem_esta_na_pagina(pagina, referencia):
    maria, resposta = pagina
    texto = ci.texto_visivel(resposta)
    narrativa = montar(consultas.entrada_da_pessoa(maria, referencia, True))
    for f in narrativa.compartilhavel.formacoes:
        assert f.curso in texto
        for atributo in (f.unidade, f.nivel, f.modalidade, str(f.ano_conclusao)):
            assert atributo in texto


def test_svg_tem_titulo_e_descricao():
    svg = k.card_svg(cn.caso_maria())
    assert "<title id=\"card-titulo\">" in svg and "<desc id=\"card-descricao\">" in svg

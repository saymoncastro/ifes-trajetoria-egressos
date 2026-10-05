"""Catálogo de imagens institucionais da abertura (021 FR-076; research R20)."""

import xml.etree.ElementTree as ET

from trajetoria.narrativa import imagens


def test_exatamente_uma_generica():
    assert len([i for i in imagens.CATALOGO if i.unidade is None]) == 1


def test_metadados_obrigatorios():
    for imagem in imagens.CATALOGO:
        assert imagem.tipo in imagens.TIPOS
        assert imagem.origem.strip() and imagem.licenca.strip()


def test_arquivo_e_svg_valido_sem_texto():
    for imagem in imagens.CATALOGO:
        caminho = imagens.PASTA / imagem.arquivo
        assert caminho.suffix == ".svg" and caminho.exists()
        raiz = ET.parse(caminho).getroot()
        assert raiz.tag == "{http://www.w3.org/2000/svg}svg"
        assert raiz.get("viewBox") == "0 0 1080 900"
        assert not raiz.findall(".//{http://www.w3.org/2000/svg}text")
        assert not raiz.findall(".//{http://www.w3.org/2000/svg}image")  # nada externo


def test_escolha_pela_unidade_cai_na_generica():
    generica = next(i for i in imagens.CATALOGO if i.unidade is None)
    assert imagens.imagem_para("Serra") == generica
    assert imagens.imagem_para(None) == generica
    propria = imagens.ImagemInstitucional("Serra", "x.svg", "fotografia", "ACS", "cedida")
    original = imagens.CATALOGO
    try:
        imagens.CATALOGO = (*original, propria)
        assert imagens.imagem_para("Serra") == propria
        assert imagens.imagem_para("Vitória") == generica
    finally:
        imagens.CATALOGO = original


def test_legenda_pela_unidade_da_formacao():
    generica = imagens.imagem_para(None)
    assert imagens.legenda(generica, "Serra") == "Unidade Serra · ilustração"
    assert imagens.legenda(generica, None) == "Ifes · ilustração"

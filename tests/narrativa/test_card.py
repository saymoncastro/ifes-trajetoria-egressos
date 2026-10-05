"""Card vertical 9:16: representação-base em SVG (021 FR-031 a FR-041, FR-067, FR-072;
contracts/card.md; SC-005, SC-010, SC-013). Construído à mão: a montagem vem depois."""

import re
import xml.etree.ElementTree as ET

import pytest

from tests.narrativa import construcao as cn
from trajetoria.narrativa import card, catalogo

NS = {"s": "http://www.w3.org/2000/svg"}
X0, Y0, X1, Y1 = card.AREA_SEGURA


def _raiz(svg):
    return ET.fromstring(svg)


def _textos(svg):
    return _raiz(svg).findall("s:text", NS)


def _conteudo(svg):
    return [t.text for t in _textos(svg)]


def _luminancia(cor):
    canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    canais = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def _contraste(a, b):
    claro, escuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


CASOS = {
    "pior": (cn.pior_caso, cn.NOME_LONGO),
    "maria": (cn.caso_maria, "Maria Exemplo"),
    "sem_nome": (cn.caso_maria, None),
}


@pytest.mark.parametrize("caso", CASOS)
def test_svg_deterministico(caso):
    fabrica, nome = CASOS[caso]
    assert card.card_svg(fabrica(), nome=nome) == card.card_svg(fabrica(), nome=nome)


def test_formato_vertical_9_16():
    raiz = _raiz(card.card_svg(cn.caso_maria()))
    assert (raiz.get("width"), raiz.get("height")) == ("1080", "1920")
    assert raiz.get("viewBox") == "0 0 1080 1920"


def test_pior_caso_cabe_com_composicao_adaptativa():
    """A área segura e o corpo mínimo de cada zona estão em test_card_editorial."""
    composicao = card.compor(cn.pior_caso(), cn.NOME_LONGO, True)
    conteudo = _conteudo(card.card_svg(cn.pior_caso(), nome=cn.NOME_LONGO))
    assert 1 <= composicao.exibidas <= 4
    # Nenhuma formação some sem aviso: as não exibidas entram em "e mais N".
    omitidas = 4 - composicao.exibidas + 3
    assert catalogo.plural(catalogo.CARD_MAIS, omitidas).format(n=omitidas) in conteudo
    # O nome nunca é truncado: todas as palavras aparecem.
    assert " ".join(t for t in conteudo if t in cn.NOME_LONGO) == cn.NOME_LONGO


def test_caso_maria_mostra_tudo():
    composicao = card.compor(cn.caso_maria(), "Maria Exemplo", True)
    assert composicao.exibidas == 2 and composicao.destaques
    assert not any(t.startswith("e mais") for t in _conteudo(card.card_svg(cn.caso_maria())))


def test_nome_so_quando_fornecido():
    assert "Maria Exemplo" in _conteudo(card.card_svg(cn.caso_maria(), nome="Maria Exemplo"))
    assert "Maria Exemplo" not in card.card_svg(cn.caso_maria())


def test_marca_de_demonstracao():
    com = " ".join(_conteudo(card.card_svg(cn.caso_maria(), demonstracao=True)))
    assert catalogo.CARD_DEMO in com
    assert catalogo.CARD_DEMO not in card.card_svg(cn.caso_maria(), demonstracao=False)


@pytest.mark.parametrize("caso", CASOS)
def test_conteudo_vedado(caso):
    fabrica, nome = CASOS[caso]
    svg = card.card_svg(fabrica(), nome=nome)
    texto = " ".join(_conteudo(svg)).lower()
    for proibido in ("certificado", "comprovante", "declaração", "há ", "ingresso",
                     "subsequente", "integrado", "concomitante"):
        assert proibido not in texto, proibido
    assert not re.search(r"\d{2}/\d{2}/\d{4}", " ".join(
        t for t in _conteudo(svg) if not t.startswith("Dados institucionais")
    ))
    assert "<image" not in svg and "qr" not in texto
    assert "formações registradas no Ifes" not in texto


def test_titulo_descricao_e_fonte():
    raiz = _raiz(card.card_svg(cn.caso_maria(), nome="Maria Exemplo"))
    assert raiz.find("s:title", NS).text == catalogo.TITULO
    descricao = raiz.find("s:desc", NS).text
    assert "Maria Exemplo" in descricao and cn.cenarios.TADS in descricao
    assert "27 conclusões deste curso na unidade Serra em 2022." in descricao
    assert catalogo.FECHO in descricao
    for texto in raiz.findall("s:text", NS):
        assert texto.get("font-family").startswith("Open Sans")


def test_contraste_aa_dos_tokens():
    tema = card.TEMA_CARD
    for cor in ("texto", "suave", "profundo", "marca_escura"):
        assert _contraste(tema[cor], tema["creme"]) >= 4.5, cor
    assert _contraste(tema["suave"], tema["branco"]) >= 4.5
    assert _contraste(tema["branco"], tema["profundo"]) >= 4.5


def test_quebra_nunca_corta_palavra():
    for curso in cn.CURSOS_LONGOS:
        linhas = card.quebrar_linhas(curso, card.TAMANHO_CURSO, True)
        assert " ".join(linhas) == curso
        assert all(card.largura(linha, card.TAMANHO_CURSO, True) <= card.LARGURA_UTIL
                   for linha in linhas)


def test_atributo_nao_e_partido():
    linhas = card.quebrar_atributos(
        [cn.UNIDADE_LONGA, "Pós-graduação", "A distância", "2012"], card.TAMANHO_DETALHE,
        limite=card.LIMITE_ITEM,
    )
    assert all(not linha.endswith(" A") and not linha.startswith("distância")
               for linha in linhas)
    assert " · ".join(linhas) == " · ".join([cn.UNIDADE_LONGA, "Pós-graduação",
                                             "A distância", "2012"])

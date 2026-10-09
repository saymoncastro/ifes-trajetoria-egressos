"""Composição do card agrupada por zonas (Feature 022; research R3; data-model §1).

O agrupamento serve ao vídeo e NÃO pode mudar o card: o SVG continua idêntico byte a byte
ao gerado antes da mudança. As constantes abaixo foram calculadas com o `card.py` da `main`
em `a65d7cb`, antes do agrupamento.
"""

import hashlib
from collections import Counter

import pytest

from tests.video.construcao import CASOS, NOME
from trajetoria.narrativa import card, catalogo, imagens

SVG_ANTES_DAS_ZONAS = {
    ("maria", None): "5ebfc248e7d575d786599ada3c6b8b5249b29097c06704f3f599b0cb2eb3069f",
    ("maria", NOME): "001c8506450ab2d46881c8363fa776310991857e8831b1413232c1f7440f3773",
    ("ana", None): "e404a4e95a49d853d4946d8cbb232348e1217512cba73b3af393efaecf137625",
    ("ana", NOME): "8ea8caee19cba320dc93e3ed53eb1982e10628fda21bb96ce3fcb0258942de16",
    ("diego", None): "f257319da41b21932aa19b9b5d611960963beab016f65626509d61b3f503dbc9",
    ("diego", NOME): "fd61aa51dad321e8d540b8a909f1d201be5c3bf6e0164b7a704aaadf888d8019",
    ("quatro", None): "95943fb48a0e3248226a980ca640df7235dde197defac5d9605d442f80d534f9",
    ("quatro", NOME): "f77dc5770227a0e259f7e908eb044d825a40c62ab7f6cc7ed793fa4765d95633",
    ("pior", None): "900f6ca98979152d693a70955ae88d68f28ee89598301c1da57ebd30477dff01",
    ("pior", NOME): "a775a19b7a6d11dca1983fab3c7c2024e394313bd2f4942a2fc2fbaf1c7a3d29",
    ("sem_imagem", None): "9bb349b8326dbd7c09de82e485752234b6124d5eb5b0cfd90f0a1fe894b884a0",
    ("sem_imagem", NOME): "099559a21828c2050aea48d61524b3537f3608a8d9aa4960096afe524287584a",
    ("sem_unidade", None): "3a5e10fc44a48ca4e3984edc6956a41ba615a3d281e1bf6728184cfef2cb176b",
    ("sem_unidade", NOME): "b1ca966c2f13857a7d40f0e420380bb9217b12c9fa8ba328bdbc681dbec9f420",
}

CASOS_E_NOMES = sorted(SVG_ANTES_DAS_ZONAS, key=lambda c: (c[0], c[1] or ""))


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_svg_do_card_identico_ao_de_antes_das_zonas(caso, nome, monkeypatch):
    # 028 corrige a legenda e sua geometria. Reproduzir só a legenda histórica mantém
    # a prova do agrupamento em zonas contra os hashes originais, sem regravar fixtures.
    monkeypatch.setattr(imagens, "legenda", lambda imagem, unidade: (
        catalogo.LEGENDA.format(unidade=unidade, tipo=imagem.tipo) if unidade
        else catalogo.LEGENDA_SEM_UNIDADE.format(tipo=imagem.tipo)
    ))
    svg = card.card_svg(CASOS[caso](), nome=nome)
    assert hashlib.sha256(svg.encode()).hexdigest() == SVG_ANTES_DAS_ZONAS[(caso, nome)]


def _compor(caso, nome):
    return card.compor(CASOS[caso](), nome, demonstracao=True)


def _zona(composicao, chave):
    return next((z for z in composicao.zonas if z.chave == chave), None)


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_zonas_em_ordem_e_so_as_presentes(caso, nome):
    chaves = [z.chave for z in _compor(caso, nome).zonas]
    assert chaves == [c for c in card.ZONAS if c in chaves]
    assert {"fundo", "abertura", "marca", "legenda", "titulo", "nos", "fechamento",
            "rodape"} <= set(chaves)
    assert all(z.partes and all(z.partes) for z in _compor(caso, nome).zonas)


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_partes_cobrem_exatamente_os_elementos(caso, nome):
    composicao = _compor(caso, nome)
    das_zonas = Counter(e for z in composicao.zonas for parte in z.partes for e in parte)
    assert das_zonas == Counter(composicao.elementos)


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_presenca_condicional_das_zonas(caso, nome):
    composicao = _compor(caso, nome)
    c = CASOS[caso]()
    nos = _zona(composicao, "nos")
    assert len(nos.partes) == composicao.exibidas
    assert (_zona(composicao, "traco") is not None) == (composicao.exibidas >= 2)
    omitidas = len(c.formacoes) - composicao.exibidas + c.formacoes_omitidas
    assert (_zona(composicao, "mais") is not None) == (omitidas > 0)
    destaques = _zona(composicao, "destaques")
    if composicao.destaques:
        assert len(destaques.partes) == len(c.contextos_agregados)
        assert _zona(composicao, "apuracao") is not None
    else:
        assert destaques is None and _zona(composicao, "apuracao") is None
    assert (_zona(composicao, "nome") is not None) == bool(nome)


def test_cada_no_tem_seu_circulo_e_seus_textos():
    composicao = _compor("quatro", None)
    for parte in _zona(composicao, "nos").partes:
        classes = Counter(dict(e.atributos).get("class") for e in parte)
        assert classes["no"] == 1 and classes["no-centro"] == 1
        assert classes["ano"] == 1 and classes["curso"] >= 1 and classes["detalhe"] >= 1


def test_cada_cartao_tem_seu_numero():
    composicao = _compor("maria", None)
    for parte in _zona(composicao, "destaques").partes:
        classes = Counter(dict(e.atributos).get("class") for e in parte)
        assert classes["destaque"] == 1 and classes["numero"] == 1 and classes["rotulo"] >= 1

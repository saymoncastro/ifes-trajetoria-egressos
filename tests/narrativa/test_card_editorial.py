"""Card editorial: critérios de aceitação visual (021 SC-015, FR-074 a FR-082;
contracts/card.md). Tudo é verificado no SVG gerado, que o PNG rasteriza."""

import itertools
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tests.narrativa import construcao as cn
from trajetoria.narrativa import card, catalogo

X0, Y0, X1, Y1 = card.AREA_SEGURA
ALTURA_QUADRO = card.ALTURA

CASOS = {
    "1-formacao-agregados": (cn.caso_ana, None),
    "1-formacao-sem-unidade": (cn.caso_sem_unidade, None),
    "2-formacoes-com-nome": (cn.caso_maria, "Maria Exemplo"),
    "2-formacoes-sem-nome": (cn.caso_maria, None),
    "3-formacoes-sem-agregados": (cn.caso_diego, "Diego Exemplo"),
    "4-formacoes": (cn.caso_quatro, None),
    "mais-de-4-pior-caso": (cn.pior_caso, cn.NOME_LONGO),
    "unidade-sem-imagem-propria": (cn.caso_sem_imagem_propria, None),
}
COM_DESTAQUES = {"1-formacao-agregados", "2-formacoes-com-nome", "2-formacoes-sem-nome",
                 "unidade-sem-imagem-propria"}

ZONAS = (
    ("titulo", {"titulo", "nome"}),
    ("linha_do_tempo", {"ano", "curso", "detalhe", "mais", "no", "no-centro", "traco"}),
    ("destaques", {"destaque", "filete", "numero", "rotulo"}),
    ("fecho", {"fecho", "hashtag", "hashtag-fundo"}),
    ("rodape", {"rodape", "apuracao"}),
)
# Corpo mínimo por papel (FR-081): conteúdo ≥ 40; texto de apoio ≥ 30; rodapé ≥ 26.
MINIMOS = {"titulo": 80, "ano": 44, "numero": 80, "curso": 40, "nome": 40, "mais": 40,
           "fecho": 40, "detalhe": 30, "hashtag": 30, "rotulo": 30, "legenda": 30,
           "rodape": 26, "apuracao": 26}
FUNDO_DO_TEXTO = {"legenda": "profundo", "hashtag": "profundo", "numero": "branco",
                  "rotulo": "branco"}
ESCALA_NO_CELULAR = 360 / 1080  # o story ocupa a largura da tela


def _gerar(caso):
    fabrica, nome = CASOS[caso]
    c = fabrica()
    return c, nome, card.compor(c, nome, True), card.card_svg(c, nome=nome)


def _filhos(svg):
    return list(ET.fromstring(svg))  # só o nível de cima: as imagens embutidas ficam fora


def _tag(e):
    return e.tag.split("}")[1]


def _textos(svg):
    return [e for e in _filhos(svg) if _tag(e) == "text"]


def _classe(e):
    return e.get("class")


def _caixa_de_texto(t):
    """(esquerda, topo, direita, base) pela largura real dos glifos."""
    tamanho, y = int(t.get("font-size")), int(t.get("y"))
    largura = card.largura(t.text, tamanho, t.get("font-weight") == "700")
    x = int(t.get("x"))
    esquerda = x - largura if t.get("text-anchor") == "end" else x
    return esquerda, y - 0.72 * tamanho, esquerda + largura, y + 0.24 * tamanho


def _vertical(e):
    tag = _tag(e)
    if tag == "text":
        _, topo, _, base = _caixa_de_texto(e)
        return topo, base
    if tag == "circle":
        cy, r = float(e.get("cy")), float(e.get("r"))
        return cy - r, cy + r
    if tag == "line":
        return float(e.get("y1")), float(e.get("y2"))
    if tag in ("rect", "svg"):
        y = float(e.get("y", 0))
        return y, y + float(e.get("height"))
    return None


def _abertura(svg):
    return next(e for e in _filhos(svg) if _classe(e) == "abertura")


# --- (a) Ordem das zonas ------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_a_zonas_em_ordem(caso):
    _, _, composicao, svg = _gerar(caso)
    limites = [(0, composicao.abertura)]
    for _, classes in ZONAS:
        faixas = [_vertical(e) for e in _filhos(svg) if _classe(e) in classes]
        if faixas:
            limites.append((min(f[0] for f in faixas), max(f[1] for f in faixas)))
    for anterior, seguinte in itertools.pairwise(limites):
        assert anterior[1] <= seguinte[0], (anterior, seguinte)
    faixa = next(e for e in _filhos(svg) if _classe(e) == "faixa")
    assert float(faixa.get("y")) >= Y1  # a faixa inferior fica abaixo da área segura


# --- (b) Elemento dominante ---------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_b_abertura_ocupa_ao_menos_20_por_cento(caso):
    _, _, composicao, svg = _gerar(caso)
    imagem = _abertura(svg)
    assert int(imagem.get("height")) == composicao.abertura
    assert int(imagem.get("width")) == card.LARGURA and int(imagem.get("y")) == 0
    assert composicao.abertura / ALTURA_QUADRO >= 0.20


# --- (c) Linha do tempo -------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_c_um_no_por_formacao_exibida_e_traco(caso):
    c, _, composicao, svg = _gerar(caso)
    nos = [e for e in _filhos(svg) if _classe(e) == "no"]
    assert 1 <= composicao.exibidas == len(nos) <= 4
    tracos = [e for e in _filhos(svg) if _classe(e) == "traco"]
    assert len(tracos) == (1 if len(nos) >= 2 else 0)
    total = len(c.formacoes) + c.formacoes_omitidas
    mais = [t.text for t in _textos(svg) if _classe(t) == "mais"]
    if composicao.exibidas < total:
        n = total - composicao.exibidas
        assert " ".join(mais) == catalogo.plural(catalogo.CARD_MAIS, n).format(n=n)
    else:
        assert not mais


@pytest.mark.parametrize("caso", CASOS)
def test_c_curso_nunca_e_cortado(caso):
    c, _, composicao, svg = _gerar(caso)
    cursos = " ".join(t.text for t in _textos(svg) if _classe(t) == "curso")
    for f in c.formacoes[: composicao.exibidas]:
        if f.curso:
            assert f.curso in cursos


# --- (d) Destaques ------------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_d_destaque_com_numero_grande_e_rotulo_curto(caso):
    c, _, composicao, svg = _gerar(caso)
    numeros = [t for t in _textos(svg) if _classe(t) == "numero"]
    rotulos = [t for t in _textos(svg) if _classe(t) == "rotulo"]
    assert composicao.destaques == (caso in COM_DESTAQUES)
    if composicao.destaques:
        assert len(numeros) == len(c.contextos_agregados)
        assert len(rotulos) <= 2 * len(numeros)
        assert all(int(t.get("font-size")) >= 80 for t in numeros)
    else:
        assert not numeros and not rotulos
    # Nenhuma contagem em parágrafo: nenhum outro texto traz o número do agregado.
    for d in c.contextos_agregados:
        assert not any(re.search(rf"\b{d.numero}\b", t.text) for t in _textos(svg)
                       if _classe(t) not in ("numero", "ano"))


def test_d_destaques_saem_antes_das_formacoes():
    """Ordem de corte do FR-082: abertura no mínimo → sem destaques → "e mais N"."""
    composicao = card.compor(cn.pior_caso(), cn.NOME_LONGO, True)
    assert not composicao.destaques
    assert composicao.exibidas >= 1


# --- (e) Ocupação -------------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_e_nenhuma_faixa_vazia_maior_que_160(caso):
    _, _, _, svg = _gerar(caso)
    faixas = []
    for e in _filhos(svg):
        vertical = _vertical(e)
        if _classe(e) != "fundo" and vertical and vertical[0] < Y1 and vertical[1] > Y0:
            faixas.append((max(Y0, vertical[0]), min(Y1, vertical[1])))
    faixas.sort()
    alcance = Y0
    for topo, base in faixas:
        assert topo - alcance <= 160, (alcance, topo)
        alcance = max(alcance, base)
    assert Y1 - alcance <= 160


# --- (f) Hierarquia e proveniência --------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_f_hierarquia_e_proveniencia_no_rodape(caso):
    _, _, _, svg = _gerar(caso)
    textos = _textos(svg)
    assert len({int(t.get("font-size")) for t in textos}) >= 4
    assert all(int(t.get("font-size")) >= 80 for t in textos if _classe(t) == "titulo")
    fecho = max(int(t.get("y")) for t in textos if _classe(t) in ("fecho", "hashtag"))
    for t in textos:
        if t.text.startswith("Dados institucionais apurados"):
            assert _classe(t) == "apuracao" and int(t.get("y")) > fecho
            assert int(t.get("font-size")) <= 30
        if _classe(t) == "rodape":
            assert int(t.get("font-size")) <= 30


# --- (g) Área segura e legibilidade -------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_g_todo_texto_na_area_segura(caso):
    _, _, _, svg = _gerar(caso)
    for t in _textos(svg):
        esquerda, _, direita, _ = _caixa_de_texto(t)
        y, tamanho = int(t.get("y")), int(t.get("font-size"))
        assert X0 <= esquerda and direita <= X1, t.text
        assert y - tamanho >= Y0 and y + card.DESCENDENTE * tamanho <= Y1, t.text


@pytest.mark.parametrize("caso", CASOS)
def test_g_sem_sobreposicao(caso):
    _, _, _, svg = _gerar(caso)
    caixas = [(t.text, _caixa_de_texto(t)) for t in _textos(svg)]
    for (a, ca), (b, cb) in itertools.combinations(caixas, 2):
        separadas = ca[2] <= cb[0] or cb[2] <= ca[0] or ca[3] <= cb[1] or cb[3] <= ca[1]
        assert separadas, (a, b)
    for no in (e for e in _filhos(svg) if _classe(e) == "no"):
        cx, cy, r = (float(no.get(a)) for a in ("cx", "cy", "r"))
        for texto, (esq, topo, dir_, base) in caixas:
            assert dir_ <= cx - r or cx + r <= esq or base <= cy - r or cy + r <= topo, texto
    pilulas = {_classe(e): e for e in _filhos(svg) if _classe(e) in ("marca-fundo",
                                                                    "legenda-fundo")}
    m, leg = pilulas["marca-fundo"], pilulas["legenda-fundo"]
    mx, my = float(m.get("x")), float(m.get("y"))
    lx, ly = float(leg.get("x")), float(leg.get("y"))
    assert (mx + float(m.get("width")) <= lx or my + float(m.get("height")) <= ly)


@pytest.mark.parametrize("caso", CASOS)
def test_g_corpo_minimo_por_papel(caso):
    _, _, _, svg = _gerar(caso)
    for t in _textos(svg):
        assert int(t.get("font-size")) >= MINIMOS[_classe(t)], (t.text, _classe(t))


# --- (h) Legenda --------------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_h_legenda_honesta_e_sem_ano(caso):
    c, _, _, svg = _gerar(caso)
    legenda = " ".join(t.text for t in _textos(svg) if _classe(t) == "legenda")
    assert re.fullmatch(r"(Unidade .+|Ifes) · (ilustração|fotografia)", legenda), legenda
    assert not re.search(r"\b\d{4}\b", legenda)
    unidade = c.formacoes[0].unidade
    assert legenda.startswith(f"Unidade {unidade} ·" if unidade else "Ifes ·")


# --- (i) Catálogo e vedações --------------------------------------------------------------


def _padrao(formulacao):
    partes = re.split(r"(\{[a-z]+\})", formulacao)
    return re.compile(
        "^" + "".join(".+?" if p.startswith("{") else re.escape(p) for p in partes) + "$"
    )


PADROES = [_padrao(f) for f in catalogo.FORMULACOES]


def _valores(c, nome):
    valores = set(card.TITULO_LINHAS)
    for f in c.formacoes:
        valores |= set(f.linhas_curso) | set(f.linhas_detalhe)
        if f.ano_conclusao is not None:
            valores.add(str(f.ano_conclusao))
    valores |= {card.numero_formatado(d.numero) for d in c.contextos_agregados}
    if nome:
        valores |= set(card.quebrar_linhas(nome, card.MEDIDAS["nome"].tamanho))
    return valores


@pytest.mark.parametrize("caso", CASOS)
def test_i_toda_frase_do_catalogo_e_nenhum_termo_vedado(caso):
    c, nome, _, svg = _gerar(caso)
    valores = _valores(c, nome)
    for t in _textos(svg):
        if t.text not in valores:
            for parte in t.text.split(" · ") if _classe(t) == "rodape" else [t.text]:
                assert any(p.match(parte) for p in PADROES), t.text
        for termo in catalogo.VEDADAS:
            assert termo.lower() not in t.text.lower(), (termo, t.text)


# --- (j) Fecho e hashtag ------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_j_fecho_e_hashtag(caso):
    _, _, _, svg = _gerar(caso)
    textos = [t.text for t in _textos(svg)]
    assert catalogo.FECHO in textos and catalogo.HASHTAG in textos


# --- (k) Determinismo ---------------------------------------------------------------------


@pytest.mark.parametrize("caso", CASOS)
def test_k_mesma_entrada_mesmo_svg(caso):
    assert _gerar(caso)[3] == _gerar(caso)[3]


# --- (l) Contraste ------------------------------------------------------------------------


def _luminancia(cor):
    canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    canais = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def _contraste(a, b):
    claro, escuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


@pytest.mark.parametrize("caso", CASOS)
def test_l_contraste_aa_de_todo_texto_no_celular(caso):
    """AA medido no tamanho do story na tela do celular: texto grande (≥ 18,66 px em
    negrito ou ≥ 24 px) pede 3:1; o resto, 4,5:1."""
    _, _, _, svg = _gerar(caso)
    tema = card.TEMA_CARD
    for t in _textos(svg):
        fundo = tema[FUNDO_DO_TEXTO.get(_classe(t), "creme")]
        tela = int(t.get("font-size")) * ESCALA_NO_CELULAR
        grande = tela >= 24 or (t.get("font-weight") == "700" and tela >= 18.66)
        assert _contraste(t.get("fill"), fundo) >= (3 if grande else 4.5), t.text


# --- (m) Hex de ação da 015 ---------------------------------------------------------------


def test_m_sem_hex_de_acao_da_015():
    raiz = Path("trajetoria/narrativa")
    arquivos = [raiz / "card.py", raiz / "imagens.py", raiz / "templates/narrativa/card.svg",
                *sorted((raiz / "imagens").glob("*.svg"))]
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8").lower()
        for proibido in ("#1351b4", "#0c326f", "#195128", "#00420c"):
            assert proibido not in texto, (arquivo, proibido)


def test_marca_oficial_embutida():
    svg = card.card_svg(cn.caso_maria())
    marca = next(e for e in _filhos(svg) if _classe(e) == "marca")
    assert marca.get("viewBox") == "0 0 709 284" and len(list(marca)) > 10
    assert float(marca.get("y")) >= Y0

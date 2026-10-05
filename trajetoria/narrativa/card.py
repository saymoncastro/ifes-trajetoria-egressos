"""Card editorial vertical 9:16 para rede social (Feature 021; contracts/card.md; R10, R19).

O SVG é a representação-base; o PNG sai dele (`rasterizacao.png_de`). O card é composto em
zonas, de cima para baixo (FR-074): abertura (imagem do catálogo, marca e legenda), título,
linha do tempo, destaques, fecho, rodapé e faixa inferior. Cada zona é uma função que
devolve os elementos posicionados e a altura que ocupa: a mesma função mede e desenha, e
nada se sobrepõe.

Todo texto fica na área segura; as faixas de topo e de base recebem só imagem e grafismo
(FR-072). A quebra de linha mede o texto com as larguras reais das fontes embutidas
(`metricas.py`), sem cortar palavras nem truncar o nome.

Ocupação e corte (FR-080, FR-082): a abertura absorve o espaço livre, entre um mínimo e um
máximo. Quando falta espaço, a abertura vai ao mínimo, depois saem os destaques e, por fim,
formações viram "e mais N". Título, nome, curso e fecho nunca são cortados.

Zonas (Feature 022; research R3): a composição também é exposta agrupada por zona e parte
(um nó da linha do tempo, um cartão de destaque), para que o vídeo anime exatamente o que o
card desenha. A lista plana `elementos` e, portanto, o SVG não mudam.
"""

from dataclasses import dataclass, field
from functools import cache, cached_property
from pathlib import Path

from django.template.loader import render_to_string

from trajetoria.narrativa import catalogo, imagens, metricas
from trajetoria.narrativa.contrato import Compartilhavel

LARGURA, ALTURA = 1080, 1920
AREA_SEGURA = (90, 270, 990, 1650)  # x0, y0, x1, y1 (orientação da Meta para stories)
X0, TOPO, X1, BASE = AREA_SEGURA
LARGURA_UTIL = X1 - X0

# Tema próprio do card, derivado da marca (FR-040). Sem as cores de ação da 015.
TEMA_CARD = {
    "profundo": "#0e3b23",
    # Grafismo e o título, grande também no celular (o AA de texto grande pede 3:1).
    "marca": "#2f9e41",
    # O ano: no celular, 44 px viram ~15 px, texto comum, que pede 4,5:1 (4,8:1 no creme).
    "marca_escura": "#257a33",
    "creme": "#f6f2e8",
    "branco": "#ffffff",
    "texto": "#1b1b1b",
    "suave": "#4a5058",
}
FAMILIA = "Open Sans, system-ui, sans-serif"
DESCENDENTE = 0.3  # fração do corpo abaixo da linha de base (Open Sans: 0,293)


@dataclass(frozen=True)
class Corpo:
    tamanho: int
    entrelinha: int
    negrito: bool = False


# Tabela única de medidas: mede e desenha (R19). Hierarquia do FR-081.
MEDIDAS = {
    "titulo": Corpo(84, 92, True),
    "nome": Corpo(44, 56),
    "ano": Corpo(44, 52, True),
    "curso": Corpo(44, 52, True),
    "detalhe": Corpo(36, 46),
    "mais": Corpo(40, 52, True),
    "numero": Corpo(88, 96, True),
    "rotulo": Corpo(30, 36),
    "fecho": Corpo(46, 58, True),
    "hashtag": Corpo(36, 60, True),
    "legenda": Corpo(30, 36),
    "rodape": Corpo(28, 36),
    "apuracao": Corpo(26, 34),
}
TAMANHO_CURSO = MEDIDAS["curso"].tamanho
TAMANHO_DETALHE = MEDIDAS["detalhe"].tamanho

RECUO_ITEM = 74  # do nó ao texto da linha do tempo
X_ITEM = X0 + RECUO_ITEM
LIMITE_ITEM = X1 - X_ITEM
RAIO_NO, RAIO_CENTRO, TRACO = 22, 9, 6

ESPACO_ABERTURA = 8  # da borda em onda ao título
ESPACO_NOME = 8
ESPACO_BLOCO = 36
ESPACO_ITEM = 28
ESPACO_FECHO = 40  # mínimo entre o conteúdo e o fecho
ESPACO_HASHTAG = 16
ESPACO_RODAPE = 24

# Abertura: borda inferior entre o mínimo e o máximo (FR-080). Com o mínimo, a imagem ocupa
# 21,9% do quadro (SC-015: ≥ 20%). A legenda divide a faixa da marca quando não colide com
# ela na horizontal; senão, a abertura cresce para a legenda caber abaixo da marca.
ABERTURA_MINIMA, ABERTURA_MAXIMA = 420, 890
ALTURA_DA_ARTE = 900  # viewBox das imagens do catálogo: 1080 × 900
MARCA = (X0 - 20, TOPO + 6, 390, 116)  # pílula branca: x, y, largura, altura
RECUO_LEGENDA = 76  # da borda da abertura à base da pílula da legenda
PILULA_LEGENDA = 22  # folga horizontal do texto na pílula

DESTAQUE_ALTO, DESTAQUE_BAIXO, DESTAQUE_VAO = 200, 140, 24
DESTAQUE_TEXTO, DESTAQUE_MARGEM = 36, 24  # recuo do texto e folga à direita no cartão

TITULO_LINHAS = ("Minha trajetória", "no Ifes")
assert " ".join(TITULO_LINHAS) == catalogo.TITULO

ASSINATURA = Path(__file__).resolve().parent.parent / (
    "interface/templates/interface/assinatura.svg"
)


# --- Medida de texto ----------------------------------------------------------------------


def largura(texto: str, tamanho: float, negrito: bool = False) -> float:
    tabela = metricas.NEGRITO if negrito else metricas.REGULAR
    maxima = metricas.MAXIMA_NEGRITO if negrito else metricas.MAXIMA_REGULAR
    return sum(tabela.get(c, maxima) for c in texto) * tamanho


def quebrar_linhas(
    texto: str, tamanho: float, negrito: bool = False, limite: float = LARGURA_UTIL
) -> tuple[str, ...]:
    """Quebra por palavras dentro do limite. Nunca corta palavra nem trunca: uma palavra
    maior que o limite ocupa sozinha a sua linha."""
    linhas, atual = [], ""
    for palavra in texto.split():
        candidata = f"{atual} {palavra}" if atual else palavra
        if atual and largura(candidata, tamanho, negrito) > limite:
            linhas.append(atual)
            atual = palavra
        else:
            atual = candidata
    if atual:
        linhas.append(atual)
    return tuple(linhas)


SEPARADOR = " · "


def quebrar_atributos(
    atributos, tamanho: float, negrito: bool = False, limite: float = LARGURA_UTIL
) -> tuple[str, ...]:
    """Junta atributos com " · " e quebra só entre eles, sem partir um atributo ("A
    distância") em duas linhas. Atributo maior que o limite cai em `quebrar_linhas`."""
    linhas, atual = [], ""
    for atributo in atributos:
        candidata = f"{atual}{SEPARADOR}{atributo}" if atual else atributo
        if atual and largura(candidata, tamanho, negrito) > limite:
            linhas.append(atual)
            atual = atributo
        else:
            atual = candidata
    if atual:
        linhas.append(atual)
    return tuple(
        parte for linha in linhas for parte in quebrar_linhas(linha, tamanho, negrito, limite)
    )


# --- Elementos ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Elemento:
    """Um elemento SVG. `interior` é marcação de um ativo versionado (imagem do catálogo,
    assinatura), embutida sem escape; o texto vem sempre escapado pelo template."""

    tag: str
    atributos: tuple[tuple[str, object], ...]
    texto: str | None = None
    interior: str | None = None


def _el(tag, texto=None, interior=None, **atributos) -> Elemento:
    pares = tuple(
        (chave.rstrip("_").replace("_", "-"), valor) for chave, valor in atributos.items()
    )
    return Elemento(tag, pares, texto, interior)


def _base(topo: float, corpo: Corpo) -> int:
    """Linha de base que centra a altura das maiúsculas e dos descendentes na linha."""
    return round(topo + corpo.entrelinha / 2 + 0.24 * corpo.tamanho)


def _texto(x, topo, texto, medida, cor, ancora=None) -> Elemento:
    corpo = MEDIDAS[medida]
    extras = {"font_weight": "700"} if corpo.negrito else {}
    if ancora:
        extras["text_anchor"] = ancora
    return _el(
        "text", texto, class_=medida, x=round(x), y=_base(topo, corpo), font_family=FAMILIA,
        font_size=corpo.tamanho, **extras, fill=cor,
    )


def _linhas(x, topo, linhas, medida, cor):
    corpo = MEDIDAS[medida]
    elementos = [
        _texto(x, topo + i * corpo.entrelinha, t, medida, cor) for i, t in enumerate(linhas)
    ]
    return elementos, len(linhas) * corpo.entrelinha


def _quebra(texto, medida, limite=LARGURA_UTIL):
    corpo = MEDIDAS[medida]
    return quebrar_linhas(texto, corpo.tamanho, corpo.negrito, limite)


def _cabe(texto, medida, limite) -> bool:
    corpo = MEDIDAS[medida]
    return largura(texto, corpo.tamanho, corpo.negrito) <= limite


@cache
def _svg_interior(caminho: Path) -> tuple[str, str]:
    """viewBox e marcação interna de um SVG versionado."""
    texto = caminho.read_text(encoding="utf-8")
    raiz = texto[texto.index("<svg"):]
    abertura = raiz[: raiz.index(">") + 1]
    viewbox = abertura.split('viewBox="', 1)[1].split('"', 1)[0]
    return viewbox, raiz[len(abertura): raiz.rindex("</svg>")].strip()


# --- Zonas --------------------------------------------------------------------------------


def _legenda(c: Compartilhavel):
    imagem = imagens.imagem_para(c.unidade_da_imagem)
    texto = imagens.legenda(imagem, c.unidade_da_imagem)
    return imagem, _quebra(texto, "legenda", LARGURA_UTIL - 2 * PILULA_LEGENDA)


def _altura_da_legenda(linhas) -> int:
    return MEDIDAS["legenda"].entrelinha * len(linhas) + 16


def abertura(c: Compartilhavel, fim: int, tema) -> list[Elemento]:
    """Imagem em sangria até `fim`, borda em onda, marca e legenda (FR-075, FR-076)."""
    imagem, linhas = _legenda(c)
    viewbox, interior = _svg_interior(imagens.PASTA / imagem.arquivo)
    elementos = [
        _el("svg", interior=interior, class_="abertura", x=0, y=0, width=LARGURA, height=fim,
            viewBox=viewbox, preserveAspectRatio="xMidYMax slice"),
        _el("path", class_="onda", fill=tema["creme"],
            d=f"M0 {fim - 60} C 270 {fim - 130} 640 {fim + 10} {LARGURA} {fim - 90} "
              f"L {LARGURA} {fim} L 0 {fim} Z"),
    ]
    elementos += marca(tema)
    alta = _altura_da_legenda(linhas)
    topo = fim - RECUO_LEGENDA - alta
    larga = _largura_da_legenda(linhas)
    elementos.append(
        _el("rect", class_="legenda-fundo", x=round(X1 + PILULA_LEGENDA - larga), y=topo,
            width=round(larga), height=alta, rx=26, fill=tema["profundo"])
    )
    for i, texto in enumerate(linhas):
        elementos.append(
            _texto(X1, topo + 8 + i * MEDIDAS["legenda"].entrelinha, texto, "legenda",
                   tema["branco"], ancora="end")
        )
    return elementos


def marca(tema) -> list[Elemento]:
    """A assinatura visual do Ifes, a mesma do cabeçalho, sobre pílula branca (FR-075)."""
    x, y, larga, alta = MARCA
    viewbox, interior = _svg_interior(ASSINATURA)
    return [
        _el("rect", class_="marca-fundo", x=x, y=y, width=larga, height=alta, rx=18,
            fill=tema["branco"]),
        _el("svg", interior=interior, class_="marca", x=x + 15, y=y + 8, width=360, height=100,
            viewBox=viewbox),
    ]


def _largura_da_legenda(linhas) -> float:
    return max(largura(t, MEDIDAS["legenda"].tamanho) for t in linhas) + 2 * PILULA_LEGENDA


def abertura_minima(c: Compartilhavel) -> int:
    _, linhas = _legenda(c)
    esquerda = X1 + PILULA_LEGENDA - _largura_da_legenda(linhas)
    lado_a_lado = esquerda >= MARCA[0] + MARCA[2] + 20
    topo = MARCA[1] if lado_a_lado else MARCA[1] + MARCA[3] + 20
    return max(ABERTURA_MINIMA, topo + _altura_da_legenda(linhas) + RECUO_LEGENDA)


def titulo(topo: float, nome: str | None, tema):
    corpo = MEDIDAS["titulo"]
    elementos = [
        _texto(X0, topo, TITULO_LINHAS[0], "titulo", tema["profundo"]),
        _texto(X0, topo + corpo.entrelinha, TITULO_LINHAS[1], "titulo", tema["marca"]),
    ]
    altura = 2 * corpo.entrelinha
    if nome:
        bloco, alta = _linhas(X0, topo + altura + ESPACO_NOME, _quebra(nome, "nome"), "nome",
                              tema["suave"])
        elementos += bloco
        altura += ESPACO_NOME + alta
    return elementos, altura


def _mais(n: int) -> str:
    return catalogo.plural(catalogo.CARD_MAIS, n).format(n=n)


def linha_do_tempo(topo: float, formacoes, omitidas: int, tema):
    """Um nó por formação, ano em destaque, curso em negrito e atributos; traço entre os
    nós (FR-077). As não exibidas entram em "e mais N" (FR-082)."""
    textos, centros, y = [], [], topo
    textos_dos_nos = []
    for i, f in enumerate(formacoes):
        if i:
            y += ESPACO_ITEM
        inicio = y
        do_no = []
        if f.ano_conclusao is not None:
            do_no.append(_texto(X_ITEM, y, str(f.ano_conclusao), "ano", tema["marca_escura"]))
            y += MEDIDAS["ano"].entrelinha
        bloco, alta = _linhas(X_ITEM, y, f.linhas_curso, "curso", tema["texto"])
        do_no += bloco
        y += alta
        bloco, alta = _linhas(X_ITEM, y, f.linhas_detalhe, "detalhe", tema["suave"])
        do_no += bloco
        y += alta
        textos += do_no
        textos_dos_nos.append(do_no)
        primeira = "ano" if f.ano_conclusao is not None else "curso"
        centros.append(round(inicio + MEDIDAS[primeira].entrelinha / 2))
        y = max(y, inicio + 2 * RAIO_NO)
    if omitidas:
        y += ESPACO_ITEM
        bloco, alta = _linhas(X_ITEM, y, _quebra(_mais(omitidas), "mais", LIMITE_ITEM), "mais",
                              tema["suave"])
        textos += bloco
        y += alta
    grafismo = []
    cx = X0 + RAIO_NO
    if len(centros) > 1:
        grafismo.append(_el("line", class_="traco", x1=cx, y1=centros[0], x2=cx, y2=centros[-1],
                            stroke=tema["marca"], stroke_width=TRACO))
    nos = []
    for cy, do_no in zip(centros, textos_dos_nos, strict=True):
        circulos = [
            _el("circle", class_="no", cx=cx, cy=cy, r=RAIO_NO, fill=tema["marca"]),
            _el("circle", class_="no-centro", cx=cx, cy=cy, r=RAIO_CENTRO, fill=tema["creme"]),
        ]
        grafismo += circulos
        nos.append(tuple(circulos + do_no))
    return grafismo + textos, y - topo, tuple(nos)


def numero_formatado(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _arranjo(contextos) -> str | None:
    """"lado" (dois cartões lado a lado), "faixa" (um cartão por linha, número à esquerda)
    ou None, quando algum rótulo não cabe em duas linhas (FR-078)."""
    if not contextos:
        return None
    meia = (LARGURA_UTIL - DESTAQUE_VAO) / 2 - DESTAQUE_TEXTO - DESTAQUE_MARGEM
    if len(contextos) == 2 and all(
        _cabe(numero_formatado(d.numero), "numero", meia)
        and all(_cabe(r, "rotulo", meia) for r in d.rotulo)
        for d in contextos
    ):
        return "lado"
    resto = LARGURA_UTIL - 2 * DESTAQUE_TEXTO - DESTAQUE_MARGEM - _coluna_do_numero(contextos)
    if not all(_cabe(r, "rotulo", resto) for d in contextos for r in d.rotulo):
        return None
    return "faixa"


def _coluna_do_numero(contextos) -> float:
    """Largura do maior número: na faixa, os rótulos se alinham depois dele."""
    corpo = MEDIDAS["numero"]
    return max(largura(numero_formatado(d.numero), corpo.tamanho, True) for d in contextos)


def destaques(topo: float, contextos, tema):
    """Cartões brancos com filete verde: número ≥ 80 px e rótulo de até 2 linhas (FR-078)."""
    arranjo = _arranjo(contextos)
    if arranjo is None:
        return [], 0, ()
    elementos, cartoes = [], []
    rotulo = MEDIDAS["rotulo"]
    if arranjo == "lado":
        larga = (LARGURA_UTIL - DESTAQUE_VAO) / 2
        caixas = [(X0 + i * (larga + DESTAQUE_VAO), topo, larga, DESTAQUE_ALTO)
                  for i in range(len(contextos))]
        altura = DESTAQUE_ALTO
    else:
        caixas = [(X0, topo + i * (DESTAQUE_BAIXO + DESTAQUE_VAO), LARGURA_UTIL, DESTAQUE_BAIXO)
                  for i in range(len(contextos))]
        altura = len(contextos) * (DESTAQUE_BAIXO + DESTAQUE_VAO) - DESTAQUE_VAO
    for d, (x, y, larga, alta) in zip(contextos, caixas, strict=True):
        inicio = len(elementos)
        elementos.append(_el("rect", class_="destaque", x=round(x), y=round(y),
                             width=round(larga), height=alta, rx=24, fill=tema["branco"]))
        elementos.append(_el("rect", class_="filete", x=round(x), y=round(y + 24), width=8,
                             height=alta - 48, rx=4, fill=tema["marca"]))
        numero = numero_formatado(d.numero)
        if arranjo == "lado":
            elementos.append(_texto(x + DESTAQUE_TEXTO, y + 12, numero, "numero",
                                    tema["profundo"]))
            topo_rotulo = y + 12 + MEDIDAS["numero"].entrelinha
            x_rotulo = x + DESTAQUE_TEXTO
        else:
            meio = y + (alta - MEDIDAS["numero"].entrelinha) / 2
            elementos.append(_texto(x + DESTAQUE_TEXTO, meio, numero, "numero",
                                    tema["profundo"]))
            x_rotulo = x + 2 * DESTAQUE_TEXTO + _coluna_do_numero(contextos)
            topo_rotulo = y + (alta - len(d.rotulo) * rotulo.entrelinha) / 2
        bloco, _ = _linhas(x_rotulo, topo_rotulo, d.rotulo, "rotulo", tema["suave"])
        elementos += bloco
        cartoes.append(tuple(elementos[inicio:]))
    return elementos, altura, tuple(cartoes)


def _linhas_do_rodape(c: Compartilhavel, demonstracao: bool, mostrar_apuracao: bool):
    corpo = MEDIDAS["rodape"]
    instituicao = [catalogo.CARD_RODAPE] + ([catalogo.CARD_DEMO] if demonstracao else [])
    linhas = [(t, "rodape") for t in quebrar_atributos(instituicao, corpo.tamanho)]
    if mostrar_apuracao and c.apuracao:
        linhas += [(t, "apuracao") for t in _quebra(c.apuracao, "apuracao")]
    return linhas


def _altura_do_fecho(linhas_rodape) -> int:
    return (
        len(_quebra(catalogo.FECHO, "fecho")) * MEDIDAS["fecho"].entrelinha
        + ESPACO_HASHTAG + MEDIDAS["hashtag"].entrelinha + ESPACO_RODAPE
        + sum(MEDIDAS[m].entrelinha for _, m in linhas_rodape)
    )


def fecho_e_rodape(linhas_rodape, tema):
    """Fecho, pílula da hashtag (FR-079) e rodapé ancorados na base da área segura. A
    proveniência só aparece aqui (FR-081)."""
    y = BASE - _altura_do_fecho(linhas_rodape)
    elementos, alta = _linhas(X0, y, _quebra(catalogo.FECHO, "fecho"), "fecho", tema["profundo"])
    y += alta + ESPACO_HASHTAG
    hashtag = MEDIDAS["hashtag"]
    larga = largura(catalogo.HASHTAG, hashtag.tamanho, True) + 2 * 28
    elementos.append(_el("rect", class_="hashtag-fundo", x=X0, y=y, width=round(larga),
                         height=hashtag.entrelinha, rx=hashtag.entrelinha // 2,
                         fill=tema["profundo"]))
    elementos.append(_texto(X0 + 28, y, catalogo.HASHTAG, "hashtag", tema["branco"]))
    y += hashtag.entrelinha + ESPACO_RODAPE
    for texto, medida in linhas_rodape:
        elementos.append(_texto(X0, y, texto, medida, tema["suave"]))
        y += MEDIDAS[medida].entrelinha
    return elementos


def faixa_inferior(tema) -> list[Elemento]:
    """Grafismo sem texto na faixa coberta pela interface do story."""
    y = BASE + 30
    elementos = [_el("rect", class_="faixa", x=0, y=y, width=LARGURA, height=ALTURA - y,
                     fill=tema["profundo"])]
    elementos += [
        _el("rect", class_="faixa-quadro", x=x + 18, y=y + 40, width=24, height=24, rx=4,
            fill=tema["marca"], opacity="0.35")
        for x in range(0, LARGURA, 60)
    ]
    return elementos


# --- Composição ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Zona:
    """Uma zona do card (Feature 022) e suas partes: um nó, um cartão ou a zona inteira."""

    chave: str
    partes: tuple[tuple[Elemento, ...], ...]


# Ordem de pintura das zonas (022 data-model §1.4). Cada classe de elemento pertence a uma
# zona; nós e cartões têm uma parte cada.
ZONAS = (
    "fundo", "abertura", "marca", "legenda", "titulo", "nome", "traco", "nos", "mais",
    "destaques", "apuracao", "fechamento", "rodape",
)
_ZONA_DA_CLASSE = {
    "fundo": "fundo", "faixa": "fundo", "faixa-quadro": "fundo",
    "abertura": "abertura", "onda": "abertura",
    "marca-fundo": "marca", "marca": "marca",
    "legenda-fundo": "legenda", "legenda": "legenda",
    "titulo": "titulo", "nome": "nome", "traco": "traco", "mais": "mais",
    "apuracao": "apuracao",
    "fecho": "fechamento", "hashtag-fundo": "fechamento", "hashtag": "fechamento",
    "rodape": "rodape",
}


@dataclass(frozen=True)
class Composicao:
    elementos: tuple[Elemento, ...]
    exibidas: int
    destaques: bool
    abertura: int
    # Falso quando nem o mínimo (título, um curso e fecho) coube na área segura. O card mantém
    # o comportamento da 021; o vídeo recusa a composição (022 FR-039).
    cabe: bool = True
    # Nós e cartões já agrupados por quem os desenhou; só o vídeo os usa (`zonas`).
    grupos: dict = field(default_factory=dict, compare=False, repr=False)

    @cached_property
    def zonas(self) -> tuple[Zona, ...]:
        """A composição agrupada por zona (Feature 022). Calculada só quando pedida: o card
        (SVG e PNG) nunca passa por aqui, então uma classe nova no card não o quebra."""
        return _zonas(self.elementos, self.grupos)


def _conteudo(c, nome, exibidas, com_destaques, tema, topo=0.0):
    """Título, linha do tempo e destaques a partir de `topo`. Devolve elementos, altura e as
    partes agrupadas (nós e cartões)."""
    elementos, altura = titulo(topo, nome, tema)
    altura += ESPACO_BLOCO
    omitidas = len(c.formacoes) - exibidas + c.formacoes_omitidas
    bloco, alta, nos = linha_do_tempo(topo + altura, c.formacoes[:exibidas], omitidas, tema)
    elementos += bloco
    altura += alta
    cartoes = ()
    if com_destaques:
        bloco, alta, cartoes = destaques(
            topo + altura + ESPACO_BLOCO, c.contextos_agregados, tema
        )
        if bloco:
            elementos += bloco
            altura += ESPACO_BLOCO + alta
    return elementos, altura, {"nos": nos, "destaques": cartoes}


class ZonaDesconhecida(Exception):
    """Elemento do card com classe sem zona do vídeo: falta mapeá-la em `_ZONA_DA_CLASSE`."""


def _zonas(elementos, grupos) -> tuple[Zona, ...]:
    """Agrupa os elementos já posicionados por zona, sem reordenar a lista plana."""
    agrupados = {id(e) for partes in grupos.values() for parte in partes for e in parte}
    por_zona = {}
    for e in elementos:
        if id(e) in agrupados:
            continue
        classe = dict(e.atributos).get("class")
        if classe not in _ZONA_DA_CLASSE:
            raise ZonaDesconhecida(classe)
        por_zona.setdefault(_ZONA_DA_CLASSE[classe], []).append(e)
    partes = {chave: (tuple(lista),) for chave, lista in por_zona.items()}
    partes.update({chave: tuple(p) for chave, p in grupos.items() if p})
    return tuple(Zona(chave, partes[chave]) for chave in ZONAS if chave in partes)


def compor(
    c: Compartilhavel, nome: str | None, demonstracao: bool, tema=TEMA_CARD
) -> Composicao:
    """Zonas posicionadas. Determinística. Ordem de corte do FR-082."""
    minimo = abertura_minima(c)
    total = len(c.formacoes)
    candidatos = []
    if _arranjo(c.contextos_agregados):
        candidatos.append((total, True))
    candidatos += [(n, False) for n in range(total, 0, -1)] or [(0, False)]
    for exibidas, com_destaques in candidatos:
        rodape = _linhas_do_rodape(c, demonstracao, com_destaques)
        _, altura, _ = _conteudo(c, nome, exibidas, com_destaques, tema)
        fim = BASE - _altura_do_fecho(rodape) - ESPACO_FECHO - altura - ESPACO_ABERTURA
        if fim >= minimo:
            break
    ideal = round(fim)
    cabe = ideal >= minimo
    fim = max(minimo, min(ABERTURA_MAXIMA, ideal))
    # Acima do máximo, a sobra se divide entre os dois lados do conteúdo (FR-080).
    folga = max(0, ideal - fim) // 2
    elementos = [_el("rect", class_="fundo", width=LARGURA, height=ALTURA, fill=tema["creme"])]
    elementos += abertura(c, fim, tema)
    bloco, _, grupos = _conteudo(
        c, nome, exibidas, com_destaques, tema, topo=fim + ESPACO_ABERTURA + folga
    )
    elementos += bloco
    elementos += fecho_e_rodape(rodape, tema)
    elementos += faixa_inferior(tema)
    return Composicao(tuple(elementos), exibidas, com_destaques, fim, cabe, grupos)


def descricao(c: Compartilhavel, nome: str | None, demonstracao: bool = True) -> str:
    """Resumo textual do que o card mostra (SVG `<desc>` e `alt` da prévia; FR-067)."""
    composicao = compor(c, nome, demonstracao)
    partes = [catalogo.TITULO + "."]
    if nome:
        partes.append(nome + ".")
    for f in c.formacoes[: composicao.exibidas]:
        atributos = (f.curso, f.unidade, f.nivel, f.modalidade, f.ano_conclusao)
        partes.append(SEPARADOR.join(str(a) for a in atributos if a is not None) + ".")
    omitidas = len(c.formacoes) - composicao.exibidas + c.formacoes_omitidas
    if omitidas:
        partes.append(_mais(omitidas).capitalize() + ".")
    if composicao.destaques:
        for d in c.contextos_agregados:
            partes.append(f"{numero_formatado(d.numero)} {' '.join(d.rotulo)}.")
    partes += [catalogo.FECHO, catalogo.HASHTAG + "."]
    if composicao.destaques and c.apuracao:
        partes.append(c.apuracao)
    return " ".join(partes)


def card_svg(
    c: Compartilhavel, tema=TEMA_CARD, nome: str | None = None, demonstracao: bool = True
) -> str:
    composicao = compor(c, nome, demonstracao, tema)
    return render_to_string(
        "narrativa/card.svg",
        {
            "largura": LARGURA,
            "altura": ALTURA,
            "elementos": composicao.elementos,
            "titulo": catalogo.TITULO,
            "descricao": descricao(c, nome, demonstracao),
        },
    )

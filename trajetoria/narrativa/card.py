"""Card vertical 9:16 para rede social (Feature 021; contracts/card.md; research R10).

O SVG é a representação-base; o PNG sai dele (`rasterizacao.png_de`). Todo texto fica na
área segura: as faixas de topo e de base, cobertas pela interface do story, recebem só
grafismo (FR-072). A quebra de linha mede o texto com as larguras reais das fontes
embutidas (`metricas.py`), sem cortar palavras nem truncar o nome.

A composição é adaptativa: mostra até 4 formações, tantas quantas couberem com o corpo
mínimo; as demais entram em "e mais N" (nenhuma some sem aviso). O par de agregados entra
só se couber depois das formações exibidas.
"""

from dataclasses import dataclass

from django.template.loader import render_to_string

from trajetoria.narrativa import catalogo, metricas
from trajetoria.narrativa.contrato import Compartilhavel

LARGURA, ALTURA = 1080, 1920
AREA_SEGURA = (90, 270, 990, 1570)  # x0, y0, x1, y1
LARGURA_UTIL = AREA_SEGURA[2] - AREA_SEGURA[0]
CORPO_MINIMO, CORPO_TITULO = 40, 64

TAMANHO_TITULO = CORPO_TITULO
TAMANHO_NOME = 44
TAMANHO_CURSO = 44
TAMANHO_TEXTO = CORPO_MINIMO
ENTRELINHA = 1.25
DESCENDENTE = 0.3  # fração do corpo abaixo da linha de base (Open Sans: 0,293)

RECUO_TOPO = 40  # respiro entre o fio da faixa de topo e o título
ESPACO_TITULO = 28
ESPACO_NOME = 36
ESPACO_FORMACAO = 28
ESPACO_BLOCO = 32

# Tokens da 015 (interface/templates/interface/estilo.css). A cor de marca só em grafismo.
TEMA_PADRAO = {
    "fundo": "#eef7f0",   # --cor-institucional
    "texto": "#1b1b1b",   # --cor-texto (≈ 15,8:1 sobre o fundo)
    "suave": "#565c65",   # --cor-texto-suave
    "faixa": "#1b1b1b",   # --cor-texto, só nas faixas (sem as cores de ação: 015 FR-012)
    "marca": "#2f9e41",   # --cor-marca, só nos fios
}
FAMILIA = "Open Sans, system-ui, sans-serif"


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


@dataclass(frozen=True)
class Linha:
    texto: str
    x: int
    y: int  # linha de base
    tamanho: int
    negrito: bool
    cor: str


def _altura(qtd_linhas: int, tamanho: int) -> float:
    return qtd_linhas * tamanho * ENTRELINHA


def _bloco(linhas, y, tamanho, negrito, cor) -> tuple[list[Linha], float]:
    saida = []
    for texto in linhas:
        base = y + tamanho  # topo da linha + corpo ≈ linha de base com folga da entrelinha
        saida.append(Linha(texto, AREA_SEGURA[0], round(base), tamanho, negrito, cor))
        y += tamanho * ENTRELINHA
    return saida, y


def compor(c: Compartilhavel, nome: str | None, demonstracao: bool, tema=TEMA_PADRAO):
    """Linhas posicionadas e o número de formações exibidas. Determinística."""
    x0, y0, _, y1 = AREA_SEGURA
    texto, suave = tema["texto"], tema["suave"]
    titulo = quebrar_linhas(catalogo.TITULO, TAMANHO_TITULO, True)
    linhas_nome = quebrar_linhas(nome, TAMANHO_NOME) if nome else ()
    registradas = catalogo.plural(catalogo.CARD_REGISTRADAS, c.formacoes_registradas).format(
        n=c.formacoes_registradas
    )
    rodape = [catalogo.CARD_RODAPE] + ([catalogo.CARD_DEMO] if demonstracao else [])
    linhas_rodape = [linha for t in rodape for linha in quebrar_linhas(t, TAMANHO_TEXTO)]

    def mais(n):
        return quebrar_linhas(
            catalogo.plural(catalogo.CARD_MAIS, n).format(n=n), TAMANHO_TEXTO
        )

    fixo = (
        _altura(len(titulo), TAMANHO_TITULO) + ESPACO_TITULO
        + (_altura(len(linhas_nome), TAMANHO_NOME) + ESPACO_NOME if linhas_nome else 0)
        + _altura(len(quebrar_linhas(registradas, TAMANHO_TEXTO)), TAMANHO_TEXTO)
        + ESPACO_BLOCO
        + _altura(len(linhas_rodape), TAMANHO_TEXTO)
    )
    disponivel = (y1 - y0) - RECUO_TOPO - fixo

    def altura_formacao(f):
        return (
            _altura(len(f.linhas_curso), TAMANHO_CURSO)
            + _altura(len(f.linhas_detalhe), TAMANHO_TEXTO)
            + ESPACO_FORMACAO
        )

    exibidas, usado = 0, 0.0
    total = len(c.formacoes)
    for f in c.formacoes:
        restantes = total - exibidas - 1 + c.formacoes_omitidas
        reserva = _altura(len(mais(restantes)), TAMANHO_TEXTO) if restantes else 0
        if exibidas and usado + altura_formacao(f) + reserva > disponivel:
            break
        exibidas += 1
        usado += altura_formacao(f)
    omitidas = total - exibidas + c.formacoes_omitidas
    if omitidas:
        usado += _altura(len(mais(omitidas)), TAMANHO_TEXTO)

    agregados = [linha for a in c.contextos_agregados for linha in a.linhas]
    altura_agregados = (
        ESPACO_BLOCO + _altura(len(agregados), TAMANHO_TEXTO) if agregados else 0
    )
    mostrar_agregados = bool(agregados) and usado + altura_agregados <= disponivel

    saida: list[Linha] = []
    y = float(y0 + RECUO_TOPO)
    bloco, y = _bloco(titulo, y, TAMANHO_TITULO, True, texto)
    saida += bloco
    y += ESPACO_TITULO
    if linhas_nome:
        bloco, y = _bloco(linhas_nome, y, TAMANHO_NOME, False, texto)
        saida += bloco
        y += ESPACO_NOME
    for f in c.formacoes[:exibidas]:
        bloco, y = _bloco(f.linhas_curso, y, TAMANHO_CURSO, True, texto)
        saida += bloco
        bloco, y = _bloco(f.linhas_detalhe, y, TAMANHO_TEXTO, False, suave)
        saida += bloco
        y += ESPACO_FORMACAO
    if omitidas:
        bloco, y = _bloco(mais(omitidas), y, TAMANHO_TEXTO, False, suave)
        saida += bloco
    bloco, y = _bloco(quebrar_linhas(registradas, TAMANHO_TEXTO), y, TAMANHO_TEXTO, True, texto)
    saida += bloco
    if mostrar_agregados:
        y += ESPACO_BLOCO
        bloco, y = _bloco(agregados, y, TAMANHO_TEXTO, False, texto)
        saida += bloco
    # Rodapé ancorado na base da área segura.
    # A última linha de base fica a um descendente da borda (nada invade a faixa de base).
    y_rodape = y1 - _altura(len(linhas_rodape), TAMANHO_TEXTO) - TAMANHO_TEXTO * (
        DESCENDENTE - (ENTRELINHA - 1)
    )
    bloco, _ = _bloco(linhas_rodape, y_rodape, TAMANHO_TEXTO, False, suave)
    saida += bloco
    return saida, exibidas, mostrar_agregados


def descricao(c: Compartilhavel, nome: str | None) -> str:
    """Resumo textual do card (SVG `<desc>` e `alt` da prévia; FR-067)."""
    partes = [catalogo.TITULO + "."]
    if nome:
        partes.append(nome + ".")
    for f in c.formacoes:
        partes.append(" · ".join(f.linhas_curso + f.linhas_detalhe).replace("  ", " ") + ".")
    if c.formacoes_omitidas:
        n = c.formacoes_omitidas
        partes.append(catalogo.plural(catalogo.CARD_MAIS, n).format(n=n).capitalize() + ".")
    for a in c.contextos_agregados:
        partes.append(a.texto)
    return " ".join(partes)


def card_svg(
    c: Compartilhavel, tema=TEMA_PADRAO, nome: str | None = None, demonstracao: bool = True
) -> str:
    linhas, _, _ = compor(c, nome, demonstracao, tema)
    return render_to_string(
        "narrativa/card.svg",
        {
            "largura": LARGURA,
            "altura": ALTURA,
            "area": AREA_SEGURA,
            "tema": tema,
            "familia": FAMILIA,
            "linhas": linhas,
            "titulo": catalogo.TITULO,
            "descricao": descricao(c, nome),
        },
    )

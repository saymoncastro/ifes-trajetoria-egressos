"""Composição visual serializada do card (Feature 022; contracts/composicao-visual.md).

É a entrada do template de vídeo: a projeção mecânica de `card.compor()`, agrupada por zona,
com a marcação SVG de cada parte produzida pelo mesmo template do card, com o mesmo escape.
Não há regra nova: o vídeo mostra exatamente o que o card mostra, e o último quadro é o card.

A chave (SHA-256 do JSON canônico, que traz a versão do template) identifica o vídeo no
estado técnico. Ela nunca é exposta em URL, HTML ou log (022 research R6): é hash de conteúdo
de baixa entropia (nome e cursos).
"""

import hashlib
import json
import logging

from django.template.loader import render_to_string

from trajetoria.narrativa import card
from trajetoria.narrativa.contrato import Compartilhavel

logger = logging.getLogger("trajetoria.narrativa")

VERSAO_CONTRATO = 1
TEMPLATE_DE_VIDEO = "trajetoria-v1"


class ComposicaoImpossivel(Exception):
    """O card não consegue representar a trajetória nem no mínimo (FR-039)."""


def _marcacao(parte) -> str:
    svg = render_to_string(
        "narrativa/card.svg",
        {"largura": card.LARGURA, "altura": card.ALTURA, "elementos": parte, "titulo": "",
         "descricao": ""},
    )
    return svg[svg.index("</desc>") + len("</desc>"):svg.rindex("</svg>")].strip()


def _zona(zona: card.Zona, centros: list[int]) -> dict:
    dados = {"chave": zona.chave, "partes": [_marcacao(parte) for parte in zona.partes]}
    if zona.chave == "traco":
        linha = dict(zona.partes[0][0].atributos)
        # `paradas`: o centro de cada nó, para o traço chegar a cada um quando ele entra.
        dados.update(y1=linha["y1"], y2=linha["y2"], paradas=centros)
    return dados


def _centros_dos_nos(zonas) -> list[int]:
    nos = next((z for z in zonas if z.chave == "nos"), None)
    return [
        dict(e.atributos)["cy"]
        for parte in (nos.partes if nos else ())
        for e in parte
        if dict(e.atributos).get("class") == "no"
    ]


def composicao_visual(c: Compartilhavel, nome: str | None, demonstracao: bool) -> dict:
    composicao = card.compor(c, nome, demonstracao)
    if not composicao.cabe or (c.formacoes and composicao.exibidas == 0):
        # Só o fato técnico: nada da trajetória no log (FR-027).
        logger.warning("video: composição impossível")
        raise ComposicaoImpossivel
    try:
        zonas = composicao.zonas
    except card.ZonaDesconhecida as erro:
        # Falha explícita só no vídeo: o card continua sendo gerado (FR-039).
        logger.warning("video: elemento do card sem zona (%s)", erro)
        raise ComposicaoImpossivel from erro
    centros = _centros_dos_nos(zonas)
    return {
        "versao_contrato": VERSAO_CONTRATO,
        "template": TEMPLATE_DE_VIDEO,
        "largura": card.LARGURA,
        "altura": card.ALTURA,
        "area_segura": list(card.AREA_SEGURA),
        "zonas": [_zona(z, centros) for z in zonas],
    }


def canonico(composicao: dict) -> str:
    return json.dumps(composicao, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def chave_da_composicao(composicao: dict) -> str:
    return hashlib.sha256(canonico(composicao).encode()).hexdigest()

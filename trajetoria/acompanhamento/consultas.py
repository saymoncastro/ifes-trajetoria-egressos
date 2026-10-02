"""Consultas do acompanhamento da coleta (Feature 011; contracts/consultas.md; research R4–R8).

Nada aqui grava. Toda contagem é feita no banco (`count`, `aggregate`,
`values().annotate()`); nenhum registro individual de Conclusão ou Participação é carregado, e
nenhuma Resposta é lida (spec FR-070 a FR-073, FR-090).

**Elegibilidade**: só `populacao_no_momento` (004). O acompanhamento apenas a refina com o
escopo e agrega; nenhuma condição da Campanha é reimplementada aqui (spec FR-030, FR-140).

**Escopo** (010): aplicado na consulta, antes de contar, pela unidade institucional da
Conclusão, nos dois lados — elegíveis e Participações. O universo depende só do escopo do
operador; o critério de unidades da Campanha nunca entra nele (spec FR-023): nos elegíveis
ele já está na população da 004; nas Participações seria reavaliar elegibilidade (FR-038).
`unidades_relevantes` só define as linhas com zero do recorte por unidade; a oferta do
recorte por unidade e a coluna Unidade do recorte por curso dependem do escopo (`_varias_unidades`),
porque as Participações podem vir de qualquer unidade do escopo.

**Privacidade**: recortes agregados sem supressão nem limiar (DP-1101 aberta). A exposição
produtiva dos recortes finos (curso, ano) DEVE revisitar DP-1101 antes de ocorrer
(010/DP-1001).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from django.db.models import Count, F, Q, QuerySet

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.apresentacao import Indicadores
from trajetoria.campanha.consultas import (
    EstadoCampanha,
    FormaEncerramento,
    encerramento,
    estado,
    momento_de_referencia,
    populacao_no_momento,
)
from trajetoria.campanha.models import Campanha
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.instrumento.models import EstadoVersao
from trajetoria.participacao.models import Participacao

__all__ = [
    "CampanhaAcompanhada",
    "Instrumento",
    "LinhaDeRecorte",
    "Recorte",
    "campanha_acompanhada",
    "campanhas_acompanhadas",
    "campanhas_visiveis",
    "indicadores_da_campanha",
    "recortes_oferecidos",
    "unidades_relevantes",
]


# --- Visibilidade e escopo --------------------------------------------------------------------


def campanhas_visiveis(escopo: EscopoDeAcompanhamento) -> QuerySet[Campanha]:
    """Institucional: todas. Unidades: sem critério de unidades, ou critério que tem ao menos
    uma unidade do escopo, por igualdade exata (FR-020 a FR-022). Não depende de número, estado
    nem Participação. A lista e a verificação de escopo do detalhe usam esta mesma função."""
    campanhas = Campanha.objects.select_related("versao__pesquisa").order_by(
        F("inicio").desc(nulls_last=True), "nome", "id"
    )
    if escopo.institucional:
        return campanhas
    return campanhas.filter(Q(unidades__isnull=True) | Q(unidades__overlap=sorted(escopo.unidades)))


def _universo(escopo: EscopoDeAcompanhamento) -> Q:
    """Conclusões do escopo. `unidade__in` nunca casa com `NULL`: Conclusão sem unidade não
    pertence a nenhuma CSAEG (FR-015)."""
    return Q() if escopo.institucional else Q(unidade__in=sorted(escopo.unidades))


def _universo_participacao(escopo: EscopoDeAcompanhamento) -> Q:
    """Participações cuja Conclusão está no escopo, pela unidade institucional da Conclusão."""
    return Q() if escopo.institucional else Q(conclusao__unidade__in=sorted(escopo.unidades))


def unidades_relevantes(campanha: Campanha, escopo: EscopoDeAcompanhamento) -> frozenset | None:
    """Só apresentação: as linhas com zero do recorte por unidade. `None` no escopo
    institucional."""
    if escopo.institucional:
        return None
    if campanha.unidades is None:
        return escopo.unidades
    return escopo.unidades & frozenset(campanha.unidades)


# --- Indicadores ------------------------------------------------------------------------------

_INICIADAS = Count("id")
_CONCLUIDAS = Count("id", filter=Q(concluida_em__isnull=False))


def indicadores_da_campanha(campanha: Campanha, escopo: EscopoDeAcompanhamento) -> Indicadores:
    """Totais no escopo, em duas consultas. Iniciadas e concluídas **não** passam pela
    elegibilidade atual (FR-038): Participação é fato registrado."""
    elegiveis = populacao_no_momento(campanha).filter(_universo(escopo)).count()
    participacoes = (
        Participacao.objects.filter(campanha=campanha)
        .filter(_universo_participacao(escopo))
        .aggregate(iniciadas=_INICIADAS, concluidas=_CONCLUIDAS)
    )
    return Indicadores(elegiveis, participacoes["iniciadas"], participacoes["concluidas"])


# --- Recortes ---------------------------------------------------------------------------------


class Recorte(Enum):
    """Os seis recortes, fechados (FR-050). `campos` são atributos institucionais da Conclusão
    (001); curso é identificado pelo par (unidade, curso), sem entidade de Curso."""

    UNIDADE = ("unidade", "Unidade", ("unidade",))
    CURSO = ("curso", "Curso", ("unidade", "curso"))
    NIVEL = ("nivel", "Nível", ("nivel",))
    MODALIDADE = ("modalidade", "Modalidade", ("modalidade",))
    FORMA_OFERTA = ("forma-oferta", "Forma de oferta", ("forma_oferta",))
    ANO_CONCLUSAO = ("ano-conclusao", "Ano de conclusão", ("ano_conclusao",))

    def __init__(self, valor, rotulo, campos):
        self.valor = valor
        self.rotulo = rotulo
        self.campos = campos

    @classmethod
    def de_valor(cls, texto) -> "Recorte | None":
        return next((r for r in cls if r.valor == texto), None)


NAO_INFORMADO = {
    "unidade": "Unidade não informada",
    "curso": "Curso não informado",
    "nivel": "Nível não informado",
    "modalidade": "Modalidade não informada",
    "forma_oferta": "Forma de oferta não informada",
    "ano_conclusao": "Ano de conclusão não informado",
}


@dataclass(frozen=True)
class LinhaDeRecorte:
    chave: tuple  # valores dos `campos`, como registrados; None = não informado
    indicadores: Indicadores

    def rotulos(self, recorte: Recorte) -> tuple[str, ...]:
        return tuple(
            NAO_INFORMADO[campo] if valor is None else str(valor)
            for campo, valor in zip(recorte.campos, self.chave, strict=True)
        )


def _varias_unidades(escopo: EscopoDeAcompanhamento) -> bool:
    """Os números podem cobrir mais de uma unidade: escopo institucional ou várias CSAEG. Vale
    pelo escopo, e não pelo critério da Campanha, porque as Participações são contadas por
    todas as unidades do escopo (FR-023, FR-038)."""
    return escopo.institucional or len(escopo.unidades) > 1


def recortes_oferecidos(escopo: EscopoDeAcompanhamento) -> tuple[Recorte, ...]:
    """Os seis, menos o recorte por unidade quando o escopo tem uma única unidade (FR-057)."""
    if _varias_unidades(escopo):
        return tuple(Recorte)
    return tuple(r for r in Recorte if r is not Recorte.UNIDADE)


def _linhas(campanha, escopo, recorte: Recorte) -> tuple[LinhaDeRecorte, ...]:
    """Uma consulta agrupada de cada lado; nenhuma consulta por linha. As linhas são combinadas
    pela chave. O `order_by()` vazio tira a ordenação padrão dos modelos do `GROUP BY`."""
    campos = recorte.campos
    elegiveis = (
        populacao_no_momento(campanha)
        .filter(_universo(escopo))
        .values_list(*campos)
        .annotate(n=Count("id"))
        .order_by()
    )
    participacoes = (
        Participacao.objects.filter(campanha=campanha)
        .filter(_universo_participacao(escopo))
        .values_list(*(f"conclusao__{c}" for c in campos))
        .annotate(iniciadas=_INICIADAS, concluidas=_CONCLUIDAS)
        .order_by()
    )
    contagens: dict[tuple, Indicadores] = {}
    for *chave, n in elegiveis:
        contagens[tuple(chave)] = contagens.get(tuple(chave), Indicadores()) + Indicadores(n)
    for *chave, iniciadas, concluidas in participacoes:
        parcial = Indicadores(0, iniciadas, concluidas)
        contagens[tuple(chave)] = contagens.get(tuple(chave), Indicadores()) + parcial
    if recorte is Recorte.UNIDADE:
        # Linhas com zero só onde há conjunto conhecido de unidades (FR-055).
        relevantes = unidades_relevantes(campanha, escopo)
        conhecidas = relevantes if relevantes is not None else (campanha.unidades or ())
        for unidade in conhecidas:
            contagens.setdefault((unidade,), Indicadores())
    return tuple(
        LinhaDeRecorte(chave, indicadores)
        for chave, indicadores in sorted(contagens.items(), key=lambda i: ap.chave_de_ordem(i[0]))
    )


# --- Campanha acompanhada ---------------------------------------------------------------------


@dataclass(frozen=True)
class Instrumento:
    texto: str
    endereco: str | None


def instrumento(campanha: Campanha, *, pode_consultar_rascunho: bool) -> Instrumento:
    """Versão em rascunho, para quem não consulta rascunhos (010): só o texto operacional, sem
    nome, designação nem link (FR-042)."""
    versao = campanha.versao
    if versao.estado != EstadoVersao.PUBLICADA and not pode_consultar_rascunho:
        return Instrumento(ap.INSTRUMENTO_NAO_PUBLICADO, None)
    return Instrumento(
        f"{versao.pesquisa.nome} — {versao.designacao}", f"/editor/versoes/{versao.pk}/"
    )


@dataclass(frozen=True)
class CampanhaAcompanhada:
    campanha: Campanha
    estado: EstadoCampanha
    encerramento: tuple[FormaEncerramento, datetime] | None
    instrumento: Instrumento
    indicadores: Indicadores
    recorte: Recorte | None = None
    linhas: tuple[LinhaDeRecorte, ...] = ()
    recortes_oferecidos: tuple[Recorte, ...] = ()
    coluna_unidade: bool = True

    @property
    def rotulo_nao_concluidas(self) -> str:
        return ap.rotulo_nao_concluidas(self.estado)

    @property
    def situacao(self) -> str:
        return ap.situacao(self.estado)

    @property
    def avisos(self) -> tuple[str, ...]:
        if self.estado is EstadoCampanha.EM_PREPARACAO:
            return (ap.AVISO_PREPARACAO,)
        if self.estado is EstadoCampanha.EM_COLETA:
            return (ap.AVISO_COLETA,)
        if self.campanha.aberta_em is None:
            return (ap.AVISO_NUNCA_ABERTA, ap.AVISO_POPULACAO_ATUAL)
        return (ap.AVISO_COLETA_ENCERRADA, ap.AVISO_POPULACAO_ATUAL)


def _acompanhada(campanha, escopo, pode_consultar_rascunho, agora, **detalhe):
    return CampanhaAcompanhada(
        campanha=campanha,
        estado=estado(campanha, agora=agora),
        encerramento=encerramento(campanha, agora=agora),
        instrumento=instrumento(campanha, pode_consultar_rascunho=pode_consultar_rascunho),
        indicadores=indicadores_da_campanha(campanha, escopo),
        **detalhe,
    )


def campanhas_acompanhadas(
    escopo: EscopoDeAcompanhamento, *, pode_consultar_rascunho: bool, agora=None
) -> tuple[CampanhaAcompanhada, ...]:
    """Lista. Custo proporcional ao número de Campanhas (duas consultas por Campanha), aceito
    no MVP (research R6): cada Campanha tem critérios próprios, aplicados só pela 004."""
    agora = momento_de_referencia(agora)
    return tuple(
        _acompanhada(c, escopo, pode_consultar_rascunho, agora) for c in campanhas_visiveis(escopo)
    )


def campanha_acompanhada(
    campanha: Campanha,
    escopo: EscopoDeAcompanhamento,
    *,
    pode_consultar_rascunho: bool,
    recorte: Recorte | None = None,
    agora=None,
) -> CampanhaAcompanhada:
    """Detalhe. Pré-condição: a Campanha é visível para o escopo (a view verifica antes)."""
    oferecidos = recortes_oferecidos(escopo)
    if recorte is None:
        recorte = Recorte.UNIDADE if Recorte.UNIDADE in oferecidos else Recorte.CURSO
    return _acompanhada(
        campanha,
        escopo,
        pode_consultar_rascunho,
        momento_de_referencia(agora),
        recorte=recorte,
        linhas=_linhas(campanha, escopo, recorte),
        recortes_oferecidos=oferecidos,
        coluna_unidade=_varias_unidades(escopo),
    )

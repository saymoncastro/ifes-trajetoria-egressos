"""Consultas de Campanha (specs/004-campanhas-populacao-elegivel/contracts/consultas.md).

Nada aqui grava. O estado temporal controla a coleta; a imutabilidade é controlada só por
`aberta_em`, em `operacoes.py`.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum

from django.db.models import Q, QuerySet
from django.utils import timezone

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.models import Campanha

__all__ = [
    "Criterio",
    "Elegibilidade",
    "EstadoCampanha",
    "FormaEncerramento",
    "MotivoPendencia",
    "Pendencia",
    "Resultado",
    "admite_participacao",
    "avaliar",
    "campanhas_em_coleta_para",
    "data_de_referencia",
    "encerramento",
    "estado",
    "momento_de_referencia",
    "populacao_no_momento",
]


class EstadoCampanha(Enum):
    EM_PREPARACAO = "em_preparacao"
    EM_COLETA = "em_coleta"
    ENCERRADA = "encerrada"


def momento_de_referencia(agora: datetime | None) -> datetime:
    """`agora`, ou o relógio do sistema quando omitido. Único ponto que consulta o relógio:
    os testes sempre passam `agora` (research R6). `agora` precisa ser um `datetime` com
    timezone; `date` ou `datetime` ingênuo é erro de programação."""
    if agora is None:
        return timezone.now()
    if not isinstance(agora, datetime) or timezone.is_naive(agora):
        raise TypeError(f"agora deve ser datetime com timezone, não {agora!r}")
    return agora


def data_de_referencia(agora: datetime | None) -> date:
    """A data civil de `agora` na timezone configurada do projeto."""
    return timezone.localdate(momento_de_referencia(agora))


def estado(campanha: Campanha, *, agora: datetime | None = None) -> EstadoCampanha:
    """Precedência: encerramento explícito → fim do período (aberta ou não) → abertura →
    preparação. Derivado; nenhum processo grava o encerramento por data (FR-038). Abertura e
    encerramento explícito só valem a partir do momento em que ocorreram: com `agora`
    anterior a eles, a Campanha ainda não estava aberta ou encerrada."""
    agora = momento_de_referencia(agora)
    if campanha.encerrada_em is not None and campanha.encerrada_em <= agora:
        return EstadoCampanha.ENCERRADA
    if campanha.fim is not None and data_de_referencia(agora) > campanha.fim:
        return EstadoCampanha.ENCERRADA
    if campanha.aberta_em is not None and campanha.aberta_em <= agora:
        return EstadoCampanha.EM_COLETA
    return EstadoCampanha.EM_PREPARACAO


class FormaEncerramento(Enum):
    EXPLICITA = "explicita"
    FIM_DO_PERIODO = "fim_do_periodo"


def encerramento(
    campanha: Campanha, *, agora: datetime | None = None
) -> tuple[FormaEncerramento, datetime] | None:
    """Forma e momento efetivo do encerramento; `None` fora de ENCERRADA. Pelo fim do
    período, o momento é o início do dia seguinte ao fim, na timezone configurada, e vale
    também para Campanha nunca aberta (`aberta_em` diz se houve coleta)."""
    agora = momento_de_referencia(agora)
    if estado(campanha, agora=agora) is not EstadoCampanha.ENCERRADA:
        return None
    if campanha.encerrada_em is not None and campanha.encerrada_em <= agora:
        return FormaEncerramento.EXPLICITA, campanha.encerrada_em
    dia_seguinte = datetime.combine(campanha.fim + timedelta(days=1), time.min)
    return FormaEncerramento.FIM_DO_PERIODO, timezone.make_aware(dia_seguinte)


# --- Elegibilidade ----------------------------------------------------------------------


class Resultado(Enum):
    ELEGIVEL = "elegivel"
    NAO_ELEGIVEL = "nao_elegivel"


class Criterio(Enum):
    """A ordem de declaração é a ordem das pendências."""

    ANO_CONCLUSAO = "ano_conclusao"
    UNIDADE = "unidade"
    NIVEL = "nivel"
    MODALIDADE = "modalidade"
    FORMA_OFERTA = "forma_oferta"


class MotivoPendencia(Enum):
    NAO_INFORMADO = "nao_informado"  # atributo ausente na Conclusão (FR-028)
    NAO_ATENDE = "nao_atende"  # atributo informado, fora do critério


@dataclass(frozen=True)
class Pendencia:
    criterio: Criterio
    motivo: MotivoPendencia


@dataclass(frozen=True)
class Elegibilidade:
    pendencias: tuple[Pendencia, ...]  # vazia ⇔ ELEGIVEL

    @property
    def resultado(self) -> Resultado:
        return Resultado.NAO_ELEGIVEL if self.pendencias else Resultado.ELEGIVEL

    @property
    def elegivel(self) -> bool:
        return not self.pendencias


# Critérios de conjunto: (critério, campo da Campanha, atributo da Conclusão). Única fonte
# para `avaliar` e `_filtro`, para não haver duas semânticas independentes.
_CONJUNTOS = (
    (Criterio.UNIDADE, "unidades", "unidade"),
    (Criterio.NIVEL, "niveis", "nivel"),
    (Criterio.MODALIDADE, "modalidades", "modalidade"),
    (Criterio.FORMA_OFERTA, "formas_oferta", "forma_oferta"),
)


def _verificar_ano(campanha: Campanha, conclusao: ConclusaoAcademica):
    """Mínimo e máximo formam um único critério (FR-027); limite ausente não restringe."""
    minimo, maximo = campanha.ano_minimo, campanha.ano_maximo
    if minimo is None and maximo is None:
        return None
    ano = conclusao.ano_conclusao
    if ano is None:
        return MotivoPendencia.NAO_INFORMADO
    if (minimo is not None and ano < minimo) or (maximo is not None and ano > maximo):
        return MotivoPendencia.NAO_ATENDE
    return None


def _verificar_conjunto(permitidos: list[str] | None, valor: str | None):
    """OR dentro do critério, por igualdade exata, sem normalização (FR-020, FR-022)."""
    if permitidos is None:
        return None
    if valor is None:
        return MotivoPendencia.NAO_INFORMADO
    if valor not in permitidos:
        return MotivoPendencia.NAO_ATENDE
    return None


def avaliar(campanha: Campanha, conclusao: ConclusaoAcademica) -> Elegibilidade:
    """Função pura: depende só dos critérios da Campanha e dos atributos da Conclusão; não
    acessa o banco nem a data e não grava nada (FR-025, FR-030)."""
    verificacoes = [(Criterio.ANO_CONCLUSAO, _verificar_ano(campanha, conclusao))]
    verificacoes += [
        (criterio, _verificar_conjunto(getattr(campanha, campo), getattr(conclusao, atributo)))
        for criterio, campo, atributo in _CONJUNTOS
    ]
    return Elegibilidade(
        tuple(Pendencia(criterio, motivo) for criterio, motivo in verificacoes if motivo)
    )


# --- População ----------------------------------------------------------------------------


def _filtro(campanha: Campanha) -> Q:
    """O mesmo predicado de `avaliar`, no banco. Comparações e `IN` do SQL nunca casam com
    `NULL`, o que coincide com NAO_INFORMADO."""
    filtro = Q()
    if campanha.ano_minimo is not None:
        filtro &= Q(ano_conclusao__gte=campanha.ano_minimo)
    if campanha.ano_maximo is not None:
        filtro &= Q(ano_conclusao__lte=campanha.ano_maximo)
    for _, campo, atributo in _CONJUNTOS:
        if (permitidos := getattr(campanha, campo)) is not None:
            filtro &= Q(**{f"{atributo}__in": permitidos})
    return filtro


def _campanhas_que_admitem(conclusao: ConclusaoAcademica) -> Q:
    """O predicado de `avaliar` visto do lado da Campanha: as Campanhas em que a Conclusão é
    ELEGÍVEL. Atributo ausente só passa por critério não definido (FR-028)."""
    ano = conclusao.ano_conclusao
    if ano is None:
        filtro = Q(ano_minimo__isnull=True, ano_maximo__isnull=True)
    else:
        filtro = (Q(ano_minimo__isnull=True) | Q(ano_minimo__lte=ano)) & (
            Q(ano_maximo__isnull=True) | Q(ano_maximo__gte=ano)
        )
    for _, campo, atributo in _CONJUNTOS:
        valor = getattr(conclusao, atributo)
        sem_criterio = Q(**{f"{campo}__isnull": True})
        if valor is None:
            filtro &= sem_criterio
        else:
            filtro &= sem_criterio | Q(**{f"{campo}__contains": [valor]})
    return filtro


def populacao_no_momento(campanha: Campanha) -> QuerySet[ConclusaoAcademica]:
    """Conclusões existentes agora que satisfazem os critérios. Não é denominador
    histórico e nada é guardado (FR-031, FR-032; DP-408)."""
    return ConclusaoAcademica.objects.filter(_filtro(campanha))


# --- Contrato com a futura Participação (005) -------------------------------------------


def admite_participacao(
    campanha: Campanha, conclusao: ConclusaoAcademica, *, agora: datetime | None = None
) -> bool:
    """Condição necessária: EM_COLETA e ELEGÍVEL. Não depende de convite, envio ou
    destinatário (FR-048, FR-053); a 005 pode acrescentar condições."""
    return (
        estado(campanha, agora=agora) is EstadoCampanha.EM_COLETA
        and avaliar(campanha, conclusao).elegivel
    )


def campanhas_em_coleta_para(
    conclusao: ConclusaoAcademica, *, agora: datetime | None = None
) -> tuple[Campanha, ...]:
    """Todas as Campanhas EM_COLETA em que a Conclusão é ELEGÍVEL. A ordem (inicio, id) é
    só determinística: sem prioridade, ranking ou exclusividade (FR-051, FR-052; DP-404)."""
    agora = momento_de_referencia(agora)
    em_coleta = Campanha.objects.filter(
        Q(encerrada_em__isnull=True) | Q(encerrada_em__gt=agora),
        aberta_em__lte=agora,
        fim__gte=data_de_referencia(agora),
    )
    return tuple(em_coleta.filter(_campanhas_que_admitem(conclusao)).order_by("inicio", "id"))

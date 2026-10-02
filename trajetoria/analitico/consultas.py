"""Leitura do snapshot analítico (contracts/consultas.md). Nada aqui grava.

Toda função recebe o snapshot explicitamente: não existe "snapshot atual", "vigente" ou
"último" (spec FR-061, FR-064; DP-1201).

**Nunca o estado acadêmico atual** (spec FR-076, FR-080): nenhuma consulta lê a Conclusão
nem a Pessoa. O contexto vem dos registros congelados; a Participação, imutável depois do
encerramento, é encontrada pela Campanha do snapshot e pela `conclusao_id` do registro.

**Fronteira mínima** (spec FR-070, FR-074): objetos de valor pequenos e semânticos. Não é a
013: sem schema tabular, colunas, serializador, achatamento, nomes externos, CSV ou GeN.
`conclusao_id` e `ParticipacaoNoDataset.id` são referências técnicas internas, não
identificadores exportáveis (spec FR-047; 005/DP-505).
"""

from collections.abc import Iterator
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from uuid import UUID

from django.db.models import Count, Exists, OuterRef, QuerySet

from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.percurso import (
    percorrer,
    perguntas_do_percurso,
    respondidas,
    secoes_nao_suportadas,
)
from trajetoria.participacao.regras import ParticipacaoRejeitada

__all__ = [
    "ContextoCongelado",
    "IndicadoresDoSnapshot",
    "LinhaDoDataset",
    "LinhaDoRecorte",
    "ParticipacaoNoDataset",
    "RecorteDoSnapshot",
    "RespostaNoDataset",
    "indicadores_do_snapshot",
    "linhas_do_dataset",
    "recorte_do_snapshot",
    "snapshots_da_campanha",
]


# --- Snapshots da Campanha -------------------------------------------------------------------


def snapshots_da_campanha(campanha) -> QuerySet[SnapshotAnalitico]:
    """Todos os snapshots da Campanha, em ordem `(capturado_em, id)`.

    Ordem **administrativa, sem autoridade institucional** (DP-1201): nenhum consumidor deve
    tomar o primeiro ou o último como autoritativo; toda leitura recebe o snapshot
    explicitamente (spec FR-063, FR-064). Não filtra, não deduplica, não marca nenhum."""
    return SnapshotAnalitico.objects.filter(campanha=campanha).order_by("capturado_em", "id")


# --- Dataset ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class ContextoCongelado:
    """Contexto **institucional** da Conclusão no momento da captura (spec FR-044). `None` =
    não informado."""

    curso: str | None
    unidade: str | None
    nivel: str | None
    modalidade: str | None
    forma_oferta: str | None
    ano_conclusao: int | None
    data_conclusao: date | None


@dataclass(frozen=True)
class ParticipacaoNoDataset:
    """O estado da Participação, sem a instância (que alcançaria Conclusão e Pessoa)."""

    id: UUID
    iniciada_em: datetime
    concluida_em: datetime | None

    @property
    def concluida(self) -> bool:
        return self.concluida_em is not None


@dataclass(frozen=True)
class RespostaNoDataset:
    """Valor **declarado**, na estrutura da 005, sem a instância de `Resposta` (que
    alcançaria a Participação por `resposta.participacao`). `Pergunta` e `Opcao` são do
    instrumento imutável e não têm acessor reverso para Resposta."""

    pergunta: Pergunta
    opcao_id: UUID | None  # lido por `percurso.respondidas` (006)
    opcao: Opcao | None
    opcoes: tuple[Opcao, ...]  # escolha múltipla, na ordem do instrumento
    texto: str | None
    escala: int | None
    complemento: str | None


@dataclass(frozen=True)
class LinhaDoDataset:
    """Um registro do snapshot combinado com os fatos históricos preservados.

    `fora_do_percurso`: `∅` sem Participação ou com Participação concluída (a 006 já removeu
    as inativas); para não concluída, as Perguntas com Resposta preservada fora do percurso;
    `None` quando o percurso não é determinável: Versão com estrutura não suportada (006
    FR-016) ou Respostas que a 006 rejeita ao percorrer (só por escrita fora das operações).
    Nada é descartado em nenhum dos casos."""

    conclusao_id: UUID
    elegivel_no_snapshot: bool
    contexto: ContextoCongelado
    participacao: ParticipacaoNoDataset | None
    respostas: MappingProxyType  # id da Pergunta → RespostaNoDataset
    fora_do_percurso: frozenset | None


_SEM_RESPOSTAS = MappingProxyType({})


def linhas_do_dataset(snapshot: SnapshotAnalitico) -> Iterator[LinhaDoDataset]:
    """Uma linha por registro, em ordem de `conclusao_id` (só determinismo).

    Consultas em número fixo, independente do número de registros: a Versão e seu conteúdo,
    os registros, as Participações da Campanha e as Respostas delas. As Respostas são lidas
    das tabelas da 005 e convertidas em objetos de valor; nada é gravado (spec FR-071,
    FR-121). Volume: Participações e Respostas da Campanha são carregadas numa só passada;
    ler em blocos, se o volume real exigir, é mudança local, sem alterar o contrato
    (research R12)."""
    campanha = snapshot.campanha
    conteudo = conteudo_da_versao(campanha.versao)
    # A estrutura é da Versão inteira: verificada uma vez, não por rascunho (006 FR-016).
    percurso_executavel = not secoes_nao_suportadas(conteudo)
    registros = list(
        RegistroDoSnapshot.objects.filter(snapshot=snapshot)
        .order_by("conclusao_id")
        .values_list("conclusao_id", "elegivel_no_snapshot", *CAMPOS_DE_CONTEXTO)
    )
    participacoes = {
        p.conclusao_id: p for p in Participacao.objects.filter(campanha_id=campanha.pk)
    }
    respostas: dict[UUID, dict[UUID, RespostaNoDataset]] = {}
    lidas = (
        Resposta.objects.filter(participacao__campanha_id=campanha.pk)
        .select_related("pergunta", "opcao")
        .prefetch_related("opcoes")
    )
    for r in lidas:
        respostas.setdefault(r.participacao_id, {})[r.pergunta_id] = RespostaNoDataset(
            pergunta=r.pergunta,
            opcao_id=r.opcao_id,
            opcao=r.opcao,
            opcoes=tuple(r.opcoes.all()),
            texto=r.texto,
            escala=r.escala,
            complemento=r.complemento,
        )
    for conclusao_id, elegivel, *contexto in registros:
        participacao = participacoes.get(conclusao_id)
        if participacao is None:
            no_dataset, da_participacao, fora = None, _SEM_RESPOSTAS, frozenset()
        else:
            no_dataset = ParticipacaoNoDataset(
                participacao.id, participacao.iniciada_em, participacao.concluida_em
            )
            da_participacao = MappingProxyType(respostas.get(participacao.id, {}))
            if no_dataset.concluida:
                fora = frozenset()
            elif percurso_executavel:
                fora = _fora_do_percurso(conteudo, da_participacao)
            else:
                fora = None
        yield LinhaDoDataset(
            conclusao_id=conclusao_id,
            elegivel_no_snapshot=elegivel,
            contexto=ContextoCongelado(**dict(zip(CAMPOS_DE_CONTEXTO, contexto, strict=True))),
            participacao=no_dataset,
            respostas=da_participacao,
            fora_do_percurso=fora,
        )


def _fora_do_percurso(conteudo, respostas) -> frozenset | None:
    """A mesma composição de `situacao_da_jornada` (006), sobre as funções puras do
    percurso; nenhuma segunda implementação da jornada (research R9). Uma Participação cujas
    Respostas a 006 rejeita (Opção ausente ou alheia na Pergunta com regra) fica com percurso
    não determinável, sem interromper a leitura das demais linhas."""
    try:
        passagens = percorrer(conteudo, respondidas(respostas))
    except ParticipacaoRejeitada:
        return None
    return frozenset(respostas) - perguntas_do_percurso(passagens)


# --- Indicadores ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class IndicadoresDoSnapshot:
    """Contagens sobre os registros do snapshot (spec FR-081 a FR-084). O denominador é
    **elegíveis no snapshot**, nunca elegíveis atuais (spec FR-090); o numerador são todas as
    Participações das Conclusões representadas, inclusive de registros não elegíveis. Iniciada
    = Participação existente; concluída = conclusão registrada, inclusive por recusa (011
    FR-032, FR-033; 007/DP-703, 006/DP-601). Contagens de Conclusões e Participações, nunca
    de Pessoas."""

    elegiveis: int = 0
    iniciadas_elegiveis: int = 0
    iniciadas_nao_elegiveis: int = 0
    concluidas_elegiveis: int = 0
    concluidas_nao_elegiveis: int = 0

    @property
    def iniciadas(self) -> int:
        return self.iniciadas_elegiveis + self.iniciadas_nao_elegiveis

    @property
    def concluidas(self) -> int:
        return self.concluidas_elegiveis + self.concluidas_nao_elegiveis

    @property
    def nao_concluidas(self) -> int:
        return self.iniciadas - self.concluidas

    @property
    def nao_concluidas_elegiveis(self) -> int:
        return self.iniciadas_elegiveis - self.concluidas_elegiveis

    @property
    def nao_concluidas_nao_elegiveis(self) -> int:
        return self.iniciadas_nao_elegiveis - self.concluidas_nao_elegiveis

    @property
    def registros(self) -> int:
        """Todo registro não elegível tem Participação, por construção do universo."""
        return self.elegiveis + self.iniciadas_nao_elegiveis

    @property
    def taxa_inicio(self) -> Decimal | None:
        return _taxa(self.iniciadas, self.elegiveis)

    @property
    def taxa_conclusao(self) -> Decimal | None:
        return _taxa(self.concluidas, self.elegiveis)

    def __add__(self, outro: "IndicadoresDoSnapshot") -> "IndicadoresDoSnapshot":
        return IndicadoresDoSnapshot(
            **{f.name: getattr(self, f.name) + getattr(outro, f.name) for f in fields(self)}
        )


def _taxa(numerador: int, denominador: int) -> Decimal | None:
    """Sem teto e sem arredondamento: pode passar de 1 (spec FR-083); arredondar é
    apresentação, da 013. `None` = não se aplica."""
    return None if denominador == 0 else Decimal(numerador) / Decimal(denominador)


def _contagens(snapshot: SnapshotAnalitico, campos: tuple[str, ...]) -> dict:
    """`chave → IndicadoresDoSnapshot`, numa consulta agrupada por `campos` **e** pela
    elegibilidade. Cada `Exists` de Participação (pela Campanha do snapshot e pela
    `conclusao_id` do registro) aparece uma única vez no SQL; a separação por elegibilidade
    vem do agrupamento, não de filtros repetidos. Nenhuma tabela da 001 nem de Resposta entra
    no SQL."""
    participacao = Participacao.objects.filter(
        campanha_id=snapshot.campanha_id, conclusao_id=OuterRef("conclusao_id")
    )
    agrupado = (
        RegistroDoSnapshot.objects.filter(snapshot=snapshot)
        .values(*campos, "elegivel_no_snapshot")
        .annotate(
            registros=Count("id"),
            iniciadas=Count("id", filter=Exists(participacao)),
            concluidas=Count("id", filter=Exists(participacao.filter(concluida_em__isnull=False))),
        )
        .order_by()
    )
    contagens: dict[tuple, IndicadoresDoSnapshot] = {}
    for linha in agrupado:
        chave = tuple(linha[campo] for campo in campos)
        if linha["elegivel_no_snapshot"]:
            parcial = IndicadoresDoSnapshot(
                elegiveis=linha["registros"],
                iniciadas_elegiveis=linha["iniciadas"],
                concluidas_elegiveis=linha["concluidas"],
            )
        else:
            parcial = IndicadoresDoSnapshot(
                iniciadas_nao_elegiveis=linha["iniciadas"],
                concluidas_nao_elegiveis=linha["concluidas"],
            )
        contagens[chave] = contagens.get(chave, IndicadoresDoSnapshot()) + parcial
    return contagens


def indicadores_do_snapshot(snapshot: SnapshotAnalitico) -> IndicadoresDoSnapshot:
    """Totais do snapshot recebido, numa consulta."""
    return _contagens(snapshot, ()).get((), IndicadoresDoSnapshot())


# --- Recortes ------------------------------------------------------------------------------------


class RecorteDoSnapshot(Enum):
    """Os seis recortes de uma dimensão da 011, fechados, sobre os campos **congelados** do
    registro (spec FR-085). Curso é identificado por (unidade, curso), sem entidade de Curso
    (spec FR-045). Definido aqui, sem importar o app de interface da 011 (research R11)."""

    # O valor é o identificador (único por construção); os campos são atributo à parte, para
    # que dois recortes com os mesmos campos nunca virem aliases do Enum.
    UNIDADE = ("unidade", ("unidade",))
    CURSO = ("curso", ("unidade", "curso"))
    NIVEL = ("nivel", ("nivel",))
    MODALIDADE = ("modalidade", ("modalidade",))
    FORMA_OFERTA = ("forma-oferta", ("forma_oferta",))
    ANO_CONCLUSAO = ("ano-conclusao", ("ano_conclusao",))

    def __init__(self, identificador: str, campos: tuple[str, ...]):
        self.identificador = identificador
        self.campos = campos


@dataclass(frozen=True)
class LinhaDoRecorte:
    chave: tuple  # valores congelados dos `campos`; None = não informado
    indicadores: IndicadoresDoSnapshot


def _ordem(chave: tuple) -> tuple:
    """Determinística, com não informado por último; sem significado de ranking."""
    return tuple((valor is None, valor) for valor in chave)


def recorte_do_snapshot(
    snapshot: SnapshotAnalitico, recorte: RecorteDoSnapshot
) -> tuple[LinhaDoRecorte, ...]:
    """Uma consulta agrupada pelos campos congelados; nenhuma consulta por linha. Só os
    valores presentes nos registros: as linhas com zero da 011 são apresentação dela."""
    linhas = [
        LinhaDoRecorte(chave, indicadores)
        for chave, indicadores in _contagens(snapshot, recorte.campos).items()
    ]
    return tuple(sorted(linhas, key=lambda linha: _ordem(linha.chave)))

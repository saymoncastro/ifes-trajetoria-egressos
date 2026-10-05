"""Capacidade de contexto da trajetória (Feature 021, P2; contracts/contexto-da-trajetoria.md).

Fronteira **separada** da `FonteAcademica` (contrato.py, inalterado): a identidade e a
incorporação (001, 018, 019) nunca dependem dela (FR-071). Informa, para Conclusões já
conhecidas, o complemento individual (ingresso) e o contexto institucional agregado. Um
adaptador real pode ler uma única view larga e alimentar os dois contratos.

Python puro: não importa Django nem fonte concreta. Atributo ausente é `None`; cadeia vazia
é proibida.
"""

from dataclasses import dataclass, fields
from datetime import date
from enum import Enum
from typing import Protocol


class ContextoIndisponivel(Exception):
    """A fonte de contexto não pôde responder. Nunca equivale a "sem complemento" nem a
    "sem agregado"."""


class MetricaAgregada(Enum):
    """As duas métricas fechadas (FR-053). Contam Conclusões, não pessoas."""

    CONCLUSOES_CURSO_UNIDADE_ANO = "conclusoes_curso_unidade_ano"
    CONCLUSOES_UNIDADE_ANO = "conclusoes_unidade_ano"


def _exigir_texto(valor: str, campo: str) -> None:
    if not valor:
        raise ValueError(f"{campo} não pode ser vazio")


def _rejeitar_cadeias_vazias(objeto: object) -> None:
    for campo in fields(objeto):
        if getattr(objeto, campo.name) == "":
            raise ValueError(f"{campo.name} não pode ser cadeia vazia; use None")


@dataclass(frozen=True)
class ComplementoNaFonte:
    """Ingresso na matrícula que resultou nesta Conclusão (DP-2104)."""

    id_externo_conclusao: str
    ano_ingresso: int
    data_ingresso: date | None = None

    def __post_init__(self) -> None:
        _exigir_texto(self.id_externo_conclusao, "id_externo_conclusao")
        if self.data_ingresso is not None and self.data_ingresso.year != self.ano_ingresso:
            raise ValueError("ano_ingresso deve ser o ano de data_ingresso")


@dataclass(frozen=True)
class AgregadoNaFonte:
    metrica: MetricaAgregada
    unidade: str
    ano: int
    valor: int
    apurado_em: date
    curso: str | None = None

    def __post_init__(self) -> None:
        _rejeitar_cadeias_vazias(self)
        _exigir_texto(self.unidade, "unidade")
        if self.valor < 0:
            raise ValueError("valor não pode ser negativo")
        exige_curso = self.metrica is MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO
        if exige_curso != (self.curso is not None):
            raise ValueError("curso é obrigatório na métrica por curso e proibido na por unidade")

    @property
    def chave(self) -> tuple:
        return (self.metrica, self.curso, self.unidade, self.ano, self.apurado_em)


@dataclass(frozen=True)
class ContextoDaTrajetoriaNaFonte:
    complementos: tuple[ComplementoNaFonte, ...]
    agregados: tuple[AgregadoNaFonte, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.complementos, tuple) or not isinstance(self.agregados, tuple):
            raise TypeError("complementos e agregados devem ser tuple")
        ids = [c.id_externo_conclusao for c in self.complementos]
        if len(ids) != len(set(ids)):
            raise ValueError("complementos não pode repetir id_externo_conclusao")
        chaves = [a.chave for a in self.agregados]
        if len(chaves) != len(set(chaves)):
            raise ValueError("agregados não pode repetir a chave")


class FonteDeContextoDaTrajetoria(Protocol):
    """`codigo` é o mesmo da fonte das Conclusões. `obter_contexto` pode lançar
    `ContextoIndisponivel`."""

    codigo: str

    def obter_contexto(
        self, ids_externos_conclusoes: tuple[str, ...]
    ) -> ContextoDaTrajetoriaNaFonte: ...

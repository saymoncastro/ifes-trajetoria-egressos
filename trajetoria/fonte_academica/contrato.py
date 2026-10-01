"""Contrato da fronteira de dados acadêmicos (conceitualmente, `AcademicDataProvider`).

Python puro: este módulo não importa Django nem qualquer fonte concreta. Toda
implementação, simulada ou real, obedece a este contrato
(specs/001-nucleo-academico-fonte-simulada/contracts/fonte-academica.md).

Atributo ausente é `None` e significa "não informado pela fonte". Cadeia vazia é
proibida, para que não exista uma segunda forma de ausência.
"""

from dataclasses import dataclass, fields
from datetime import date
from typing import Protocol


class FonteAcademicaIndisponivel(Exception):
    """A fonte não pôde responder. Nunca equivale a "inexistente" nem a "sem conclusões"."""


def _exigir_texto(valor: str, campo: str) -> None:
    if not valor:
        raise ValueError(f"{campo} não pode ser vazio")


def _rejeitar_cadeias_vazias(objeto: object) -> None:
    for campo in fields(objeto):
        if getattr(objeto, campo.name) == "":
            raise ValueError(f"{campo.name} não pode ser cadeia vazia; use None")


@dataclass(frozen=True)
class ConclusaoNaFonte:
    """Conclusão reconhecida pela fonte, já na forma canônica do NIAE."""

    id_externo: str
    curso: str | None = None
    unidade: str | None = None
    nivel: str | None = None
    modalidade: str | None = None
    forma_oferta: str | None = None
    ano_conclusao: int | None = None
    data_conclusao: date | None = None

    def __post_init__(self) -> None:
        _exigir_texto(self.id_externo, "id_externo")
        _rejeitar_cadeias_vazias(self)
        if self.data_conclusao is not None and self.ano_conclusao != self.data_conclusao.year:
            raise ValueError("ano_conclusao deve estar preenchido e ser o ano de data_conclusao")


@dataclass(frozen=True)
class PessoaEncontrada:
    """Pessoa conhecida pela fonte, com suas conclusões reconhecidas (possivelmente nenhuma)."""

    id_externo: str
    nome: str | None
    conclusoes: tuple[ConclusaoNaFonte, ...]

    def __post_init__(self) -> None:
        _exigir_texto(self.id_externo, "id_externo")
        _rejeitar_cadeias_vazias(self)
        if not isinstance(self.conclusoes, tuple):
            raise TypeError("conclusoes deve ser tuple")


@dataclass(frozen=True)
class PessoaInexistente:
    id_externo: str


@dataclass(frozen=True)
class ConclusaoEncontrada:
    conclusao: ConclusaoNaFonte
    id_externo_pessoa: str

    def __post_init__(self) -> None:
        _exigir_texto(self.id_externo_pessoa, "id_externo_pessoa")


@dataclass(frozen=True)
class RegistroNaoReconhecidoComoConclusao:
    """O registro existe na fonte, mas não corresponde a formação concluída."""

    id_externo: str


@dataclass(frozen=True)
class ConclusaoInexistente:
    id_externo: str


class FonteAcademica(Protocol):
    """Fronteira entre o núcleo e uma fonte acadêmica. Ambas as operações podem lançar
    `FonteAcademicaIndisponivel`."""

    codigo: str

    def obter_pessoa(self, id_externo: str) -> PessoaEncontrada | PessoaInexistente: ...

    def obter_conclusao(
        self, id_externo: str
    ) -> ConclusaoEncontrada | RegistroNaoReconhecidoComoConclusao | ConclusaoInexistente: ...

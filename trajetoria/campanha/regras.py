"""Vocabulário de rejeição de Campanha (contracts/operacoes.md, "Rejeição").

Separado de `operacoes.py` para que consultas e testes importem `Motivo` sem importar as
operações. Mesmo padrão de `trajetoria/instrumento/regras.py`.
"""

from dataclasses import dataclass
from enum import Enum


class Motivo(Enum):
    NOME_VAZIO = "nome_vazio"  # FR-002 a
    CAMPANHA_JA_ABERTA = "campanha_ja_aberta"  # FR-043, FR-044
    PERIODO_INCOMPLETO = "periodo_incompleto"  # FR-012
    PERIODO_INVERTIDO = "periodo_invertido"  # FR-012
    ANO_INVALIDO = "ano_invalido"  # FR-023 a
    ANOS_INVERTIDOS = "anos_invertidos"  # FR-023 b
    CONJUNTO_VAZIO = "conjunto_vazio"  # FR-023 c
    VALOR_VAZIO = "valor_vazio"  # FR-023 d
    VERSAO_NAO_PUBLICADA = "versao_nao_publicada"  # FR-009, FR-036 a
    PERIODO_NAO_DEFINIDO = "periodo_nao_definido"  # FR-036 b
    FORA_DO_PERIODO = "fora_do_periodo"  # FR-036 d
    CAMPANHA_NUNCA_ABERTA = "campanha_nunca_aberta"  # FR-040
    ANTES_DA_ABERTURA = "antes_da_abertura"  # FR-057: encerrar com agora < aberta_em


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None
    detalhe: str


class CampanhaRejeitada(Exception):
    """Operação rejeitada; nada foi gravado (FR-057)."""

    def __init__(self, violacoes):
        violacoes = tuple(violacoes)
        if not violacoes:
            raise ValueError("CampanhaRejeitada exige ao menos uma violação")
        self.violacoes = violacoes
        super().__init__(str(self))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)

    def __str__(self) -> str:
        return "; ".join(
            f"{v.motivo.name} ({v.campo or '—'}): {v.detalhe}" for v in self.violacoes
        )

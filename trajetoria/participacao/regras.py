"""Vocabulário de rejeição de Participação e Resposta (contracts/operacoes.md, "Rejeição").

Separado de `operacoes.py` para que consultas e testes importem `Motivo` sem importar as
operações. Mesmo padrão de `trajetoria/campanha/regras.py`.

O `detalhe` cita motivo, campo e UUIDs técnicos; nunca texto, inteiro ou complemento
declarados, nem atributos da Conclusão (FR-059).
"""

from dataclasses import dataclass
from enum import Enum


class Motivo(Enum):
    COLETA_NAO_ADMITIDA = "coleta_nao_admitida"  # FR-052 a
    CONCLUSAO_NAO_ELEGIVEL = "conclusao_nao_elegivel"  # FR-052 b
    PARTICIPACAO_INEXISTENTE = "participacao_inexistente"  # FR-052 c
    PERGUNTA_DE_OUTRA_VERSAO = "pergunta_de_outra_versao"  # FR-052 d
    OPCAO_DE_OUTRA_PERGUNTA = "opcao_de_outra_pergunta"  # FR-052 e (inclui outra Versão)
    VALOR_INCOMPATIVEL = "valor_incompativel"  # FR-052 f
    ESCALA_FORA_DOS_LIMITES = "escala_fora_dos_limites"  # FR-052 g
    COMPLEMENTO_NAO_ADMITIDO = "complemento_nao_admitido"  # FR-052 h
    VALOR_VAZIO = "valor_vazio"  # FR-052 i: ausente, vazio ou só espaços


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None
    detalhe: str


class ParticipacaoRejeitada(Exception):
    """Operação rejeitada; nada foi gravado (FR-051)."""

    def __init__(self, violacoes):
        violacoes = tuple(violacoes)
        if not violacoes:
            raise ValueError("ParticipacaoRejeitada exige ao menos uma violação")
        self.violacoes = violacoes
        super().__init__(str(self))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)

    def __str__(self) -> str:
        return "; ".join(f"{v.motivo.name} ({v.campo or '—'}): {v.detalhe}" for v in self.violacoes)

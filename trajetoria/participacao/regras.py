"""Vocabulário de rejeição de Participação e Resposta (005 contracts/operacoes.md,
"Rejeição"; 006 contracts/conclusao.md, "Motivos novos").

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
    # Feature 006 — jornada e conclusão.
    PARTICIPACAO_CONCLUIDA = "participacao_concluida"  # 006 FR-038: escrita após concluir
    ESTRUTURA_NAO_SUPORTADA = "estrutura_nao_suportada"  # 006 FR-016: 2+ regras numa Seção
    OBRIGATORIA_PENDENTE = "obrigatoria_pendente"  # 006 FR-019, FR-037: na Seção atual


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None
    detalhe: str


def coleta_nao_admitida() -> Violacao:
    """A violação de coleta, montada num só lugar para início, escritas, conclusão e consulta
    da jornada (004 FR-053; 005 FR-039; 006 FR-034 b)."""
    return Violacao(Motivo.COLETA_NAO_ADMITIDA, "campanha", "a Campanha não está em coleta")


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

"""Vocabulário de recusa da captura (contracts/operacoes.md, "Vocabulário").

Separado de `operacoes.py` para que consultas e testes importem `Motivo` sem importar as
operações. Mesmo padrão de `trajetoria/campanha/regras.py`.

Nada é gravado quando qualquer uma das duas exceções é levantada. As mensagens citam motivo,
identificadores técnicos e contagens, nunca valores acadêmicos nem Respostas (spec FR-124).
"""

from enum import Enum
from uuid import UUID


class Motivo(Enum):
    CAMPANHA_NUNCA_ABERTA = "campanha_nunca_aberta"  # spec FR-012
    COLETA_NAO_ENCERRADA = "coleta_nao_encerrada"  # spec FR-011


_TEXTO = {
    Motivo.CAMPANHA_NUNCA_ABERTA: "a Campanha nunca entrou em coleta",
    Motivo.COLETA_NAO_ENCERRADA: "a coleta ainda não terminou",
}


class SnapshotRecusado(Exception):
    """Recusa de domínio: a Campanha não pode ser capturada agora (spec FR-010 a FR-014)."""

    def __init__(self, motivo: Motivo, campanha_id: UUID):
        self.motivo = motivo
        self.campanha_id = campanha_id
        super().__init__(f"{motivo.name}: {_TEXTO[motivo]} (Campanha {campanha_id})")


class CapturaInconsistente(Exception):
    """Falha de integridade da captura (spec FR-053 b a f). Não é decisão de domínio e não
    gera estado de validação: a transação é desfeita e a captura pode ser repetida."""

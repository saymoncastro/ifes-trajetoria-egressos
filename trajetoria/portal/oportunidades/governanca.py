"""Competência de curadoria de oportunidades (025 FR-025, FR-026; research R2).

A regra fica na camada, e não em `trajetoria/governanca/regras.py`: o núcleo não pode
conhecer competências da camada, e o conjunto de regras do núcleo é congelado por teste
(plan, Complexity Tracking). É construída só com primitivas da 010 e mantém a convenção de
uma regra nomeada por ação (010 FR-034).

Hipóteses de demonstração: CPAEG institucional (DP-2501); público independente da unidade
responsável (DP-2502).
"""

from trajetoria.governanca.models import Papel
from trajetoria.governanca.regras import escopo_de_acompanhamento


def pode_curar_oportunidades(vinculos) -> bool:
    """CPAEG ou CSAEG ativo (FR-025). Nenhum outro papel ou perfil técnico."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def escopo_de_curadoria(vinculos):
    """Mesma semântica do acompanhamento: CPAEG vence e é institucional; as CSAEG somam
    unidades."""
    return escopo_de_acompanhamento(vinculos)


def administra(escopo, unidade_responsavel: str) -> bool:
    """A administração é da unidade responsável (FR-026). "" (Ifes) só no institucional."""
    if escopo is None:
        return False
    if escopo.institucional:
        return True
    return unidade_responsavel != "" and unidade_responsavel in escopo.unidades

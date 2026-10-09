"""Quem recebe as contribuições (026 FR-009, FR-010; plan R7).

A regra fica na camada, como a curadoria da 025: o núcleo não conhece competências da camada.
Hipóteses de demonstração: CSAEG da unidade da formação de referência; CPAEG vê todas
(DP-2501). Quem recebe na operação real é a D4.
"""

from trajetoria.governanca.models import Papel
from trajetoria.governanca.regras import escopo_de_acompanhamento


def pode_receber_contribuicoes(vinculos) -> bool:
    """CPAEG ou CSAEG ativo. Nenhum outro papel ou perfil técnico."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def escopo_de_recebimento(vinculos):
    """Mesma semântica do acompanhamento: CPAEG vence e é institucional; as CSAEG somam
    unidades."""
    return escopo_de_acompanhamento(vinculos)


def recebe(escopo, unidade: str) -> bool:
    """A unidade copiada da formação decide. "" (sem unidade registrada) só no
    institucional."""
    if escopo is None:
        return False
    if escopo.institucional:
        return True
    return unidade != "" and unidade in escopo.unidades

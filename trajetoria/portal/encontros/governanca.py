"""Moderação de encontros (031 FR-015, FR-016; research R8; H-3102).

Na camada, como a curadoria da 025 e o recebimento da 026: o núcleo não conhece competências
da camada. Hipótese da demonstração, e não competência institucional aprovada (D8):

- a CSAEG da unidade modera quando o critério de unidades do público tem exatamente uma;
- a CPAEG modera todos os demais e também pode agir nos de unidade única (clarify 2).
"""

from trajetoria.governanca.models import Papel
from trajetoria.governanca.regras import escopo_de_acompanhamento

INSTITUCIONAL = "institucional"


def pode_moderar_encontros(vinculos) -> bool:
    """CPAEG ou CSAEG ativo. Nenhum outro papel ou perfil técnico."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def escopo_de_moderacao(vinculos):
    """Mesma semântica do acompanhamento: CPAEG prevalece e é institucional."""
    return escopo_de_acompanhamento(vinculos)


def responsavel(publico_unidades) -> str:
    """A unidade, quando o público tem exatamente uma; senão, "institucional" (FR-016)."""
    if publico_unidades is not None and len(publico_unidades) == 1:
        return publico_unidades[0]
    return INSTITUCIONAL


def modera(escopo, encontro) -> bool:
    if escopo is None:
        return False
    if escopo.institucional:
        return True
    return responsavel(encontro.publico_unidades) in escopo.unidades


def escopo_da_decisao(escopo, encontro) -> str:
    """O que vai para `publicado_por_escopo`: quem efetivamente decidiu (analyze F1). A CSAEG
    só modera encontros de unidade única, e decide por aquela unidade."""
    return INSTITUCIONAL if escopo.institucional else responsavel(encontro.publico_unidades)

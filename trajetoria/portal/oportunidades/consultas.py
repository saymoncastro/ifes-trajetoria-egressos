"""Leituras da Oportunidade (025; data-model.md, "Leituras"; research R8). Nada grava."""

from datetime import date

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.portal.models import Oportunidade
from trajetoria.portal.oportunidades.pertinencia import pertinentes


def em_divulgacao(hoje: date):
    """Publicada, não retirada e com hoje no período, inclusive nas pontas (FR-012)."""
    return Oportunidade.objects.filter(
        publicada_em__isnull=False, retirada_em__isnull=True, inicio__lte=hoje, fim__gte=hoje
    )


def itens_da_pessoa(pessoa, hoje: date):
    """A mesma lista para a página e para o Início (FR-021): Conclusões na ordem da 007."""
    return pertinentes(em_divulgacao(hoje), pessoa.conclusoes.all())


def da_curadoria(escopo):
    """Tudo no institucional; só a unidade responsável no escopo da CSAEG (FR-027)."""
    if escopo.institucional:
        return Oportunidade.objects.all()
    return Oportunidade.objects.filter(unidade_responsavel__in=sorted(escopo.unidades))


def opcoes_de_publico() -> dict[str, list[str]]:
    """Valores registrados nas Conclusões, como escritos: grafias diferentes são opções
    diferentes (FR-007; DP-1005; DP-2507). Não usa a abrangência das Campanhas (ADR 0004).

    Uma só consulta (combinações distintas), repartida em Python: o formulário a usa para o
    público e para as unidades responsáveis."""
    cursos, niveis, unidades = set(), set(), set()
    for curso, nivel, unidade in (
        ConclusaoAcademica.objects.values_list("curso", "nivel", "unidade").distinct()
    ):
        cursos.add(curso)
        niveis.add(nivel)
        unidades.add(unidade)
    return {
        "publico_unidades": sorted(unidades - {None}),
        "publico_niveis": sorted(niveis - {None}),
        "publico_cursos": sorted(cursos - {None}),
    }


def unidades_responsaveis(escopo, unidades_registradas: list[str]) -> list[str]:
    """CPAEG: "" (Ifes) e as unidades registradas. CSAEG: as unidades do escopo."""
    if escopo.institucional:
        return ["", *unidades_registradas]
    return sorted(escopo.unidades)

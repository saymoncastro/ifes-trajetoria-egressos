"""Vínculos ativos de um operador já identificado (contracts/governanca.md)."""

from trajetoria.governanca.models import VinculoDeGovernanca


def vinculos_ativos(identificador: str | None) -> list[VinculoDeGovernanca]:
    """Vínculos ativos do operador, em ordem de papel e unidade. Sem identificador, `[]`
    sem consultar o banco. O identificador é opaco: não é normalizado nem interpretado."""
    if not identificador:
        return []
    return list(
        VinculoDeGovernanca.objects.filter(
            identificador_operador=identificador, ativo=True
        ).order_by("papel", "unidade")
    )

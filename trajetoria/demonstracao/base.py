"""Predicado único para as fronteiras de demonstração (018 R11)."""

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada


def base_somente_simulada():
    return not (
        Pessoa.objects.exclude(fonte=FonteSimulada.codigo).exists()
        or ConclusaoAcademica.objects.exclude(fonte=FonteSimulada.codigo).exists()
    )

"""Predicado único para as fronteiras de demonstração (018 R11)."""

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.acervo_historico import CODIGO as ACERVO_HISTORICO
from trajetoria.fonte_academica.simulada import FonteSimulada

# 019 FR-131: além da simulada, só o acervo histórico fictício registrado na demonstração.
_FONTES_ADMITIDAS = (FonteSimulada.codigo, ACERVO_HISTORICO)


def base_somente_simulada():
    return not (
        Pessoa.objects.exclude(fonte__in=_FONTES_ADMITIDAS).exists()
        or ConclusaoAcademica.objects.exclude(fonte__in=_FONTES_ADMITIDAS).exists()
    )

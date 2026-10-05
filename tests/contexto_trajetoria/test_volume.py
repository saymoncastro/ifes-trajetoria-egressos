"""Deduplicação dos agregados (021 SC-008): N Pessoas do mesmo recorte → um registro por
métrica e apuração."""

import pytest

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.contexto_trajetoria.carga import carregar_contexto
from trajetoria.contexto_trajetoria.models import ContextoInstitucionalAgregado
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contexto_da_trajetoria import ContextoDaTrajetoriaNaFonte
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado

pytestmark = pytest.mark.django_db


class MesmoRecorte:
    """Responde os agregados de TADS · Serra · 2022 para qualquer conclusão pedida."""

    codigo = "simulada"

    def obter_contexto(self, ids):
        agregados = ContextoSimulado().obter_contexto(("SIM-C-0001",)).agregados
        return ContextoDaTrajetoriaNaFonte((), agregados)


def _carregar(n):
    for i in range(n):
        pessoa = Pessoa.objects.create(fonte="simulada", id_externo=f"VOL-P-{i}")
        ConclusaoAcademica.objects.create(
            pessoa=pessoa, fonte="simulada", id_externo=f"VOL-C-{i}", curso=cenarios.TADS,
            unidade="Serra", ano_conclusao=2022,
        )
        carregar_contexto(MesmoRecorte(), pessoa)
    return ContextoInstitucionalAgregado.objects.count()


def test_vinte_pessoas_dois_registros():
    assert _carregar(20) == 2


@pytest.mark.volume
def test_quinhentas_pessoas_dois_registros():
    assert _carregar(500) == 2

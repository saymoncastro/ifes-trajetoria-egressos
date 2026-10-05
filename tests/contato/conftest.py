from datetime import UTC, datetime, timedelta

import pytest

from trajetoria.academico.models import Pessoa
from trajetoria.contato.models import ContatoDaPessoa, Origem

T0 = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


@pytest.fixture
def pessoa(db):
    return Pessoa.objects.create(fonte="simulada", id_externo="TESTE-P-1")


def contato(pessoa, valor, origem=Origem.FONTE_ACADEMICA, *, em=T0, posicao=0, fonte="simulada"):
    if origem == Origem.EGRESSO:
        fonte = posicao = None
    return ContatoDaPessoa.objects.create(
        pessoa=pessoa, valor=valor, origem=origem, fonte=fonte, posicao=posicao, obtido_em=em
    )


def depois(minutos):
    return T0 + timedelta(minutes=minutos)

"""Política de escolha do contato (020 FR-008; T008)."""

import pytest

from tests.contato.conftest import T0, contato, depois
from trajetoria.contato.models import ContatoDaPessoa, Origem
from trajetoria.contato.politica import contato_utilizavel

pytestmark = pytest.mark.django_db


def test_sem_registros(pessoa):
    assert contato_utilizavel(pessoa.pk, depois(1)) is None


def test_egresso_mais_recente_vence_importado(pessoa):
    contato(pessoa, "fonte@example.invalid", em=depois(10))
    antigo = contato(pessoa, "velho@example.invalid", Origem.EGRESSO, em=T0)
    novo = contato(pessoa, "novo@example.invalid", Origem.EGRESSO, em=depois(5))
    assert contato_utilizavel(pessoa.pk, depois(20)) == novo
    assert contato_utilizavel(pessoa.pk, depois(1)) == antigo


def test_observacao_mais_recente_e_menor_posicao(pessoa):
    contato(pessoa, "a@example.invalid", em=T0, posicao=0)
    segunda_b = contato(pessoa, "b@example.invalid", em=depois(5), posicao=0)
    contato(pessoa, "a@example.invalid", em=depois(5), posicao=1)
    assert contato_utilizavel(pessoa.pk, depois(6)) == segunda_b


def test_invalido_e_pulado_na_mesma_ordem(pessoa):
    ContatoDaPessoa.objects.create(
        pessoa=pessoa, valor="invalido", origem=Origem.FONTE_ACADEMICA, fonte="simulada",
        posicao=0, obtido_em=T0,
    )
    valido = contato(pessoa, "ok@example.invalid", em=T0, posicao=1)
    assert contato_utilizavel(pessoa.pk, depois(1)) == valido
    ContatoDaPessoa.objects.create(
        pessoa=pessoa, valor="tambem invalido", origem=Origem.EGRESSO, obtido_em=depois(2)
    )
    assert contato_utilizavel(pessoa.pk, depois(3)) == valido


def test_instante_ignora_registros_posteriores(pessoa):
    contato(pessoa, "futuro@example.invalid", Origem.EGRESSO, em=depois(30))
    assert contato_utilizavel(pessoa.pk, depois(1)) is None

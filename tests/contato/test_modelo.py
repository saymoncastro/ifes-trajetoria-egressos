"""ContatoDaPessoa (020 data-model §1; T007)."""

import pytest
from django.db import IntegrityError, transaction

from tests.contato.conftest import T0, contato
from trajetoria.academico.models import Pessoa
from trajetoria.contato.models import ContatoDaPessoa, Origem

pytestmark = pytest.mark.django_db


def _recusa(**campos):
    with pytest.raises(IntegrityError), transaction.atomic():
        ContatoDaPessoa.objects.create(obtido_em=T0, **campos)


def test_proveniencia_coerente(pessoa):
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.FONTE_ACADEMICA)
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.FONTE_ACADEMICA,
            fonte="simulada")
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.EGRESSO, fonte="simulada")
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.EGRESSO, posicao=0)
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem="OUTRA")
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.EGRESSO, canal="TELEFONE")


def test_textos_nao_vazios(pessoa):
    _recusa(pessoa=pessoa, valor="", origem=Origem.EGRESSO)
    _recusa(pessoa=pessoa, valor="a@example.invalid", origem=Origem.FONTE_ACADEMICA, fonte="",
            posicao=0)


def test_observacao_unica_por_posicao(pessoa):
    contato(pessoa, "a@example.invalid")
    with pytest.raises(IntegrityError), transaction.atomic():
        contato(pessoa, "b@example.invalid")
    # O egresso pode informar o mesmo valor em momentos diferentes (fatos distintos).
    contato(pessoa, "a@example.invalid", Origem.EGRESSO)
    contato(pessoa, "a@example.invalid", Origem.EGRESSO)


def test_pessoa_nao_ganha_campo_nem_relacao():
    assert {f.name for f in Pessoa._meta.fields} == {
        "id", "fonte", "id_externo", "nome", "incorporado_em",
    }
    reversas = {r.get_accessor_name() for r in Pessoa._meta.related_objects}
    assert not [n for n in reversas if n and "contato" in n.lower()]


def test_representacao_sem_endereco(pessoa):
    registro = contato(pessoa, "marcador-unico@example.invalid")
    assert "marcador-unico" not in str(registro) + repr(registro)

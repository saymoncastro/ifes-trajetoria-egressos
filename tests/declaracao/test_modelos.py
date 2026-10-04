from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from tests.declaracao.construcao import declaracao_concluida, validar
from tests.participacao import construcao as c
from trajetoria.declaracao.models import FormacaoDeclarada, ReferenciaDeAcervo

pytestmark = pytest.mark.django_db


@pytest.fixture
def formacao():
    return declaracao_concluida(c.campanha_aberta(c.instrumento().versao))


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("nome", ""),
        ("unidade", ""),
        ("curso", ""),
        ("nivel", ""),
        ("identificador_cpf", "a" * 63),
        ("verificador", "x" * 64),
    ],
)
def test_check_declaracao(formacao, campo, valor):
    with pytest.raises(IntegrityError), transaction.atomic():
        FormacaoDeclarada.objects.filter(pk=formacao.pk).update(**{campo: valor})


@pytest.mark.parametrize(
    "resultado,conclusao,fora,conflito",
    [
        ("CONFIRMADA", False, False, False),
        ("NAO_CONFIRMADA", True, False, False),
        ("NAO_CONFIRMADA", False, True, False),
        ("NAO_CONFIRMADA", False, False, True),
        ("CONFIRMADA", True, True, True),
        ("outra", False, False, False),
    ],
)
def test_check_decisao(formacao, resultado, conclusao, fora, conflito):
    x = c.conclusao() if conclusao else None
    with pytest.raises(IntegrityError), transaction.atomic():
        validar(formacao, x, resultado, fora, conflito)


def test_decisao_unica(formacao):
    validar(formacao, resultado="NAO_CONFIRMADA")
    with pytest.raises(IntegrityError), transaction.atomic():
        validar(formacao, resultado="NAO_CONFIRMADA")


def test_criacao_unica(formacao):
    formacao.pk = uuid4()
    with pytest.raises(IntegrityError), transaction.atomic():
        formacao.save(force_insert=True)


@pytest.mark.parametrize(
    "campos",
    [
        dict(modalidade=""),
        dict(forma_oferta=""),
        dict(data_conclusao="2003-01-01"),
        dict(unidade=""),
        dict(referencia=""),
    ],
)
def test_check_acervo(campos):
    with pytest.raises(IntegrityError), transaction.atomic():
        ReferenciaDeAcervo.objects.create(
            **(
                dict(
                    unidade="Serra",
                    referencia="Livro 1",
                    nivel="Técnico",
                    curso="Informática",
                    ano_conclusao=2004,
                    operador="A",
                    registrada_em=c.NO_PERIODO,
                )
                | campos
            )
        )

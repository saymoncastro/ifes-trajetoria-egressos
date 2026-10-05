"""Restrições dos models da P2 (021 data-model §2)."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction

from tests.participacao import construcao as c
from trajetoria.contexto_trajetoria.models import (
    ComplementoDaConclusao,
    ContextoInstitucionalAgregado,
    MetricaDoAgregado,
)

pytestmark = pytest.mark.django_db
APURACAO = date(2026, 1, 31)


def _falha(**campos):
    with pytest.raises(IntegrityError), transaction.atomic():
        ContextoInstitucionalAgregado.objects.create(**campos)


def _agregado(**campos):
    base = dict(fonte="simulada", metrica=MetricaDoAgregado.CONCLUSOES_CURSO_UNIDADE_ANO,
                curso="TADS", unidade="Serra", ano=2022, valor=27, apurado_em=APURACAO)
    return base | campos


def test_complemento_um_por_conclusao():
    conclusao = c.conclusao()
    ComplementoDaConclusao.objects.create(conclusao=conclusao, ano_ingresso=2019)
    with pytest.raises(IntegrityError), transaction.atomic():
        ComplementoDaConclusao.objects.create(conclusao=conclusao, ano_ingresso=2018)


def test_complemento_ano_coerente_com_data():
    with pytest.raises(IntegrityError), transaction.atomic():
        ComplementoDaConclusao.objects.create(
            conclusao=c.conclusao(), ano_ingresso=2019, data_ingresso=date(2018, 3, 1)
        )
    ComplementoDaConclusao.objects.create(
        conclusao=c.conclusao(), ano_ingresso=2019, data_ingresso=date(2019, 3, 1)
    )


def test_complemento_exige_ano():
    with pytest.raises(IntegrityError), transaction.atomic():
        ComplementoDaConclusao.objects.create(conclusao=c.conclusao(), ano_ingresso=None)


def test_chave_unica_inclusive_com_curso_nulo():
    unidade = dict(metrica=MetricaDoAgregado.CONCLUSOES_UNIDADE_ANO, curso=None, valor=812)
    ContextoInstitucionalAgregado.objects.create(**_agregado(**unidade))
    _falha(**_agregado(**unidade | {"valor": 813}))
    ContextoInstitucionalAgregado.objects.create(**_agregado())
    _falha(**_agregado(valor=28))
    # Nova apuração é um registro novo.
    ContextoInstitucionalAgregado.objects.create(**_agregado(apurado_em=date(2027, 1, 31)))


def test_curso_conforme_a_metrica():
    _falha(**_agregado(curso=None))
    _falha(**_agregado(metrica=MetricaDoAgregado.CONCLUSOES_UNIDADE_ANO))


@pytest.mark.parametrize("campo", ["fonte", "curso", "unidade"])
def test_textos_nao_vazios(campo):
    _falha(**_agregado(**{campo: ""}))


def test_valor_nao_negativo():
    _falha(**_agregado(valor=-1))

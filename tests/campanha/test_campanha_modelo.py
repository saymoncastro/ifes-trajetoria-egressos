"""Restrições do banco de `Campanha` (data-model.md), por escrita direta no ORM, fora das
operações."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from tests.campanha.construcao import momento
from trajetoria.campanha.models import Campanha

pytestmark = pytest.mark.django_db

INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)
ARRAYS = ("unidades", "niveis", "modalidades", "formas_oferta")


def _cria(versao, **campos):
    with transaction.atomic():
        return Campanha.objects.create(**{"nome": "Campanha", "versao": versao, **campos})


def _rejeita(versao, **campos):
    with pytest.raises(IntegrityError):
        _cria(versao, **campos)


def test_nome_vazio(versao_publicada):
    _rejeita(versao_publicada, nome="")


@pytest.mark.parametrize("periodo", [(INICIO, None), (None, FIM)])
def test_periodo_com_uma_so_data(versao_publicada, periodo):
    _rejeita(versao_publicada, inicio=periodo[0], fim=periodo[1])


def test_periodo_invertido(versao_publicada):
    _rejeita(versao_publicada, inicio=FIM, fim=INICIO)


def test_periodo_de_um_dia_e_sem_periodo(versao_publicada):
    _cria(versao_publicada, inicio=INICIO, fim=INICIO)
    _cria(versao_publicada)


def test_anos_invertidos(versao_publicada):
    _rejeita(versao_publicada, ano_minimo=2025, ano_maximo=2020)
    _cria(versao_publicada, ano_minimo=2020, ano_maximo=2020)
    _cria(versao_publicada, ano_minimo=2020)


@pytest.mark.parametrize("campo", ARRAYS)
def test_array_vazio_ou_com_cadeia_vazia(versao_publicada, campo):
    _rejeita(versao_publicada, **{campo: []})
    _rejeita(versao_publicada, **{campo: [""]})
    _rejeita(versao_publicada, **{campo: ["Serra", ""]})


@pytest.mark.parametrize("campo", ARRAYS)
def test_array_nulo_ou_com_valores(versao_publicada, campo):
    assert getattr(_cria(versao_publicada, **{campo: None}), campo) is None
    assert getattr(_cria(versao_publicada, **{campo: ["Serra"]}), campo) == ["Serra"]


def test_aberta_exige_periodo(versao_publicada):
    _rejeita(versao_publicada, aberta_em=momento(2027, 4, 1))


def test_encerrada_exige_aberta(versao_publicada):
    _rejeita(versao_publicada, inicio=INICIO, fim=FIM, encerrada_em=momento(2027, 5, 1))


def test_encerrada_depois_da_abertura(versao_publicada):
    _rejeita(
        versao_publicada,
        inicio=INICIO,
        fim=FIM,
        aberta_em=momento(2027, 5, 1),
        encerrada_em=momento(2027, 4, 15),
    )
    _cria(
        versao_publicada,
        inicio=INICIO,
        fim=FIM,
        aberta_em=momento(2027, 4, 1),
        encerrada_em=momento(2027, 4, 15),
    )


def test_versao_referenciada_nao_e_removida(versao_publicada):
    _cria(versao_publicada)
    with pytest.raises(ProtectedError):
        versao_publicada.delete()

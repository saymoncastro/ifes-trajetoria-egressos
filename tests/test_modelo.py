"""Restrições do modelo (data-model.md) e validação do contrato."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.contrato import ConclusaoNaFonte, PessoaEncontrada

pytestmark = pytest.mark.django_db


def _pessoa(**campos):
    return Pessoa.objects.create(**{"fonte": "f", "id_externo": "P1", **campos})


def _conclusao(pessoa, **campos):
    return ConclusaoAcademica.objects.create(
        **{"pessoa": pessoa, "fonte": "f", "id_externo": "C1", **campos}
    )


def _deve_violar(criar):
    with pytest.raises(IntegrityError), transaction.atomic():
        criar()


def test_origem_repetida_viola_unicidade_de_pessoa_e_conclusao():
    pessoa = _pessoa()
    _conclusao(pessoa)
    _deve_violar(lambda: _pessoa())
    _deve_violar(lambda: _conclusao(pessoa))


def test_mesmo_id_externo_em_fontes_diferentes_gera_pessoas_distintas():
    # Unicidade por par (fonte, id_externo); não há fusão entre fontes (FR-034).
    a = _pessoa(fonte="fonte-a", id_externo="X")
    b = _pessoa(fonte="fonte-b", id_externo="X")
    assert a.id != b.id
    assert Pessoa.objects.count() == 2


@pytest.mark.parametrize("campo", ["fonte", "id_externo", "nome"])
def test_cadeia_vazia_proibida_na_pessoa(campo):
    _deve_violar(lambda: _pessoa(**{campo: ""}))


@pytest.mark.parametrize("campo", ["fonte", "id_externo", "curso"])
def test_cadeia_vazia_proibida_na_conclusao(campo):
    pessoa = _pessoa()
    _deve_violar(lambda: _conclusao(pessoa, **{campo: ""}))


@pytest.mark.parametrize("ano", [2019, None])
def test_data_exige_ano_igual_ao_ano_da_data(ano):
    # ano=None cobre o caso em que a comparação daria UNKNOWN (aceito pelo CHECK).
    pessoa = _pessoa()
    _deve_violar(lambda: _conclusao(pessoa, data_conclusao=date(2020, 7, 10), ano_conclusao=ano))


def test_so_ano_e_data_coerente_sao_aceitos():
    pessoa = _pessoa()
    _conclusao(pessoa, id_externo="C1", ano_conclusao=2014)
    _conclusao(pessoa, id_externo="C2", ano_conclusao=2020, data_conclusao=date(2020, 7, 10))
    assert pessoa.conclusoes.count() == 2


def test_pessoa_com_conclusao_nao_pode_ser_excluida():
    pessoa = _pessoa()
    _conclusao(pessoa)
    with pytest.raises(ProtectedError):
        pessoa.delete()


def test_campos_do_modelo_sao_exatamente_os_previstos():
    # Pessoa sem atributos acadêmicos (FR-003) e sem marcador de "mock"; nenhum campo
    # declarado ou derivado: todo atributo acadêmico é institucional (FR-036).
    assert {f.name for f in Pessoa._meta.concrete_fields} == {
        "id", "fonte", "id_externo", "nome", "incorporado_em",
    }
    assert {f.name for f in ConclusaoAcademica._meta.concrete_fields} == {
        "id", "pessoa", "fonte", "id_externo", "curso", "unidade", "nivel", "modalidade",
        "forma_oferta", "ano_conclusao", "data_conclusao", "incorporado_em",
    }


@pytest.mark.parametrize(
    "campos",
    [
        {"curso": ""},
        {"id_externo": ""},
        {"ano_conclusao": 2019, "data_conclusao": date(2020, 7, 10)},
        {"ano_conclusao": None, "data_conclusao": date(2020, 7, 10)},
    ],
)
def test_contrato_rejeita_conclusao_invalida(campos):
    with pytest.raises(ValueError):
        ConclusaoNaFonte(**{"id_externo": "C1", **campos})


def test_contrato_rejeita_nome_vazio():
    with pytest.raises(ValueError):
        PessoaEncontrada("P1", "", ())

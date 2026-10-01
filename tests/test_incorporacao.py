"""Incorporação de Pessoas e Conclusões a partir de uma fonte acadêmica."""

from datetime import date

import pytest

from trajetoria.academico.incorporacao import SituacaoIncorporacao, incorporar_pessoa
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.cenarios import PessoaSimulada, RegistroSimulado
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db


# --- US1: Pessoa com sua Conclusão Acadêmica ---------------------------------------------


def test_cenario_a_incorpora_pessoa_com_uma_conclusao(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0001")

    assert resultado.situacao is SituacaoIncorporacao.INCORPORADA
    assert resultado.pessoa_criada is True
    assert Pessoa.objects.count() == 1
    assert ConclusaoAcademica.objects.count() == 1

    conclusao = resultado.pessoa.conclusoes.get()
    assert conclusao.curso == "Tecnologia em Análise e Desenvolvimento de Sistemas"
    assert conclusao.unidade == "Serra"
    assert conclusao.nivel == "Graduação"
    assert conclusao.modalidade == "Presencial"
    assert conclusao.ano_conclusao == 2022
    assert conclusao.data_conclusao == date(2022, 12, 16)
    # Não informado pela fonte: fica ausente, sem valor padrão (FR-010).
    assert conclusao.forma_oferta is None


def test_conclusao_so_com_ano_nao_fabrica_data(fonte_simulada):
    incorporar_pessoa(fonte_simulada, "SIM-P-0002")

    conclusao = ConclusaoAcademica.objects.get(id_externo="SIM-C-0002")
    assert conclusao.ano_conclusao == 2014
    assert conclusao.data_conclusao is None


# --- US2: uma Pessoa, múltiplas Conclusões -----------------------------------------------


@pytest.mark.parametrize(
    ("id_pessoa", "quantidade"), [("SIM-P-0002", 2), ("SIM-P-0003", 2), ("SIM-P-0004", 3)]
)
def test_pessoa_com_varias_conclusoes_e_uma_unica_pessoa(fonte_simulada, id_pessoa, quantidade):
    resultado = incorporar_pessoa(fonte_simulada, id_pessoa)

    assert Pessoa.objects.count() == 1
    conclusoes = list(resultado.pessoa.conclusoes.all())
    assert len(conclusoes) == quantidade
    assert len({c.id for c in conclusoes}) == quantidade


def test_conclusoes_em_unidades_diferentes(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0003")
    assert {c.unidade for c in resultado.pessoa.conclusoes.all()} == {"Serra", "Cefor"}


def test_conclusoes_em_niveis_diferentes(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0004")
    assert {c.nivel for c in resultado.pessoa.conclusoes.all()} == {
        "Técnico", "Graduação", "Pós-graduação",
    }


def test_homonimos_sao_pessoas_distintas(fonte_simulada):
    # O nome não identifica nem deduplica (FR-005, FR-031).
    a = incorporar_pessoa(fonte_simulada, "SIM-P-0010").pessoa
    b = incorporar_pessoa(fonte_simulada, "SIM-P-0011").pessoa

    assert a.nome == b.nome == "Carla Exemplo"
    assert a.id != b.id
    assert Pessoa.objects.count() == 2


def test_pessoa_sem_nome_e_incorporada(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0009")

    assert resultado.pessoa.nome is None
    assert resultado.pessoa.conclusoes.count() == 1


def test_conclusoes_parecidas_com_origens_distintas_nao_se_fundem():
    # Mesmo curso e unidade, id_externo diferente: duas conclusões (FR-014).
    registros = [
        RegistroSimulado(
            f"SIM-C-T{n}", "SIM-P-T1", "concluida", "Técnico em Informática", "Serra",
            "Técnico", "Presencial", "Subsequente", ano,
        )
        for n, ano in ((1, 2015), (2, 2019))
    ]
    fonte = FonteSimulada(pessoas=[PessoaSimulada("SIM-P-T1", None)], registros=registros)

    resultado = incorporar_pessoa(fonte, "SIM-P-T1")

    assert resultado.pessoa.conclusoes.count() == 2

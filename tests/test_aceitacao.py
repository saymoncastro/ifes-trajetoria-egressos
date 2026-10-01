"""US3: cada conclusão conserva seu contexto, e o consumidor não precisa conhecer a fonte."""

import pytest

from trajetoria.academico.incorporacao import incorporar_pessoa
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica import cenarios

pytestmark = pytest.mark.django_db

ATRIBUTOS = ("curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao")


def test_sc002_tres_conclusoes_cada_uma_com_seu_proprio_contexto(fonte_simulada):
    pessoa = incorporar_pessoa(fonte_simulada, "SIM-P-0004").pessoa

    assert Pessoa.objects.count() == 1
    conclusoes = list(pessoa.conclusoes.all())
    assert len(conclusoes) == 3

    declarados = {r.id_externo: r for r in cenarios.REGISTROS if r.id_pessoa == "SIM-P-0004"}
    for conclusao in conclusoes:
        registro = declarados[conclusao.id_externo]
        assert {a: getattr(conclusao, a) for a in ATRIBUTOS} == {
            a: getattr(registro, a) for a in ATRIBUTOS
        }


def test_contexto_de_uma_conclusao_consultado_isoladamente(fonte_simulada):
    pessoa = incorporar_pessoa(fonte_simulada, "SIM-P-0003").pessoa
    alvo = pessoa.conclusoes.get(unidade="Cefor")

    conclusao = ConclusaoAcademica.objects.get(id=alvo.id)

    assert conclusao.curso == "Especialização em Informática na Educação"
    assert conclusao.pessoa == pessoa


def test_ordem_das_conclusoes_e_deterministica(fonte_simulada):
    # Ordem só de apresentação (FR-017): por ano, depois pela identidade interna.
    pessoa = incorporar_pessoa(fonte_simulada, "SIM-P-0004").pessoa

    conclusoes = list(pessoa.conclusoes.all())
    assert [c.ano_conclusao for c in conclusoes] == [2012, 2017, 2020]
    assert conclusoes == sorted(conclusoes, key=lambda c: (c.ano_conclusao, c.id))


def descrever_trajetoria(pessoa: Pessoa) -> list[str]:
    """Consumidor de demonstração (SC-008): recebe só a Pessoa e usa só os modelos."""
    return [
        " — ".join([c.curso, c.unidade, c.nivel, c.modalidade, str(c.ano_conclusao)])
        for c in pessoa.conclusoes.all()
    ]


def test_sc008_experiencia_esperada(fonte_simulada):
    pessoa = incorporar_pessoa(fonte_simulada, "SIM-P-0003").pessoa

    assert descrever_trajetoria(pessoa) == [
        "Tecnologia em Análise e Desenvolvimento de Sistemas — Serra — Graduação — "
        "Presencial — 2022",
        "Especialização em Informática na Educação — Cefor — Pós-graduação — A distância — 2025",
    ]

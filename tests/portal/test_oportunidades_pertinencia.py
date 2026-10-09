"""Pertinência e explicação (025 FR-012 a FR-016; contracts/pertinencia.md; T017–T019).

Funções puras: Oportunidades não gravadas e Conclusões em memória, sem banco.
"""

import itertools
import re
import uuid
from datetime import date
from types import SimpleNamespace

import pytest

from trajetoria.portal.models import Oportunidade
from trajetoria.portal.oportunidades.pertinencia import (
    FORMACAO,
    TODOS,
    explicacao,
    pertinentes,
)

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
REDES = "Tecnologia em Redes de Computadores"


def _c(curso, unidade, nivel, ano):
    return SimpleNamespace(curso=curso, unidade=unidade, nivel=nivel, ano_conclusao=ano)


ANA = (_c(TADS, "Serra", "Graduação", 2022),)
MARIA = (_c(TADS, "Serra", "Graduação", 2022),
         _c("Especialização em Informática na Educação", "Cefor", "Pós-graduação", 2025))
BRUNO = (_c("Técnico em Edificações", "Vitória", "Técnico", 2014),
         _c("Bacharelado em Engenharia Civil", "Vitória", "Graduação", 2020))
DIEGO = (_c("Técnico em Química", "Vila Velha", "Técnico", 2012),
         _c("Licenciatura em Química", "Vila Velha", "Graduação", 2017),
         _c("Mestrado Profissional em Química", "Vila Velha", "Pós-graduação", 2020))
CARLA_REDES = (_c(REDES, "Serra", "Graduação", 2023),)


def _o(titulo="Oportunidade", *, cursos=None, niveis=None, unidades=None, inicio=date(2026, 10, 1),
       unidade_responsavel="Serra", endereco="https://oportunidades.example/x"):
    return Oportunidade(
        id=uuid.uuid5(uuid.NAMESPACE_URL, titulo), titulo=titulo, resumo="r", categoria="cursos",
        unidade_responsavel=unidade_responsavel, endereco=endereco, inicio=inicio,
        fim=date(2026, 12, 1), publico_cursos=cursos, publico_niveis=niveis,
        publico_unidades=unidades,
    )


def _titulos(itens):
    return [i.oportunidade.titulo for i in itens]


# --- Regra (FR-012; T017) ----------------------------------------------------------------


def test_sem_conclusao_nada():
    assert pertinentes([_o()], ()) == []


def test_sem_publico_vai_para_todos():
    (item,) = pertinentes([_o()], ANA)
    assert item.grupo == TODOS and item.explicacao == "Aberta a todos os egressos do Ifes."


@pytest.mark.parametrize(
    "criterios, conclusoes, aparece",
    [
        ({"cursos": [REDES]}, CARLA_REDES, True),
        ({"cursos": [REDES]}, ANA, False),
        ({"niveis": ["Pós-graduação"]}, MARIA, True),
        ({"niveis": ["Pós-graduação"]}, BRUNO, False),
        ({"unidades": ["Vitória"]}, BRUNO, True),
        ({"unidades": ["Vitória"]}, ANA, False),
        ({"niveis": ["Técnico"], "unidades": ["Vila Velha"]}, DIEGO, True),
    ],
)
def test_cada_criterio(criterios, conclusoes, aparece):
    assert bool(pertinentes([_o(**criterios)], conclusoes)) is aparece


def test_criterios_nunca_combinam_formacoes_diferentes():
    """Maria tem Pós-graduação (Cefor) e Graduação na Serra; nenhuma formação é as duas
    coisas (O5 do catálogo)."""
    assert pertinentes([_o(niveis=["Pós-graduação"], unidades=["Serra"])], MARIA) == []


def test_varias_formacoes_aparece_uma_vez_e_cita_todas_na_ordem():
    (item,) = pertinentes([_o(unidades=["Vitória"])], BRUNO)
    assert item.formacoes == BRUNO
    assert item.explicacao == (
        "Aparece porque você concluiu Técnico em Edificações na unidade Vitória (2014) e "
        "Bacharelado em Engenharia Civil na unidade Vitória (2020)."
    )


def test_valor_ausente_nao_satisfaz():
    sem_nivel = (_c(TADS, "Serra", None, 2022),)
    assert pertinentes([_o(niveis=["Graduação"])], sem_nivel) == []


@pytest.mark.parametrize("valor", [TADS.lower(), f" {TADS}", f"{TADS} ", "TADS"])
def test_igualdade_exata(valor):
    assert pertinentes([_o(cursos=[valor])], ANA) == []


def test_duas_grafias_so_com_as_duas_marcadas():
    """A fonte real pode ter grafias divergentes (DP-1005; DP-2507). A demonstração não tem;
    aqui são Conclusões de teste."""
    grafia_a = (_c(TADS, "Serra", "Graduação", 2022),)
    grafia_b = (_c("Análise e Desenvolvimento de Sistemas", "Serra", "Graduação", 2022),)
    so_uma = _o(cursos=[TADS])
    as_duas = _o("as duas", cursos=[TADS, "Análise e Desenvolvimento de Sistemas"])
    assert pertinentes([so_uma], grafia_b) == []
    assert pertinentes([as_duas], grafia_a) and pertinentes([as_duas], grafia_b)


def test_ordem_e_determinismo():
    catalogo = [
        _o("todos-antigo", inicio=date(2026, 9, 1)),
        _o("B formação", unidades=["Vitória"], inicio=date(2026, 10, 3)),
        _o("A formação", unidades=["Vitória"], inicio=date(2026, 10, 3)),
        _o("formação recente", unidades=["Vitória"], inicio=date(2026, 10, 6)),
        _o("todos-recente", inicio=date(2026, 10, 5)),
    ]
    esperado = ["formação recente", "A formação", "B formação", "todos-recente", "todos-antigo"]
    assert _titulos(pertinentes(catalogo, BRUNO)) == esperado
    assert _titulos(pertinentes(list(reversed(catalogo)), BRUNO)) == esperado
    grupos = [i.grupo for i in pertinentes(catalogo, BRUNO)]
    assert grupos == [FORMACAO] * 3 + [TODOS] * 2


# --- Explicação (FR-013; P-EXPL; T018) ---------------------------------------------------

_SETE = [
    ({"cursos": [REDES]}, CARLA_REDES,
     "Aparece porque você concluiu Tecnologia em Redes de Computadores (Serra, 2023)."),
    ({"niveis": ["Pós-graduação"]}, DIEGO[2:],
     "Aparece porque você concluiu Mestrado Profissional em Química, formação de "
     "Pós-graduação (Vila Velha, 2020)."),
    ({"unidades": ["Vitória"]}, BRUNO[:1],
     "Aparece porque você concluiu Técnico em Edificações na unidade Vitória (2014)."),
    ({"cursos": [TADS], "niveis": ["Graduação"]}, ANA,
     "Aparece porque você concluiu Tecnologia em Análise e Desenvolvimento de Sistemas, "
     "formação de Graduação (Serra, 2022)."),
    ({"cursos": [REDES], "unidades": ["Serra"]}, CARLA_REDES,
     "Aparece porque você concluiu Tecnologia em Redes de Computadores na unidade Serra "
     "(2023)."),
    ({"cursos": ["Técnico em Química"], "niveis": ["Técnico"], "unidades": ["Vila Velha"]},
     DIEGO[:1],
     "Aparece porque você concluiu Técnico em Química, formação de Técnico na unidade Vila "
     "Velha (2012)."),
    ({"niveis": ["Técnico"], "unidades": ["Vila Velha"]}, DIEGO[:1],
     "Aparece porque você concluiu Técnico em Química, formação de Técnico na unidade Vila "
     "Velha (2012)."),
]


@pytest.mark.parametrize("criterios, formacoes, esperado", _SETE)
def test_os_sete_casos_do_contrato(criterios, formacoes, esperado):
    assert explicacao(_o(**criterios), formacoes) == esperado


def test_curso_e_nivel_cita_o_nivel():
    """Caso que a versão anterior do contrato omitia."""
    (item,) = pertinentes([_o(cursos=[TADS], niveis=["Graduação"])], ANA)
    assert "formação de Graduação" in item.explicacao


_TODAS = ANA + MARIA + BRUNO + DIEGO + CARLA_REDES


def _valores(atributo):
    return sorted({getattr(c, atributo) for c in _TODAS})


@pytest.mark.parametrize(
    "criterios",
    [
        dict(zip(chaves, valores, strict=True))
        for n in (1, 2, 3)
        for chaves in itertools.combinations(("cursos", "niveis", "unidades"), n)
        for valores in itertools.product(
            *[[[v] for v in _valores({"cursos": "curso", "niveis": "nivel",
                                       "unidades": "unidade"}[k])][:4] for k in chaves]
        )
    ],
)
def test_invariante_todo_criterio_aparece_em_cada_formacao(criterios):
    """Para toda oportunidade com público, o valor satisfeito de cada critério definido
    aparece literalmente na descrição de cada formação citada (contracts/pertinencia.md)."""
    oportunidade = _o(**criterios)
    for pessoa in (ANA, MARIA, BRUNO, DIEGO, CARLA_REDES):
        for item in pertinentes([oportunidade], pessoa):
            for formacao in item.formacoes:
                descricao = explicacao(oportunidade, (formacao,))
                if "cursos" in criterios:
                    assert formacao.curso in descricao
                if "niveis" in criterios:
                    assert f"formação de {formacao.nivel}" in descricao
                if "unidades" in criterios:
                    assert f"na unidade {formacao.unidade}" in descricao
                trecho = descricao.removeprefix("Aparece porque você concluiu ").rstrip(".")
                assert trecho in item.explicacao


# --- Vocabulário (FR-013, FR-022; P-EXPL; T019) ------------------------------------------

_VETADO = re.compile(r"recomend|selecionad|não perca|vaga|egressos viram|\d+ egressos", re.I)


@pytest.mark.parametrize("criterios, formacoes, _", _SETE)
def test_explicacao_sem_vocabulario_vetado_nem_dado_da_pessoa(criterios, formacoes, _):
    texto = explicacao(_o(**criterios), formacoes)
    assert not _VETADO.search(texto)
    assert "Exemplo" not in texto  # nome das personas
    assert explicacao(_o(), formacoes) == "Aberta a todos os egressos do Ifes."

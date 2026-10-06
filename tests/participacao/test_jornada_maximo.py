"""Máximo de partes restantes (023 FR-013, FR-014; research R8; SC-004).

A propriedade central: em cada Seção de cada um dos 17 percursos esperados da baseline, o
máximo nunca é menor que o número de Seções que de fato vieram depois. E é exato nos pontos
em que a auditoria o cita.
"""

# As fixtures do manifesto são importadas pelo nome; o parâmetro do teste as "redefine".
# ruff: noqa: F401, F811

import pytest

from tests.instrumento.formulario_2024_esperado import PERCURSOS, baseline
from tests.participacao import construcao as c
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.participacao.percurso import maximo_restante

pytestmark = pytest.mark.django_db


def _por_rotulo(conteudo):
    return {(s.titulo or f"#{s.posicao}"): s for s in conteudo.secoes}


def test_nunca_subestima_nos_17_percursos(baseline):
    secoes = _por_rotulo(baseline)
    assert len(PERCURSOS) == 17
    for percurso in PERCURSOS:
        rotulos = percurso[:-1]  # sem "FIM"
        for k, rotulo in enumerate(rotulos):
            restantes = len(rotulos) - k - 1
            assert maximo_restante(baseline, secoes[rotulo].id) >= restantes, (percurso, k)


def test_valores_da_baseline(baseline):
    secoes = _por_rotulo(baseline)
    assert maximo_restante(baseline, secoes["Termos e condições"].id) == 8
    assert maximo_restante(baseline, secoes["Avaliação"].id) == 4
    assert maximo_restante(baseline, secoes["Estudo"].id) == 2
    assert maximo_restante(baseline, secoes["Egresso que estuda"].id) == 1
    assert maximo_restante(baseline, secoes["#13"].id) == 0


def test_deterministico(baseline):
    secao = baseline.secoes[0].id
    assert {maximo_restante(baseline, secao) for _ in range(3)} == {8}


def test_regra_opcional_inclui_o_destino_padrao():
    # S1 com regra opcional "Sim" → S3; sem resposta, a 006 segue para S2.
    conteudo = c.versao_mem(
        c.secao_mem(c.pergunta_mem(obrigatoria=False, regras={"Sim": 3})),
        c.secao_mem(c.pergunta_mem()),
        c.secao_mem(c.pergunta_mem()),
    )
    assert maximo_restante(conteudo, conteudo.secoes[0].id) == 2


def test_opcao_sem_regra_inclui_o_destino_padrao():
    conteudo = c.versao_mem(
        c.secao_mem(c.pergunta_mem(regras={"Sim": c.FIM})),
        c.secao_mem(c.pergunta_mem()),
    )
    assert maximo_restante(conteudo, conteudo.secoes[0].id) == 1


def test_regra_obrigatoria_completa_ignora_o_destino_padrao():
    conteudo = c.versao_mem(
        c.secao_mem(c.pergunta_mem(regras={"Sim": c.FIM, "Não": 3})),
        c.secao_mem(c.pergunta_mem()),
        c.secao_mem(c.pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
    )
    assert maximo_restante(conteudo, conteudo.secoes[0].id) == 1


def test_encaminhamento():
    conteudo = c.versao_mem(
        c.secao_mem(c.pergunta_mem(), encaminhamento=3),
        c.secao_mem(c.pergunta_mem()),
        c.secao_mem(c.pergunta_mem()),
    )
    assert maximo_restante(conteudo, conteudo.secoes[0].id) == 1

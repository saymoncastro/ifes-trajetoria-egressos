"""Navegação da baseline do Formulário Egresso Ifes 2024 (specs/003, US4).

Só a descrição da navegação; nada aqui executa a jornada nem define o momento de
aplicação das regras (DP-302).
"""

# As fixtures do manifesto são importadas pelo nome; o parâmetro do teste as "redefine".
# ruff: noqa: F401, F811

import dataclasses

import pytest

from tests.instrumento.construcao import percursos_de_secoes
from tests.instrumento.formulario_2024_esperado import (
    ENCAMINHAMENTOS,
    PERCURSOS,
    REGRAS,
    baseline,
    perguntas_por_chave,
)
from trajetoria.formulario_2024 import materializar
from trajetoria.instrumento.conteudo import ConteudoOpcao, ConteudoPergunta
from trajetoria.instrumento.models import Versao
from trajetoria.instrumento.regras import verificar_completude

pytestmark = pytest.mark.django_db


def _chave_da_secao(conteudo):
    return {s.id: f"S{n}" for n, s in enumerate(conteudo.secoes, 1)}


def test_regras(baseline):
    secao = _chave_da_secao(baseline)
    obtidas = {
        (chave, o.texto): "FINALIZAR" if o.regra.finaliza else secao[o.regra.destino_secao_id]
        for chave, p in perguntas_por_chave(baseline).items()
        for o in p.opcoes
        if o.regra is not None
    }
    assert obtidas == REGRAS


def test_q51_sem_regra_redundante(baseline):
    assert all(o.regra is None for o in perguntas_por_chave(baseline)["Q51"].opcoes)


def test_encaminhamentos(baseline):
    secao = _chave_da_secao(baseline)
    obtidos = {
        secao[s.id]: secao[s.encaminhamento_id]
        for s in baseline.secoes
        if s.encaminhamento_id is not None
    }
    assert obtidos == ENCAMINHAMENTOS


def test_percursos(baseline):
    percursos = percursos_de_secoes(baseline)
    assert percursos == set(PERCURSOS)
    assert len(percursos) == 17
    # Q1 = "Não" finaliza sem apresentar outra Seção.
    assert ("Termos e condições", "FIM") in percursos


def test_q46_q47_q48_sem_momento_de_aplicacao(baseline):
    perguntas = perguntas_por_chave(baseline)
    s11 = baseline.secoes[10]
    assert [p.id for p in s11.perguntas] == [perguntas[c].id for c in ("Q46", "Q47", "Q48")]
    assert [p.posicao for p in s11.perguntas] == [1, 2, 3]

    # Q46 é a única Pergunta com regras que tem outra Pergunta depois dela na Seção.
    seguidas = [
        p.texto
        for s in baseline.secoes
        for p in s.perguntas[:-1]
        if any(o.regra for o in p.opcoes)
    ]
    assert seguidas == [perguntas["Q46"].texto]

    # Nenhum atributo de momento de aplicação (002, FR-053).
    campos = {f.name for f in dataclasses.fields(ConteudoPergunta)} | {
        f.name for f in dataclasses.fields(ConteudoOpcao)
    }
    assert not {c for c in campos if "momento" in c or "timing" in c or "aplica" in c}


def test_completude_sem_publicar():
    # A fixture `baseline` desfaz a transação; a completude precisa da Versão gravada (U1).
    versao = materializar().versao
    assert verificar_completude(versao) == ()
    assert Versao.objects.get(pk=versao.pk).estado == "RASCUNHO"

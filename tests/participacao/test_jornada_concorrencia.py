"""Concorrência da conclusão (FR-043; research R12).

A proteção principal é determinística: `concluir` bloqueia a linha da Participação antes de
ler Respostas, e a segunda conclusão relê `concluida_em` sob o bloqueio. O teste com threads
é opcional (como 005 R17) e só permanece se for estável.
"""

import threading

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.participacao import construcao as c
from tests.participacao.construcao import NO_PERIODO, preencher_instrumento
from trajetoria.participacao.consultas import respostas_atuais
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import (
    SituacaoConclusao,
    concluir,
    responder_escolha_multipla,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


def _indices(consultas, tabela):
    return [i for i, q in enumerate(consultas) if f'"{tabela}"' in q["sql"]]


@pytest.mark.parametrize("repetida", [False, True], ids=["primeira", "repetida"])
def test_bloqueio_da_participacao_precede_a_leitura_das_respostas(participacao, inst, repetida):
    preencher_instrumento(participacao, inst)
    if repetida:
        concluir(participacao, agora=NO_PERIODO)
    with CaptureQueriesContext(connection) as capturadas:
        concluir(participacao, agora=NO_PERIODO)
    consultas = capturadas.captured_queries
    participacoes = _indices(consultas, "participacao_participacao")
    primeira = consultas[participacoes[0]]["sql"]
    assert "FOR UPDATE" in primeira
    respostas = _indices(consultas, "participacao_resposta")
    if repetida:
        assert respostas == []  # devolve JA_CONCLUIDA sem ler Respostas
    else:
        assert participacoes[0] < respostas[0]


def test_segunda_conclusao_nao_remove_nada(participacao, inst):
    preencher_instrumento(participacao, inst)
    assert concluir(participacao, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA
    linhas = Resposta.objects.filter(participacao=participacao).count()
    assert concluir(participacao, agora=NO_PERIODO).situacao is SituacaoConclusao.JA_CONCLUIDA
    assert Resposta.objects.filter(participacao=participacao).count() == linhas


def test_escrita_antes_e_considerada_e_depois_e_rejeitada(participacao, inst):
    preencher_instrumento(participacao, inst)
    responder_escolha_multipla(
        participacao, inst.multipla, [inst.opcao(inst.multipla, "B")], agora=NO_PERIODO
    )
    concluir(participacao, agora=NO_PERIODO)
    assert inst.multipla.id in respostas_atuais(participacao)
    c.rejeita(
        [Motivo.PARTICIPACAO_CONCLUIDA],
        responder_texto,
        participacao,
        inst.texto,
        "28",
        agora=NO_PERIODO,
    )


@pytest.mark.django_db(transaction=True)
def test_conclusoes_simultaneas_em_threads(participacao, inst):
    # Opcional (research R12, como 005 R17): remover se ficar instável no CI.
    preencher_instrumento(participacao, inst)
    barreira = threading.Barrier(2)
    resultados, erros = [], []

    def tentar():
        try:
            barreira.wait(timeout=10)
            resultados.append(concluir(participacao, agora=NO_PERIODO))
        except Exception as erro:  # noqa: BLE001 — o teste exibe qualquer falha da thread
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=tentar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not erros
    assert sorted(r.situacao.value for r in resultados) == ["concluida", "ja_concluida"]
    assert Participacao.objects.get(pk=participacao.pk).concluida_em == NO_PERIODO


def test_consulta_da_jornada_le_participacao_e_respostas_como_um_estado_so(participacao, inst):
    # Regressão (code review): a linha da Participação é lida com FOR NO KEY UPDATE, que
    # espera uma conclusão em andamento, antes das Respostas — nunca um estado misturado.
    from trajetoria.participacao.consultas import situacao_da_jornada

    preencher_instrumento(participacao, inst)
    with CaptureQueriesContext(connection) as capturadas:
        situacao_da_jornada(participacao, agora=NO_PERIODO)
    consultas = capturadas.captured_queries
    participacoes = _indices(consultas, "participacao_participacao")
    assert "FOR NO KEY UPDATE" in consultas[participacoes[0]]["sql"]
    assert participacoes[0] < _indices(consultas, "participacao_resposta")[0]
    assert Participacao.objects.get(pk=participacao.pk).concluida_em is None  # nada gravado

"""Participação concluída é imutável; conclusão repetida é idempotente (US7; FR-036 a FR-041).

Usa o instrumento de teste da 005 (`construcao.instrumento`): Seção 1 com os quatro tipos e
Seção 2 opcional, então responder as obrigatórias da Seção 1 finaliza a jornada.
"""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO, preencher_instrumento
from trajetoria.participacao import operacoes
from trajetoria.participacao.consultas import admite_escrita, situacao_da_jornada
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import (
    SituacaoConclusao,
    SituacaoInicio,
    concluir,
    iniciar_participacao,
    remover_resposta,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


@pytest.fixture
def concluida(participacao, inst):
    preencher_instrumento(participacao, inst)
    assert concluir(participacao, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA
    return Participacao.objects.get(pk=participacao.pk)


def _escritas(inst):
    return [
        (responder_escolha_unica, (inst.unica, inst.opcao(inst.unica, "Não"))),
        (responder_escolha_multipla, (inst.multipla, [inst.opcao(inst.multipla, "A")])),
        (responder_texto, (inst.texto, "28")),
        (responder_escala, (inst.escala, 5)),
        (remover_resposta, (inst.texto,)),
    ]


@pytest.mark.parametrize("agora", [NO_PERIODO, DEPOIS_DO_FIM], ids=["em_coleta", "encerrada"])
def test_escritas_rejeitadas_depois_da_conclusao(concluida, inst, agora):
    antes = c.retrato(concluida)
    for operacao, argumentos in _escritas(inst):
        c.rejeita([Motivo.PARTICIPACAO_CONCLUIDA], operacao, concluida, *argumentos, agora=agora)
        assert c.retrato(concluida) == antes


@pytest.mark.parametrize("agora", [NO_PERIODO, DEPOIS_DO_FIM], ids=["em_coleta", "encerrada"])
def test_conclusao_repetida_e_idempotente(concluida, agora):
    antes = c.retrato(concluida)
    resultado = concluir(concluida, agora=agora)
    assert resultado.situacao is SituacaoConclusao.JA_CONCLUIDA
    assert resultado.participacao.concluida_em == NO_PERIODO
    assert c.retrato(concluida) == antes


def test_conclusao_repetida_nao_revalida_nada(concluida, monkeypatch):
    # A conclusão histórica já ocorreu: sem consultar Campanha, Versão ou Respostas.
    def proibido(*args, **kwargs):
        raise AssertionError("a conclusão repetida não deve reavaliar nada")

    for nome in ("estado", "conteudo_da_versao", "respostas_atuais", "percorrer"):
        monkeypatch.setattr(operacoes, nome, proibido)
    assert concluir(concluida, agora=NO_PERIODO).situacao is SituacaoConclusao.JA_CONCLUIDA


def test_inicio_repetido_devolve_a_concluida(concluida):
    inicio = iniciar_participacao(concluida.campanha, concluida.conclusao, agora=NO_PERIODO)
    assert inicio.situacao is SituacaoInicio.JA_EXISTENTE
    assert inicio.participacao.id == concluida.id
    assert inicio.participacao.concluida_em == NO_PERIODO
    assert Participacao.objects.count() == 1


def test_leitura_da_concluida_nao_admite_escrita(concluida, participacao):
    # `participacao` é a instância anterior à conclusão: `admite_escrita` relê do banco.
    assert participacao.concluida_em is None
    assert not admite_escrita(participacao, agora=NO_PERIODO)
    situacao = situacao_da_jornada(participacao, agora=NO_PERIODO)
    assert not situacao.admite_escrita
    assert not situacao.pode_concluir
    assert situacao.finalizada
    assert situacao.fora_do_percurso == frozenset()
    assert situacao.impedimentos == ()


def test_nao_existe_reabertura():
    proibidas = ("reabr", "desfaz", "reverter", "editar")
    assert not [n for n in operacoes.__all__ if any(p in n.lower() for p in proibidas)]


def test_admite_escrita_de_participacao_inexistente_e_falso(campanha, conclusao):
    # Regressão (code review): devolve bool, como no contrato da 005, em vez de levantar.
    nao_gravada = Participacao(campanha=campanha, conclusao=conclusao, iniciada_em=NO_PERIODO)
    assert admite_escrita(nao_gravada, agora=NO_PERIODO) is False

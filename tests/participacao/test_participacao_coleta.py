"""Campanha sem coleta admitida (US11): nenhuma escrita; leitura e dados intactos.
Elegibilidade verificada só na criação (FR-034)."""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO, ULTIMO_DIA, momento
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.participacao.consultas import (
    admite_escrita,
    localizar_participacao,
    respostas_atuais,
)
from trajetoria.participacao.operacoes import (
    SituacaoInicio,
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
def respondida(participacao, inst):
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    return participacao


def _escritas(inst):
    """Cada escrita possível: registrar os quatro tipos, substituir e remover."""
    return [
        (responder_escolha_unica, inst.unica, inst.opcao(inst.unica, "Não")),
        (responder_escolha_multipla, inst.multipla, [inst.opcao(inst.multipla, "A")]),
        (responder_texto, inst.texto, "28"),
        (responder_escala, inst.escala, 3),
        (remover_resposta, inst.texto),
    ]


def _todas_rejeitadas(participacao, inst, agora):
    antes = c.retrato(participacao)
    for operacao, *args in _escritas(inst):
        c.rejeita([Motivo.COLETA_NAO_ADMITIDA], operacao, participacao, *args, agora=agora)
    assert c.retrato(participacao) == antes


def test_escrita_bloqueada_apos_encerramento_explicito(respondida, inst):
    op_campanha.encerrar(respondida.campanha, agora=momento(2027, 5, 10))
    _todas_rejeitadas(respondida, inst, momento(2027, 5, 11))


def test_escrita_bloqueada_apos_fim_do_periodo(respondida, inst):
    _todas_rejeitadas(respondida, inst, DEPOIS_DO_FIM)


def test_ultimo_dia_aceito_dia_seguinte_rejeitado(respondida, inst):
    responder_texto(respondida, inst.texto, "28", agora=ULTIMO_DIA)
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        responder_texto,
        respondida,
        inst.texto,
        "29",
        agora=DEPOIS_DO_FIM,
    )
    assert respostas_atuais(respondida)[inst.texto.id].texto == "28"


def test_nova_participacao_apos_o_fim(campanha):
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        iniciar_participacao,
        campanha,
        c.conclusao(),
        agora=DEPOIS_DO_FIM,
    )


def test_leitura_apos_encerramento(respondida, inst):
    antes = respostas_atuais(respondida)
    retrato = c.retrato(respondida)

    op_campanha.encerrar(respondida.campanha, agora=momento(2027, 5, 10))

    assert not admite_escrita(respondida, agora=momento(2027, 5, 11))
    assert localizar_participacao(respondida.campanha, respondida.conclusao) == respondida
    depois = respostas_atuais(respondida)
    assert {k: (r.id, r.opcao_id, r.texto) for k, r in depois.items()} == {
        k: (r.id, r.opcao_id, r.texto) for k, r in antes.items()
    }
    # Nada apagado ou marcado (FR-040).
    assert c.retrato(respondida) == retrato


def test_inicio_repetido_apos_o_fim_nao_habilita_escrita(respondida, inst):
    inicio = iniciar_participacao(respondida.campanha, respondida.conclusao, agora=DEPOIS_DO_FIM)
    assert (inicio.situacao, inicio.participacao.id) == (
        SituacaoInicio.JA_EXISTENTE,
        respondida.id,
    )
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        responder_texto,
        inicio.participacao,
        inst.texto,
        "28",
        agora=DEPOIS_DO_FIM,
    )


def test_elegibilidade_so_na_criacao(participacao, inst):
    # A Conclusão sai dos critérios (simula 001/DP-005); a escrita continua aceita durante a
    # coleta, porque a elegibilidade não é reavaliada (FR-034, DP-507).
    conclusao = participacao.conclusao
    conclusao.ano_conclusao = 2010
    conclusao.save(update_fields=["ano_conclusao"])

    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    assert respostas_atuais(participacao)[inst.texto.id].texto == "27"


def test_relogio_lido_depois_do_bloqueio(participacao, inst, monkeypatch):
    """Regressão (code review): sem `agora` explícito, o momento de referência é lido depois
    do bloqueio da Participação. Uma escrita que espera pelo bloqueio enquanto o período
    termina é julgada pelo instante em que obtém o bloqueio, não pelo de antes da espera."""
    from django.utils import timezone

    from trajetoria.participacao import operacoes

    relogio = {"agora": NO_PERIODO}
    monkeypatch.setattr(timezone, "now", lambda: relogio["agora"])
    bloquear = operacoes._bloquear

    def bloquear_enquanto_o_periodo_termina(p):
        relogio["agora"] = DEPOIS_DO_FIM  # a espera atravessa o fim do período
        return bloquear(p)

    monkeypatch.setattr(operacoes, "_bloquear", bloquear_enquanto_o_periodo_termina)
    antes = c.retrato(participacao)
    c.rejeita([Motivo.COLETA_NAO_ADMITIDA], responder_texto, participacao, inst.texto, "27")
    assert c.retrato(participacao) == antes

"""Alterar e remover respostas em rascunho (US7): só o valor atual, sem histórico."""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import NO_PERIODO
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import (
    SituacaoRemocao,
    remover_resposta,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


def _resposta(participacao, pergunta):
    return Resposta.objects.filter(participacao=participacao, pergunta=pergunta).first()


def test_substituir_escolha_unica_no_lugar(participacao, inst):
    primeira = responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    segunda = responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=NO_PERIODO
    )
    assert segunda.id == primeira.id
    assert _resposta(participacao, inst.unica).opcao.texto == "Não"
    assert Resposta.objects.filter(participacao=participacao).count() == 1


def test_substituir_escolha_multipla_integralmente(participacao, inst):
    a, b, cc = (inst.opcao(inst.multipla, t) for t in ("A", "B", "C"))
    responder_escolha_multipla(participacao, inst.multipla, [a, b], agora=NO_PERIODO)
    responder_escolha_multipla(participacao, inst.multipla, [cc], agora=NO_PERIODO)

    r = _resposta(participacao, inst.multipla)
    assert [o.texto for o in r.opcoes.all()] == ["C"]
    assert RespostaOpcao.objects.count() == 1


def test_remover_resposta(participacao, inst):
    responder_escolha_multipla(
        participacao, inst.multipla, [inst.opcao(inst.multipla, "A")], agora=NO_PERIODO
    )
    situacao = remover_resposta(participacao, inst.multipla, agora=NO_PERIODO)

    assert situacao is SituacaoRemocao.REMOVIDA
    assert _resposta(participacao, inst.multipla) is None
    # "Limpar" a múltipla é remover: nenhuma seleção sobra (Clarifications).
    assert not RespostaOpcao.objects.exists()


def test_remover_inexistente_nao_muda_nada(participacao, inst):
    antes = c.retrato(participacao)
    assert (
        remover_resposta(participacao, inst.texto, agora=NO_PERIODO) is SituacaoRemocao.INEXISTENTE
    )
    assert c.retrato(participacao) == antes


def test_remover_resposta_de_pergunta_obrigatoria(participacao, inst):
    assert inst.texto.obrigatoria
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    assert remover_resposta(participacao, inst.texto, agora=NO_PERIODO) is SituacaoRemocao.REMOVIDA


def test_participacao_parcial_ou_completa_nao_e_conclusao(participacao, inst):
    # Zero, algumas e todas as respostas: escrever nunca conclui nem marca progresso (US7.6).
    # `concluida_em` existe desde a 006 e só `concluir` o grava (006 research R16).
    campos = {f.name for f in Participacao._meta.concrete_fields}
    assert campos == {"id", "campanha", "conclusao", "iniciada_em", "concluida_em"}

    def em_rascunho():
        gravada = Participacao.objects.get(pk=participacao.pk)
        return gravada.concluida_em is None and gravada.iniciada_em == NO_PERIODO

    assert em_rascunho()
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    assert em_rascunho()
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    responder_escala(participacao, inst.escala, 4, agora=NO_PERIODO)
    assert em_rascunho()


def test_atomicidade_da_substituicao_de_multipla(participacao, inst):
    a, b, cc = (inst.opcao(inst.multipla, t) for t in ("A", "B", "C"))
    gravada = responder_escolha_multipla(participacao, inst.multipla, [a, b], agora=NO_PERIODO)
    antes = c.retrato(participacao)

    c.rejeita(
        [Motivo.OPCAO_DE_OUTRA_PERGUNTA],
        responder_escolha_multipla,
        participacao,
        inst.multipla,
        [cc, inst.opcao(inst.unica, "Sim")],
        agora=NO_PERIODO,
    )
    c.rejeita(
        [Motivo.COMPLEMENTO_NAO_ADMITIDO],
        responder_escolha_multipla,
        participacao,
        inst.multipla,
        [cc],
        complemento="x",
        agora=NO_PERIODO,
    )

    assert c.retrato(participacao) == antes
    assert [o.texto for o in _resposta(participacao, inst.multipla).opcoes.all()] == ["A", "B"]
    assert _resposta(participacao, inst.multipla).id == gravada.id


def test_navegacao_nao_e_aplicada(participacao, inst):
    # "Não" em `unica` finaliza o instrumento; mesmo assim a Seção 2 é respondível, e mudar
    # a resposta com regra não remove nem altera outras (FR-038).
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=NO_PERIODO
    )
    responder_texto(participacao, inst.posterior, "comentário", agora=NO_PERIODO)
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=NO_PERIODO
    )

    assert _resposta(participacao, inst.posterior).texto == "comentário"


def test_remover_com_pergunta_de_outra_versao(participacao, inst):
    outro = c.instrumento_derivado(inst)
    c.rejeita(
        [Motivo.PERGUNTA_DE_OUTRA_VERSAO],
        remover_resposta,
        participacao,
        outro.texto,
        agora=NO_PERIODO,
    )

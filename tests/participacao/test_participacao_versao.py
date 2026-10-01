"""Referências e valores incompatíveis (US12): a Versão aplicada pela Campanha é a única
régua; cada item da lista mínima de rejeições (FR-052 a–i) tem caso de teste."""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import (
    iniciar_participacao,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

pytestmark = pytest.mark.django_db


def test_pergunta_de_outra_versao(participacao, inst):
    inst28 = c.instrumento_derivado(inst)
    antes = c.retrato(participacao)
    c.rejeita(
        [Motivo.PERGUNTA_DE_OUTRA_VERSAO],
        responder_texto,
        participacao,
        inst28.texto,
        "27",
        agora=NO_PERIODO,
    )
    assert c.retrato(participacao) == antes


def test_opcao_da_pergunta_correspondente_de_outra_versao(participacao, inst):
    inst28 = c.instrumento_derivado(inst)
    c.rejeita(
        [Motivo.OPCAO_DE_OUTRA_PERGUNTA],
        responder_escolha_unica,
        participacao,
        inst.unica,
        inst28.opcao(inst28.unica, "Sim"),
        agora=NO_PERIODO,
    )
    c.rejeita(
        [Motivo.OPCAO_DE_OUTRA_PERGUNTA],
        responder_escolha_multipla,
        participacao,
        inst.multipla,
        [inst28.opcao(inst28.multipla, "A")],
        agora=NO_PERIODO,
    )


def test_versao_posterior_nao_muda_respostas_nem_validacao(participacao, inst):
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    responder_escala(participacao, inst.escala, 4, agora=NO_PERIODO)
    antes = c.retrato(participacao)

    c.instrumento_derivado(inst)  # 2028, criada e publicada depois

    assert c.retrato(participacao) == antes
    # A validação continua pela Versão 2027.
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=NO_PERIODO
    )


def _casos(participacao, inst, campanha):
    """FR-052 a–i: (motivo, operação, argumentos posicionais, kwargs)."""
    nao_gravada = Participacao(campanha=campanha, conclusao=participacao.conclusao)
    inst28 = c.instrumento_derivado(inst, "2029")
    outro = inst.opcao(inst.unica_outro, "Outro:")
    return {
        "a": (
            Motivo.COLETA_NAO_ADMITIDA,
            responder_texto,
            (participacao, inst.texto, "x"),
            {"agora": DEPOIS_DO_FIM},
        ),
        "b": (
            Motivo.CONCLUSAO_NAO_ELEGIVEL,
            iniciar_participacao,
            (campanha, c.conclusao(ano=2010)),
            {},
        ),
        "c": (Motivo.PARTICIPACAO_INEXISTENTE, responder_texto, (nao_gravada, inst.texto, "x"), {}),
        "d": (
            Motivo.PERGUNTA_DE_OUTRA_VERSAO,
            responder_texto,
            (participacao, inst28.texto, "x"),
            {},
        ),
        "e": (
            Motivo.OPCAO_DE_OUTRA_PERGUNTA,
            responder_escolha_unica,
            (participacao, inst.unica, inst.opcao(inst.campus, "Campus Serra")),
            {},
        ),
        "f": (Motivo.VALOR_INCOMPATIVEL, responder_escala, (participacao, inst.escala, "3"), {}),
        "g": (Motivo.ESCALA_FORA_DOS_LIMITES, responder_escala, (participacao, inst.escala, 6), {}),
        "h": (
            Motivo.COMPLEMENTO_NAO_ADMITIDO,
            responder_escolha_unica,
            (participacao, inst.unica_outro, inst.opcao(inst.unica_outro, "B")),
            {"complemento": "x"},
        ),
        "i": (
            Motivo.VALOR_VAZIO,
            responder_escolha_unica,
            (participacao, inst.unica_outro, outro),
            {"complemento": "   "},
        ),
    }


@pytest.mark.parametrize("item", list("abcdefghi"))
def test_lista_minima_de_rejeicoes(participacao, inst, campanha, item):
    motivo, operacao, args, kwargs = _casos(participacao, inst, campanha)[item]
    kwargs = {"agora": NO_PERIODO, **kwargs}
    antes = c.retrato(participacao)
    participacoes = Participacao.objects.count()

    c.rejeita([motivo], operacao, *args, **kwargs)

    assert c.retrato(participacao) == antes
    assert Participacao.objects.count() == participacoes


def test_mensagens_sem_valores_declarados(participacao, inst):
    declarados = ["Segredo declarado 123", "99"]
    tentativas = [
        lambda: responder_escala(participacao, inst.escala, 99, agora=NO_PERIODO),
        lambda: responder_texto(participacao, inst.texto, declarados[0], agora=DEPOIS_DO_FIM),
        lambda: responder_escolha_unica(
            participacao,
            inst.unica_outro,
            inst.opcao(inst.unica_outro, "A"),
            complemento=declarados[0],
            agora=NO_PERIODO,
        ),
    ]
    for tentativa in tentativas:
        with pytest.raises(ParticipacaoRejeitada) as erro:
            tentativa()
        mensagem = str(erro.value) + " ".join(v.detalhe for v in erro.value.violacoes)
        assert not any(valor in mensagem for valor in declarados)

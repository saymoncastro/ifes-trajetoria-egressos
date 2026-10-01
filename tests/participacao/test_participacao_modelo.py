"""Restrições do banco de Participação e Resposta (data-model.md), por escrita direta no ORM,
fora das operações.

Os CHECKs protegem só invariantes da própria linha. Tipo da Pergunta, pertença da Opção,
Versão da Campanha, limites da escala, ≥ 1 seleção e complemento × Opção são das
operações: os testes de limite abaixo documentam que o banco não os garante.
"""

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from tests.participacao.construcao import NO_PERIODO
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao

pytestmark = pytest.mark.django_db


def _rejeita(modelo, **campos):
    with pytest.raises(IntegrityError), transaction.atomic():
        modelo.objects.create(**campos)


@pytest.fixture
def part(campanha, conclusao):
    return Participacao.objects.create(
        campanha=campanha, conclusao=conclusao, iniciada_em=NO_PERIODO
    )


def test_participacao_unica_por_par(part):
    _rejeita(
        Participacao,
        campanha=part.campanha,
        conclusao=part.conclusao,
        iniciada_em=NO_PERIODO,
    )


def test_resposta_unica_por_pergunta(part, inst):
    Resposta.objects.create(participacao=part, pergunta=inst.texto, texto="27")
    _rejeita(Resposta, participacao=part, pergunta=inst.texto, texto="28")


def test_no_maximo_um_valor_direto(part, inst):
    sim = inst.opcao(inst.unica, "Sim")
    _rejeita(Resposta, participacao=part, pergunta=inst.unica, opcao=sim, texto="x")
    _rejeita(Resposta, participacao=part, pergunta=inst.unica, opcao=sim, escala=3)
    _rejeita(Resposta, participacao=part, pergunta=inst.texto, texto="x", escala=3)


def test_textos_nao_vazios(part, inst):
    _rejeita(Resposta, participacao=part, pergunta=inst.texto, texto="")
    outro = inst.opcao(inst.unica_outro, "Outro:")
    _rejeita(Resposta, participacao=part, pergunta=inst.unica_outro, opcao=outro, complemento="")


def test_selecao_sem_repeticao(part, inst):
    resposta = Resposta.objects.create(participacao=part, pergunta=inst.multipla)
    a = inst.opcao(inst.multipla, "A")
    RespostaOpcao.objects.create(resposta=resposta, opcao=a)
    _rejeita(RespostaOpcao, resposta=resposta, opcao=a)


def test_formas_validas_de_linha(part, inst):
    Resposta.objects.create(participacao=part, pergunta=inst.escala, escala=3)
    Resposta.objects.create(participacao=part, pergunta=inst.texto, texto="27")
    Resposta.objects.create(
        participacao=part,
        pergunta=inst.unica_outro,
        opcao=inst.opcao(inst.unica_outro, "Outro:"),
        complemento="Cuidando de familiar",
    )
    Resposta.objects.create(participacao=part, pergunta=inst.multipla, complemento="x")


def test_limites_que_o_banco_nao_garante(part, inst):
    # Escolha múltipla sem seleção e complemento ao lado de texto passam pelo banco: são
    # regras entre tabelas, garantidas pelas operações (data-model, "Restrições").
    Resposta.objects.create(participacao=part, pergunta=inst.multipla)
    Resposta.objects.create(participacao=part, pergunta=inst.texto, texto="x", complemento="y")


def test_referencias_protegidas(part, inst):
    resposta = Resposta.objects.create(
        participacao=part, pergunta=inst.unica, opcao=inst.opcao(inst.unica, "Sim")
    )
    multipla = Resposta.objects.create(participacao=part, pergunta=inst.multipla)
    RespostaOpcao.objects.create(resposta=multipla, opcao=inst.opcao(inst.multipla, "C"))
    for objeto in (
        part.campanha,
        part.conclusao,
        resposta.pergunta,
        resposta.opcao,
        inst.opcao(inst.multipla, "C"),
        part,
    ):
        with pytest.raises(ProtectedError), transaction.atomic():
            objeto.delete()


def test_remover_resposta_apaga_selecoes(part, inst):
    resposta = Resposta.objects.create(participacao=part, pergunta=inst.multipla)
    RespostaOpcao.objects.create(resposta=resposta, opcao=inst.opcao(inst.multipla, "A"))
    resposta.delete()
    assert not RespostaOpcao.objects.exists()

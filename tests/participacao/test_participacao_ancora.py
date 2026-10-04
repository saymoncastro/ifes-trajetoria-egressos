import pytest
from django.db import IntegrityError, transaction

from tests.declaracao.construcao import declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import concluir, remover_resposta, responder_escolha_unica
from trajetoria.participacao.regras import ParticipacaoRejeitada

pytestmark = pytest.mark.django_db


def test_ancora_unica(campanha, conclusao):
    with pytest.raises(IntegrityError), transaction.atomic():
        Participacao.objects.create(campanha=campanha, iniciada_em=c.NO_PERIODO)
    formacao = declaracao_concluida(campanha)
    assert formacao.participacao.pessoa is None
    with pytest.raises(IntegrityError), transaction.atomic():
        Participacao.objects.filter(pk=formacao.participacao.pk).update(conclusao=conclusao)


def test_jornada_declarada(campanha, inst):
    formacao = declaracao_concluida(campanha)
    p = formacao.participacao
    p.concluida_em = None
    p.save()
    opcao = inst.opcao(inst.unica, "Não")
    responder_escolha_unica(p, inst.unica, opcao, agora=c.NO_PERIODO)
    remover_resposta(p, inst.unica, agora=c.NO_PERIODO)
    responder_escolha_unica(p, inst.unica, opcao, agora=c.NO_PERIODO)
    c.preencher_instrumento(p, inst)
    concluir(p, agora=c.NO_PERIODO)
    with pytest.raises(ParticipacaoRejeitada):
        remover_resposta(p, inst.unica, agora=c.NO_PERIODO)

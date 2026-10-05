"""Mobilizar não restringe quem pode responder (ADR 0004; Princípio II; 020 FR-040, FR-041,
SC-007; achado C1 do analyze; T066)."""

from urllib.parse import urlsplit

import pytest
from django.apps import apps

from tests.editor.construcao_editor import A
from tests.interface import construcao_interface as ci
from tests.mobilizacao.conftest import pessoa
from trajetoria.campanha.consultas import admite_participacao
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote
from trajetoria.participacao.entrada import situacao_de_entrada
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db
PROTEGIDOS = (
    "academico.Pessoa", "academico.ConclusaoAcademica", "campanha.Campanha",
    "participacao.Participacao", "participacao.Resposta", "declaracao.FormacaoDeclarada",
    "analitico.SnapshotAnalitico", "analitico.RegistroDoSnapshot",
)


def _retrato():
    return {
        nome: sorted(map(repr, apps.get_model(nome).objects.values()))
        for nome in PROTEGIDOS
    }


def test_lote_nao_altera_admissao_nem_entidades(ampla):
    ids = ("SIM-P-0001", "SIM-P-0002", "SIM-P-0010")
    antes_entrada = {i: repr(situacao_de_entrada(pessoa(i))) for i in ids}
    antes_admissao = {
        c.pk: admite_participacao(ampla, c) for i in ids for c in pessoa(i).conclusoes.all()
    }
    antes = _retrato()
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    enviar_lote(lote.pk, A)
    confirmar_lote(ampla.pk, A, "Serra", {"unidades": ["Serra"]})  # Ana: excluída de nada
    assert _retrato() == antes
    assert {i: repr(situacao_de_entrada(pessoa(i))) for i in ids} == antes_entrada
    assert {
        c.pk: admite_participacao(ampla, c) for i in ids for c in pessoa(i).conclusoes.all()
    } == antes_admissao


def test_pessoa_fora_de_qualquer_lote_responde_normalmente(ampla, client):
    confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    ana = pessoa("SIM-P-0001")  # Serra: fora do Lote
    resposta = ci.iniciar(client, ana)
    participacao = Participacao.objects.get(pk=ci.participacao_de(resposta))
    _, url = ci.percorrer_pela_interface(client, participacao.pk, ampla.versao, {})
    assert client.post(urlsplit(url).path).status_code == 302
    participacao.refresh_from_db()
    assert participacao.concluida_em is not None


def test_membro_abordado_continua_admitido(ampla, client):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    enviar_lote(lote.pk, A)
    bruno = pessoa("SIM-P-0002")
    resposta = ci.iniciar(client, bruno, bruno.conclusoes.first())
    assert Participacao.objects.filter(pk=ci.participacao_de(resposta)).exists()

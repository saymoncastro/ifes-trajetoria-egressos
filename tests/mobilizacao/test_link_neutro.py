"""Seguir o link do convite não identifica, autentica nem inicia nada (020 FR-027; 018
FR-053; T028)."""

import re

import pytest
from django.contrib.sessions.models import Session
from django.core import mail
from django.test import Client

from tests.editor.construcao_editor import A
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def test_link_neutro(ampla):
    enviar_lote(confirmar_lote(ampla.pk, A, "Todos", {}, True).pk, A)
    urls = {re.search(r"http://\S+", m.body).group(0) for m in mail.outbox}
    assert urls == {"http://127.0.0.1:8000/acesso/"}
    antes = (Participacao.objects.count(), Session.objects.count())
    cliente = Client()
    resposta = cliente.get("/acesso/")
    assert resposta.status_code == 200
    assert (Participacao.objects.count(), Session.objects.count()) == antes
    assert cliente.get("/formacoes/").status_code in (302, 303)  # sem sessão de Pessoa

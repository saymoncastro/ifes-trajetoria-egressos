"""SC-005: rastros da importação, acesso e comunicação nunca levam dados em claro."""

import logging

import pytest
from django.apps import apps
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.cache import caches

from tests.acesso.construcao import ANA, DADOS
from tests.acesso.test_verificacao import CASOS_NAO_CONFIRMADOS
from trajetoria.demonstracao.cenario import preparar

pytestmark = pytest.mark.django_db


def test_varredura_completa(client, settings, caplog, django_capture_on_commit_callbacks):
    caplog.set_level(logging.DEBUG)
    settings.TRAJETORIA_DEMONSTRACAO = True
    with django_capture_on_commit_callbacks(execute=True):
        preparar()
    requisicoes = []
    respostas = []
    dados = {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}
    respostas.append(client.post("/acesso/", dados))
    for cpf, data in CASOS_NAO_CONFIRMADOS:
        caches["acesso"].clear()
        respostas.append(client.post("/acesso/", {"cpf": cpf, "data_nascimento": data}))
    respostas.append(client.post("/acesso/", {"cpf": "123", "data_nascimento": "31/02/2000"}))
    caches["acesso"].clear()
    for _ in range(5):
        respostas.append(client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": "13/04/1998"}))
    respostas.append(client.post("/acesso/sair/"))
    from trajetoria.campanha.models import Campanha
    from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.TRAJETORIA_COMUNICACAO_TESTE = True
    campanha = Campanha.objects.get(nome="Demonstração — coleta ampla")
    lote = confirmar_lote(campanha.pk, "demonstracao:operador-a", "Todos", {}, True)
    enviar_lote(lote.pk, "demonstracao:operador-a")
    assert mail.outbox  # 020: o envio por Lote também não expõe CPF nem data
    for r in respostas:
        requisicoes.extend([r.wsgi_request.get_full_path(), r.get("Location", ""), str(r.cookies)])
    banco = []
    for m in apps.get_models():
        banco.extend(str(row) for row in m.objects.values())
    banco.extend(str(s.get_decoded()) for s in Session.objects.all())
    cache = repr(caches["acesso"]._cache)
    artefatos = caplog.text + "\n".join(requisicoes + banco) + cache + repr(mail.outbox)
    for d in DADOS:
        proibidos = [d.cpf, d.cpf11] if d.cpf else []
        if d.data:
            proibidos.extend([d.data.isoformat(), d.nascimento])
        for valor in proibidos:
            assert valor not in artefatos
    # Resultados HTTP só ecoam os próprios valores na entrada e exibem o painel fictício.
    assert all("no-store" in r["Cache-Control"] for r in respostas)

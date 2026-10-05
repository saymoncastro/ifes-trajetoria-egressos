"""Nenhum endereço fora do registro de contato e do envio (020 FR-039; research R9 C2, C3;
SC-004; T055)."""

import logging

import pytest
from django.apps import apps
from django.contrib.sessions.models import Session
from django.core.cache import caches
from django.test import Client

from tests.acesso.construcao import BRUNO
from tests.editor.construcao_editor import A, atuar_como
from trajetoria.campanha.models import Campanha
from trajetoria.contato.models import ContatoDaPessoa
from trajetoria.demonstracao.cenario import preparar

pytestmark = pytest.mark.django_db
MARCADOR = "marcador-vazamento@example.invalid"


def test_endereco_nao_vaza(settings, caplog):
    caplog.set_level(logging.DEBUG)
    settings.TRAJETORIA_DEMONSTRACAO = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.TRAJETORIA_COMUNICACAO_TESTE = True
    preparar()
    respostas = []
    egresso = Client()
    respostas.append(egresso.post("/acesso/", {"cpf": BRUNO.cpf,
                                               "data_nascimento": BRUNO.nascimento}))
    respostas.append(egresso.get("/meu-email/"))
    respostas.append(egresso.post("/meu-email/", {"acao": "salvar", "email": MARCADOR}))
    respostas.append(egresso.get("/meu-email/"))
    respostas.append(egresso.get("/formacoes/"))

    operador = atuar_como(Client(), A)
    campanha = Campanha.objects.get(nome="Demonstração — coleta ampla")
    base = f"/acompanhamento/campanhas/{campanha.pk}/"
    respostas.append(operador.get(base))
    respostas.append(operador.get(base + "lotes/?previa=1&unidade=Vitória"))
    confirmacao = operador.post(base + "lotes/confirmar/", {"nome": "V", "unidade": "Vitória"})
    respostas.append(confirmacao)
    detalhe = confirmacao["Location"]
    respostas.append(operador.get(detalhe))
    respostas.append(operador.post(detalhe + "enviar/"))

    rastros = [caplog.text]
    for r in respostas:
        rastros += [r.wsgi_request.get_full_path(), r.get("Location", ""), str(r.cookies),
                    r.content.decode()]
    for modelo in apps.get_models():
        linhas = modelo.objects.values()
        if modelo is ContatoDaPessoa:
            linhas = linhas.values(*[f.attname for f in modelo._meta.fields if f.name != "valor"])
        rastros += [str(linha) for linha in linhas]
    rastros += [str(s.get_decoded()) for s in Session.objects.all()]
    rastros += [repr(c._cache) for c in (caches["acesso"], caches["default"])]
    texto = "\n".join(rastros)
    assert MARCADOR not in texto
    assert "marcador-vazamento" not in texto
    # O endereço existe só no registro de contato (e foi o destino do envio, C1).
    assert ContatoDaPessoa.objects.filter(valor=MARCADOR).exists()

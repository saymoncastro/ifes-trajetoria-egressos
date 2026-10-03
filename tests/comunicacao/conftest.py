from io import StringIO

import pytest
from django.apps import apps
from django.core.management import call_command
from django.test import Client

from tests.editor.construcao_editor import A, B, atuar_como
from trajetoria.campanha.models import Campanha


@pytest.fixture(autouse=True)
def ambiente(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.TRAJETORIA_COMUNICACAO_TESTE = True
    settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO = "http://127.0.0.1:8000/demonstracao/"


@pytest.fixture
def campanha(db):
    call_command("preparar_demonstracao", stdout=StringIO())
    return Campanha.objects.get(nome="Demonstração — acompanhamento Serra e Vitória")


@pytest.fixture
def clientes(campanha):
    return {i: atuar_como(Client(), i) for i in (A, B, "demonstracao:operador-c")}


@pytest.fixture
def snapshot():
    def obter():
        return {
            m._meta.label: sorted(
                [tuple(sorted(row.items())) for row in m.objects.values()], key=repr
            )
            for m in apps.get_models(include_auto_created=True)
        }

    return obter

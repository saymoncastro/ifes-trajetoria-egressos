from datetime import UTC, datetime
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import Client
from django.utils import timezone

from tests.editor.construcao_editor import A, B, C, atuar_como
from trajetoria.academico.models import Pessoa
from trajetoria.campanha.models import Campanha
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.mobilizacao.models import LoteDeMobilizacao

AMPLA = "Demonstração — coleta ampla"
PREPARACAO = "Demonstração — rodada em preparação"
SOBREPOSTA = "Demonstração — coleta sobreposta"
INSTITUCIONAL = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
VITORIA = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vitória"}))
SERRA = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Serra"}))


@pytest.fixture(autouse=True)
def ambiente(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.TRAJETORIA_COMUNICACAO_TESTE = True
    settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO = "http://127.0.0.1:8000/acesso/"
    settings.TRAJETORIA_ENVIO_REAL = ""
    settings.TRAJETORIA_LOTE_ENVIO_POR_ACAO = 100


@pytest.fixture
def demo(db):
    call_command("preparar_demonstracao", stdout=StringIO())


@pytest.fixture
def ampla(demo):
    return Campanha.objects.get(nome=AMPLA)


@pytest.fixture
def em_preparacao(demo):
    return Campanha.objects.get(nome=PREPARACAO)


@pytest.fixture
def clientes(demo):
    return {i: atuar_como(Client(), i) for i in (A, B, C)}


def pessoa(id_externo):
    return Pessoa.objects.get(fonte="simulada", id_externo=id_externo)


def lote_direto(campanha, **campos):
    """Só para testes de modelo: as operações são o único caminho de escrita."""
    dados = dict(
        campanha=campanha, nome="Lote de teste", escopo_institucional=True,
        confirmado_em=datetime(2026, 10, 4, 12, tzinfo=UTC), operador=A,
    )
    dados.update(campos)
    return LoteDeMobilizacao.objects.create(**dados)


def agora():
    return timezone.now()

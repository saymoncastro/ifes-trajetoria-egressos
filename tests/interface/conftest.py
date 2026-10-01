"""Fixtures dos testes da interface (Feature 008).

Toda a interface só existe em modo de demonstração; aqui ele fica ligado por padrão, e cada
teste que verifica o modo desligado o desliga explicitamente. O relógio é controlado:
nenhum teste depende do relógio real (research R18).
"""

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c


@pytest.fixture(autouse=True)
def modo_demonstracao(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


@pytest.fixture(autouse=True)
def relogio(monkeypatch):
    """`relogio.agora` é o "agora" de toda leitura de relógio (`timezone.now`)."""
    relogio = ci.Relogio(c.NO_PERIODO)
    monkeypatch.setattr("django.utils.timezone.now", lambda: relogio.agora)
    return relogio


@pytest.fixture
def cenario(db):
    return ci.cenario_baseline()

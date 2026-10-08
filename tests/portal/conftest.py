"""Fixtures dos testes da Feature 024 (Início do egresso e shell do Portal).

O Portal só existe em modo de demonstração; aqui ele fica ligado por padrão, como o próprio
Portal (`TRAJETORIA_PORTAL`, research R8). Cada teste que verifica um dos dois desligado o
desliga explicitamente. O relógio é controlado como nos testes da interface e da 021.
"""

import pytest

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn
from tests.participacao import construcao as c


@pytest.fixture(autouse=True)
def modo_demonstracao(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


@pytest.fixture(autouse=True)
def relogio(monkeypatch):
    relogio = ci.Relogio(c.NO_PERIODO)
    monkeypatch.setattr("django.utils.timezone.now", lambda: relogio.agora)
    return relogio


@pytest.fixture(autouse=True)
def sem_video(monkeypatch):
    """Sem o renderizador, a página da trajetória é a da 021 (022 FR-037). Os testes que
    verificam o atalho do vídeo o ligam explicitamente."""
    monkeypatch.setattr("trajetoria.video.renderizador.disponivel", lambda: False)


@pytest.fixture
def cenario(db):
    return cn.cenario_narrativa()

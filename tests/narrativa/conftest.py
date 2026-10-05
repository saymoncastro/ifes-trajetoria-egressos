"""Fixtures dos testes da Feature 021 (Minha trajetória).

A página só existe em modo de demonstração; aqui ele fica ligado por padrão. O relógio é
controlado como nos testes da interface: nenhum teste depende do relógio real.
"""

from datetime import date

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
    """Os testes da 021 verificam a página sem o vídeo da 022, que tem testes próprios
    (`tests/video/`). Com o renderizador indisponível, a página é exatamente a da 021
    (022 FR-037), mesmo numa máquina que tenha o Node instalado."""
    monkeypatch.setattr("trajetoria.video.renderizador.disponivel", lambda: False)


@pytest.fixture
def referencia():
    return date(2026, 10, 4)


@pytest.fixture
def cenario(db):
    return cn.cenario_narrativa()

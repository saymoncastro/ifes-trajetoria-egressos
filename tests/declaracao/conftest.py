import pytest
from django.utils import timezone

from tests.participacao.construcao import NO_PERIODO


@pytest.fixture(autouse=True)
def ambiente(settings, monkeypatch):
    settings.TRAJETORIA_DEMONSTRACAO = True
    monkeypatch.setattr(timezone, "now", lambda: NO_PERIODO)

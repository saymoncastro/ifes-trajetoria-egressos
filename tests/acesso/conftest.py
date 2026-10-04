import pytest
from django.utils import timezone

from tests.acesso.construcao import Relogio
from trajetoria.demonstracao.cenario import preparar


@pytest.fixture(autouse=True)
def modo(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


@pytest.fixture
def preparado(db, relogio):
    preparar()


@pytest.fixture
def relogio(monkeypatch):
    r = Relogio()
    monkeypatch.setattr(timezone, "now", lambda: r.agora)
    return r

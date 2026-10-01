"""Fixtures dos testes de Campanha. `fonte_simulada` vem de `tests/conftest.py`."""

import pytest

from tests.campanha import construcao as c


@pytest.fixture
def versao_publicada():
    return c.versao_publicada()


@pytest.fixture
def versao_rascunho():
    return c.versao_rascunho()

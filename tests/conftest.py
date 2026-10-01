import pytest

from trajetoria.fonte_academica.simulada import FonteSimulada


@pytest.fixture
def fonte_simulada():
    return FonteSimulada()


@pytest.fixture
def fonte_indisponivel():
    return FonteSimulada(indisponivel=True)

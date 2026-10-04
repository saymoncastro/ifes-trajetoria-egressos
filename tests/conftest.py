import pytest

from trajetoria.fonte_academica.simulada import FonteSimulada


@pytest.fixture
def fonte_simulada():
    return FonteSimulada()


@pytest.fixture
def fonte_indisponivel():
    return FonteSimulada(indisponivel=True)


@pytest.fixture(autouse=True)
def chaves_de_acesso(settings):
    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = "a1" * 32
    settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO = "b2" * 32


@pytest.fixture(autouse=True)
def limpar_cache_acesso():
    from django.core.cache import caches

    caches["acesso"].clear()


@pytest.fixture(autouse=True)
def chaves_de_declaracao(settings):
    from cryptography.fernet import Fernet

    settings.TRAJETORIA_CHAVE_SELO_DECLARACAO = Fernet.generate_key().decode()
    settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO = Fernet.generate_key().decode()

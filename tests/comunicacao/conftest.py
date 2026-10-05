import pytest


@pytest.fixture(autouse=True)
def ambiente(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.TRAJETORIA_COMUNICACAO_TESTE = True
    settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO = "http://127.0.0.1:8000/acesso/"
    settings.TRAJETORIA_ENVIO_REAL = ""

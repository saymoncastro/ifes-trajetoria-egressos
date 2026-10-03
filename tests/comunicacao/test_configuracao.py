import pytest

from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.seguranca import transporte_local, validar_url


@pytest.mark.parametrize(
    "setting,valor",
    [
        ("EMAIL_BACKEND", ""),
        ("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"),
        ("TRAJETORIA_COMUNICACAO_TESTE", False),
        ("TRAJETORIA_DEMONSTRACAO", False),
        ("DEFAULT_FROM_EMAIL", "real@external.test"),
    ],
)
def test_config_insegura(settings, setting, valor):
    setattr(settings, setting, valor)
    with pytest.raises(RecusaComunicacao):
        transporte_local()


@pytest.mark.parametrize(
    "setting,valor",
    [
        ("EMAIL_HOST", "smtp.real.test"),
        ("EMAIL_HOST", "localhost"),
        ("EMAIL_PORT", 25),
        ("EMAIL_HOST_USER", "credencial"),
        ("EMAIL_HOST_PASSWORD", "sentinela"),
        ("EMAIL_USE_TLS", True),
        ("EMAIL_USE_SSL", True),
        ("EMAIL_TIMEOUT", None),
    ],
)
def test_smtp_inseguro(settings, setting, valor):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "127.0.0.1"
    settings.EMAIL_PORT = 1025
    settings.EMAIL_HOST_USER = settings.EMAIL_HOST_PASSWORD = ""
    settings.EMAIL_USE_TLS = settings.EMAIL_USE_SSL = False
    settings.EMAIL_TIMEOUT = 5
    setattr(settings, setting, valor)
    with pytest.raises(RecusaComunicacao):
        transporte_local()


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/demonstracao/",
        "http://localhost:8000/demonstracao/",
        "http://127.0.0.1:8000/demonstracao/?pessoa=1",
        "http://127.0.0.1:8000/demonstracao/#x",
        "http://user@127.0.0.1:8000/demonstracao/",
        "http://127.0.0.1:25/demonstracao/",
        "http://127.0.0.1:8000/other/",
        "http://127.0.0.1:bad/demonstracao/",
    ],
)
def test_url_insegura(url):
    with pytest.raises(RecusaComunicacao):
        validar_url(url)

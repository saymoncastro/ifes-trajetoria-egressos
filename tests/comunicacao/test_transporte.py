"""Fronteira de transporte por modos (020 research R8, FR-032 a FR-034; T024)."""

import pytest
from django.core.mail.backends.smtp import EmailBackend

from trajetoria.academico.models import Pessoa
from trajetoria.comunicacao.seguranca import RecusaDeTransporte
from trajetoria.comunicacao.transporte import transporte_de_envio

pytestmark = pytest.mark.django_db
SMTP = "django.core.mail.backends.smtp.EmailBackend"


@pytest.fixture(autouse=True)
def sem_conexao(monkeypatch):
    def proibido(*_, **__):
        raise AssertionError("nenhuma recusa pode abrir conexão")

    monkeypatch.setattr(EmailBackend, "open", proibido)


def _recusa(categoria=None):
    with pytest.raises(RecusaDeTransporte) as exc:
        transporte_de_envio()
    if categoria:
        assert exc.value.categoria == categoria


def _demonstracao(settings):
    settings.EMAIL_BACKEND = SMTP
    settings.EMAIL_HOST = "127.0.0.1"
    settings.EMAIL_PORT = 1025
    settings.EMAIL_HOST_USER = settings.EMAIL_HOST_PASSWORD = ""
    settings.EMAIL_USE_TLS = settings.EMAIL_USE_SSL = False
    settings.EMAIL_TIMEOUT = 5
    settings.TRAJETORIA_COMUNICACAO_TESTE = False


def _real(settings):
    settings.TRAJETORIA_ENVIO_REAL = "1"
    settings.TRAJETORIA_DEMONSTRACAO = False
    settings.EMAIL_BACKEND = SMTP
    settings.EMAIL_HOST = "smtp.ifes.example"
    settings.EMAIL_PORT = 587
    settings.EMAIL_HOST_USER = "conta"
    settings.EMAIL_HOST_PASSWORD = "segredo-de-teste"
    settings.EMAIL_USE_TLS, settings.EMAIL_USE_SSL = True, False
    settings.EMAIL_TIMEOUT = 5
    settings.TRAJETORIA_REMETENTE_INSTITUCIONAL = "Ifes — Egressos <egressos@ifes.example>"
    settings.TRAJETORIA_URL_ENTRADA = "https://egressos.ifes.example/acesso/"
    Pessoa.objects.create(fonte="fonte_real_de_teste", id_externo="R-1")


def test_teste_so_com_marcador(settings):
    assert transporte_de_envio().modo == "teste"
    settings.TRAJETORIA_COMUNICACAO_TESTE = False
    _recusa("transporte_inseguro")


def test_demonstracao_com_as_barreiras_da_016(settings):
    _demonstracao(settings)
    assert transporte_de_envio().modo == "demonstracao"


@pytest.mark.parametrize(
    "setting,valor",
    [
        ("EMAIL_BACKEND", ""), ("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"),
        ("EMAIL_HOST", "smtp.real.test"), ("EMAIL_HOST", "localhost"), ("EMAIL_PORT", 25),
        ("EMAIL_HOST_USER", "credencial"), ("EMAIL_HOST_PASSWORD", "sentinela"),
        ("EMAIL_USE_TLS", True), ("EMAIL_USE_SSL", True), ("EMAIL_TIMEOUT", None),
        ("DEFAULT_FROM_EMAIL", "real@external.test"),
        ("TRAJETORIA_URL_ENTRADA_DEMONSTRACAO", "https://egressos.ifes.example/acesso/"),
    ],
)
def test_demonstracao_insegura(settings, setting, valor):
    _demonstracao(settings)
    setattr(settings, setting, valor)
    _recusa()


def test_demonstracao_desligada(settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    _recusa("modo_desligado")


def test_demonstracao_recusa_base_real(settings):
    Pessoa.objects.create(fonte="fonte_real_de_teste", id_externo="R-1")
    _recusa("origem_indevida")


@pytest.mark.parametrize("valor", ["yes", "true", "2", "on"])
def test_valor_ambiguo_nunca_liga(settings, valor):
    settings.TRAJETORIA_ENVIO_REAL = valor
    _recusa("transporte_inseguro")


def test_real_valido_so_como_validacao_de_fronteira(settings):
    _real(settings)
    transporte = transporte_de_envio()
    assert transporte.modo == "real" and transporte.use_tls
    assert "segredo" not in repr(transporte)


@pytest.mark.parametrize(
    "setting,valor,categoria",
    [
        ("TRAJETORIA_DEMONSTRACAO", True, "transporte_inseguro"),
        ("EMAIL_BACKEND", "django.core.mail.backends.locmem.EmailBackend", "transporte_inseguro"),
        ("EMAIL_USE_TLS", False, "transporte_inseguro"),
        ("EMAIL_USE_SSL", True, "transporte_inseguro"),
        ("EMAIL_HOST_USER", "", "transporte_inseguro"),
        ("EMAIL_HOST_PASSWORD", "", "transporte_inseguro"),
        ("TRAJETORIA_REMETENTE_INSTITUCIONAL", "", "remetente_inseguro"),
        ("TRAJETORIA_REMETENTE_INSTITUCIONAL", "x <a@example.invalid>", "remetente_inseguro"),
        ("TRAJETORIA_REMETENTE_INSTITUCIONAL", "a\r\nBcc: b@c.d", "remetente_inseguro"),
        ("TRAJETORIA_URL_ENTRADA", "", "url_insegura"),
        ("TRAJETORIA_URL_ENTRADA", "http://egressos.ifes.example/acesso/", "url_insegura"),
        ("TRAJETORIA_URL_ENTRADA", "https://egressos.ifes.example/acesso/?t=1", "url_insegura"),
        # Code review #2: porta inválida (settings converte valor não numérico em -1).
        ("EMAIL_PORT", -1, "transporte_inseguro"),
        ("EMAIL_PORT", 0, "transporte_inseguro"),
        ("EMAIL_PORT", 70000, "transporte_inseguro"),
        ("EMAIL_PORT", "587", "transporte_inseguro"),
        ("EMAIL_PORT", True, "transporte_inseguro"),
    ],
)
def test_real_recusa_cada_exigencia_isoladamente(settings, setting, valor, categoria):
    _real(settings)
    setattr(settings, setting, valor)
    _recusa(categoria)


def test_real_recusa_base_com_dados_simulados(settings):
    _real(settings)
    Pessoa.objects.create(fonte="simulada", id_externo="SIM-P-0001")
    _recusa("origem_indevida")

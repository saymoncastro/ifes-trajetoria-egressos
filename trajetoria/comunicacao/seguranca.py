"""Barreiras específicas da demonstração 016, não política de envio produtivo."""

from dataclasses import dataclass

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.fonte_academica.simulada import FonteSimulada


def validar_origem():
    if (
        Pessoa.objects.exclude(fonte=FonteSimulada.codigo).exists()
        or ConclusaoAcademica.objects.exclude(fonte=FonteSimulada.codigo).exists()
    ):
        raise RecusaComunicacao("origem_indevida", 422)


def validar_endereco(endereco):
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email

    if not isinstance(endereco, str) or any(c in endereco for c in "\r\n<>,; \t"):
        raise RecusaComunicacao("contato_inseguro", 422)
    try:
        validate_email(endereco)
    except ValidationError:
        raise RecusaComunicacao("contato_inseguro", 422) from None
    if endereco.rsplit("@", 1)[-1].lower() != "example.invalid":
        raise RecusaComunicacao("contato_inseguro", 422)


NOME_REMETENTE = "Trajetória Ifes — demonstração institucional"
MAILBOX_REMETENTE = "trajetoria@example.invalid"
REMETENTE = f"{NOME_REMETENTE} <{MAILBOX_REMETENTE}>"
SMTP = "django.core.mail.backends.smtp.EmailBackend"
LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


def validar_url(url):
    from urllib.parse import urlsplit

    try:
        u = urlsplit(url)
        segura = (
            isinstance(url, str)
            and not any(ord(c) <= 32 for c in url)
            and u.scheme == "http"
            and u.hostname in ("127.0.0.1", "::1")
            and u.port == 8000
            and u.path == "/demonstracao/"
            and u.username is None
            and u.password is None
            and not u.query
            and not u.fragment
        )
    except (ValueError, TypeError):
        segura = False
    if not segura:
        raise RecusaComunicacao("url_insegura", 422)
    return url


@dataclass(frozen=True)
class TransporteLocal:
    backend: str
    host: str = "127.0.0.1"
    port: int = 1025

    def conexao(self):
        from django.core.mail import get_connection

        return get_connection(
            backend=self.backend,
            fail_silently=False,
            host=self.host,
            port=self.port,
            username="",
            password="",
            use_tls=False,
            use_ssl=False,
            timeout=5,
        )


def transporte_local():
    from django.conf import settings

    if not settings.TRAJETORIA_DEMONSTRACAO:
        raise RecusaComunicacao("modo_desligado", 404)
    validar_url(settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO)
    if settings.DEFAULT_FROM_EMAIL != MAILBOX_REMETENTE:
        raise RecusaComunicacao("remetente_inseguro", 422)
    backend = settings.EMAIL_BACKEND
    if backend == LOCMEM and settings.TRAJETORIA_COMUNICACAO_TESTE is True:
        return TransporteLocal(backend)
    if backend != SMTP or (
        settings.EMAIL_HOST not in ("127.0.0.1", "::1")
        or settings.EMAIL_PORT != 1025
        or settings.EMAIL_HOST_USER
        or settings.EMAIL_HOST_PASSWORD
        or settings.EMAIL_USE_TLS
        or settings.EMAIL_USE_SSL
        or settings.EMAIL_TIMEOUT != 5
    ):
        raise RecusaComunicacao("transporte_inseguro", 422)
    return TransporteLocal(backend, settings.EMAIL_HOST, settings.EMAIL_PORT)


def validar_conteudo(texto, html):
    """Mesmo critério na prévia e no envio: nome de Campanha ou Pessoa com link ou markup
    ativo recusa o convite inteiro, em vez de aparecer só no POST."""
    import re

    if re.search(
        r"<\s*(script|img|link|iframe|object|embed|base)\b|\bon\w+\s*=|url\s*\(|@import", html, re.I
    ):
        raise RecusaComunicacao("conteudo_inseguro", 422)
    for url in re.findall(r'https?://[^\s<>"\']+', texto + "\n" + html):
        try:
            validar_url(url)
        except RecusaComunicacao:
            raise RecusaComunicacao("conteudo_inseguro", 422) from None


def validar_mensagem(msg):
    if (
        msg.from_email != REMETENTE
        or len(msg.to) != 1
        or msg.cc
        or msg.bcc
        or msg.attachments
        or msg.extra_headers
    ):
        raise RecusaComunicacao("mensagem_insegura", 422)
    validar_endereco(msg.to[0])
    if len(msg.alternatives) != 1 or msg.alternatives[0].mimetype != "text/html":
        raise RecusaComunicacao("mensagem_insegura", 422)
    if any(c in msg.subject for c in "\r\n"):
        raise RecusaComunicacao("mensagem_insegura", 422)
    validar_conteudo(msg.body, msg.alternatives[0].content)

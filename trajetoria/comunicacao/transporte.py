"""Fronteira de transporte por modos (Feature 020; research R8; contracts/transporte.md).

Três modos exclusivos, decididos **antes** de qualquer mensagem ou conexão. Nenhum padrão
implícito habilita envio; qualquer outra combinação recusa.

- `teste`: backend em memória, só sob o marcador de teste da suíte.
- `demonstracao`: as barreiras da 016 — SMTP em loopback:1025, sem credenciais nem TLS,
  remetente e destinatários `example.invalid`, URL local, base só de dados fictícios.
- `real`: **desativado** até os Gates A e B (DP-2010). Só `TRAJETORIA_ENVIO_REAL == "1"`
  o pede; mesmo assim exige demonstração desligada, SMTP com TLS ou SSL, credenciais por
  ambiente, remetente institucional, URL `https` e base sem dados simulados. Com a
  demonstração desligada o middleware responde 404 a toda rota: nesta base o modo real
  existe só como validação desta fronteira.

O fornecedor nunca é nomeado: a troca de SMTP por API de provedor fica restrita a este
módulo (FR-034).
"""

from dataclasses import dataclass

from django.conf import settings

from trajetoria.comunicacao.seguranca import (
    DEMONSTRACAO,
    MAILBOX_REMETENTE,
    REAL,
    REMETENTE,
    TESTE,
    RecusaDeTransporte,
    validar_remetente,
    validar_url,
)

SMTP = "django.core.mail.backends.smtp.EmailBackend"
LOCMEM = "django.core.mail.backends.locmem.EmailBackend"

__all__ = ["Transporte", "RecusaDeTransporte", "transporte_de_envio"]


@dataclass(frozen=True)
class Transporte:
    modo: str
    backend: str
    remetente: str
    url: str
    host: str = "127.0.0.1"
    port: int = 1025
    username: str = ""
    password: str = ""
    use_tls: bool = False
    use_ssl: bool = False

    def conexao(self):
        from django.core.mail import get_connection

        return get_connection(
            backend=self.backend,
            fail_silently=False,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls,
            use_ssl=self.use_ssl,
            timeout=5,
        )

    def __repr__(self) -> str:  # nunca a senha
        return f"Transporte(modo={self.modo!r})"


def _base_somente_simulada() -> bool:
    from trajetoria.demonstracao.base import base_somente_simulada

    return base_somente_simulada()


def _base_contem_simulados() -> bool:
    from trajetoria.academico.models import ConclusaoAcademica, Pessoa
    from trajetoria.demonstracao.base import _FONTES_ADMITIDAS

    return (
        Pessoa.objects.filter(fonte__in=_FONTES_ADMITIDAS).exists()
        or ConclusaoAcademica.objects.filter(fonte__in=_FONTES_ADMITIDAS).exists()
    )


def _real() -> Transporte:
    if settings.TRAJETORIA_DEMONSTRACAO:
        raise RecusaDeTransporte("transporte_inseguro")
    if (
        settings.EMAIL_BACKEND != SMTP
        or not settings.EMAIL_HOST
        or not isinstance(settings.EMAIL_PORT, int)
        or isinstance(settings.EMAIL_PORT, bool)
        or not 1 <= settings.EMAIL_PORT <= 65535
        or not (settings.EMAIL_USE_TLS or settings.EMAIL_USE_SSL)
        or (settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL)
        or not settings.EMAIL_HOST_USER
        or not settings.EMAIL_HOST_PASSWORD
        or settings.EMAIL_TIMEOUT != 5
    ):
        raise RecusaDeTransporte("transporte_inseguro")
    remetente = validar_remetente(settings.TRAJETORIA_REMETENTE_INSTITUCIONAL, REAL)
    url = validar_url(settings.TRAJETORIA_URL_ENTRADA, REAL)
    if _base_contem_simulados():
        raise RecusaDeTransporte("origem_indevida")
    return Transporte(
        REAL, SMTP, remetente, url, settings.EMAIL_HOST, settings.EMAIL_PORT,
        settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD,
        bool(settings.EMAIL_USE_TLS), bool(settings.EMAIL_USE_SSL),
    )


def _local() -> Transporte:
    if not settings.TRAJETORIA_DEMONSTRACAO:
        raise RecusaDeTransporte("modo_desligado", 404)
    url = validar_url(settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO, DEMONSTRACAO)
    if settings.DEFAULT_FROM_EMAIL != MAILBOX_REMETENTE:
        raise RecusaDeTransporte("remetente_inseguro")
    if not _base_somente_simulada():
        raise RecusaDeTransporte("origem_indevida")
    backend = settings.EMAIL_BACKEND
    if backend == LOCMEM and settings.TRAJETORIA_COMUNICACAO_TESTE is True:
        return Transporte(TESTE, LOCMEM, REMETENTE, url)
    if backend != SMTP or (
        settings.EMAIL_HOST not in ("127.0.0.1", "::1")
        or settings.EMAIL_PORT != 1025
        or settings.EMAIL_HOST_USER
        or settings.EMAIL_HOST_PASSWORD
        or settings.EMAIL_USE_TLS
        or settings.EMAIL_USE_SSL
        or settings.EMAIL_TIMEOUT != 5
    ):
        raise RecusaDeTransporte("transporte_inseguro")
    return Transporte(DEMONSTRACAO, SMTP, REMETENTE, url, settings.EMAIL_HOST, settings.EMAIL_PORT)


def transporte_de_envio() -> Transporte:
    pedido = settings.TRAJETORIA_ENVIO_REAL
    if pedido == "1":
        return _real()
    if pedido not in ("", "0", None):
        raise RecusaDeTransporte("transporte_inseguro")  # valor ambíguo nunca liga nada
    return _local()

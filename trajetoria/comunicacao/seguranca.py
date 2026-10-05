"""Validações do convite e do destino, por modo de transporte (Feature 020; research R8;
contracts/transporte.md). Herdadas da 016.

- Teste e demonstração: as barreiras da 016 (destinatário e remetente só `example.invalid`,
  URL local `/acesso/`). Destinatário e transporte são barreiras independentes.
- Real: destinatário válido em qualquer domínio, remetente institucional configurado e URL
  `https` neutra. Só existe como validação de fronteira até os Gates A e B (DP-2010).

Toda recusa é `RecusaDeTransporte(categoria)`, sem texto de exceção externa.
"""

import re
from email.utils import parseaddr
from urllib.parse import urlsplit

from trajetoria.contato.endereco import EnderecoInvalido, normalizar_email

TESTE, DEMONSTRACAO, REAL = "teste", "demonstracao", "real"
MODOS_LOCAIS = (TESTE, DEMONSTRACAO)
DOMINIO_DE_DEMONSTRACAO = "example.invalid"
NOME_REMETENTE = "Trajetória Ifes — demonstração institucional"
MAILBOX_REMETENTE = "trajetoria@example.invalid"
REMETENTE = f"{NOME_REMETENTE} <{MAILBOX_REMETENTE}>"


class RecusaDeTransporte(Exception):
    """Somente categoria fixa; nunca dados de uma exceção externa."""

    def __init__(self, categoria="transporte_inseguro", status=422):
        self.categoria = categoria
        self.status = status
        super().__init__(categoria)


def _sem_controle(texto) -> bool:
    return isinstance(texto, str) and not any(ord(c) <= 32 for c in texto)


def validar_url(url, modo=DEMONSTRACAO):
    """Demonstração e teste: `http://127.0.0.1:8000/acesso/` (016, revisada pela 018). Real:
    `https`, sem credenciais, query ou fragmento. Nunca identidade, token ou formação."""
    try:
        u = urlsplit(url)
        comum = (
            _sem_controle(url)
            and u.username is None
            and u.password is None
            and not u.query
            and not u.fragment
        )
        if modo in MODOS_LOCAIS:
            segura = (
                comum
                and u.scheme == "http"
                and u.hostname in ("127.0.0.1", "::1")
                and u.port == 8000
                and u.path == "/acesso/"
            )
        else:
            segura = comum and u.scheme == "https" and bool(u.hostname) and u.port in (None, 443)
    except (ValueError, TypeError):
        segura = False
    if not segura:
        raise RecusaDeTransporte("url_insegura")
    return url


def validar_destinatario(endereco, modo=DEMONSTRACAO) -> str:
    try:
        normalizado = normalizar_email(endereco)
    except EnderecoInvalido:
        raise RecusaDeTransporte("contato_inseguro") from None
    if normalizado != endereco:
        raise RecusaDeTransporte("contato_inseguro")  # só endereço simples, já normalizado
    if modo in MODOS_LOCAIS and normalizado.rsplit("@", 1)[1] != DOMINIO_DE_DEMONSTRACAO:
        raise RecusaDeTransporte("contato_inseguro")
    return normalizado


def validar_remetente(remetente, modo=DEMONSTRACAO) -> str:
    if modo in MODOS_LOCAIS:
        if remetente != REMETENTE:
            raise RecusaDeTransporte("remetente_inseguro")
        return remetente
    if not isinstance(remetente, str) or any(c in remetente for c in "\r\n"):
        raise RecusaDeTransporte("remetente_inseguro")
    _, mailbox = parseaddr(remetente)
    try:
        if not mailbox or normalizar_email(mailbox) != mailbox:
            raise EnderecoInvalido
    except EnderecoInvalido:
        raise RecusaDeTransporte("remetente_inseguro") from None
    if mailbox.rsplit("@", 1)[1] == DOMINIO_DE_DEMONSTRACAO:
        raise RecusaDeTransporte("remetente_inseguro")
    return remetente


def validar_conteudo(texto, html, url_permitida, modo=DEMONSTRACAO):
    """Sem markup ativo, recurso externo, pixel ou rastreador; toda URL do conteúdo é a URL
    neutra permitida do modo (016 FR-018; 020 FR-027, FR-030)."""
    if re.search(
        r"<\s*(script|img|link|iframe|object|embed|base)\b|\bon\w+\s*=|url\s*\(|@import", html, re.I
    ):
        raise RecusaDeTransporte("conteudo_inseguro")
    for url in re.findall(r'https?://[^\s<>"\']+', texto + "\n" + html):
        if url != url_permitida:
            raise RecusaDeTransporte("conteudo_inseguro")
    validar_url(url_permitida, modo)


def validar_mensagem(msg, *, modo=DEMONSTRACAO, remetente=REMETENTE, url_permitida):
    if (
        msg.from_email != remetente
        or len(msg.to) != 1
        or msg.cc
        or msg.bcc
        or msg.attachments
        or msg.extra_headers
        or msg.reply_to
    ):
        raise RecusaDeTransporte("mensagem_insegura")
    validar_remetente(msg.from_email, modo)
    validar_destinatario(msg.to[0], modo)
    if len(msg.alternatives) != 1 or msg.alternatives[0].mimetype != "text/html":
        raise RecusaDeTransporte("mensagem_insegura")
    if any(c in msg.subject for c in "\r\n"):
        raise RecusaDeTransporte("mensagem_insegura")
    validar_conteudo(msg.body, msg.alternatives[0].content, url_permitida, modo)

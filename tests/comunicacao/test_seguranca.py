"""Barreiras do convite por modo (016, revistas pela 020 research R8)."""

import pytest

from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.seguranca import (
    REAL,
    RecusaDeTransporte,
    validar_destinatario,
    validar_mensagem,
    validar_url,
)

URL = "http://127.0.0.1:8000/acesso/"


@pytest.mark.parametrize(
    "endereco",
    [
        "real@external.test",
        "a@sub.example.invalid",
        "a@example.invalid.evil",
        "Name <a@example.invalid>",
        "a@example.invalid,b@example.invalid",
        "a@example.invalid\r\nBcc:x",
        "invalido",
    ],
)
def test_dominio_independente_do_smtp(endereco, settings):
    settings.EMAIL_HOST = "smtp.incorreto.test"
    with pytest.raises(RecusaDeTransporte):
        validar_destinatario(endereco)


def test_dominio_exato():
    validar_destinatario("a@example.invalid")
    with pytest.raises(RecusaDeTransporte):
        validar_destinatario("a@EXAMPLE.INVALID")  # só endereço já normalizado


def test_modo_real_aceita_qualquer_dominio_valido():
    assert validar_destinatario("egresso@exemplo.org", REAL) == "egresso@exemplo.org"
    with pytest.raises(RecusaDeTransporte):
        validar_destinatario("Nome <egresso@exemplo.org>", REAL)


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("from_email", "Outro <trajetoria@example.invalid>"),
        ("from_email", "Institucional <real@external.test>"),
        ("to", ["a@example.invalid", "b@example.invalid"]),
        ("cc", ["a@example.invalid"]),
        ("bcc", ["a@example.invalid"]),
        ("reply_to", ["a@example.invalid"]),
        ("subject", "a\nb"),
    ],
)
def test_mensagem_final_adulterada(campo, valor):
    msg = renderizar_convite(None, "C", URL).mensagem("a@example.invalid")
    setattr(msg, campo, valor)
    with pytest.raises(RecusaDeTransporte):
        validar_mensagem(msg, url_permitida=URL)


def test_url_do_conteudo_deve_ser_a_neutra():
    msg = renderizar_convite(None, "C", URL).mensagem("a@example.invalid")
    msg.body += "\nhttp://127.0.0.1:8000/acesso/?pessoa=1"
    with pytest.raises(RecusaDeTransporte):
        validar_mensagem(msg, url_permitida=URL)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/demonstracao/",
        "https://example.com/acesso/",
        "http://localhost:8000/acesso/",
        "http://127.0.0.1:8000/acesso/?pessoa=1",
        "http://127.0.0.1:8000/acesso/#x",
        "http://user@127.0.0.1:8000/acesso/",
        "http://127.0.0.1:25/acesso/",
        "http://127.0.0.1:8000/other/",
        "http://127.0.0.1:bad/acesso/",
    ],
)
def test_url_insegura_na_demonstracao(url):
    with pytest.raises(RecusaDeTransporte):
        validar_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://egressos.ifes.example/acesso/",
        "https://egressos.ifes.example/acesso/?token=1",
        "https://egressos.ifes.example/acesso/#pessoa",
        "https://u:s@egressos.ifes.example/acesso/",
        "https:///acesso/",
        "https://egressos.ifes.example/ac esso/",
    ],
)
def test_url_insegura_no_modo_real(url):
    with pytest.raises(RecusaDeTransporte):
        validar_url(url, REAL)
    assert validar_url("https://egressos.ifes.example/acesso/", REAL)

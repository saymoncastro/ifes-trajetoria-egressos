import pytest

from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.seguranca import validar_endereco, validar_mensagem


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
    with pytest.raises(RecusaComunicacao):
        validar_endereco(endereco)


def test_dominio_exato():
    validar_endereco("a@EXAMPLE.INVALID")


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("from_email", "Outro <trajetoria@example.invalid>"),
        ("from_email", "Institucional <real@external.test>"),
        ("to", ["a@example.invalid", "b@example.invalid"]),
        ("cc", ["a@example.invalid"]),
        ("bcc", ["a@example.invalid"]),
    ],
)
def test_mensagem_final_adulterada(campo, valor):
    msg = renderizar_convite(None, "C", "http://127.0.0.1:8000/acesso/").mensagem(
        "a@example.invalid"
    )
    setattr(msg, campo, valor)
    with pytest.raises(RecusaComunicacao):
        validar_mensagem(msg)


def test_remetente_institucional_permitido():
    msg = renderizar_convite(None, "C", "http://127.0.0.1:8000/acesso/").mensagem(
        "a@example.invalid"
    )
    validar_mensagem(msg)

from email.utils import parseaddr

import pytest

from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.seguranca import RecusaDeTransporte

URL = "http://127.0.0.1:8000/acesso/"


def test_mime_fixo():
    c = renderizar_convite(None, "Campanha", URL)
    msg = c.mensagem("sim-p-0001@example.invalid")
    assert parseaddr(msg.from_email) == (
        "Trajetória Ifes — demonstração institucional",
        "trajetoria@example.invalid",
    )
    assert msg.to == ["sim-p-0001@example.invalid"]
    assert msg.body == c.texto
    assert msg.alternatives[0].content == c.html
    assert msg.alternatives[0].mimetype == "text/html"
    assert msg.message().get_content_type() == "multipart/alternative"
    assert not msg.cc and not msg.bcc and not msg.attachments


@pytest.mark.parametrize(
    "destino",
    [
        "real@dominio.com",
        "Nome <a@example.invalid>",
        "a@example.invalid\r\nBcc: x",
        "a@sub.example.invalid",
        " a@example.invalid",
    ],
)
def test_destinatario_simples_e_reservado(destino):
    c = renderizar_convite(None, "Campanha", URL)
    with pytest.raises(RecusaDeTransporte):
        c.mensagem(destino)

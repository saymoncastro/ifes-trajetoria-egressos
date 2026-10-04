from email.utils import parseaddr

import pytest
from django.test import Client

from trajetoria.comunicacao.convite import renderizar_convite


def test_mime_fixo():
    c = renderizar_convite(None, "Campanha", "http://127.0.0.1:8000/acesso/")
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


def test_cta_neutro_nao_muda_dominio(campanha, snapshot):
    antes = snapshot()
    c = renderizar_convite(None, campanha.nome, "http://127.0.0.1:8000/acesso/")
    assert Client().get("/acesso/").status_code == 200
    assert c.url.endswith("/acesso/")
    assert snapshot() == antes


@pytest.mark.parametrize(
    "destino",
    [
        "real@dominio.com",
        "Nome <a@example.invalid>",
        "a@example.invalid\r\nBcc: x",
        "a@sub.example.invalid",
    ],
)
def test_destinatario_simples_e_reservado(destino):
    from trajetoria.comunicacao.acesso import RecusaComunicacao

    c = renderizar_convite(None, "Campanha", "http://127.0.0.1:8000/acesso/")
    with pytest.raises(RecusaComunicacao):
        c.mensagem(destino)

from html.parser import HTMLParser

import pytest
from django.core import mail

from tests.editor.construcao_editor import A, B
from trajetoria.comunicacao.convite import renderizar_convite

pytestmark = pytest.mark.django_db


def test_preview_com_mesmo_renderer(campanha, clientes, snapshot):
    antes = snapshot()
    resposta = clientes[B].get(f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/")
    assert resposta.context["destinatario"] == "sim-p-0002@example.invalid"
    convite = renderizar_convite(
        "Bruno Exemplo", campanha.nome, "http://127.0.0.1:8000/demonstracao/"
    )
    assert resposta.context["convite"] == convite
    assert b'sandbox=""' in resposta.content
    assert not getattr(mail, "outbox", [])
    assert snapshot() == antes


def test_generico_sem_contato(campanha, clientes):
    campanha.ano_minimo = 3000
    campanha.save()
    resposta = clientes[A].get(f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/")
    assert resposta.context["destinatario"] is None
    assert "Olá!" in resposta.context["convite"].texto


def test_falha_renderer_segura(campanha, clientes, monkeypatch, caplog):
    from trajetoria.comunicacao import views

    def falhar(*args):
        raise RuntimeError("SENTINELA-email-corpo-credencial")

    monkeypatch.setattr(views, "renderizar_convite", falhar, raising=False)
    resposta = clientes[A].get(f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/")
    assert resposta.status_code == 422
    assert "SENTINELA" not in caplog.text + resposta.content.decode()


def test_srcdoc_e_codigo_escapados_mesmo_com_safe_string(campanha, clientes):
    resposta = clientes[A].get(f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/")

    class Inspecao(HTMLParser):
        def __init__(self):
            super().__init__()
            self.iframes = []
            self.htmls = 0

        def handle_starttag(self, tag, attrs):
            if tag == "iframe":
                self.iframes.append(dict(attrs))
            if tag == "html":
                self.htmls += 1

    parser = Inspecao()
    parser.feed(resposta.content.decode())
    assert len(parser.iframes) == 1
    assert parser.iframes[0]["srcdoc"] == resposta.context["convite"].html
    assert parser.iframes[0]["style"].startswith("width:100%")
    assert parser.iframes[0]["sandbox"] == ""
    assert parser.htmls == 1
    assert "&lt;html lang=&quot;pt-BR&quot;&gt;" in resposta.content.decode()


def test_texto_da_previa_escapa_markup_do_nome(campanha, clientes):
    from trajetoria.academico.models import Pessoa

    Pessoa.objects.filter(id_externo="SIM-P-0001").update(nome="<script>alert(1)</script>")
    resposta = clientes[A].get(f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/")
    assert b"<script>" not in resposta.content
    assert b"Ol\xc3\xa1, &lt;script&gt;alert(1)&lt;/script&gt;!" in resposta.content

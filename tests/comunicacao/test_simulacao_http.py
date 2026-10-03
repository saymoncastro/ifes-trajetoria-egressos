import pytest
from django.core import mail
from django.test import Client

from tests.editor.construcao_editor import A, B, C, atuar_como
from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.operacoes import simular_comunicacao

pytestmark = pytest.mark.django_db


def url(c):
    return f"/acompanhamento/campanhas/{c.pk}/comunicacao/simular/"


def test_post_e_projecao_agregada(campanha, clientes):
    r = clientes[B].post(
        url(campanha),
        {"destinatario": "real@external.test", "assunto": "adulterado", "operador": A},
    )
    assert r.status_code == 200
    assert r.context["totais"]["aceitas"] == 1
    assert mail.outbox[0].to == ["sim-p-0002@example.invalid"]
    assert "individuais" not in r.context and "resultado" not in r.context
    assert "no-store" in r["Cache-Control"]
    assert not r.cookies
    assert clientes[B].get(url(campanha)).status_code == 405
    clientes[B].get(url(campanha).removesuffix("simular/"))
    assert len(mail.outbox) == 1
    clientes[B].post(url(campanha))
    assert len(mail.outbox) == 2


def test_csrf_real(campanha):
    cliente = atuar_como(Client(enforce_csrf_checks=True), B)
    assert cliente.post(url(campanha)).status_code == 403
    pagina = cliente.get(url(campanha).removesuffix("simular/"))
    assert b"csrfmiddlewaretoken" in pagina.content
    assert (
        cliente.post(
            url(campanha), {"csrfmiddlewaretoken": cliente.cookies["csrftoken"].value}
        ).status_code
        == 200
    )


def test_operacao_direta_e_rotas_nao_autorizam_egresso(campanha, clientes):
    for op in (C, "real", None):
        with pytest.raises(RecusaComunicacao):
            simular_comunicacao(campanha.pk, op)
    assert clientes[C].post(url(campanha)).status_code == 403
    assert not getattr(mail, "outbox", [])


@pytest.mark.parametrize("tipo,status", [("preflight", 422), ("inesperada", 500)])
def test_erros_http_sem_dados_sensiveis(
    campanha, clientes, monkeypatch, caplog, snapshot, tipo, status
):
    from django.core.mail.backends.locmem import EmailBackend

    from trajetoria.comunicacao import consultas

    antes = snapshot()

    def falhar(*args):
        raise RuntimeError("SENTINELA-nome-email-corpo-credencial-resposta")

    if tipo == "preflight":
        monkeypatch.setattr(consultas, "contato_ficticio", falhar)
    else:
        monkeypatch.setattr(EmailBackend, "send_messages", falhar)
    resposta = clientes[A].post(url(campanha))
    assert resposta.status_code == status
    assert "SENTINELA" not in resposta.content.decode() + caplog.text
    assert "no-store" in resposta["Cache-Control"] and not resposta.cookies
    assert "individuais" not in resposta.context and "resultado" not in resposta.context
    if tipo == "inesperada":
        assert resposta.context["totais"]["falhas"] == 1
        assert resposta.context["totais"]["nao_tentadas"] == 3
    assert not getattr(mail, "outbox", [])
    assert snapshot() == antes


def test_encerramento_entre_preview_e_post(campanha, clientes, snapshot):
    from trajetoria.campanha.operacoes import encerrar

    ampla = campanha.__class__.objects.get(nome="Demonstração — coleta ampla")
    assert clientes[A].get(url(ampla).removesuffix("simular/")).status_code == 200
    encerrar(ampla)
    antes = snapshot()
    resposta = clientes[A].post(url(ampla))
    assert resposta.status_code == 409
    preview = clientes[A].get(url(ampla).removesuffix("simular/"))
    assert preview.status_code == 200 and not preview.context["pode_simular"]
    assert b"Simular envio local" not in preview.content
    assert not getattr(mail, "outbox", [])
    assert snapshot() == antes

from smtplib import SMTPException

import pytest
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend
from django.db import connection

from tests.editor.construcao_editor import A
from trajetoria.comunicacao.operacoes import simular_comunicacao

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize("falha", [SMTPException, OSError, TimeoutError, None])
def test_falha_parcial_nao_desfaz_anteriores(campanha, monkeypatch, caplog, snapshot, falha):
    antes = snapshot()
    original = EmailBackend.send_messages
    calls = []
    conexoes = []
    fechadas = []

    original_close = EmailBackend.close

    def fechar(backend):
        fechadas.append(backend)
        return original_close(backend)

    monkeypatch.setattr(EmailBackend, "close", fechar)

    def enviar(backend, mensagens):
        assert not connection.in_atomic_block
        conexoes.append(backend)
        calls.append(mensagens[0].to[0])
        if len(calls) == 2:
            if falha:
                raise falha("SENTINELA-nome-email-corpo-credencial-resposta")
            return 0
        return original(backend, mensagens)

    monkeypatch.setattr(EmailBackend, "send_messages", enviar)
    r = simular_comunicacao(campanha.pk, A)
    assert r.totais["submetidas"] == 4
    assert r.totais["aceitas"] == 3 and r.totais["falhas"] == 1
    assert r.totais["sem_contato"] == 1
    assert len(mail.outbox) == 3 and len(set(calls)) == 4
    assert len({id(c) for c in conexoes}) == 4
    assert fechadas == conexoes
    assert "SENTINELA" not in caplog.text + repr(r)
    assert snapshot() == antes


def test_inesperada_interrompe_sem_retry(campanha, monkeypatch, caplog):
    original = EmailBackend.send_messages
    n = 0

    def enviar(backend, mensagens):
        nonlocal n
        n += 1
        if n == 2:
            raise RuntimeError("SENTINELA-credencial")
        return original(backend, mensagens)

    monkeypatch.setattr(EmailBackend, "send_messages", enviar)
    r = simular_comunicacao(campanha.pk, A)
    assert (
        r.totais["submetidas"],
        r.totais["aceitas"],
        r.totais["falhas"],
        r.totais["nao_tentadas"],
    ) == (2, 1, 1, 2)
    assert r.interrompida and len(mail.outbox) == 1
    assert "SENTINELA" not in caplog.text + repr(r)


def test_timeout_pode_ter_mensagem(campanha, monkeypatch):
    original = EmailBackend.send_messages

    def enviar(backend, mensagens):
        original(backend, mensagens)
        raise TimeoutError("sem confirmação após aceite")

    monkeypatch.setattr(EmailBackend, "send_messages", enviar)
    r = simular_comunicacao(campanha.pk, A)
    assert r.totais["aceitas"] == 0 and r.totais["falhas"] == 4
    assert len(mail.outbox) == 4


@pytest.mark.parametrize("etapa", ["barreira_final", "conexao"])
def test_erro_antes_do_send_nao_conta_tentativa(campanha, monkeypatch, etapa):
    """Interrupção antes do send: a mensagem não saiu, logo não é submetida nem falha."""
    from trajetoria.comunicacao import operacoes
    from trajetoria.comunicacao.seguranca import TransporteLocal

    n = 0
    alvo = (
        (operacoes, "validar_mensagem")
        if etapa == "barreira_final"
        else (
            TransporteLocal,
            "conexao",
        )
    )
    original = getattr(*alvo)

    def quebrar(*args):
        nonlocal n
        n += 1
        if n == 2:
            raise RuntimeError("SENTINELA-credencial")
        return original(*args)

    monkeypatch.setattr(*alvo, quebrar)
    r = simular_comunicacao(campanha.pk, A)
    assert (
        r.totais["submetidas"],
        r.totais["aceitas"],
        r.totais["falhas"],
        r.totais["nao_tentadas"],
    ) == (1, 1, 0, 3)
    assert r.interrompida and len(mail.outbox) == 1

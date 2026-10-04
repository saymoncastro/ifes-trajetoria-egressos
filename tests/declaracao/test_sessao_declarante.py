from datetime import timedelta

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory
from django.utils import timezone

from tests.declaracao.construcao import declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.acesso.sessao import encerrar, pessoa_em_uso
from trajetoria.declaracao.sessao import declaracoes_em_uso, estabelecer_declarante

pytestmark = pytest.mark.django_db


def test_sessao_uuid_exclusividade_expiracao(monkeypatch):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    r = RequestFactory().get("/declaracao/")
    r.session = SessionStore()
    r.session["acesso.pessoa"] = "anterior"
    estabelecer_declarante(r, [f.pk], c.NO_PERIODO)
    assert "acesso.pessoa" not in r.session
    assert pessoa_em_uso(r) is None
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO)
    assert declaracoes_em_uso(r) == (f.pk,)
    assert f.verificador not in repr(dict(r.session))
    # Requisição seguinte, mesma sessão: a revalidação vale por requisição (cache por request).
    seguinte = RequestFactory().get("/declaracao/")
    seguinte.session = r.session
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO + timedelta(minutes=31))
    assert declaracoes_em_uso(seguinte) is None
    encerrar(seguinte)
    assert not dict(seguinte.session)


def test_revalidacao_uma_vez_por_requisicao(monkeypatch, django_assert_num_queries):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    r = RequestFactory().get("/declaracao/")
    r.session = SessionStore()
    estabelecer_declarante(r, [f.pk], c.NO_PERIODO)
    seguinte = RequestFactory().get("/declaracao/")
    seguinte.session = r.session
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO)
    with django_assert_num_queries(1):
        assert declaracoes_em_uso(seguinte) == (f.pk,)
        assert declaracoes_em_uso(seguinte) == (f.pk,)

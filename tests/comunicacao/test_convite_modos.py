"""Renderer por modo (020 FR-027, FR-035; T025)."""

import pytest

from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.seguranca import REAL, RecusaDeTransporte

URL_DEMO = "http://127.0.0.1:8000/acesso/"
URL_REAL = "https://egressos.ifes.example/acesso/"
REMETENTE_REAL = "Ifes — Egressos <egressos@ifes.example>"
PROVISORIO = "Texto provisório — pendente de aprovação institucional"


def _real(**k):
    return renderizar_convite("Ana", "Campanha 2026", URL_REAL, modo=REAL,
                              remetente=REMETENTE_REAL, **k)


def test_demonstracao_mantem_o_texto_da_016():
    c = renderizar_convite("Ana", "C", URL_DEMO)
    assert "Abrir a demonstração" in c.texto and PROVISORIO not in c.texto


def test_real_usa_template_provisorio_marcado():
    c = _real()
    assert PROVISORIO in c.texto and PROVISORIO in c.html
    assert "fictícios" not in c.texto and "demonstração" not in c.texto
    assert "Responder à pesquisa" in c.texto and URL_REAL in c.texto and URL_REAL in c.html
    msg = c.mensagem("egresso@exemplo.org")
    assert msg.from_email == REMETENTE_REAL and msg.to == ["egresso@exemplo.org"]


def test_link_neutro_igual_para_todos_e_sem_identificadores():
    a = renderizar_convite("Ana", "C", URL_DEMO)
    b = renderizar_convite("Bruno", "C", URL_DEMO)
    assert a.url == b.url == URL_DEMO
    for convite in (a, b, _real()):
        for proibido in ("pessoa", "lote", "membro", "token", "cpf", "?", "#"):
            assert proibido not in convite.url.lower()


def test_remetente_e_url_do_modo():
    with pytest.raises(RecusaDeTransporte):
        renderizar_convite("Ana", "C", URL_DEMO, modo=REAL, remetente=REMETENTE_REAL)
    with pytest.raises(RecusaDeTransporte):
        renderizar_convite("Ana", "C", URL_REAL, modo=REAL,
                           remetente="Ifes <trajetoria@example.invalid>")
    with pytest.raises(RecusaDeTransporte):
        renderizar_convite("Ana", "C", URL_REAL)  # demonstração exige URL local


def test_destinatario_por_modo():
    with pytest.raises(RecusaDeTransporte):
        renderizar_convite("Ana", "C", URL_DEMO).mensagem("egresso@exemplo.org")
    _real().mensagem("egresso@exemplo.org")

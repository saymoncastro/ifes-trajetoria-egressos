"""Governança e escopo dos Lotes (020 FR-036, FR-037; US7; T052)."""

import pytest
from django.test import Client

from tests.editor.construcao_editor import A, B, C, atuar_como
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.operacoes import desativar_vinculo
from trajetoria.mobilizacao.acesso import RecusaDeLote
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote, previa

pytestmark = pytest.mark.django_db


def _rotas(campanha, lote):
    base = f"/acompanhamento/campanhas/{campanha.pk}/lotes/"
    return [
        ("get", base, {}),
        ("get", base + "?previa=1&unidade=Vitória", {}),
        ("post", base + "confirmar/", {"nome": "x", "unidade": "Vitória"}),
        ("get", f"{base}{lote.pk}/", {}),
        ("post", f"{base}{lote.pk}/enviar/", {}),
    ]


def test_operador_sem_vinculo_e_sem_operador(ampla, clientes):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    for metodo, url, dados in _rotas(ampla, lote):
        assert getattr(clientes[C], metodo)(url, dados).status_code == 403, url
        resposta = getattr(Client(), metodo)(url, dados)
        assert resposta.status_code == 302 and "operador" in resposta["Location"]


def test_demonstracao_desligada(ampla, clientes, settings):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    settings.TRAJETORIA_DEMONSTRACAO = False
    for metodo, url, dados in _rotas(ampla, lote):
        assert getattr(clientes[A], metodo)(url, dados).status_code == 404, url


def test_csaeg_limitada_as_suas_unidades(ampla, clientes):
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/"
    for dados in ({"nome": "x"}, {"nome": "x", "unidade": "Serra"},
                  {"nome": "x", "unidade": ["Vitória", "Serra"]}):
        assert clientes[B].post(base + "confirmar/", dados).status_code == 403
    assert clientes[B].post(base + "confirmar/",
                            {"nome": "x", "unidade": "Vitória"}).status_code == 303
    with pytest.raises(RecusaDeLote):
        previa(ampla.pk, B, {})


def test_visibilidade_dos_lotes(ampla, clientes):
    serra = confirmar_lote(ampla.pk, A, "Serra", {"unidades": ["Serra"]})
    vitoria = confirmar_lote(ampla.pk, A, "Só Vitória", {"unidades": ["Vitória"]})
    institucional = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/"
    lista = clientes[B].get(base).content.decode()
    assert "Só Vitória" in lista and "Serra" not in lista.split("<h2>Preparar")[0]
    for lote in (institucional, serra):
        assert clientes[B].get(f"{base}{lote.pk}/").status_code == 403
        with pytest.raises(RecusaDeLote):
            enviar_lote(lote.pk, B)
    assert clientes[B].get(f"{base}{vitoria.pk}/").status_code == 200
    assert clientes[A].get(f"{base}{serra.pk}/").status_code == 200


def test_vinculo_desativado_entre_confirmacao_e_envio(ampla, clientes):
    lote = confirmar_lote(ampla.pk, B, "Vitória", {"unidades": ["Vitória"]})
    for vinculo in vinculos_ativos(B):
        desativar_vinculo(vinculo)
    resposta = clientes[B].post(
        f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/enviar/"
    )
    assert resposta.status_code == 403
    with pytest.raises(RecusaDeLote):
        enviar_lote(lote.pk, B)


def test_acompanhar_ou_gerir_nao_concedem_lote(monkeypatch, ampla):
    from trajetoria.mobilizacao import acesso

    monkeypatch.setattr(acesso, "pode_consultar_lotes", lambda v: False)
    with pytest.raises(RecusaDeLote):
        previa(ampla.pk, A, {"unidades": ["Vitória"]})
    monkeypatch.undo()
    monkeypatch.setattr(acesso, "pode_preparar_lote", lambda v: False)
    with pytest.raises(RecusaDeLote):
        confirmar_lote(ampla.pk, A, "x", {"unidades": ["Vitória"]})
    monkeypatch.undo()
    lote = confirmar_lote(ampla.pk, A, "x", {"unidades": ["Vitória"]})
    monkeypatch.setattr(acesso, "pode_enviar_lote", lambda v: False)
    with pytest.raises(RecusaDeLote):
        enviar_lote(lote.pk, A)


def test_csaeg_ve_link_no_detalhe_da_campanha(ampla):
    html = atuar_como(Client(), B).get(f"/acompanhamento/campanhas/{ampla.pk}/").content.decode()
    assert f"/acompanhamento/campanhas/{ampla.pk}/lotes/" in html

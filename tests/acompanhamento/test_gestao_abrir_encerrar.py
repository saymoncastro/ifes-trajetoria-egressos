from datetime import timedelta

import pytest
from django.test import Client

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel
from trajetoria.acompanhamento.gestao.mensagens import SOBREPOSICAO
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import campanhas_em_coleta_para
from trajetoria.campanha.models import Campanha


def url(c, acao="abrir"):
    return f"/acompanhamento/campanhas/{c.pk}/{acao}/"


def test_confirmacao_abertura(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    r = cliente_cpaeg.get(url(c))
    assert r.status_code == 200
    texto = texto_visivel(r)
    assert "aceitar respostas imediatamente" in texto
    assert "não há reabertura nem prorrogação" in texto
    assert SOBREPOSICAO not in texto
    assert "fim de hoje" not in texto
    outra = k.campanha(inst.versao, nome="Outra Campanha aberta")
    texto = texto_visivel(cliente_cpaeg.get(url(c)))
    assert SOBREPOSICAO in texto and outra.nome in texto
    c.refresh_from_db()
    assert c.aberta_em is None


def test_abertura_ultimo_dia(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    op.definir_periodo(c, k.hoje(), k.hoje())
    assert "fim de hoje" in texto_visivel(cliente_cpaeg.get(url(c)))


def test_abrir_e_reenvio(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    versao_antes = inst.versao.__class__.objects.filter(pk=inst.versao.pk).values().get()
    r = cliente_cpaeg.post(url(c))
    assert r.status_code == 302 and r.url.endswith("?aviso=coleta-aberta")
    c.refresh_from_db()
    aberta = c.aberta_em
    assert aberta is not None
    assert c in campanhas_em_coleta_para(k.conclusao())
    assert cliente_cpaeg.post(url(c)).url.endswith("?aviso=ja-em-coleta")
    c.refresh_from_db()
    assert c.aberta_em == aberta
    op.encerrar(c)
    assert cliente_cpaeg.post(url(c)).url.endswith("?aviso=ja-encerrada")
    assert inst.versao.__class__.objects.filter(pk=inst.versao.pk).values().get() == versao_antes


@pytest.mark.parametrize("mudanca", ["rascunho", "futura"])
def test_abertura_revalida_post(inst, cliente_cpaeg, mudanca):
    c = k.campanha(inst.versao, estado="pronta")
    assert cliente_cpaeg.get(url(c)).status_code == 200
    if mudanca == "rascunho":
        op.alterar_campanha(c, versao=k.versao_em_rascunho(inst))
    else:
        op.definir_periodo(c, k.hoje() + timedelta(days=10), k.hoje() + timedelta(days=30))
    r = cliente_cpaeg.post(url(c))
    assert r.status_code == 409
    assert "<form" not in r.content.decode()
    c.refresh_from_db()
    assert c.aberta_em is None
    assert ("não foi publicada" if mudanca == "rascunho" else "a partir de") in texto_visivel(r)


def test_get_impedido_sem_form(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="sem_periodo")
    r = cliente_cpaeg.get(url(c))
    assert r.status_code == 200 and "<form" not in r.content.decode()
    assert "O período de coleta não foi definido" in texto_visivel(r)


def test_csrf_abertura(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    cliente = Client(enforce_csrf_checks=True)
    cliente.cookies.update(cliente_cpaeg.cookies)
    assert cliente.post(url(c)).status_code == 403
    c.refresh_from_db()
    assert c.aberta_em is None


def test_encerrar_preserva_participacoes(inst, cliente_cpaeg):
    from trajetoria.participacao.models import Participacao
    from trajetoria.participacao.operacoes import iniciar_participacao
    from trajetoria.participacao.regras import ParticipacaoRejeitada

    c = k.campanha(inst.versao)
    p = k.iniciada(c, k.conclusao())
    antes = Participacao.objects.filter(pk=p.pk).values().get()
    r = cliente_cpaeg.get(url(c, "encerrar"))
    assert r.status_code == 200
    texto = texto_visivel(r)
    assert "Novas respostas deixarão de ser aceitas" in texto
    assert "Participações existentes são preservadas" in texto
    assert "Não há reabertura" in texto
    r = cliente_cpaeg.post(url(c, "encerrar"))
    assert r.status_code == 302 and r.url.endswith("?aviso=coleta-encerrada")
    c.refresh_from_db()
    encerrada = c.encerrada_em
    assert encerrada is not None
    assert Participacao.objects.filter(pk=p.pk).values().get() == antes
    with pytest.raises(ParticipacaoRejeitada):
        iniciar_participacao(c, k.conclusao())
    assert cliente_cpaeg.post(url(c, "encerrar")).url.endswith("?aviso=ja-encerrada")
    c.refresh_from_db()
    assert c.encerrada_em == encerrada


@pytest.mark.parametrize(
    "estado", ["pronta", "expirada_sem_abertura", "encerrada_explicita", "encerrada_por_periodo"]
)
def test_get_encerramento_fora_de_coleta(inst, cliente_cpaeg, estado):
    c = k.campanha(inst.versao, estado=estado)
    r = cliente_cpaeg.get(url(c, "encerrar"))
    assert r.status_code == 409 and "<form" not in r.content.decode()
    antes = Campanha.objects.filter(pk=c.pk).values().get()
    r = cliente_cpaeg.post(url(c, "encerrar"))
    assert r.status_code == (409 if c.aberta_em is None else 302)
    assert Campanha.objects.filter(pk=c.pk).values().get() == antes

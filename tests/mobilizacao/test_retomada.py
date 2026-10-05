"""Retomada após interrupção (020 FR-028, FR-029; research R7; T027)."""

import pytest
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend
from django.utils import timezone

from tests.editor.construcao_editor import A
from trajetoria.mobilizacao.models import MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote

pytestmark = pytest.mark.django_db
S = SituacaoDoMembro


def test_limite_por_acao_e_continuar(ampla, settings, clientes):
    settings.TRAJETORIA_LOTE_ENVIO_POR_ACAO = 3
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    resultados = [enviar_lote(lote.pk, A) for _ in range(4)]
    assert [r.processados for r in resultados] == [3, 3, 2, 0]
    assert [r.restantes_nao_tentados for r in resultados] == [5, 2, 0, 0]
    destinos = [m.to[0] for m in mail.outbox]
    assert len(destinos) == len(set(destinos)) == 8


def test_botao_continuar_envio(ampla, settings, clientes):
    settings.TRAJETORIA_LOTE_ENVIO_POR_ACAO = 1
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/"
    assert ">Enviar</button>" in clientes[A].get(base).content.decode()
    html = clientes[A].post(base + "enviar/").content.decode()
    assert "Continuar envio" in html and "Restam 7 não tentados" in html
    assert "1 tentativa —" in html


def test_interrupcao_deixa_incerto_que_nunca_e_retentado(ampla, monkeypatch, clientes):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    original = EmailBackend.send_messages
    chamadas = []

    def enviar(backend, mensagens):
        chamadas.append(mensagens[0].to[0])
        if len(chamadas) == 3:
            raise RuntimeError("SENTINELA queda inesperada")
        return original(backend, mensagens)

    monkeypatch.setattr(EmailBackend, "send_messages", enviar)
    resposta = clientes[A].post(f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/enviar/")
    assert resposta.status_code == 500
    html = resposta.content.decode()
    assert "interrompido" in html and "SENTINELA" not in html
    incerto = lote.membros.get(situacao=S.EM_TENTATIVA)
    assert incerto.contato.valor == chamadas[2]
    r = enviar_lote(lote.pk, A)
    assert r.processados == 5 and not r.interrompido
    assert chamadas.count(incerto.contato.valor) == 1  # nunca reenviado
    incerto.refresh_from_db()
    assert incerto.situacao == S.EM_TENTATIVA
    assert "Resultado incerto" in clientes[A].get(
        f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/").content.decode()


def test_queda_simulada_no_banco_nunca_volta_a_nao_tentado(ampla):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    membro = lote.membros.filter(situacao=S.NAO_TENTADO).first()
    MembroDoLote.objects.filter(pk=membro.pk).update(
        situacao=S.EM_TENTATIVA, tentativa_iniciada_em=timezone.now()
    )
    enviar_lote(lote.pk, A)
    membro.refresh_from_db()
    assert membro.situacao == S.EM_TENTATIVA
    assert membro.contato.valor not in [m.to[0] for m in mail.outbox]

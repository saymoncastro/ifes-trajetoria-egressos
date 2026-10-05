"""Envio do Lote (020 FR-026 a FR-031; T026)."""

from smtplib import SMTPException

import pytest
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend
from django.db import connection

from tests.contato.conftest import contato
from tests.editor.construcao_editor import A
from tests.mobilizacao.conftest import pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.contato.models import Origem
from trajetoria.mobilizacao.acesso import RecusaDeLote
from trajetoria.mobilizacao.models import MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote
from trajetoria.mobilizacao.views import situacao_do_lote

pytestmark = pytest.mark.django_db
S = SituacaoDoMembro


def _situacoes(lote):
    return {m.pessoa.id_externo: m.situacao for m in lote.membros.select_related("pessoa")}


def test_envio_basico(ampla):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    r = enviar_lote(lote.pk, A)
    assert (r.processados, r.submetidos, r.falhas, r.restantes_nao_tentados) == (1, 1, 0, 0)
    assert [m.to for m in mail.outbox] == [["sim-p-0002@example.invalid"]]
    assert _situacoes(lote) == {
        "SIM-P-0002": S.SUBMETIDO_AO_TRANSPORTE, "SIM-P-0010": S.SEM_CONTATO,
    }
    membro = lote.membros.get(situacao=S.SUBMETIDO_AO_TRANSPORTE)
    assert membro.tentativa_iniciada_em <= membro.resultado_em
    # Acionar de novo não reenvia nada.
    assert enviar_lote(lote.pk, A).processados == 0
    assert len(mail.outbox) == 1


def test_so_em_coleta(ampla, em_preparacao):
    lote = confirmar_lote(em_preparacao.pk, A, "Cedo", {"unidades": ["Vitória"]})
    with pytest.raises(RecusaDeLote) as exc:
        enviar_lote(lote.pk, A)
    assert (exc.value.categoria, exc.value.status) == ("campanha_fora_da_coleta", 409)
    encerrado = confirmar_lote(ampla.pk, A, "Tarde", {"unidades": ["Vitória"]})
    op_campanha.encerrar(ampla)
    with pytest.raises(RecusaDeLote) as exc:
        enviar_lote(encerrado.pk, A)
    assert exc.value.categoria == "campanha_encerrada"
    assert set(MembroDoLote.objects.values_list("situacao", flat=True)) == {
        S.NAO_TENTADO, S.SEM_CONTATO,
    }
    assert not getattr(mail, "outbox", [])


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("falha", [SMTPException, OSError, TimeoutError, None])
def test_falha_de_transporte_sem_retry(ampla, monkeypatch, caplog, falha):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    original = EmailBackend.send_messages
    chamadas = []

    def enviar(backend, mensagens):
        assert not connection.in_atomic_block  # (b) fora de transação
        chamadas.append(mensagens[0].to[0])
        if len(chamadas) == 2:
            if falha:
                raise falha("SENTINELA-nome-email-corpo-credencial")
            return 0
        return original(backend, mensagens)

    monkeypatch.setattr(EmailBackend, "send_messages", enviar)
    r = enviar_lote(lote.pk, A)
    assert (r.processados, r.falhas, r.submetidos) == (8, 1, 7)
    assert lote.membros.filter(situacao=S.FALHA_DE_TRANSPORTE).count() == 1
    assert "SENTINELA" not in caplog.text
    assert enviar_lote(lote.pk, A).processados == 0  # falha não é retentada
    assert len(chamadas) == 8


def test_destino_e_o_contato_congelado(ampla):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    contato(pessoa("SIM-P-0002"), "novo@example.invalid", Origem.EGRESSO)
    enviar_lote(lote.pk, A)
    assert mail.outbox[0].to == ["sim-p-0002@example.invalid"]


def test_pessoa_que_sai_da_populacao_segue_o_congelado(ampla):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    op_campanha_campo = type(ampla).objects.filter(pk=ampla.pk)
    op_campanha_campo.update(unidades=["Serra"])  # simula mudança de abrangência
    enviar_lote(lote.pk, A)
    assert mail.outbox[0].to == ["sim-p-0002@example.invalid"]


def test_mensagem_sem_identificadores(ampla):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    enviar_lote(lote.pk, A)
    for msg in mail.outbox:
        conteudo = msg.body + msg.alternatives[0].content + msg.subject
        membro = MembroDoLote.objects.get(lote=lote, contato__valor=msg.to[0])
        for proibido in (str(membro.pk), str(lote.pk), str(membro.pessoa_id), "SIM-P-",
                         "token"):
            assert proibido not in conteudo
        assert "http://127.0.0.1:8000/acesso/" in msg.body


def test_situacao_derivada():
    assert situacao_do_lote({S.NAO_TENTADO: 2, S.SEM_CONTATO: 1}) == "Não enviado"
    assert situacao_do_lote({S.NAO_TENTADO: 1, S.SUBMETIDO_AO_TRANSPORTE: 1}) == "Envio parcial"
    assert situacao_do_lote({S.FALHA_DE_TRANSPORTE: 1, S.SEM_CONTATO: 1}) == "Envio concluído"


def test_tela_do_lote_sem_termos_proibidos(ampla, clientes):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/"
    resposta = clientes[A].post(base + "enviar/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Aceite do transporte não comprova entrega" in html
    assert "não prova que a comunicação causou uma resposta" in html
    for termo in ("Entregue", "entregues", "Aberto", "Clicado", "alcance", "conversão",
                  "example.invalid"):
        assert termo not in html
    assert "no-store" in resposta["Cache-Control"]
    assert clientes[A].get(base + "enviar/").status_code == 405


# --- Regressões do code review de 2026-10-05 -------------------------------------------------


def test_contato_recusado_pelo_modo_nao_vira_incerto(ampla, clientes):
    """Code review #1: na demonstração, e-mail informado fora de `example.invalid` é recusado
    ANTES de qualquer tentativa; o membro continua `NAO_TENTADO`, a ação não é interrompida
    e os demais membros são enviados."""
    contato(pessoa("SIM-P-0002"), "bruno@gmail.com", Origem.EGRESSO)
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    bruno = lote.membros.get(pessoa__id_externo="SIM-P-0002")
    assert bruno.contato.valor == "bruno@gmail.com"
    resposta = clientes[A].post(f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/enviar/")
    assert resposta.status_code == 200
    r = resposta.context["resultado"]
    assert (r.interrompido, r.nao_enviaveis, r.submetidos, r.processados) == (False, 1, 7, 7)
    bruno.refresh_from_db()
    assert (bruno.situacao, bruno.tentativa_iniciada_em) == (S.NAO_TENTADO, None)
    assert not lote.membros.filter(situacao=S.EM_TENTATIVA).exists()
    assert "bruno@gmail.com" not in [m.to[0] for m in mail.outbox]
    html = resposta.content.decode()
    assert "contato não aceito neste ambiente" in html and "gmail" not in html
    # Repetir não queima o membro: continua não tentado, sem mensagem.
    assert enviar_lote(lote.pk, A).nao_enviaveis == 1
    bruno.refresh_from_db()
    assert bruno.situacao == S.NAO_TENTADO


def test_conteudo_recusado_nao_queima_membros(ampla):
    """Code review #1: nome de Campanha com URL torna a mensagem inválida para todos; nada é
    reservado nem marcado como incerto."""
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    type(ampla).objects.filter(pk=ampla.pk).update(nome="Pesquisa http://externo.test/x")
    r = enviar_lote(lote.pk, A)
    assert (r.processados, r.nao_enviaveis, r.interrompido) == (0, 8, False)
    assert set(lote.membros.values_list("situacao", flat=True)) == {S.NAO_TENTADO, S.SEM_CONTATO}
    assert not getattr(mail, "outbox", [])


def test_campanha_encerrada_durante_a_acao_para_o_envio(ampla, monkeypatch):
    """Code review #3: o estado é revalidado a cada membro; encerrar no meio da ação
    interrompe os envios seguintes, que continuam não tentados."""
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    original = EmailBackend.send_messages
    enviados = []

    def enviar_e_encerrar(backend, mensagens):
        enviados.append(mensagens[0].to[0])
        resultado = original(backend, mensagens)
        if len(enviados) == 2:
            op_campanha.encerrar(type(ampla).objects.get(pk=ampla.pk))
        return resultado

    monkeypatch.setattr(EmailBackend, "send_messages", enviar_e_encerrar)
    r = enviar_lote(lote.pk, A)
    assert r.saiu_da_coleta and (r.processados, r.submetidos) == (2, 2)
    assert len(mail.outbox) == 2
    assert lote.membros.filter(situacao=S.NAO_TENTADO).count() == 6
    assert not lote.membros.filter(situacao=S.EM_TENTATIVA).exists()

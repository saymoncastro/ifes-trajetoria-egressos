"""Envio pendente (023 FR-002 a FR-009; research R1 a R3): registro de sessão separado da
sessão do sujeito, com validade de 30 minutos, que atravessa a nova confirmação e some ao
sair, ao vencer e ao ser substituído."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import RequestFactory

from tests.acesso.construcao import AGORA, ANA, preparar_material
from trajetoria.acesso import pendente

pytestmark = pytest.mark.django_db


def _request():
    request = RequestFactory().post("/participacoes/x/secoes/2/")
    request.session = SessionStore()
    request.session.save()
    return request


def _registro(request):
    return SessionStore(session_key=request.session[pendente.CHAVE])


def test_guardar_cria_registro_separado_e_so_a_chave_na_sessao(relogio):
    request = _request()
    participacao = uuid4()
    pendente.guardar(request, participacao, 2, {"p1": ["1"], "p2": ["x" * 3000]})
    assert dict(request.session) == {pendente.CHAVE: request.session[pendente.CHAVE]}
    assert request.session[pendente.CHAVE] != request.session.session_key
    registro = _registro(request)
    assert registro["participacao"] == str(participacao) and registro["posicao"] == 2
    assert len(registro["dados"]["p2"][0]) == pendente.LIMITE_VALOR
    assert registro.get_expiry_age() == int(pendente.VALIDADE.total_seconds())
    linha = Session.objects.get(session_key=request.session[pendente.CHAVE])
    assert linha.expire_date == AGORA + pendente.VALIDADE
    envio = pendente.ler(request)
    assert envio.participacao == participacao and envio.posicao == 2
    assert envio.dados["p1"] == ["1"] and not envio.apresentado
    assert pendente.guardado_nesta_requisicao(request)


def test_vencido_some(relogio):
    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    chave = request.session[pendente.CHAVE]
    relogio.agora += pendente.VALIDADE + timedelta(seconds=1)
    assert pendente.ler(request) is None
    assert pendente.CHAVE not in request.session
    assert not Session.objects.filter(session_key=chave).exists()


def test_novo_envio_substitui_o_anterior_e_descartar_apaga(relogio):
    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    primeira = request.session[pendente.CHAVE]
    pendente.guardar(request, uuid4(), 3, {"p1": ["2"]})
    assert not Session.objects.filter(session_key=primeira).exists()
    assert pendente.ler(request).posicao == 3
    segunda = request.session[pendente.CHAVE]
    pendente.descartar(request)
    assert pendente.ler(request) is None
    assert not Session.objects.filter(session_key=segunda).exists()


def test_marcar_apresentado(relogio):
    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    pendente.marcar_apresentado(request)
    assert pendente.ler(request).apresentado


def test_chave_atravessa_estabelecer_e_some_ao_encerrar(relogio):
    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import dados_de_sessao, encerrar, estabelecer
    from trajetoria.acesso.verificacao import Confirmada

    p = preparar_material("SIM-P-0001")[0].pessoa
    m = MaterialDeVerificacao.objects.get(pessoa=p)
    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    chave = request.session[pendente.CHAVE]
    estabelecer(request, Confirmada(p, m.atualizado_em), AGORA)
    assert dict(request.session) == {
        **dados_de_sessao(p, m.atualizado_em, AGORA),
        pendente.CHAVE: chave,
    }
    assert ANA.cpf11 not in repr(dict(_registro(request)))
    encerrar(request)
    assert pendente.CHAVE not in request.session
    assert not Session.objects.filter(session_key=chave).exists()


def test_chave_atravessa_o_declarante(relogio):
    from trajetoria.declaracao.sessao import estabelecer_declarante

    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    chave = request.session[pendente.CHAVE]
    estabelecer_declarante(request, [uuid4()], AGORA)
    assert request.session[pendente.CHAVE] == chave


def test_sessao_expirada_marca_e_preserva_a_chave(relogio, settings):
    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import destino_da_entrada, estabelecer, pessoa_em_uso
    from trajetoria.acesso.verificacao import Confirmada

    p = preparar_material("SIM-P-0001")[0].pessoa
    m = MaterialDeVerificacao.objects.get(pessoa=p)
    request = _request()
    estabelecer(request, Confirmada(p, m.atualizado_em), AGORA)
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    chave = request.session[pendente.CHAVE]
    request.session.save()
    relogio.agora += settings.TRAJETORIA_SESSAO_INATIVIDADE + timedelta(seconds=1)
    nova = RequestFactory().get("/formacoes/")
    nova.session = SessionStore(session_key=request.session.session_key)
    assert pessoa_em_uso(nova) is None
    assert nova._sessao_expirada
    assert nova.session[pendente.CHAVE] == chave
    assert destino_da_entrada(nova) == "/acesso/?aviso=sessao"
    sem_sessao = RequestFactory().get("/formacoes/")
    sem_sessao.session = SessionStore()
    assert pessoa_em_uso(sem_sessao) is None
    assert destino_da_entrada(sem_sessao) == "/acesso/"


def test_marcar_apresentado_nao_estende_a_retencao(relogio):
    request = _request()
    pendente.guardar(request, uuid4(), 2, {"p1": ["1"]})
    relogio.agora += timedelta(minutes=20)
    pendente.marcar_apresentado(request)
    linha = Session.objects.get(session_key=request.session[pendente.CHAVE])
    assert linha.expire_date == AGORA + pendente.VALIDADE


def test_limites(relogio):
    request = _request()
    # Cada valor é cortado em LIMITE_VALOR; o total de todos os campos é que tem teto.
    grande = {f"p{n}": ["x" * pendente.LIMITE_VALOR] for n in range(11)}
    assert not pendente.guardar(request, uuid4(), 2, grande)
    assert pendente.ler(request) is None and not pendente.guardado_nesta_requisicao(request)
    assert pendente.guardar(request, uuid4(), 2, {f"p{n}": ["1"] for n in range(100)})
    assert len(pendente.ler(request).dados) == pendente.LIMITE_CAMPOS

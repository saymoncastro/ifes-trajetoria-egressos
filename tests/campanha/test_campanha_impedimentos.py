from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from tests.campanha.construcao import versao_rascunho
from trajetoria.campanha import consultas, operacoes
from trajetoria.campanha.regras import CampanhaRejeitada
from trajetoria.instrumento.operacoes import publicar

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("publicada", [True, False])
@pytest.mark.parametrize("janela", [None, -10, 0, 10])
def test_equivalencia_sem_escrita(publicada, janela):
    v = versao_rascunho("Impedimentos")
    if publicada:
        publicar(v)
    c = operacoes.criar_campanha("Rodada", v)
    agora = timezone.now()
    hoje = timezone.localdate(agora)
    if janela is not None:
        operacoes.definir_periodo(
            c, hoje + timedelta(days=janela), hoje + timedelta(days=janela + 2)
        )
    with CaptureQueriesContext(connection) as queries:
        impedimentos = consultas.impedimentos_de_abertura(c, agora=agora)
    assert isinstance(impedimentos, tuple)
    assert all(
        not any(t in q["sql"].upper() for t in ("INSERT", "UPDATE", "DELETE", "FOR UPDATE"))
        for q in queries
    )
    c.refresh_from_db()
    assert c.aberta_em is None
    if impedimentos:
        with pytest.raises(CampanhaRejeitada) as erro:
            operacoes.abrir(c, agora=agora)
        assert impedimentos == erro.value.violacoes
    else:
        assert operacoes.abrir(c, agora=agora) is operacoes.SituacaoAbertura.ABERTA


@pytest.mark.parametrize("inicio,fim", [(None, None), (1, None), (None, 1), (2, 1), (1, 1)])
def test_periodo_regra_unica(inicio, fim):
    """`violacoes_de_periodo` é a regra que `definir_periodo` aplica (code review da 017)."""
    hoje = timezone.localdate()
    datas = [None if d is None else hoje + timedelta(days=d) for d in (inicio, fim)]
    c = operacoes.criar_campanha("Rodada", versao_rascunho("Período"))
    violacoes = operacoes.violacoes_de_periodo(*datas)
    if violacoes:
        with pytest.raises(CampanhaRejeitada) as erro:
            operacoes.definir_periodo(c, *datas)
        assert erro.value.violacoes == violacoes
    else:
        operacoes.definir_periodo(c, *datas)


def test_campanhas_em_coleta_coincide_com_estado():
    v = versao_rascunho("Coleta")
    publicar(v)
    agora = timezone.now()
    hoje = timezone.localdate(agora)
    aberta = operacoes.criar_campanha("Aberta", v)
    operacoes.definir_periodo(aberta, hoje, hoje + timedelta(days=5))
    operacoes.abrir(aberta, agora=agora)
    preparada = operacoes.criar_campanha("Preparada", v)
    encerrada = operacoes.criar_campanha("Encerrada", v)
    operacoes.definir_periodo(encerrada, hoje, hoje + timedelta(days=5))
    operacoes.abrir(encerrada, agora=agora)
    operacoes.encerrar(encerrada, agora=agora + timedelta(hours=1))
    depois = agora + timedelta(minutes=30)
    for c in (aberta, preparada, encerrada):
        c.refresh_from_db()
        em_coleta = consultas.campanhas_em_coleta(agora=depois).filter(pk=c.pk).exists()
        assert em_coleta is (
            consultas.estado(c, agora=depois) is consultas.EstadoCampanha.EM_COLETA
        )

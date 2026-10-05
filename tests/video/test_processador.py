"""Processador de pedidos (022 US1; research R7; data-model §3.1; analyze U2)."""

from datetime import timedelta

import pytest
from django.core.management import call_command

from tests.video.conftest import MP4_FALSO
from tests.video.construcao import NOME, composicao
from trajetoria.narrativa.composicao import chave_da_composicao
from trajetoria.video import operacoes, renderizador
from trajetoria.video.models import GeracaoDeVideo as G

pytestmark = pytest.mark.django_db


def _linha(c):
    return G.objects.get(chave=chave_da_composicao(c))


def test_processa_o_pedido(renderizador_falso, relogio, settings):
    c = composicao("maria", NOME)
    operacoes.solicitar(c)
    call_command("processar_videos", "--uma-vez")
    linha = _linha(c)
    assert linha.estado == G.PRONTO
    assert bytes(linha.video) == MP4_FALSO and linha.tamanho == len(MP4_FALSO)
    assert linha.concluido_em == relogio.agora
    assert linha.expira_em == relogio.agora + settings.TRAJETORIA_VIDEO_RETENCAO
    assert linha.composicao is None
    assert renderizador_falso == [c]


def test_sem_pedido_termina(renderizador_falso):
    call_command("processar_videos", "--uma-vez")
    assert renderizador_falso == []


def test_falha_de_renderizacao(renderizador_com_falha):
    c = composicao("ana")
    operacoes.solicitar(c)
    call_command("processar_videos", "--uma-vez")
    linha = _linha(c)
    assert linha.estado == G.FALHOU and linha.motivo == "codigo_1"
    assert linha.composicao is None and linha.video is None


def test_um_por_ciclo_o_mais_antigo(renderizador_falso, relogio):
    antigo, novo = composicao("ana"), composicao("diego")
    operacoes.solicitar(antigo)
    relogio.agora += timedelta(seconds=5)
    operacoes.solicitar(novo)
    call_command("processar_videos", "--uma-vez")
    assert _linha(antigo).estado == G.PRONTO
    assert _linha(novo).estado == G.SOLICITADO


def test_toma_com_skip_locked(renderizador_falso, monkeypatch):
    usados = []
    original = G.objects.select_for_update

    def espiao(**kwargs):
        usados.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(G.objects, "select_for_update", espiao)
    operacoes.solicitar(composicao("ana"))
    operacoes.processar_proximo()
    assert {"skip_locked": True} in usados


@pytest.mark.parametrize("mudanca", ["tentar_de_novo", "apagada"])
def test_resultado_descartado_se_a_linha_mudou(mudanca, monkeypatch, relogio, caplog):
    c = composicao("maria", NOME)
    operacoes.solicitar(c)

    def renderizar(composicao_recebida):
        if mudanca == "apagada":
            G.objects.all().delete()
        else:
            G.objects.update(estado=G.FALHOU, motivo="tempo_esgotado", composicao=None)
            relogio.agora += timedelta(seconds=1)
            operacoes.solicitar(c)
        return MP4_FALSO

    monkeypatch.setattr(renderizador, "renderizar", renderizar)
    operacoes.processar_proximo()
    if mudanca == "apagada":
        assert not G.objects.exists()
    else:
        linha = _linha(c)
        assert linha.estado == G.SOLICITADO and linha.video is None
    assert "video: resultado descartado" in caplog.text
    assert NOME not in caplog.text and chave_da_composicao(c) not in caplog.text


def test_logs_sem_conteudo(renderizador_com_falha, caplog):
    c = composicao("maria", NOME)
    operacoes.solicitar(c)
    call_command("processar_videos", "--uma-vez")
    assert NOME not in caplog.text
    assert "Tecnologia" not in caplog.text
    assert chave_da_composicao(c) not in caplog.text

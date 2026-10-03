"""Acesso, recusa e URL direta (Feature 011; US5; spec FR-150 a FR-158; caso N)."""

import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import URLPattern

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel
from trajetoria.acompanhamento import urls

LISTA = "/acompanhamento/"


@pytest.mark.parametrize("recorte", [None, "curso"])
def test_csaeg_fora_do_escopo_recebe_recusa_sem_dados(ref, cliente_csaeg_vitoria, recorte):
    with CaptureQueriesContext(connection) as capturadas:
        resposta = k.detalhe(cliente_csaeg_vitoria, ref.R, recorte)
    assert resposta.status_code == 403
    texto = texto_visivel(resposta)
    assert "não está no escopo de acompanhamento da sua atuação" in texto
    for dado in ("Campanha R", "Serra", "Cefor", ref.inst.versao.designacao, "Elegíveis"):
        assert dado not in texto
    assert not any(
        '"academico_conclusaoacademica"' in q["sql"] or '"participacao_participacao"' in q["sql"]
        for q in capturadas
    )


def test_operador_sem_vinculo_recusado(ref, cliente_sem_vinculo):
    for endereco in (LISTA, f"/acompanhamento/campanhas/{ref.I.pk}/"):
        resposta = cliente_sem_vinculo.get(endereco)
        assert resposta.status_code == 403
        assert "Não há vínculo institucional ativo" in texto_visivel(resposta)
        assert "Campanha I" not in texto_visivel(resposta)


def test_nao_identificado_vai_para_escolha_com_destino_fechado(ref, cliente_nao_identificado):
    for endereco in (LISTA, f"/acompanhamento/campanhas/{ref.I.pk}/"):
        resposta = cliente_nao_identificado.get(endereco)
        assert resposta.status_code == 302
        assert resposta["Location"] == "/demonstracao/operador/?destino=acompanhamento"


def test_campanha_inexistente(ref, cliente_csaeg_vitoria, cliente_sem_vinculo):
    endereco = f"/acompanhamento/campanhas/{uuid.uuid4()}/"
    assert cliente_csaeg_vitoria.get(endereco).status_code == 404
    assert cliente_sem_vinculo.get(endereco).status_code == 403


def test_modo_desligado(ref, cliente_cpaeg, settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    for endereco in (LISTA, f"/acompanhamento/campanhas/{ref.I.pk}/"):
        assert cliente_cpaeg.get(endereco).status_code == 404


def test_somente_get(ref, cliente_cpaeg):
    for endereco in (LISTA, f"/acompanhamento/campanhas/{ref.I.pk}/"):
        assert cliente_cpaeg.post(endereco).status_code == 405


def test_toda_rota_exige_o_gate_de_acompanhamento():
    """As rotas da 011 usam `@acompanhamento`; as da comunicação simulada (016), a barreira
    própria `@comunicacao`. Nenhuma rota sem barreira e nenhuma com as duas marcas."""
    rotas = [p for p in urls.urlpatterns if isinstance(p, URLPattern)]
    assert len(rotas) == len(urls.urlpatterns) == 4
    for rota in rotas:
        comunicacao = "/comunicacao/" in str(rota.pattern)
        assert getattr(rota.callback, "acompanhamento", False) is not comunicacao, rota.pattern
        assert getattr(rota.callback, "comunicacao", False) is comunicacao, rota.pattern

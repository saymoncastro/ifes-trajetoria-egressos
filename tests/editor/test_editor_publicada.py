"""Versão publicada somente leitura, em três níveis (US12; FR-018 a FR-020; research R12).

UI: nenhum controle de edição. View: POST recusado antes de qualquer operação. Domínio: com a
guarda da view desligada, a 002 continua recusando.
"""

import re

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.editor import views
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import TipoPergunta

pytestmark = pytest.mark.django_db
ESCRITAS = [n for n in op.__all__ if n not in ("FINALIZAR", "Finalizar", "SituacaoPublicacao")]


@pytest.fixture
def alvos(publicada):
    secao = ce.secao(publicada, 1)
    pergunta = ce.pergunta(publicada, 1, 1)
    assert pergunta.tipo == TipoPergunta.ESCOLHA_UNICA
    return publicada, secao, pergunta, pergunta.opcoes.order_by("posicao").first()


@pytest.fixture
def espiao(monkeypatch):
    chamadas = []
    for nome in ESCRITAS:
        original = getattr(op, nome)
        monkeypatch.setattr(
            op, nome, lambda *a, _n=nome, _o=original, **k: chamadas.append(_n) or _o(*a, **k)
        )
    return chamadas


def _escritas(versao, secao, pergunta, opcao):
    outra = ce.secao(versao, 2)
    return [
        (f"/editor/versoes/{versao.pk}/dados/", {"designacao": "X"}),
        (f"/editor/versoes/{versao.pk}/secoes/nova/", {"titulo": "Nova"}),
        (f"/editor/secoes/{secao.pk}/editar/", {"titulo": "X"}),
        (f"/editor/secoes/{secao.pk}/mover/", {"direcao": "baixo"}),
        (f"/editor/secoes/{secao.pk}/remover/", {}),
        (f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=TEXTO_CURTO",
         {"texto": "X", "obrigatoria": "sim"}),
        (f"/editor/perguntas/{pergunta.pk}/editar/", {"texto": "X", "obrigatoria": "sim"}),
        (f"/editor/perguntas/{pergunta.pk}/mover/", {"direcao": "baixo"}),
        (f"/editor/perguntas/{pergunta.pk}/trocar-secao/", {"secao": str(outra.pk)}),
        (f"/editor/perguntas/{pergunta.pk}/remover/", {}),
        (f"/editor/perguntas/{pergunta.pk}/opcoes/nova/", {"texto": "Nova"}),
        (f"/editor/opcoes/{opcao.pk}/", {"texto": "X", "desvio": "finalizar"}),
        (f"/editor/opcoes/{opcao.pk}/mover/", {"direcao": "baixo"}),
        (f"/editor/opcoes/{opcao.pk}/remover/", {}),
    ]  # fmt: skip


def test_ui_sem_controles_de_edicao(client, alvos):
    versao, secao, pergunta, _ = alvos
    for url in (
        f"/editor/versoes/{versao.pk}/",
        f"/editor/secoes/{secao.pk}/",
        f"/editor/perguntas/{pergunta.pk}/",
    ):
        resposta = client.get(url)
        html = resposta.content.decode()
        assert "<form" not in html, url
        for trecho in ("/editar/", "/remover/", "/nova/", "/mover/", "/trocar-secao/",
                       "/dados/", "/diagnostico/", "/opcoes/"):  # fmt: skip
            assert trecho not in html, (url, trecho)
        texto = ce.texto_visivel(resposta)
        assert "Publicada" in texto and "não pode ser alterada" in texto
    estrutura = client.get(f"/editor/versoes/{versao.pk}/").content.decode()
    assert f"/editor/versoes/{versao.pk}/previa/" in estrutura
    assert f"/editor/versoes/{versao.pk}/nova-a-partir/" in estrutura


def test_get_de_formulario_volta_a_consulta(client, alvos):
    for url, _ in _escritas(*alvos):
        if url.endswith("/mover/"):
            continue
        resposta = client.get(url)
        assert resposta.status_code == 302, url
        assert resposta["Location"].endswith("?aviso=publicada"), url


def test_post_recusado_antes_de_qualquer_operacao(client, alvos, espiao):
    versao = alvos[0]
    antes = ce.retrato(versao)
    for url, dados in _escritas(*alvos):
        resposta = client.post(url, dados)
        assert resposta.status_code == 409, url
        assert "Esta Versão está publicada e não pode ser alterada" in ce.texto_visivel(resposta)
    assert espiao == []
    assert ce.retrato(versao) == antes


def test_dominio_continua_sendo_a_protecao_definitiva(client, alvos, monkeypatch):
    versao, _, pergunta, _ = alvos
    monkeypatch.setattr(views, "_exigir_rascunho", lambda *a, **k: None)
    antes = ce.retrato(versao)
    resposta = client.post(
        f"/editor/perguntas/{pergunta.pk}/editar/", {"texto": "X", "obrigatoria": "sim"}
    )
    assert resposta.status_code == 409
    assert ce.retrato(versao) == antes


def test_sem_acao_de_despublicar_corrigir_ou_publicar(client, alvos):
    versao = alvos[0]
    html = client.get(f"/editor/versoes/{versao.pk}/").content.decode()
    acoes = re.findall(r"<(?:a|button)\b[^>]*>(.*?)</(?:a|button)>", html, re.S)
    for acao in acoes:
        assert not re.search(r"publicar|corrigir|editar mesmo assim", acao, re.I), acao

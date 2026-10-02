"""Recusas e erros em linguagem operacional (US14; FR-094 a FR-097; research R10).

Recusa conhecida → no campo ou em tela própria; motivo não mapeado e exceção inesperada
continuam sendo erro (500), nunca mensagem de validação.
"""

import re
import uuid

import pytest
from django.test import Client

from tests.editor import construcao_editor as ce
from tests.editor.construcao_editor import A, atuar_como
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.editor import acoes
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Secao, TipoPergunta
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada, Violacao

pytestmark = pytest.mark.django_db


def _rejeicao(motivo):
    def rejeitar(*args, **kwargs):
        raise OperacaoRejeitada((Violacao(motivo, None, ""),))

    return rejeitar


@pytest.fixture
def multipla(versao):
    secao = op.adicionar_secao(versao, 1)
    pergunta = op.adicionar_pergunta(
        secao, 1, TipoPergunta.ESCOLHA_MULTIPLA, "Quais?", obrigatoria=True
    )
    op.adicionar_opcao(pergunta, 1, "Estágio")
    return pergunta


def test_formulario_recusado_resumo_no_topo_e_valores_preservados(client, multipla):
    resposta = client.post(
        f"/editor/perguntas/{multipla.pk}/opcoes/nova/", {"texto": "Estágio", "complemento": "on"}
    )
    assert resposta.status_code == 200
    html = resposta.content.decode()
    main = html[html.index("<main") :]
    assert main.index('class="resumo-erros"') < main.index("<h1>")
    assert re.search(r"<title>Erro: ", html)
    assert (
        'aria-invalid="true"' in html and 'aria-describedby="id_texto-ajuda id_texto-erro"' in html
    )
    assert 'value="Estágio"' in html and "checked" in html
    assert ce.padroes_tecnicos(resposta) == []


def test_conflito_de_ordem_na_mesma_requisicao(client, pesquisa, monkeypatch):
    versao = ce.versao_de(pesquisa, secao_mem(), secao_mem())
    antes = ce.retrato(versao)
    monkeypatch.setattr(op, "reordenar_secoes", _rejeicao(Motivo.ORDEM_INCOMPLETA))
    resposta = client.post(f"/editor/secoes/{ce.secao(versao, 2).pk}/mover/", {"direcao": "cima"})
    assert resposta.status_code == 409
    assert "O conteúdo mudou desde que esta página foi aberta" in ce.texto_visivel(resposta)
    assert ce.retrato(versao) == antes


def test_conflito_de_posicao_na_inclusao(client, versao, monkeypatch):
    op.adicionar_secao(versao, 1)
    monkeypatch.setattr(acoes, "proxima_posicao", lambda conjunto: 1)
    resposta = client.post(f"/editor/versoes/{versao.pk}/secoes/nova/", {"titulo": "Nova"})
    assert resposta.status_code == 409
    assert versao.secoes.count() == 1


def test_post_em_elemento_removido(client, db):
    resposta = client.post(f"/editor/opcoes/{uuid.uuid4()}/", {"texto": "X"})
    assert resposta.status_code == 404
    assert "O conteúdo mudou" in ce.texto_visivel(resposta)


def test_motivo_nao_mapeado_continua_sendo_erro(multipla, monkeypatch, vinculo_cpaeg):
    monkeypatch.setattr(op, "adicionar_opcao", _rejeicao(Motivo.TIPO_NAO_SUPORTADO))
    cliente = atuar_como(Client(raise_request_exception=False), A)
    resposta = cliente.post(f"/editor/perguntas/{multipla.pk}/opcoes/nova/", {"texto": "Nova"})
    assert resposta.status_code == 500
    assert "Informe" not in resposta.content.decode()
    with pytest.raises(OperacaoRejeitada):
        atuar_como(Client(), A).post(
            f"/editor/perguntas/{multipla.pk}/opcoes/nova/", {"texto": "Nova"}
        )


def test_excecao_inesperada_e_500_sem_rastro(multipla, monkeypatch, vinculo_cpaeg):
    def falha(*args, **kwargs):
        raise RuntimeError("falha inesperada")

    monkeypatch.setattr(op, "adicionar_opcao", falha)
    resposta = atuar_como(Client(raise_request_exception=False), A).post(
        f"/editor/perguntas/{multipla.pk}/opcoes/nova/", {"texto": "Nova"}
    )
    assert resposta.status_code == 500
    corpo = resposta.content.decode()
    assert "Traceback" not in corpo and "RuntimeError" not in corpo


def test_paginas_de_recusa_sem_padroes_tecnicos(client, pesquisa, publicada):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)))
    respostas = [
        client.post(f"/editor/secoes/{ce.secao(versao, 1).pk}/remover/"),
        client.post(f"/editor/versoes/{publicada.pk}/dados/", {"designacao": "X"}),
        client.post(f"/editor/secoes/{uuid.uuid4()}/editar/", {"titulo": "X"}),
    ]
    for resposta in respostas:
        assert ce.padroes_tecnicos(resposta) == [], resposta.status_code
        assert 'role="alert"' not in resposta.content.decode()


def test_destino_removido_entre_validacao_e_gravacao_e_conflito(client, pesquisa, monkeypatch):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
        secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
    )
    pergunta = ce.pergunta(versao, 1, 1)
    destino = ce.secao(versao, 2)
    antes = ce.retrato(versao)
    original = Secao.objects.get

    def sumiu(*args, **kwargs):
        if kwargs.get("pk") == str(destino.pk):
            raise Secao.DoesNotExist
        return original(*args, **kwargs)

    monkeypatch.setattr(Secao.objects, "get", sumiu)
    resposta = client.post(
        f"/editor/perguntas/{pergunta.pk}/trocar-secao/", {"secao": str(destino.pk)}
    )
    assert resposta.status_code == 409
    assert "O conteúdo mudou" in ce.texto_visivel(resposta)
    monkeypatch.undo()
    assert ce.retrato(versao) == antes


def test_post_sem_campos_e_validado(client, multipla):
    resposta = client.post(f"/editor/perguntas/{multipla.pk}/editar/", {})
    assert resposta.status_code == 200
    assert "Indique se a Pergunta é obrigatória ou opcional." in resposta.content.decode()

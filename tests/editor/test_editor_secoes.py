"""Seções e dados da Versão em rascunho (US6; FR-026 a FR-030, FR-061 a FR-064)."""

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Secao, TipoPergunta

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


def _nova(client, versao, **dados):
    dados.setdefault("titulo", "")
    dados.setdefault("texto", "")
    return client.post(f"/editor/versoes/{versao.pk}/secoes/nova/", dados)


# --- criar e editar ------------------------------------------------------------------------


def test_nova_secao_entra_ao_final(client, versao):
    op.adicionar_secao(versao, 5, titulo="Existente")
    resposta = _nova(client, versao, titulo="Nova")
    nova = versao.secoes.get(titulo="Nova")
    assert resposta["Location"] == f"/editor/secoes/{nova.pk}/?aviso=secao-criada"
    assert nova.posicao == 6


def test_nova_secao_sem_titulo(client, versao):
    _nova(client, versao)
    secao = versao.secoes.get()
    assert secao.titulo is None and secao.texto is None
    assert "Seção 1 (sem título)" in ce.texto_visivel(client.get(f"/editor/secoes/{secao.pk}/"))


def test_editar_e_apagar_titulo(client, versao):
    secao = op.adicionar_secao(versao, 1, titulo="Antigo", texto="Intro")
    url = f"/editor/secoes/{secao.pk}/editar/"
    assert 'value="Antigo"' in client.get(url).content.decode()
    resposta = client.post(url, {"titulo": "Novo", "texto": "Intro"})
    assert resposta["Location"] == f"/editor/secoes/{secao.pk}/?aviso=dados-salvos"
    secao.refresh_from_db()
    assert secao.titulo == "Novo"
    client.post(url, {"titulo": "   ", "texto": "Intro"})
    secao.refresh_from_db()
    assert secao.titulo is None and secao.texto == "Intro"


# --- subir / descer ------------------------------------------------------------------------


def _tres(versao):
    return [op.adicionar_secao(versao, p, titulo=t) for p, t in ((1, "A"), (2, "B"), (3, "C"))]


def test_pontas_nao_oferecem_movimento_invalido(client, versao):
    _tres(versao)
    html = client.get(f"/editor/versoes/{versao.pk}/").content.decode()
    assert 'aria-label="Subir a Seção 1 — A"' not in html
    assert 'aria-label="Descer a Seção 1 — A"' in html
    assert 'aria-label="Subir a Seção 3 — C"' in html
    assert 'aria-label="Descer a Seção 3 — C"' not in html


def test_subir_e_descer(client, versao):
    a, b, c = _tres(versao)
    resposta = client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "cima"})
    assert resposta["Location"] == f"/editor/versoes/{versao.pk}/#secao-2"
    client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "cima"})
    assert ce.ordem(versao.secoes) == ["C", "A", "B"]
    client.post(f"/editor/secoes/{a.pk}/mover/", {"direcao": "baixo"})
    assert ce.ordem(versao.secoes) == ["C", "B", "A"]
    assert ce.posicoes(versao.secoes) == [1, 2, 3]


def test_mover_na_ponta_nao_grava(client, versao):
    a, _, _ = _tres(versao)
    antes = ce.retrato(versao)
    resposta = client.post(f"/editor/secoes/{a.pk}/mover/", {"direcao": "cima"})
    assert resposta["Location"] == f"/editor/versoes/{versao.pk}/?aviso=sem-movimento"
    assert ce.retrato(versao) == antes


# --- remover -------------------------------------------------------------------------------


def test_remover_secao_vazia_com_confirmacao(client, versao):
    a, b, _ = _tres(versao)
    url = f"/editor/secoes/{b.pk}/remover/"
    confirmacao = client.get(url)
    assert "Seção 2 — B" in ce.texto_visivel(confirmacao)
    assert Secao.objects.filter(pk=b.pk).exists()
    resposta = client.post(url)
    assert resposta["Location"] == f"/editor/versoes/{versao.pk}/?aviso=secao-removida"
    assert ce.ordem(versao.secoes) == ["A", "C"]


def test_remover_secao_com_perguntas_e_recusado_pela_002(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TEXTO)))
    secao = ce.secao(versao, 1)
    antes = ce.retrato(versao)
    resposta = client.post(f"/editor/secoes/{secao.pk}/remover/")
    assert resposta.status_code == 200
    texto = ce.texto_visivel(resposta)
    assert "Remova ou mova as Perguntas" in texto
    assert ">Remover</button>" not in resposta.content.decode()
    assert ce.retrato(versao) == antes


def test_remover_secao_referenciada_explica_quem_aponta(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": 3})),
        secao_mem(pergunta_mem(tipo=TEXTO), encaminhamento=3),
        secao_mem(),
    )
    alvo = ce.secao(versao, 3)
    resposta = client.post(f"/editor/secoes/{alvo.pk}/remover/")
    texto = ce.texto_visivel(resposta)
    assert "o encaminhamento da Seção 2 (sem título)" in texto
    assert "a Opção «Não» da Pergunta 1 da Seção 1" in texto
    assert Secao.objects.filter(pk=alvo.pk).exists()


# --- dados da Versão -----------------------------------------------------------------------


def test_dados_da_versao(client, versao):
    url = f"/editor/versoes/{versao.pk}/dados/"
    resposta = client.post(
        url,
        {
            "designacao": "Teste 2",
            "titulo": "Título",
            "texto_abertura": "Abertura",
            "texto_encerramento": "Fim!",
        },
    )
    assert resposta["Location"] == f"/editor/versoes/{versao.pk}/?aviso=dados-salvos"
    versao.refresh_from_db()
    assert (versao.designacao, versao.titulo, versao.texto_encerramento) == (
        "Teste 2",
        "Título",
        "Fim!",
    )
    client.post(
        url,
        {"designacao": "Teste 2", "titulo": "", "texto_abertura": " ", "texto_encerramento": ""},
    )
    versao.refresh_from_db()
    assert versao.titulo is None and versao.texto_abertura is None


def test_dados_com_designacao_repetida(client, pesquisa, versao):
    op.criar_versao(pesquisa, "Outra")
    resposta = client.post(f"/editor/versoes/{versao.pk}/dados/", {"designacao": "Outra"})
    assert resposta.status_code == 200
    assert "Já existe uma Versão com esta designação" in resposta.content.decode()
    versao.refresh_from_db()
    assert versao.designacao == "Teste 1"


def test_pagina_da_secao_lista_perguntas(client, pesquisa):
    versao = ce.versao_de(
        pesquisa, secao_mem(pergunta_mem(regras={"Não": 2}), pergunta_mem(tipo=TEXTO)), secao_mem()
    )
    secao = ce.secao(versao, 1)
    resposta = client.get(f"/editor/secoes/{secao.pk}/")
    texto = ce.texto_visivel(resposta)
    assert "Pergunta 1" in texto and "Escolha única" in texto and "Texto curto" in texto
    assert "«Não» → segue para a Seção 2" in texto
    html = resposta.content.decode()
    assert f'href="/editor/secoes/{secao.pk}/perguntas/nova/"' in html
    assert 'id="pergunta-1"' in html and 'id="pergunta-2"' in html
    assert ce.padroes_tecnicos(resposta) == []

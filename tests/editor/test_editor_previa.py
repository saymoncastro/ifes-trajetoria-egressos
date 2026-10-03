"""Pré-visualização: leitura, não jornada (US13; FR-085 a FR-093; research R13).

Uma Seção por página, navegação por links GET na ordem estrutural, desvios como anotação.
Nunca cria Participação, Campanha ou Resposta, nem calcula ramo ativo.
"""

import re

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import TipoPergunta

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


@pytest.fixture
def proibir_jornada(monkeypatch):
    """Falha se qualquer coisa da jornada (006) ou da Participação for chamada."""

    def proibido(*args, **kwargs):
        raise AssertionError("a pré-visualização não executa a jornada")

    for alvo in (
        "trajetoria.participacao.operacoes.concluir",
        "trajetoria.participacao.percurso.percorrer",
        "trajetoria.participacao.consultas.situacao_da_jornada",
        "trajetoria.participacao.operacoes.iniciar_participacao",
    ):
        monkeypatch.setattr(alvo, proibido)


def test_indice_da_previa(client, copia):
    op.alterar_versao(copia, texto_encerramento="Encerramento fictício.")
    resposta = client.get(f"/editor/versoes/{copia.pk}/previa/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<title>Pré-visualização", html) and "<h1>Pré-visualização" in html
    texto = ce.texto_visivel(resposta)
    assert "nada é gravado; os desvios não são executados" in texto
    assert "Egresso Ifes" in texto and "Encerramento fictício." in texto
    for n in range(1, 14):
        assert f'href="/editor/versoes/{copia.pk}/previa/secoes/{n}/"' in html


def test_controles_por_tipo_e_sem_envio(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(
            pergunta_mem(),
            pergunta_mem(tipo=TipoPergunta.ESCOLHA_MULTIPLA, outro=True),
            pergunta_mem(tipo=TEXTO),
            pergunta_mem(tipo=TipoPergunta.ESCALA),
        ),
    )
    resposta = client.get(f"/editor/versoes/{versao.pk}/previa/secoes/1/")
    html = resposta.content.decode()
    assert 'type="radio"' in html and 'type="checkbox"' in html and 'type="text"' in html
    assert "<form" not in html and 'type="submit"' not in html
    assert "Descreva: «Outro»" in html  # rótulo da 008 (UX-14), reutilizado na prévia
    assert not resposta.cookies
    # 014 (FR-018 a FR-022): a prévia acompanha os controles da jornada — o grupo exclusivo
    # da escala é o próprio contêiner dos pontos, não o fieldset.
    assert re.search(r'<div class="escala" role="radiogroup" aria-labelledby="p4-enunciado"', html)
    assert not re.search(r'<fieldset[^>]*role="radiogroup"', html)


def test_lista_longa_usa_a_forma_compacta_da_008(client, pesquisa):
    opcoes = tuple(f"Curso {n}" for n in range(1, 13))
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(opcoes=opcoes)))
    html = client.get(f"/editor/versoes/{versao.pk}/previa/secoes/1/").content.decode()
    assert "<select" in html and "Curso 12" in html


def test_anotacoes_estruturais_e_navegacao_pela_ordem(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": 3}), titulo="A"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="B", encaminhamento=3),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="C"),
    )
    base = f"/editor/versoes/{versao.pk}/previa/secoes/"
    a = client.get(base + "1/")
    texto = ce.texto_visivel(a)
    assert "Se «Não» for escolhida na aplicação real, a próxima seção será: Seção 3 — C." in texto
    html = a.content.decode()
    assert f'href="{base}2/"' in html and f'href="{base}3/"' not in html  # ordem, não ramo
    b = ce.texto_visivel(client.get(base + "2/"))
    assert "Na aplicação real, depois desta seção vem: Seção 3 — C." in b
    assert client.get(base + "4/").status_code == 404
    assert client.get(base + "0/").status_code == 404


def test_secao_sem_titulo(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TEXTO)))
    resposta = client.get(f"/editor/versoes/{versao.pk}/previa/secoes/1/")
    assert "Seção 1 (sem título)" in ce.texto_visivel(resposta)


def test_previa_nao_escreve_nem_executa_jornada(client, copia, proibir_jornada):
    antes = ce.retrato(copia), ce.contagens()
    respostas = [client.get(f"/editor/versoes/{copia.pk}/previa/")]
    respostas += [
        client.get(f"/editor/versoes/{copia.pk}/previa/secoes/{n}/") for n in range(1, 14)
    ]
    assert all(r.status_code == 200 for r in respostas)
    assert all(not r.cookies for r in respostas)
    assert (ce.retrato(copia), ce.contagens()) == antes


def test_previa_da_publicada_e_sem_pessoa(client, publicada):
    resposta = client.get(f"/editor/versoes/{publicada.pk}/previa/secoes/1/")
    assert resposta.status_code == 200
    assert "Pessoa fictícia" not in ce.texto_visivel(resposta)


def test_previa_herda_so_o_tratamento_interno_da_pergunta(client, baseline):
    """015 FR-040: tipografia, estados e controles da jornada; não o ritmo nem o shell."""
    from tests.interface import construcao_interface as ci

    html = client.get(f"/editor/versoes/{baseline.pk}/previa/secoes/8/").content.decode()
    assert "Camada da jornada do egresso (015)" not in html
    assert ci.valor(html, {"pergunta", "fieldset"}, "", "legend", "font-size") == "1.125rem"
    acao = ci.tokens(html)["--cor-acao"]
    assert ci.valor(html, {"pergunta", "opcao"}, "", "input", "accent-color") == acao
    margem = ci.valor(html, {"previa"}, "pergunta", "fieldset", ("margin", "margin-bottom"))
    assert margem == "0.5rem"  # composição do editor: Perguntas intercaladas com anotações

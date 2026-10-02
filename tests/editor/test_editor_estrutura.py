"""Estrutura da Versão (US5; FR-065, FR-084)."""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import FIM, pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import TipoPergunta

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


def test_estrutura_da_copia_da_baseline(client, copia, baseline):
    resposta = client.get(f"/editor/versoes/{copia.pk}/")
    assert resposta.status_code == 200
    texto = ce.texto_visivel(resposta)
    assert copia.pesquisa.nome in texto and "Cópia de teste" in texto and "Rascunho" in texto
    assert f"criada a partir de «{baseline.designacao}»" in texto
    assert "13 Seções" in texto and "54 Perguntas" in texto
    for n in range(1, 14):
        assert f"Seção {n} " in texto
    assert "(sem título)" in texto
    for palavra in ("Escolha única", "Escolha múltipla", "Texto curto", "Escala"):
        assert palavra in texto
    assert "Obrigatória" in texto and "Opcional" in texto
    assert "segue para a Seção" in texto and "finaliza o instrumento" in texto
    assert "tem desvio" in texto and "De 1 a 5" in texto and "Opções" in texto
    html = resposta.content.decode()
    controles = re.findall(r"<(input|textarea|select)\b([^>]*)>", html)
    assert all('type="hidden"' in attrs for _, attrs in controles)
    secao = ce.secao(copia, 1)
    assert f'href="/editor/secoes/{secao.pk}/"' in html
    assert ce.padroes_tecnicos(resposta) == []


def test_textos_da_versao_ausentes_sao_explicitos(client, versao):
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{versao.pk}/"))
    assert "sem título apresentado" in texto
    assert "sem texto de abertura" in texto and "sem texto de encerramento" in texto
    assert "0 Seções" in texto


def test_textos_da_versao_presentes(client, versao):
    op.alterar_versao(versao, titulo="Egresso fictício", texto_encerramento="Obrigado!")
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{versao.pk}/"))
    assert "Egresso fictício" in texto and "Obrigado!" in texto


def test_estrutura_nao_lista_todas_as_opcoes(client, copia):
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{copia.pk}/"))
    longa = max(
        (p for s in copia.secoes.all() for p in s.perguntas.all()),
        key=lambda p: p.opcoes.count(),
    )
    ultima = longa.opcoes.order_by("posicao").last()
    assert f"{longa.opcoes.count()} Opções" in texto
    assert ultima.texto not in texto


def test_consultas_independem_do_tamanho(client, pesquisa, copia):
    pequena = ce.versao_de(
        pesquisa, secao_mem(pergunta_mem(regras={"Não": FIM})), secao_mem(pergunta_mem(tipo=TEXTO))
    )
    contagens = []
    for versao in (pequena, copia):
        with CaptureQueriesContext(connection) as consultas:
            assert client.get(f"/editor/versoes/{versao.pk}/").status_code == 200
        contagens.append(len(consultas))
    assert contagens[0] == contagens[1]

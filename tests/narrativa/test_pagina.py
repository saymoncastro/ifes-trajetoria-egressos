"""Estrutura da página (021 FR-026 a FR-030, FR-066; SC-003)."""

import re
from pathlib import Path

import pytest

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn

pytestmark = pytest.mark.django_db

CSS = Path("trajetoria/narrativa/templates/narrativa/narrativa.css")


@pytest.fixture
def pagina(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    cenario.concluir(maria.conclusoes.first())
    cn.entrar(client, maria)
    return client.get("/minha-trajetoria/")


def _principal(resposta):
    return resposta.content.decode().split('<main id="conteudo"')[1].split("</main>")[0]


def test_um_h1_e_secoes_com_h2(pagina):
    html = _principal(pagina)
    assert re.findall(r"<h1[^>]*>\s*(.*?)\s*</h1>", html) == ["Minha trajetória no Ifes"]
    h2 = re.findall(r"<h2[^>]*>\s*(.*?)\s*</h2>", html)
    assert h2[:3] == [
        "O que o Ifes registra sobre você", "Sua trajetória acadêmica", "Outras formações no Ifes",
    ]
    assert "Naquele ano no Ifes" not in h2  # P1: sem agregado, a seção não existe


def test_formacoes_em_lista_ordenada(pagina):
    html = _principal(pagina)
    lista = re.search(r"<ol[^>]*>(.*?)</ol>", html, re.S).group(1)
    assert lista.count("<li") == 2


def test_nome_uma_vez_e_discreto(pagina):
    assert _principal(pagina).count("Maria Exemplo") == 1


def test_volta_as_formacoes(pagina):
    assert re.search(r'<a href="/formacoes/">Voltar às suas formações</a>', _principal(pagina))


def test_sem_placeholders_nem_recursos_externos(pagina):
    principal = _principal(pagina)
    assert "em breve" not in principal.lower() and "—" not in principal
    assert "não informado" not in principal.lower()
    assert "http" not in principal


def test_hierarquia_sem_saltos(pagina):
    niveis = [int(n) for n in re.findall(r"<h([1-6])", _principal(pagina))]
    assert niveis[0] == 1 and all(b - a <= 1 for a, b in zip(niveis, niveis[1:], strict=False))


def test_sem_formulario_de_pesquisa_nem_respostas(pagina):
    texto = ci.texto_visivel(pagina)
    assert ci.TEXTO_FICTICIO not in texto
    assert "Atualmente você trabalha" not in texto


def test_css_sem_largura_fixa_nem_nowrap():
    css = CSS.read_text()
    larguras = [int(px) for px in re.findall(r"(?:^|[^-])width:\s*(\d+)px", css)]
    assert all(px <= 320 for px in larguras)
    assert "nowrap" not in css
    assert "http" not in css

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


def test_um_h1_e_capitulos_com_h2(pagina):
    html = _principal(pagina)
    assert re.findall(r"<h1[^>]*>\s*(.*?)\s*</h1>", html) == ["Minha trajetória no Ifes"]
    h2 = re.findall(r"<h2[^>]*>\s*(.*?)\s*</h2>", html)
    # P1: sem agregado, "Naquele ano no Ifes" não existe (FR-026, FR-027).
    assert h2 == ["Sua formação", "Sua continuidade no Ifes", "Seu card"]
    indicadores = re.findall(r'<p class="narrativa-indicador">(.*?)</p>', html)
    assert indicadores == ["Capítulo 1 de 3", "Capítulo 2 de 3", "Capítulo 3 de 3"]


def test_abertura_com_imagem_e_legenda_sem_ano(pagina):
    html = _principal(pagina)
    abertura = html.split('<div class="narrativa-abertura">')[1].split("</div>")[0]
    assert '<svg aria-hidden="true"' in abertura and "<text" not in abertura
    legenda = re.search(r"<figcaption>(.*?)</figcaption>", abertura).group(1)
    assert legenda == "Unidade Serra · ilustração"
    assert not re.search(r"\b\d{4}\b", legenda)


def test_linha_do_tempo_por_capitulo(pagina):
    html = _principal(pagina)
    listas = re.findall(r'<ol class="narrativa-linha">(.*?)</ol>', html, re.S)
    assert [lista.count("<li") for lista in listas] == [1, 1]
    assert "2022" in listas[0] and "Tecnologia em Análise" in listas[0]
    assert "Depois dessa formação" in listas[1] and "2025" in listas[1]


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


def _regra(css, seletor):
    return re.search(rf"(?:^|\n){re.escape(seletor)} \{{([^}}]*)\}}", css).group(1)


def test_css_cabe_em_320px_com_fonte_a_200(pagina):
    """FR-068 (achado A1 da 024): a 320 px com fonte a 200%, os espaçamentos em rem deixavam
    ~112 px para o texto, e "Desenvolvimento" alargava destaques e linha do tempo até 397 px."""
    css = CSS.read_text()
    assert "--respiro-lateral: min(var(--espaco-4), 5vw);" in css
    capitulo = _regra(css, ".narrativa-capitulo")
    assert "padding: var(--espaco-5) var(--respiro-lateral);" in capitulo
    assert "overflow-wrap: anywhere;" in capitulo
    assert "hyphens: auto;" in capitulo
    assert "grid-template-columns: minmax(0, 1fr);" in _regra(css, ".narrativa-destaques")
    destaque = _regra(css, ".narrativa-destaques li")
    assert "padding: var(--espaco-3) var(--respiro-lateral);" in destaque
    # A hifenização depende do idioma do documento.
    assert '<html lang="pt-BR"' in pagina.content.decode()


def test_indicador_so_com_dois_ou_mais_capitulos():
    from trajetoria.narrativa.montagem import montar
    from trajetoria.narrativa.views import _capitulos

    # Formação sem nenhum atributo: só o capítulo do card, sem indicador.
    so_card = _capitulos(montar(cn.entrada([cn.fato()])))
    assert [c["chave"] for c in so_card] == ["seu_card"] and so_card[0]["indicador"] is None
    uma = _capitulos(montar(cn.entrada([cn.fato(curso="A", ano_conclusao=2020)])))
    assert [c["chave"] for c in uma] == ["sua_formacao", "seu_card"]
    assert [c["indicador"] for c in uma] == ["Capítulo 1 de 2", "Capítulo 2 de 2"]


def test_continuidade_so_com_duas_ou_mais_formacoes():
    from trajetoria.narrativa.montagem import montar
    from trajetoria.narrativa.views import _capitulos

    duas = cn.entrada(
        [cn.fato(curso="A", ano_conclusao=2018), cn.fato(curso="B", ano_conclusao=2021)]
    )
    capitulos = {c["chave"]: c for c in _capitulos(montar(duas))}
    assert [i["ano"] for i in capitulos["continuidade"]["itens"]] == [2021]
    assert capitulos["continuidade"]["itens"][0]["relacao"].texto.startswith("Depois")
    uma = _capitulos(montar(cn.entrada([cn.fato(curso="A")])))
    assert "continuidade" not in {c["chave"] for c in uma}

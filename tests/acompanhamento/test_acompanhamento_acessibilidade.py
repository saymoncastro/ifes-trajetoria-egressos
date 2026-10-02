"""Marcação acessível, sem JavaScript, sem depender de cor (Feature 011; US13; spec FR-120 a
FR-125; SC-011, SC-012)."""

import re

import pytest

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel

RECORTES = ("unidade", "curso", "nivel", "modalidade", "forma-oferta", "ano-conclusao")
PROIBIDOS = (
    "dashboard", "kpi", "funil", "abandono", "desistência", "ranking", "melhor", "pior",
    "questionários integralmente respondidos", "role", "permission", "scope",
)  # fmt: skip


def _paginas(ref, cliente_cpaeg, cliente_csaeg_vitoria):
    paginas = [cliente_cpaeg.get("/acompanhamento/")]
    paginas += [k.detalhe(cliente_cpaeg, ref.I, r) for r in RECORTES]
    paginas.append(k.detalhe(cliente_csaeg_vitoria, ref.R))  # recusa
    return paginas


def test_estrutura_comum(ref, cliente_cpaeg, cliente_csaeg_vitoria):
    for resposta in _paginas(ref, cliente_cpaeg, cliente_csaeg_vitoria):
        html = resposta.content.decode()
        assert '<html lang="pt-BR">' in html
        assert html.count("<h1>") == 1
        assert 'href="#conteudo"' in html and 'id="conteudo"' in html
        assert "<script" not in html.lower()
        assert "<progress" not in html.lower()
        assert "<main" in html and "<footer>" in html
        assert "Este acompanhamento não está disponível para uso produtivo." in html


def test_tabelas(ref, cliente_cpaeg):
    for resposta in [cliente_cpaeg.get("/acompanhamento/")] + [
        k.detalhe(cliente_cpaeg, ref.I, r) for r in RECORTES
    ]:
        html = resposta.content.decode()
        tabelas = re.findall(r"<table>(.*?)</table>", html, re.S)
        assert tabelas
        for tabela in tabelas:
            assert "<caption>" in tabela
            assert 'scope="col"' in tabela and 'scope="row"' in tabela
        assert re.search(r'class="rolagem" role="region" aria-label="[^"]+" tabindex="0"', html)


@pytest.mark.parametrize("recorte", RECORTES)
def test_navegacao_de_recortes(ref, cliente_cpaeg, recorte):
    html = k.detalhe(cliente_cpaeg, ref.I, recorte).content.decode()
    nav = re.search(r'<nav class="recortes" aria-label="Recortes">(.*?)</nav>', html, re.S).group(1)
    assert nav.count('aria-current="page"') == 1
    assert f'href="?recorte={recorte}" aria-current="page"' in nav


def test_recorte_por_curso_tem_cabecalho_de_linha_na_primeira_coluna(ref, cliente_cpaeg):
    """Regressão do code review: com a coluna Unidade, unidade e curso são cabeçalhos de linha;
    a unidade que desambigua cursos homônimos é anunciada com cada célula."""
    html = k.detalhe(cliente_cpaeg, ref.I, "curso").content.decode()
    corpo = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    for linha in re.findall(r"<tr>(.*?)</tr>", corpo, re.S):
        celulas = re.findall(r"<(t[hd])( scope=\"row\")?", linha)
        assert celulas[:2] == [("th", ' scope="row"'), ("th", ' scope="row"')], linha


def test_traco_tem_texto_acessivel(ref, cliente_cpaeg):
    vazia = k.campanha(ref.inst.versao, unidades=["Unidade inexistente"])
    html = k.detalhe(cliente_cpaeg, vazia).content.decode()
    assert (
        '<span aria-hidden="true">—</span><span class="visualmente-oculto">não se aplica</span>'
        in html
    )


def test_termos_proibidos(ref, cliente_cpaeg, cliente_csaeg_vitoria):
    for resposta in _paginas(ref, cliente_cpaeg, cliente_csaeg_vitoria):
        texto = texto_visivel(resposta).lower()
        for termo in PROIBIDOS:
            assert not re.search(rf"\b{re.escape(termo)}\b", texto), termo

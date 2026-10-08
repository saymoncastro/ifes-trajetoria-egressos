"""Shell e navegação do Portal (024 FR-022 a FR-025; contracts/navegacao.md)."""

import re
from pathlib import Path

import pytest
from django.test import Client

from tests.interface import construcao_interface as ci
from tests.portal import construcao as cp
from trajetoria.portal import mensagens

pytestmark = pytest.mark.django_db

REFERENCIA = Path(__file__).with_name("referencia_shell.html")


def _shell(html: str) -> str:
    return html[html.index("<header"): html.index("<main")]


def _referencias() -> tuple[str, str]:
    texto = REFERENCIA.read_text("utf-8")
    acesso, secao = texto.split("\n<!-- secao -->\n")
    return acesso.removeprefix("<!-- /acesso/ -->\n"), secao.removesuffix("\n")


def test_shell_sem_navegacao_identico(client, cenario):
    """SC-007: com o slot vazio, o HTML do cabeçalho é o da linha de base (T001)."""
    acesso, secao = _referencias()
    assert _shell(client.get("/acesso/").content.decode()) == acesso
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    pagina = client.get(resposta["Location"], follow=True).content.decode()
    assert "/secoes/" in pagina and _shell(pagina) == secao


# --- Telas com e sem navegação (FR-022, FR-023; contracts/navegacao.md) ---------------------

def _nav(html: str) -> str | None:
    achado = re.search(r'<nav class="navegacao".*?</nav>', html, re.S)
    return achado.group(0) if achado else None


def _itens(nav: str) -> list[tuple[str, str, bool]]:
    return [
        (endereco, rotulo, atual is not None and "aria-current" in atual)
        for endereco, atual, rotulo in re.findall(
            r'<a href="([^"]+)"( aria-current="page")?>([^<]+)</a>', nav
        )
    ]


def test_navegacao_nas_telas_fora_das_secoes(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    cp.entrar(client, ana)
    esperado = ["/inicio/", "/minha-trajetoria/", "/formacoes/", "/meu-email/"]
    for url in esperado:
        nav = _nav(client.get(url).content.decode())
        assert nav and f'aria-label="{mensagens.ROTULO_NAVEGACAO}"' in nav, url
        itens = _itens(nav)
        assert [i[0] for i in itens] == esperado, url
        assert [i[0] for i in itens if i[2]] == [url], url
        assert "<script" not in nav
    for endereco in esperado:
        assert client.get(endereco).status_code == 200


def test_confirmacao_marca_a_pesquisa(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    participacao = cenario.concluir(ana.conclusoes.first())
    cp.entrar(client, ana)
    nav = _nav(client.get(f"/participacoes/{participacao.pk}/concluida/").content.decode())
    assert [i[0] for i in _itens(nav) if i[2]] == ["/formacoes/"]


def test_sem_navegacao_nas_secoes_entrada_e_declaracao(client, cenario):
    from tests.declaracao import construcao as cd

    ana = cenario.pessoa("SIM-P-0001")
    resposta = ci.iniciar(client, ana)
    secao = client.get(resposta["Location"], follow=True).content.decode()
    assert "/secoes/" in secao and _nav(secao) is None
    for url in ("/acesso/", "/entrar/?aviso=qualquer"):
        assert _nav(Client().get(url).content.decode()) is None
    declarante = Client()
    cp.sessao_de_declarante(declarante, cd.declaracao_concluida(cenario.campanha))
    assert _nav(declarante.get("/declaracao/").content.decode()) is None


def test_sem_conclusao_sem_item_da_trajetoria(client, cenario):
    cp.entrar(client, cp.pessoa_sem_conclusao())
    itens = _itens(_nav(client.get("/inicio/").content.decode()))
    assert [i[0] for i in itens] == ["/inicio/", "/formacoes/", "/meu-email/"]


def test_cabecalho_do_produto(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    inicio = client.get("/inicio/").content.decode()
    formacoes = client.get("/formacoes/").content.decode()
    assert f'<span class="nome">{mensagens.PRODUTO}</span>' in inicio
    assert '<span class="nome">Trajetória Ifes</span>' in formacoes
    for html in (inicio, formacoes):
        cabecalho = _shell(html)
        assert cabecalho.index('class="assinatura"') < cabecalho.index('class="produto-nome"')

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
            r'<a href="([^"]+)" data-rotulo="[^"]*"( aria-current="page")?>([^<]+)</a>', nav
        )
    ]


def test_navegacao_nas_telas_fora_das_secoes(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    cp.entrar(client, ana)
    # Revisado pela 025 (FR-020): "Oportunidades" entre "Minha trajetória" e "Pesquisa".
    # Revisado pela 026 (FR-011; plan R9): "Contribuir" logo depois de "Oportunidades".
    esperado = ["/inicio/", "/minha-trajetoria/", "/oportunidades/", "/contribuir/",
                "/formacoes/", "/meu-email/"]
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


def _nome_do_produto(html: str) -> str:
    return re.search(r'<span class="nome">([^<]+)</span>', _shell(html)).group(1)


def test_cabecalho_do_produto(client, cenario):
    """FR-024, revisado em 2026-10-08 (avaliação por IA, A1): "Portal do Egresso" em toda tela
    com a navegação do Portal; "Trajetória Ifes" nas Seções e em `/acesso/`."""
    ana = cenario.pessoa("SIM-P-0001")
    participacao = cenario.concluir(ana.conclusoes.first())
    cp.entrar(client, ana)
    telas = ("/inicio/", "/formacoes/", "/minha-trajetoria/", "/meu-email/",
             f"/participacoes/{participacao.pk}/concluida/")
    for url in telas:
        html = client.get(url).content.decode()
        assert _nav(html), url
        assert _nome_do_produto(html) == mensagens.PRODUTO, url
        assert f'<p class="ambiente">{mensagens.PRODUTO} —' in html, url
        cabecalho = _shell(html)
        assert cabecalho.index('class="assinatura"') < cabecalho.index('class="produto-nome"')
    assert _nome_do_produto(Client().get("/acesso/").content.decode()) == "Trajetória Ifes"


def test_secao_mantem_o_nome_da_pesquisa(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    secao = client.get(resposta["Location"], follow=True).content.decode()
    assert "/secoes/" in secao and _nome_do_produto(secao) == "Trajetória Ifes"


# --- Saída e retorno (revisão de 2026-10-08: A2, A3, A4) ------------------------------------

def _acao_sair(html: str) -> str:
    return re.search(r'<form method="post" action="([^"]+)"><input[^>]*><button[^>]*>Sair<',
                     html).group(1)


def test_sair_das_telas_do_portal_volta_a_entrada_do_portal(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    cp.entrar(client, ana)
    for url in ("/inicio/", "/formacoes/", "/minha-trajetoria/", "/meu-email/"):
        assert _acao_sair(client.get(url).content.decode()) == "/sair/", url
    resposta = client.post("/sair/")
    assert resposta.status_code == 303 and resposta["Location"] == "/entrar/"
    assert client.get("/inicio/")["Location"].startswith("/entrar/")


def test_sair_das_secoes_continua_pelo_convite(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    secao = client.get(resposta["Location"], follow=True).content.decode()
    assert _acao_sair(secao) == "/acesso/sair/"


def test_sair_do_portal_so_por_post(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    assert client.get("/sair/").status_code == 405
    assert client.get("/inicio/").status_code == 200


def test_fim_da_trajetoria_e_do_email_voltam_ao_inicio(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    trajetoria = client.get("/minha-trajetoria/").content.decode()
    assert f'<a href="/inicio/">{mensagens.VOLTAR_AO_INICIO}</a>' in trajetoria
    assert "Voltar às suas formações" not in trajetoria
    email = client.get("/meu-email/").content.decode()
    assert f'<a href="/inicio/">{mensagens.VOLTAR_AO_INICIO}</a>' in email
    assert "Ver suas formações no Ifes" not in email


def test_sair_com_alvo_minimo(client, cenario):
    """Revisão de 2026-10-08 (A6): o "Sair" da faixa tem o alvo mínimo da 014."""
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    estilo = client.get("/inicio/").content.decode()
    regra = re.search(r"\n\.faixa-demonstracao button \{([^}]*)\}", estilo).group(1)
    assert "min-width: var(--alvo)" in regra and "min-height: var(--alvo)" in regra

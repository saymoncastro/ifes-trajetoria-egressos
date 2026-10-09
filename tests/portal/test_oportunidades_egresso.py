"""Página de Oportunidades do egresso (025 FR-011, FR-015, FR-017 a FR-019, FR-024; T028, T040)."""

import re
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.portal import construcao as cp
from tests.portal import construcao_oportunidades as co
from trajetoria.portal.oportunidades import mensagens

pytestmark = pytest.mark.django_db

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"


def _pagina(client, pessoa):
    cp.entrar(client, pessoa)
    resposta = client.get("/oportunidades/")
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    return resposta.content.decode()


def _principal(html: str) -> str:
    return html[html.index("<main"): html.index("</main>")]


# --- Acessos (FR-011, FR-024) ---------------------------------------------------------------


def test_sem_sessao_vai_para_a_entrada_do_portal(client, cenario):
    resposta = client.get("/oportunidades/")
    assert resposta.status_code == 303 and resposta["Location"] == "/entrar/"


def test_sessao_expirada_avisa(client, cenario, relogio):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    relogio.agora += timedelta(minutes=31)
    assert client.get("/oportunidades/")["Location"] == "/entrar/?aviso=sessao"


def test_declarante_vai_para_a_declaracao(client, cenario):
    from tests.declaracao import construcao as cd

    cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
    assert client.get("/oportunidades/")["Location"] == "/declaracao/"


def test_pessoa_sem_conclusao_vai_ao_inicio(client, cenario):
    co.publicada()
    cp.entrar(client, cp.pessoa_sem_conclusao())
    resposta = client.get("/oportunidades/")
    assert resposta.status_code == 303 and resposta["Location"] == "/inicio/"


def test_so_get(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    assert client.post("/oportunidades/").status_code == 405


# --- Estrutura (FR-017, FR-023) -------------------------------------------------------------


def test_estrutura_e_item(client, cenario):
    co.publicada("Para TADS", publico_cursos=[TADS], unidade_responsavel="Serra")
    co.publicada("Para todos")
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    assert principal.count("<h1") == 1
    assert principal.index(mensagens.GRUPO_FORMACAO) < principal.index(mensagens.GRUPO_TODOS)
    assert principal.count("<h3") == 2
    assert f'<a href="{co.ENDERECO}" rel="noreferrer">Para TADS' in principal
    assert "— site externo: oportunidades.example</span>" in principal
    assert "Cursos e formação continuada" in principal
    assert "Resumo de teste." in principal
    assert f"Aparece porque você concluiu {TADS} (Serra, 2022)." in principal
    assert "Oferecida pela unidade Serra · site externo: oportunidades.example" in principal
    assert "Oferecida pelo Ifes · site externo: oportunidades.example" in principal
    assert "Aberta a todos os egressos do Ifes." in principal


def test_sem_datas_contagens_nem_script(client, cenario):
    co.publicada()
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    assert "<script" not in principal
    assert not re.search(r"\d{2}/\d{2}/\d{4}", principal)  # datas de divulgação ocultas
    assert not re.search(r"\d+ egressos", principal)


def test_grupo_vazio_omitido(client, cenario):
    co.publicada("Só para todos")
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    assert mensagens.GRUPO_FORMACAO not in principal and mensagens.GRUPO_TODOS in principal


def test_parametros_ignorados(client, cenario):
    co.publicada()
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    normal = _principal(client.get("/oportunidades/").content.decode())
    estranho = client.get("/oportunidades/?grupo=x&ordem=y&destino=/x").content.decode()
    assert _principal(estranho) == normal


def test_titulo_e_resumo_sempre_escapados(client, cenario):
    """FR-002 (U1 do /speckit-analyze)."""
    co.publicada("<script>alert(1)</script> & <b>x</b>",
                 resumo='Veja <a href="https://evil.example">aqui</a>.')
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; &lt;b&gt;x&lt;/b&gt;" in principal
    assert "<script" not in principal and "<b>" not in principal
    assert 'href="https://evil.example"' not in principal


# --- Nada gravado; leituras (FR-008, FR-011, FR-015) -------------------------------------


def test_exibir_nao_grava(client, cenario):
    co.publicada()
    antes = cp.contagens()
    _pagina(client, cenario.pessoa("SIM-P-0003"))
    assert cp.contagens() == antes


def test_nao_le_resposta_contato_declaracao_nem_campanha(client, cenario):
    co.publicada()
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    with CaptureQueriesContext(connection) as consultas:
        assert client.get("/oportunidades/").status_code == 200
    sql = " ".join(q["sql"] for q in consultas.captured_queries)
    for tabela in ("participacao_resposta", "contato_contatodapessoa", "declaracao_",
                   "campanha_"):
        assert tabela not in sql, tabela


# --- Estados invisíveis (FR-019) ------------------------------------------------------------


def test_so_em_divulgacao_aparece(client, cenario):
    from trajetoria.portal.oportunidades import operacoes

    co.rascunho("Rascunho em curso")
    co.publicada("Agendada", inicio=co.HOJE + timedelta(days=5), fim=co.HOJE + timedelta(days=9))
    retirada = co.publicada("Retirada")
    operacoes.retirar(retirada.pk, operador=co.OPERADOR_A, escopo=co.ESCOPO_A,
                      agora=retirada.publicada_em)
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    for titulo in ("Rascunho em curso", "Agendada", "Retirada"):
        assert titulo not in principal


# --- Estado vazio (FR-018; T040) ------------------------------------------------------------


def test_estado_vazio(client, cenario):
    principal = _principal(_pagina(client, cenario.pessoa("SIM-P-0001")))
    assert mensagens.VAZIO in principal
    assert '<a href="/inicio/">Voltar ao Início</a>' in principal
    assert "pesquisa" not in re.sub(r"<[^>]+>", " ", principal).lower()


def test_estado_vazio_mantem_o_item_na_navegacao(client, cenario):
    html = _pagina(client, cenario.pessoa("SIM-P-0001"))
    assert 'href="/oportunidades/" data-rotulo="Oportunidades" aria-current="page"' in html
    inicio = client.get("/inicio/").content.decode()
    assert '<section class="inicio-oportunidades' not in inicio

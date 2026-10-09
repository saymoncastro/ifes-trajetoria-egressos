"""Regressões da 028: página pública, extensão neutra e proveniência do reconhecimento."""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.portal import construcao as cp
from trajetoria.contexto_trajetoria.carga import carregar_contexto
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.portal import mensagens

pytestmark = pytest.mark.django_db


def test_publico_sem_pessoa_sem_formulario_e_sem_consulta_academica(client, cenario):
    with CaptureQueriesContext(connection) as consultas:
        resposta = client.get("/?next=/editor/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    principal = html[html.index("<main"):html.index("</main>")]
    assert 'href="/entrar/"' in principal
    assert "Exemplo com dados fictícios" in principal
    assert "<input" not in principal and "<script" not in principal
    assert principal.count("<h1") == 1
    assert cenario.pessoa("SIM-P-0001").nome not in principal
    sql = " ".join(q["sql"] for q in consultas.captured_queries)
    assert "academico_" not in sql and "participacao_" not in sql


def test_base_nova_so_nas_telas_harmonizadas(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    for url in ("/inicio/", "/minha-trajetoria/", "/meu-email/", "/oportunidades/"):
        assert "--portal-profundo:" in client.get(url).content.decode(), url
    for url in ("/acesso/", "/formacoes/"):
        assert "--portal-profundo:" not in client.get(url).content.decode(), url


def test_painel_recolhido_so_no_entrar(client, cenario):
    html = client.get("/entrar/").content.decode()
    assert '<details class="painel-ficticio">' in html
    assert "<summary>Dados fictícios para demonstração</summary>" in html
    assert '<details class="painel-ficticio" open' not in html
    assert 'class="painel-ficticio"' not in client.get("/acesso/").content.decode()


def test_inicio_previa_sem_nome_e_agregados_da_narrativa(client, cenario):
    ana = cenario.pessoa("SIM-P-0001")
    carregar_contexto(ContextoSimulado(), ana)
    cp.entrar(client, ana)
    html = client.get("/inicio/").content.decode()
    assert re.search(r'src="/minha-trajetoria/card\.(png|svg)"', html)
    assert "Naquele ano no Ifes" in html
    assert "27 conclusões" in html and "812 conclusões" in html
    assert "31/01/2026" in html
    assert "card.png?nome=" not in html and "card.svg?nome=" not in html
    card = client.get("/minha-trajetoria/card.svg")
    assert card.status_code == 200
    assert "Ifes · ilustração" in card.content.decode()


def test_sem_reconhecimento_nao_tem_previa(client, cenario, monkeypatch):
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    def falha(entrada):
        raise RuntimeError("montagem indisponível")

    monkeypatch.setattr("trajetoria.portal.inicio.montar", falha)
    html = client.get("/inicio/").content.decode()
    assert not re.search(r'src="/minha-trajetoria/card\.(png|svg)"', html)


def test_pessoa_sem_conclusao_sem_previa(client, cenario):
    cp.entrar(client, cp.pessoa_sem_conclusao())
    html = client.get("/inicio/").content.decode()
    assert not re.search(r'src="/minha-trajetoria/card\.(png|svg)"', html)
    assert "Naquele ano no Ifes" not in html


def test_sem_dependencia_de_nome_de_template_do_cliente(client, cenario):
    resposta = client.get("/entrar/?layout_base=editor/base.html")
    assert "--portal-profundo:" in resposta.content.decode()
    assert f"<h1>{mensagens.TITULO_ENTRADA}</h1>" in resposta.content.decode()


def test_formacoes_horizontais_continuam_em_ordem(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0004"))
    html = client.get("/inicio/").content.decode()
    linha = re.search(r'<ul class="inicio-formacoes.*?</ul>', html, re.S).group(0)
    assert len(re.findall(r"<li>", linha)) == 3
    assert "2012" in linha and "2017" in linha and "2020" in linha


def test_previa_do_card_no_formato_da_trajetoria_e_acao_sem_repeticao(client, cenario, monkeypatch):
    """A prévia usa o mesmo formato da Minha trajetória (PNG com fontes embutidas quando há
    rasterização) e a ação do card aparece uma vez, junto da prévia (code review da 028)."""
    from trajetoria.narrativa import rasterizacao

    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    for disponivel, formato in ((True, "png"), (False, "svg")):
        monkeypatch.setattr(rasterizacao, "rasterizacao_disponivel", lambda d=disponivel: d)
        html = client.get("/inicio/").content.decode()
        assert f'src="/minha-trajetoria/card.{formato}"' in html
        assert html.count(f">{mensagens.ACAO_CARD}<") == 1


def test_card_publico_gerado_pelo_card_da_021(client, cenario):
    from trajetoria.portal.exemplo import card_de_exemplo

    html = client.get("/").content.decode()
    assert str(card_de_exemplo()) in html
    assert "Ifes · ilustração" in html and "Técnico em Edificações" in html


def test_ligacao_no_meio_do_texto_nao_vira_caixa():
    """Só ligações isoladas ganham o alvo de 44 px como caixa (code review da 028)."""
    from pathlib import Path

    from trajetoria.portal import inicio as inicio_do_portal

    css = (Path(inicio_do_portal.__file__).with_name("templates") / "portal" / "visual.css"
           ).read_text("utf-8")
    assert not re.search(r"(^|[\s,}])main a\s*\{", css, re.M)

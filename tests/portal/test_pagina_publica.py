"""Página pública do Portal (029 FR-001 a FR-013; SC-007, SC-008). Revisado pela 032 (FR-005,
FR-006): ordem, chamadas e composição da convergência C; o resto da 029 continua valendo."""

import html as html_lib
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from trajetoria.portal.exemplo import FORMACOES_FICTICIAS, demonstracao_publica

pytestmark = pytest.mark.django_db

def _principal(client) -> str:
    resposta = client.get("/")
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    html = resposta.content.decode()
    return html[html.index("<main"):html.index("</main>")]


def _texto(fragmento: str) -> str:
    return html_lib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragmento)))


def test_ordem_da_relacao(client, cenario):
    """032 FR-005: reconhecimento com a linha → como funciona → encontros → oportunidades →
    contribuição e participação → o card e a chamada final."""
    principal = _principal(client)
    marcas = ('id="titulo-publico"', 'class="publico-linha"', 'id="titulo-como"',
              'id="titulo-encontros"', 'id="titulo-oportunidades"', 'id="titulo-contribuir"',
              'id="titulo-final"')
    posicoes = [principal.index(m) for m in marcas]
    assert posicoes == sorted(posicoes)
    assert principal.count("<h1") == 1
    linha = _texto(principal[posicoes[1]:posicoes[2]])
    etapas = [linha.index(e) for e in ("Ingresso", "Formação", "Conclusão", "Hoje", "Adiante")]
    assert etapas == sorted(etapas)


def test_chamadas_e_destinos(client, cenario):
    """032 FR-006: "Conhecer o Portal" no topo e no fim, "Entrar para oferecer" e "Ver como
    funciona" por âncora; menu da página por âncoras; nenhum link para área inexistente ou site
    externo (029 SC-008)."""
    html = client.get("/").content.decode()
    principal = html[html.index("<main"):html.index("</main>")]
    assert re.findall(r'href="/entrar/">([^<]+)</a>', principal) == [
        "Conhecer o Portal", "Entrar para oferecer", "Conhecer o Portal"]
    assert 'href="#como">Ver como funciona</a>' in principal and 'id="como"' in principal
    assert "Para entrar, você confirma seu CPF e sua data de nascimento." in principal
    assert set(re.findall(r'href="([^"]*)"', principal)) == {"/entrar/", "#como"}
    menu = html[html.index('<nav class="publico-menu"'):html.index("<main")]
    assert re.findall(r'href="([^"]*)"', menu) == ["#encontros", "#oportunidades", "#contribuir",
                                                    "/entrar/"]
    for ancora in ("encontros", "oportunidades", "contribuir"):
        assert f'id="{ancora}"' in principal


def test_demonstracao_identificada_e_coerente(client, cenario):
    """FR-009, FR-010: cada peça com o selo; as formações do card em toda a página."""
    principal = _principal(client)
    demo = demonstracao_publica()
    assert principal.count("Exemplo") == 3  # encontro, oportunidade e card (032)
    assert str(demo["card"]) in principal
    texto = _texto(principal)
    for formacao in FORMACOES_FICTICIAS:
        assert formacao.curso in texto
    assert "registro acadêmico do Ifes" in texto
    for o in demo["oportunidades"]:
        assert o.titulo in texto and o.explicacao in texto
    assert "Quando não há nenhum, nada aparece." in texto


def test_textos_de_participacao_com_a_finalidade(client, cenario):
    """FR-006: pesquisa e e-mail opcionais, com a finalidade da 020; contribuição sem prazo
    nem resposta garantidos (026 FR-014)."""
    texto = _texto(_principal(client))
    assert "deixar um e-mail para o Ifes convidar você para as próximas" in texto
    assert "As duas coisas são opcionais." in texto
    assert "Não há prazo garantido." in texto and "pode retirar quando quiser" in texto


VEDADOS = re.compile(
    r"conectad|comunidade|%|\bturma|geração|\bOlá\b|Volte ao Ifes|últimas vagas|não perca|"
    r"recomendad|selecionad[oa] para você|\blogin\b|\bconta\b|acesso seguro|Em construção|"
    r"vídeo|continua\.|garantimos|em até",
    re.I,
)


def test_sem_vocabulario_vedado_nem_funcao_inexistente(client, cenario):
    """SC-007; FR-007; ADR 0009, decisão 7; 018 FR-061."""
    assert VEDADOS.findall(_texto(_principal(client))) == []


def test_sem_formulario_script_nem_consulta(client, cenario):
    """FR-002, FR-003, FR-013: nenhum dado coletado, nenhum JavaScript, nenhuma consulta a
    Pessoa, Conclusão, Oportunidade, Manifestação ou contato."""
    with CaptureQueriesContext(connection) as consultas:
        principal = _principal(client)
    assert "<form" not in principal and "<script" not in principal
    sql = " ".join(q["sql"] for q in consultas.captured_queries)
    for tabela in ("academico_", "portal_", "contato_", "participacao_"):
        assert tabela not in sql, tabela


def test_decoracao_fora_da_acessibilidade_e_sem_a_marca(client, cenario):
    """029 FR-013; DP-3202: memórias e fio são decorativos; nenhum padrão da marca Ifes."""
    principal = _principal(client)
    assert re.search(r'<p class="publico-memorias" aria-hidden="true">', principal)
    assert re.search(r'<div class="publico-fio" aria-hidden="true">', principal)
    assert "turma" not in principal.lower()


AJUSTES = ("continua.", "Comunidade", "conexão", "formou sozinho", "Entrar no meu espaço",
           "Que bom ver", "Compartilhar")


def test_ajustes_de_texto_da_032(client, cenario):
    """032, "Ajustes de texto em relação aos mockups": nenhum dos textos retirados volta."""
    html = client.get("/").content.decode()
    texto = _texto(html[html.index("<nav class=\"publico-menu\""):html.index("</main>")])
    for retirado in AJUSTES:
        assert retirado not in texto, retirado
    assert "Ninguém se forma sozinho." in texto

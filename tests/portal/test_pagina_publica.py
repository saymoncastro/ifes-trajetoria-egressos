"""Página pública do Portal (029 FR-001 a FR-013; SC-007, SC-008)."""

import html as html_lib
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from trajetoria.portal.exemplo import FORMACOES_FICTICIAS, demonstracao_publica

pytestmark = pytest.mark.django_db

SELO = "Exemplo com dados fictícios"


def _principal(client) -> str:
    resposta = client.get("/")
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    html = resposta.content.decode()
    return html[html.index("<main"):html.index("</main>")]


def _texto(fragmento: str) -> str:
    return html_lib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragmento)))


def test_ordem_da_relacao(client, cenario):
    """FR-004: relação → oportunidades → participação → trajetória → chamada final."""
    principal = _principal(client)
    marcas = ('id="titulo-publico"', 'id="titulo-oferece"', 'id="titulo-participar"',
              'id="titulo-trajetoria"', 'id="titulo-final"')
    posicoes = [principal.index(m) for m in marcas]
    assert posicoes == sorted(posicoes)
    assert principal.count("<h1") == 1
    participar = principal[posicoes[2]:posicoes[3]]
    # FR-006 (revisado pela T024 da 026): a contribuição abre a participação.
    ordem = [participar.index(t) for t in ("Contribua com o Ifes", "Conte como sua trajetória",
                                            "Mantenha um canal")]
    assert ordem == sorted(ordem)


def test_chamadas_e_destinos(client, cenario):
    """FR-008: "Conhecer o Portal" no topo e no fim; "Ver como funciona" por âncora; nenhum
    link para área inexistente ou site externo (SC-008)."""
    principal = _principal(client)
    assert principal.count('href="/entrar/">Conhecer o Portal</a>') == 2
    assert 'href="#oferece">Ver como funciona</a>' in principal and 'id="oferece"' in principal
    assert "Para entrar, você confirma seu CPF e sua data de nascimento." in principal
    assert set(re.findall(r'href="([^"]*)"', principal)) == {"/entrar/", "#oferece"}


def test_demonstracao_identificada_e_coerente(client, cenario):
    """FR-009, FR-010: cada peça com o selo; as formações do card em toda a página."""
    principal = _principal(client)
    demo = demonstracao_publica()
    assert principal.count(SELO) == 6  # composição, 2 oportunidades, contribuição, linha, card
    assert str(demo["card"]) in principal
    texto = _texto(principal)
    for formacao in FORMACOES_FICTICIAS:
        assert formacao.curso in texto
    assert "Registro do Ifes" in texto
    for o in demo["oportunidades"]:
        assert o.titulo in texto and o.explicacao in texto
    assert "Quando não há nenhuma, nada aparece." in texto


def test_textos_de_participacao_com_a_finalidade(client, cenario):
    """FR-006: pesquisa e e-mail opcionais, com a finalidade da 020; contribuição sem prazo
    nem resposta garantidos (026 FR-014)."""
    texto = _texto(_principal(client))
    assert "Você pode deixar um e-mail para o Ifes convidar você para as próximas pesquisas " \
           "de acompanhamento. Também é opcional." in texto
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


def test_composicao_decorativa_fora_da_acessibilidade(client, cenario):
    """A composição da abertura repete peças da demonstração: fica fora da leitura (FR-013)."""
    principal = _principal(client)
    assert re.search(r'<div class="publico-visual" aria-hidden="true">', principal)

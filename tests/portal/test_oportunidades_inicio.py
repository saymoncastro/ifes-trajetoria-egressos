"""Bloco de Oportunidades no Início (025 FR-021; research R9; T027, T029).

P-270: toda variante de compactação mantém título, explicação, unidade responsável, origem
do site e domínio (FR-004, FR-013). A variante adotada é a medida na T046.
"""

import re

import pytest

from tests.portal import construcao as cp
from tests.portal import construcao_oportunidades as co
from trajetoria.portal import inicio as inicio_do_portal
from trajetoria.portal import mensagens as m_portal

pytestmark = pytest.mark.django_db

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"


def _principal(client, pessoa) -> str:
    cp.entrar(client, pessoa)
    html = client.get("/inicio/").content.decode()
    return html[html.index("<main"): html.index("</main>")]


def _bloco(principal: str) -> str | None:
    achado = re.search(r'<section class="inicio-oportunidades.*?</section>', principal, re.S)
    return achado.group(0) if achado else None


@pytest.fixture
def catalogo(cenario):
    co.publicada("Para TADS", publico_cursos=[TADS], unidade_responsavel="Serra")
    co.publicada("Para todos")


def test_ordem_dos_blocos(client, cenario, catalogo):
    principal = _principal(client, cenario.pessoa("SIM-P-0001"))
    posicoes = [principal.index(marca) for marca in (
        "inicio-formacoes", m_portal.TITULO_ACOES, 'class="inicio-oportunidades',
        'class="inicio-convite"',
    )]
    assert posicoes == sorted(posicoes)


def test_um_destaque_o_primeiro_e_link_para_as_demais(client, cenario, catalogo):
    bloco = _bloco(_principal(client, cenario.pessoa("SIM-P-0001")))
    assert bloco.count('rel="noreferrer"') == 1
    assert ">Para TADS<" in bloco and "Para todos" not in bloco
    assert '<a href="/oportunidades/">Ver as 2 oportunidades</a>' in bloco


def test_uma_so_oportunidade(client, cenario):
    co.publicada("Única")
    bloco = _bloco(_principal(client, cenario.pessoa("SIM-P-0001")))
    assert '<a href="/oportunidades/">Ver a página de Oportunidades</a>' in bloco


def test_sem_itens_sem_bloco(client, cenario):
    co.publicada("Só para Vitória", publico_unidades=["Vitória"], unidade_responsavel="Vitória")
    principal = _principal(client, cenario.pessoa("SIM-P-0001"))
    assert _bloco(principal) is None and "Oportunidade" not in principal


def test_pessoa_sem_conclusao_sem_bloco(client, cenario):
    co.publicada()
    assert _bloco(_principal(client, cp.pessoa_sem_conclusao())) is None


def test_convite_inalterado(client, cenario, catalogo):
    principal = _principal(client, cenario.pessoa("SIM-P-0001"))
    convite = principal[principal.index('class="inicio-convite"'):]
    assert m_portal.CONVITE_UMA.format(curso=TADS) in convite
    assert f'href="/formacoes/">{m_portal.ACAO_RESPONDER}<' in convite


@pytest.mark.parametrize("variante", [0, 1, 2, 3])
def test_toda_variante_mantem_a_informacao_exigida(client, cenario, catalogo, monkeypatch,
                                                   variante):
    """P-270 (T027): compactar nunca omite informação."""
    monkeypatch.setattr(inicio_do_portal, "COMPACTACAO_DO_DESTAQUE", variante)
    bloco = _bloco(_principal(client, cenario.pessoa("SIM-P-0001")))
    texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", bloco))
    assert "Para TADS" in texto
    assert f"Aparece porque você concluiu {TADS} (Serra, 2022)." in texto
    assert "Oferecida pela unidade Serra" in texto
    assert "site externo: oportunidades.example" in re.sub(r"<span class=\"visualmente-oculto\">"
                                                           r".*?</span>", "", bloco)
    if variante:
        assert f"compacto-{variante}" in bloco


def test_css_nao_esconde_a_informacao_exigida():
    """Nenhuma regra das folhas do Início e de Oportunidades esconde os elementos exigidos."""
    from pathlib import Path

    pasta = Path(inicio_do_portal.__file__).with_name("templates") / "portal"
    css = (pasta / "inicio.css").read_text("utf-8") + (pasta / "oportunidades.css").read_text(
        "utf-8")
    for regra in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        seletor, corpo = regra
        if re.search(r"oportunidade-(titulo|por-que|origem)|inicio-oportunidades", seletor):
            assert "display: none" not in corpo and "visibility: hidden" not in corpo, seletor
            assert "clip" not in corpo and "height: 0" not in corpo, seletor


def test_variante_adotada_esta_registrada():
    """T046: a variante em uso é a medida e registrada em validacao.md."""
    assert inicio_do_portal.COMPACTACAO_DO_DESTAQUE == 3

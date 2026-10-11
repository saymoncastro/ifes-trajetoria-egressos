"""Fontes do Portal servidas pela aplicação (032 FR-001, FR-002; ADR 0009, revisão de
2026-10-11)."""

import re
from pathlib import Path

import pytest

from tests.portal import construcao as cp
from trajetoria.portal.views import FONTES

pytestmark = pytest.mark.django_db

PASTA = Path(__file__).resolve().parents[2] / "trajetoria/portal/fontes"


def test_cada_fonte_servida_com_tipo_e_cache_longo(client):
    for nome in FONTES:
        resposta = client.get(f"/fontes/{nome}")
        assert resposta.status_code == 200, nome
        assert resposta["Content-Type"] == "font/woff2"
        cache = resposta["Cache-Control"]
        assert "max-age=31536000" in cache and "immutable" in cache
        assert resposta.content[:4] == b"wOF2" and resposta.content == (PASTA / nome).read_bytes()


@pytest.mark.parametrize("nome", ["OFL-bricolage-grotesque.txt", "LEIAME.md", "x.woff2",
                                  "..%2Fviews.py", "atkinson-hyperlegible-regular.ttf"])
def test_fora_da_lista_e_404(client, nome):
    assert client.get(f"/fontes/{nome}").status_code == 404


def test_licencas_junto_dos_arquivos():
    assert {p.name for p in PASTA.glob("*.woff2")} == FONTES
    for licenca in ("OFL-atkinson-hyperlegible.txt", "OFL-bricolage-grotesque.txt"):
        assert "SIL OPEN FONT LICENSE Version 1.1" in (PASTA / licenca).read_text("utf-8")


def test_nenhuma_fonte_externa_no_portal(client, cenario):
    """SC-004: só a própria aplicação; nada de CDN nem de outro domínio."""
    paginas = [client.get("/").content.decode()]
    cp.entrar(client, cenario.pessoa("SIM-P-0004"))
    paginas += [client.get(url).content.decode() for url in ("/inicio/", "/oportunidades/")]
    for html in paginas:
        assert re.findall(r'url\("([^"]+)"\)', html) and all(
            u.startswith("/fontes/") for u in re.findall(r'url\("([^"]+\.woff2)"\)', html))
        assert "fonts.googleapis" not in html and "fonts.gstatic" not in html
        assert "<link" not in html


def test_instrumento_e_acesso_sem_as_fontes(client, cenario):
    """FR-002: o shell da 015 não carrega fonte nenhuma."""
    from tests.interface import construcao_interface as ci

    assert "@font-face" not in client.get("/acesso/").content.decode()
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    secao = client.get(resposta["Location"], follow=True).content.decode()
    assert "/secoes/" in secao and "@font-face" not in secao


@pytest.mark.urls("tests.portal.urls_sem_portal")
def test_sem_o_portal_a_rota_nao_existe(client, settings):
    settings.TRAJETORIA_PORTAL = False
    assert client.get(f"/fontes/{sorted(FONTES)[0]}").status_code == 404

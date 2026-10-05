"""PNG do card: o artefato do story (021 FR-031, FR-032, FR-040; research R11; ADR 0006)."""

import struct
import time

import pytest

from trajetoria.narrativa import rasterizacao

pytestmark = pytest.mark.skipif(
    not rasterizacao.rasterizacao_disponivel(),
    reason="rasterização indisponível neste ambiente (ver ADR 0006)",
)

COM_TEXTO = """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"
 viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#eef7f0"/>
<text x="90" y="400" font-family="Open Sans" font-size="64" font-weight="700"
 fill="#1b1b1b">Minha trajetória no Ifes</text>
<text x="90" y="500" font-family="Open Sans" font-size="40"
 fill="#1b1b1b">Formação · Educação · ção</text></svg>"""
SEM_TEXTO = """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"
 viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#eef7f0"/></svg>"""


def _dimensoes(png: bytes) -> tuple[int, int]:
    assert png[12:16] == b"IHDR"
    return struct.unpack(">II", png[16:24])


def test_png_vertical_9_16():
    png = rasterizacao.png_de(COM_TEXTO)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert _dimensoes(png) == (1080, 1920)


def test_png_reprodutivel():
    assert rasterizacao.png_de(COM_TEXTO) == rasterizacao.png_de(COM_TEXTO)


def test_texto_e_desenhado_com_a_fonte_embutida():
    assert rasterizacao.png_de(COM_TEXTO) != rasterizacao.png_de(SEM_TEXTO)


def test_svg_invalido_nao_derruba(caplog):
    assert rasterizacao.png_de("<svg") is None
    assert "Falha ao rasterizar" in caplog.text


def test_tempo_de_rasterizacao():
    inicio = time.perf_counter()
    rasterizacao.png_de(COM_TEXTO)
    assert time.perf_counter() - inicio < 2  # research R11: espera-se bem menos de 1 s


def test_so_as_fontes_embutidas():
    assert [f.rsplit("/", 1)[-1] for f in rasterizacao.FONTES] == [
        "OpenSans-Regular.ttf", "OpenSans-Bold.ttf",
    ]

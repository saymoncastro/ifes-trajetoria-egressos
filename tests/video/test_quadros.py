"""Quadros do vídeo real (022 US2 e US3; FR-013 a FR-015, FR-017; SC-002, SC-004;
research R14). Tolerância visual, não pixel-perfect: Chromium e resvg só diferem no
antisserrilhado dos glifos."""

import platform
from pathlib import Path

import numpy as np
import pytest

from tests.video import midia
from tests.video.construcao import NOME, NOME_LONGO, composicao, zona
from trajetoria.narrativa import card

pytestmark = pytest.mark.precisa_renderizador

FINAIS = [("maria", NOME), ("ana", None), ("quatro_curtos", None)]


def _ultimo(caso, nome):
    c = composicao(caso, nome)
    fim = midia.duracao(c) - 1
    return midia.quadros(caso, nome)[fim], c


# --- US2: o card em movimento (T016) -----------------------------------------------------


@pytest.mark.parametrize(("caso", "nome"), FINAIS)
def test_ultimo_quadro_e_o_card(caso, nome):
    ultimo, _ = _ultimo(caso, nome)
    referencia = midia.card_png(caso, nome)
    indice = midia.ssim(ultimo, referencia)
    diferentes = midia.fracao_diferente(ultimo, referencia)
    print(f"{caso}: SSIM {indice:.4f}, {diferentes:.2%} dos pixels com diferença > 32")
    assert indice >= 0.98
    assert diferentes <= 0.03


@pytest.mark.parametrize(("caso", "nome"), FINAIS)
def test_quadro_final_estavel_por_um_segundo(caso, nome):
    c = composicao(caso, nome)
    q = midia.quadros(caso, nome)
    fim = midia.duracao(c) - 1
    assert np.abs(q[fim - 30] - q[fim]).max() <= 2


@pytest.mark.parametrize(("caso", "nome"), FINAIS)
def test_rodape_de_demonstracao_em_todos_os_quadros(caso, nome):
    x0, y0, x1, y1 = midia.caixa_dos_textos(caso, nome, {"rodape"})
    q = midia.quadros(caso, nome)
    ultimo = q[max(q)]
    for n, quadro in q.items():
        assert np.abs(quadro[y0:y1, x0:x1] - ultimo[y0:y1, x0:x1]).max() <= 2, n
    assert np.abs(q[0][y0:y1, x0:x1] - 238).max() > 50, "o rodapé tem texto no quadro 0"


@pytest.mark.parametrize(("caso", "nome"), FINAIS)
def test_faixa_inferior_parada(caso, nome):
    q = midia.quadros(caso, nome)
    ultimo = q[max(q)]
    for n, quadro in q.items():
        assert np.abs(quadro[card.BASE + 31:, :] - ultimo[card.BASE + 31:, :]).max() <= 2, n


def test_numeros_estaticos_sem_contagem():
    c = composicao("maria", NOME)
    entrada_terminada = 150 + 8 + 18
    x0, y0, x1, y1 = midia.caixa_dos_textos("maria", NOME, {"numero"})
    q = midia.quadros("maria", NOME)
    ultimo = q[midia.duracao(c) - 1]
    for n, quadro in q.items():
        if n >= entrada_terminada:
            assert np.abs(quadro[y0:y1, x0:x1] - ultimo[y0:y1, x0:x1]).max() <= 2, n


# --- US3: texto em movimento nunca fora da área segura (T022) ----------------------------

CASOS_DE_BORDA = [("diego", None), ("quatro_curtos", None), ("pior", None), ("ana", NOME_LONGO),
                  ("maria", NOME)]


@pytest.mark.parametrize(("caso", "nome"), CASOS_DE_BORDA)
def test_casos_texto_em_movimento_dentro_da_area_segura(caso, nome):
    c = composicao(caso, nome)
    pedidos = tuple(midia.quadros_de_fronteira(c))
    completos = midia.quadros(caso, nome, pedidos=pedidos)
    reduzidos = midia.quadros(caso, nome, reduzida=True, pedidos=pedidos)
    x0, y0, x1, y1 = card.AREA_SEGURA
    rx0, ry0, rx1, ry1 = midia.caixa_dos_textos(caso, nome, {"rodape"})
    for n in pedidos:
        mascara = np.abs(completos[n] - reduzidos[n]) > 32
        fora = mascara.copy()
        fora[y0:y1, x0:x1] = False
        assert not fora.any(), f"texto fora da área segura no quadro {n}"
        assert not mascara[ry0:ry1, rx0:rx1].any(), f"texto sobre o rodapé no quadro {n}"


def test_casos_composicao_reduzida_mantem_a_abertura():
    """A máscara só é válida se a abertura animar igual nos dois renders."""
    c = composicao("maria", NOME)
    pedidos = (10, 30)
    completos = midia.quadros("maria", NOME, pedidos=pedidos)
    reduzidos = midia.quadros("maria", NOME, reduzida=True, pedidos=pedidos)
    topo = card.TOPO
    for n in pedidos:
        assert np.abs(completos[n][:topo] - reduzidos[n][:topo]).max() <= 2
    assert zona(c, "abertura") is not None


# --- Referências aprovadas em ~1 s e ~4 s (T039; SC-008) ----------------------------------

EVIDENCIAS = Path(__file__).resolve().parents[2] / "specs/022-minha-trajetoria-video/evidencias"
REFERENCIAS = [
    ("maria-2-formacoes-agregados-com-nome", "maria", NOME),
    ("diego-3-formacoes-sem-agregados", "diego", None),
    ("4-formacoes", "quatro_curtos", None),
    ("pior-caso-nomes-longos-e-mais-n", "pior", None),
]


def _plataforma_das_referencias() -> str:
    return (EVIDENCIAS / "referencias-plataforma.txt").read_text().strip()


@pytest.mark.parametrize(("arquivo", "caso", "nome"), REFERENCIAS)
@pytest.mark.parametrize("quadro", [30, 120])
def test_quadros_chave_iguais_as_referencias(arquivo, caso, nome, quadro):
    # Chromium no Linux e no macOS rasterizam as fontes de forma diferente: as referências só
    # valem na plataforma em que foram geradas e aprovadas. A comparação com o card (acima) e
    # a máscara de área segura valem em qualquer plataforma.
    aqui = f"{platform.system()}-{platform.machine()}"
    if _plataforma_das_referencias() != aqui:
        pytest.skip(
            f"referências geradas em {_plataforma_das_referencias()}, não em {aqui}: "
            "regenere com evidencias/gerar_referencias.py nesta plataforma (T039)"
        )
    referencia = midia.cinza((EVIDENCIAS / f"referencia-{arquivo}-q{quadro}.png").read_bytes())
    atual = midia.quadros(caso, nome, pedidos=(quadro,))[quadro]
    indice = midia.ssim(atual, referencia)
    print(f"{arquivo} q{quadro}: SSIM {indice:.4f}")
    assert indice >= 0.97

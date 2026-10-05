"""Auxiliares dos testes de mídia da 022 (não são testes): render real em cache, ffprobe e
comparação de quadros com tolerância (research R14). Só usados com `precisa_renderizador`."""

import io
import json
import subprocess
import time
from functools import cache
from pathlib import Path

import numpy as np
from PIL import Image

from tests.video.construcao import CASOS, composicao, zona
from trajetoria.narrativa import card, rasterizacao
from trajetoria.video import renderizador

PROJETO = Path(__file__).resolve().parents[2] / "video"
QUADROS_COMUNS = (0, 21, 30, 39, 51, 120, 150, 168, 189, 207)


def duracao(c: dict) -> int:
    return 240 + (18 if len(zona(c, "nos")["partes"]) == 4 else 0)


def extra(c: dict) -> int:
    return duracao(c) - 240


@cache
def video(caso: str, nome: str | None = None) -> tuple[bytes, float]:
    inicio = time.monotonic()
    dados = renderizador.renderizar(composicao(caso, nome))
    return dados, time.monotonic() - inicio


def video_novo(caso: str, nome: str | None = None) -> bytes:
    return renderizador.renderizar(composicao(caso, nome))


def ffprobe(dados: bytes, tmp_path: Path) -> dict:
    arquivo = tmp_path / "video.mp4"
    arquivo.write_bytes(dados)
    saida = subprocess.run(
        ["npx", "remotion", "ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,pix_fmt,color_space,width,height,r_frame_rate,nb_frames"
         ":format=duration", "-of", "json", str(arquivo)],
        cwd=PROJETO, capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(saida[saida.index("{"):])


def quadros_de_fronteira(c: dict) -> list[int]:
    """Fronteiras das janelas do template (contracts/template-video.md), com `extra`."""
    e = extra(c)
    nos = len(zona(c, "nos")["partes"])
    slots = nos + (1 if zona(c, "mais") else 0)
    passo = (150 + e - 51) / slots
    dos_nos = {round(51 + i * passo + d) for i in range(slots) for d in (0, min(passo, 18))}
    fixos = {21, 39, 51, 150 + e, 168 + e, 189 + e, 207 + e, duracao(c) - 31, duracao(c) - 1}
    return sorted(q for q in fixos | dos_nos if q < duracao(c))


@cache
def quadros(caso: str, nome: str | None = None, reduzida: bool = False,
            pedidos: tuple = ()) -> dict[int, np.ndarray]:
    c = composicao(caso, nome)
    if reduzida:
        # Mesmas zonas e mesma contagem de partes (o tempo e a duração dependem dela), com a
        # marcação das partes de texto vazia: só a abertura, a marca, a legenda e o rodapé.
        c = {**c, "zonas": [
            {**z, "partes": [""] * len(z["partes"])} if z["chave"] in ZONAS_DE_TEXTO else z
            for z in c["zonas"]
        ]}
    numeros = pedidos or tuple(sorted(set(QUADROS_COMUNS) | set(quadros_de_fronteira(c))))
    imagens = renderizador.quadros(c, [str(n) for n in numeros])
    return {n: cinza(imagens[str(n)]) for n in numeros}


ZONAS_DE_TEXTO = {"titulo", "nome", "nos", "mais", "destaques", "apuracao", "fechamento"}


def cinza(png: bytes) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(png)).convert("L"), dtype=np.float64)


def card_png(caso: str, nome: str | None = None) -> np.ndarray:
    return cinza(rasterizacao.png_de(card.card_svg(CASOS[caso](), nome=nome)))


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    """SSIM global por blocos 8 × 8 em tons de cinza (como no spike, research R0)."""
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    h, w = (a.shape[0] // 8) * 8, (a.shape[1] // 8) * 8
    x = a[:h, :w].reshape(h // 8, 8, w // 8, 8)
    y = b[:h, :w].reshape(h // 8, 8, w // 8, 8)
    mx, my = x.mean((1, 3)), y.mean((1, 3))
    vx, vy = x.var((1, 3)), y.var((1, 3))
    cxy = ((x - mx[:, None, :, None]) * (y - my[:, None, :, None])).mean((1, 3))
    return float((((2 * mx * my + c1) * (2 * cxy + c2))
                  / ((mx**2 + my**2 + c1) * (vx + vy + c2))).mean())


def fracao_diferente(a: np.ndarray, b: np.ndarray, limiar: int = 32) -> float:
    return float((np.abs(a - b) > limiar).mean())


def caixa_dos_textos(caso: str, nome: str | None, classes: set[str]) -> tuple[int, int, int, int]:
    """Retângulo (x0, y0, x1, y1) que contém os textos das classes dadas no card."""
    elementos = [
        dict(e.atributos) for e in card.compor(CASOS[caso](), nome, True).elementos
        if e.tag == "text" and dict(e.atributos).get("class") in classes
    ]
    x0 = min(a["x"] for a in elementos) - 6
    x1 = max(a["x"] + card.largura(e_texto, a["font-size"], True)
             for a, e_texto in zip(elementos, _textos(caso, nome, classes), strict=True)) + 6
    # Altura real dos glifos da Open Sans: ascendentes ~0,8 e descendentes ~0,25 do corpo.
    # Sem folga vertical: a linha de apuração fica logo abaixo do rodapé.
    y0 = min(a["y"] - 0.8 * a["font-size"] for a in elementos) - 1
    y1 = max(a["y"] + 0.25 * a["font-size"] for a in elementos) + 1
    return int(x0), int(y0), int(x1) + 1, int(y1) + 1


def _textos(caso, nome, classes):
    return [
        e.texto for e in card.compor(CASOS[caso](), nome, True).elementos
        if e.tag == "text" and dict(e.atributos).get("class") in classes
    ]

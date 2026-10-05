"""Gera os vídeos e quadros de referência da 022 (T038; SC-008).

Script avulso, fora da suíte. Usa o pipeline real: card montado → `composicao_visual` →
renderizador (Remotion). Dados fictícios. Na raiz do repositório, com o renderizador
instalado (`npm ci --prefix video`; `npm --prefix video run garantir-navegador`):

    uv run python specs/022-minha-trajetoria-video/evidencias/gerar_referencias.py

Saídas, nesta pasta:
- `referencia-<caso>.mp4`;
- `referencia-<caso>-q<n>.png` em ~1 s (30), ~4 s (120) e no último quadro;
- `referencia-<caso>-folha.png`: folha de contato com 9 instantes, para revisão rápida.
"""

import io
import os
import platform
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from PIL import Image  # noqa: E402

from tests.video.construcao import NOME, composicao  # noqa: E402
from trajetoria.video import renderizador  # noqa: E402

SAIDA = Path(__file__).resolve().parent
CASOS = (
    ("maria-2-formacoes-agregados-sem-nome", "maria", None),
    ("maria-2-formacoes-agregados-com-nome", "maria", NOME),
    ("ana-1-formacao-agregados", "ana", None),
    ("diego-3-formacoes-sem-agregados", "diego", None),
    ("4-formacoes", "quatro_curtos", None),
    ("pior-caso-nomes-longos-e-mais-n", "pior", None),
    ("unidade-sem-imagem-propria", "sem_imagem", None),
)
QUADROS = ("30", "120", "fim")
FOLHA = ("5", "15", "30", "45", "70", "110", "160", "195", "fim")
PLATAFORMA = SAIDA / "referencias-plataforma.txt"


def plataforma() -> str:
    return f"{platform.system()}-{platform.machine()}"


def main():
    if not renderizador.disponivel():
        sys.exit("Renderizador indisponível: npm ci --prefix video; garantir-navegador.")
    print(f"Plataforma: {plataforma()}")
    # Os quadros de referência só são comparáveis na mesma plataforma: Chromium no Linux e no
    # macOS rasterizam as fontes de forma diferente (tests/video/test_quadros.py).
    PLATAFORMA.write_text(plataforma() + "\n")
    for nome_do_arquivo, caso, nome in CASOS:
        c = composicao(caso, nome)
        (SAIDA / f"referencia-{nome_do_arquivo}.mp4").write_bytes(renderizador.renderizar(c))
        quadros = renderizador.quadros(c, sorted(set(QUADROS) | set(FOLHA)))
        for q in QUADROS:
            (SAIDA / f"referencia-{nome_do_arquivo}-q{q}.png").write_bytes(quadros[q])
        miniaturas = [Image.open(io.BytesIO(quadros[q])).convert("RGB").resize((240, 427))
                      for q in FOLHA]
        folha = Image.new("RGB", (len(miniaturas) * 248 - 8, 427), "white")
        for i, imagem in enumerate(miniaturas):
            folha.paste(imagem, (i * 248, 0))
        folha.save(SAIDA / f"referencia-{nome_do_arquivo}-folha.png")
        print(f"ok: {nome_do_arquivo}")


if __name__ == "__main__":
    main()

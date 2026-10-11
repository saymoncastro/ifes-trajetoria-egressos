"""Medidas e capturas da página pública implementada (029 SC-001 a SC-006).

Pede `/` sem sessão à aplicação de verdade (cliente de teste do Django) e mede com o mesmo
arnês e os mesmos critérios do protótipo (`prototipo/gerar.py`: `medidor`, `avaliar`), com os
seletores da implementação (`publico-*` em vez de `pp-*`).

Uso, na raiz do repositório, com o `.env` da demonstração:

    source .env && uv run python specs/029-pagina-publica-portal/evidencias/medir.py
"""

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
CAPTURAS = PASTA / "capturas"


def prototipo():
    spec = importlib.util.spec_from_file_location(
        "prototipo_029", PASTA.parent / "prototipo/gerar.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    return g


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    g = prototipo()
    temporaria = Path(tempfile.mkdtemp(prefix="029-publica-"))
    (temporaria / "implementada.html").write_text(g.servido(), "utf-8")
    m, moldura = g.medidor()
    m.PASTA = temporaria
    (temporaria / "_moldura.html").write_text(moldura.replace(".pp-", ".publico-"), "utf-8")
    CAPTURAS.mkdir(exist_ok=True)
    v = {}
    for largura in (320, 375, 768, 1024, 1280, 1440):
        for fonte in (100, 200):
            v[f"{largura}@{fonte}"] = m.medir("implementada.html", largura, fonte=fonte)
    for chave, (largura, altura) in {"375x812": (375, 812), "1024x768": (1024, 768),
                                     "1280x720": (1280, 720), "1440x900": (1440, 900)}.items():
        v[chave] = m.medir("implementada.html", largura, altura)
        m.capturar("implementada.html", largura, altura, CAPTURAS / f"implementada-{chave}.png")
    for largura in (375, 1024, 1440):
        m.capturar("implementada.html", largura, v[f"{largura}@100"]["altura_doc"],
                   CAPTURAS / f"implementada-{largura}.png")
    (PASTA / "medidas.json").write_text(json.dumps(v, indent=1, ensure_ascii=False), "utf-8")
    contraste = {nome: round(m.contraste(a, b), 2) for nome, a, b in g.PARES}
    print("falhas:", g.avaliar(v) or "nenhuma")
    print("contraste mínimo:", min(contraste.values()))


if __name__ == "__main__":
    main()

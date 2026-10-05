"""PNG do card a partir do SVG (Feature 021; research R11; ADR 0006).

Único módulo do projeto que importa `resvg_py`. A rasterização usa só as fontes embutidas
(Open Sans Regular e Bold, SIL OFL 1.1) e ignora as do sistema, para que o mesmo SVG dê o
mesmo PNG no mesmo ambiente. Sem a biblioteca, ou com erro de rasterização, devolve `None`:
a página cai para o SVG, que mantém a experiência mas não serve ao story (FR-031).
"""

import logging
from pathlib import Path

logger = logging.getLogger("trajetoria.narrativa")

FONTES = tuple(
    str(Path(__file__).resolve().parent / "fontes" / nome)
    for nome in ("OpenSans-Regular.ttf", "OpenSans-Bold.ttf")
)

try:
    import resvg_py
except ImportError:  # pragma: no cover - depende do ambiente
    resvg_py = None


def rasterizacao_disponivel() -> bool:
    return resvg_py is not None


def png_de(svg: str) -> bytes | None:
    if resvg_py is None:
        return None
    try:
        return bytes(
            resvg_py.svg_to_bytes(
                svg_string=svg, font_files=list(FONTES), skip_system_fonts=True
            )
        )
    except Exception:
        # Sem conteúdo do card no log: só o fato (Princípio XVI).
        logger.warning("Falha ao rasterizar o card da narrativa")
        return None

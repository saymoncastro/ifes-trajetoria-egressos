"""Catálogo de imagens institucionais da abertura (Feature 021; FR-076; research R20).

Em código, sem banco nem upload. Cada entrada registra unidade (ou `None` para a genérica,
obrigatória), arquivo, tipo, origem e licença. Fotografias só entram com origem e licença
registradas (DP-2106). Na demonstração há só a ilustração vetorial própria e genérica: ela
não representa nenhuma unidade real, e a legenda diz "ilustração".
"""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from trajetoria.narrativa import catalogo

PASTA = Path(__file__).resolve().parent / "imagens"
TIPOS = ("ilustração", "fotografia")


@dataclass(frozen=True)
class ImagemInstitucional:
    unidade: str | None
    arquivo: str
    tipo: str
    origem: str
    licenca: str


CATALOGO = (
    ImagemInstitucional(
        unidade=None,
        arquivo="ifes-generica.svg",
        tipo="ilustração",
        origem="Trajetória Ifes",
        licenca="própria",
    ),
)


def imagem_para(unidade: str | None) -> ImagemInstitucional:
    """A entrada da unidade da primeira formação exibida; sem ela, a genérica."""
    proprias = [i for i in CATALOGO if unidade is not None and i.unidade == unidade]
    return proprias[0] if proprias else next(i for i in CATALOGO if i.unidade is None)


def legenda(imagem: ImagemInstitucional, unidade: str | None) -> str:
    """A unidade da legenda é a da formação, nunca um ano (FR-076)."""
    if unidade:
        return catalogo.LEGENDA.format(unidade=unidade, tipo=imagem.tipo)
    return catalogo.LEGENDA_SEM_UNIDADE.format(tipo=imagem.tipo)


@cache
def conteudo(imagem: ImagemInstitucional) -> str:
    """O SVG do arquivo, sem o prólogo XML, para ser embutido no card e na página."""
    texto = (PASTA / imagem.arquivo).read_text(encoding="utf-8")
    return texto[texto.index("<svg"):].strip()

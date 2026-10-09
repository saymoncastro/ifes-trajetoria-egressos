"""Catálogo de imagens institucionais da abertura (Feature 021; FR-076; research R20).

Em código, sem banco nem upload. Cada entrada registra unidade (ou `None` para a genérica,
obrigatória), arquivo, tipo, origem e licença. Fotografias só entram com origem e licença
registradas (DP-2106). Na demonstração há só a ilustração vetorial própria e genérica: ela
não representa nenhuma unidade real, e a legenda diz "ilustração".
"""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from django.utils.safestring import mark_safe

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


def svg_decorativo(imagem: ImagemInstitucional) -> str:
    """A ilustração inline, decorativa (a legenda é o texto; FR-076, FR-083): sem `xmlns`,
    escondida da tecnologia assistiva e sem foco. Usada pela página da 021 e pelo Início da
    024, para que a marcação não divirja."""
    return mark_safe(
        conteudo(imagem)
        .replace(' xmlns="http://www.w3.org/2000/svg"', "", 1)
        .replace(
            "<svg ",
            '<svg aria-hidden="true" focusable="false" class="narrativa-imagem" '
            'preserveAspectRatio="xMidYMax slice" ',
            1,
        )
    )


def legenda(imagem: ImagemInstitucional) -> str:
    """Identifica a imagem efetivamente usada, nunca atribui a genérica a uma unidade."""
    if imagem.unidade:
        return catalogo.LEGENDA.format(unidade=imagem.unidade, tipo=imagem.tipo)
    return catalogo.LEGENDA_SEM_UNIDADE.format(tipo=imagem.tipo)


@cache
def conteudo(imagem: ImagemInstitucional) -> str:
    """O SVG do arquivo, sem o prólogo XML, para ser embutido no card e na página."""
    texto = (PASTA / imagem.arquivo).read_text(encoding="utf-8")
    return texto[texto.index("<svg"):].strip()

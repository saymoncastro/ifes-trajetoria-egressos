"""Card de exemplo da página pública (028; ADR 0009, decisão 6).

Gerado pelo próprio código do card da 021 a partir de formações fictícias, para não divergir
do card real quando ele mudar. Sem nome, sem agregado e sem banco: a página pública não
consulta nenhuma Pessoa (FR-008).
"""

from datetime import date
from functools import cache

from django.utils.safestring import mark_safe

from trajetoria.narrativa import card
from trajetoria.narrativa.contrato import EntradaDaNarrativa, FatoDaFormacao
from trajetoria.narrativa.montagem import montar

FORMACOES_FICTICIAS = (
    FatoDaFormacao(curso="Técnico em Edificações", unidade="Vitória", nivel="Técnico",
                   modalidade="Presencial", ano_conclusao=2014),
    FatoDaFormacao(curso="Bacharelado em Engenharia Civil", unidade="Vitória",
                   nivel="Graduação", modalidade="Presencial", ano_conclusao=2020),
)


@cache
def card_de_exemplo() -> str:
    narrativa = montar(EntradaDaNarrativa(
        nome=None, formacoes=FORMACOES_FICTICIAS, agregados=(),
        referencia=date(2026, 1, 31), demonstracao=True,
    ))
    return mark_safe(card.card_svg(narrativa.compartilhavel, demonstracao=True))

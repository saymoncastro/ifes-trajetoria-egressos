"""Demonstração da página pública (028; 029 FR-009, FR-010; ADR 0009, decisão 6).

Gerada pelo próprio código da 021 (montagem e card) a partir de formações fictícias, para não
divergir do produto quando ele mudar. Sem nome, sem agregado e sem banco: a página pública não
consulta nenhuma Pessoa, Conclusão, Oportunidade ou contato (029 FR-003). As oportunidades e a
contribuição de exemplo são fictícias, fixas no código e sem link para site real.
"""

from dataclasses import dataclass
from datetime import date
from functools import cache

from django.utils.safestring import mark_safe

from trajetoria.narrativa import card
from trajetoria.narrativa.contrato import EntradaDaNarrativa, FatoDaFormacao
from trajetoria.narrativa.montagem import montar
from trajetoria.portal.models import Categoria
from trajetoria.portal.oportunidades import mensagens as m_oportunidades

FORMACOES_FICTICIAS = (
    FatoDaFormacao(curso="Técnico em Edificações", unidade="Vitória", nivel="Técnico",
                   modalidade="Presencial", ano_conclusao=2014),
    FatoDaFormacao(curso="Bacharelado em Engenharia Civil", unidade="Vitória",
                   nivel="Graduação", modalidade="Presencial", ano_conclusao=2020),
)




@dataclass(frozen=True)
class OportunidadeDeExemplo:
    """No formato do item da 025 (`portal/_oportunidade.html`), sem link."""

    categoria: str
    titulo: str
    resumo: str
    explicacao: str
    oferecida: str


@cache
def _narrativa():
    return montar(EntradaDaNarrativa(
        nome=None, formacoes=FORMACOES_FICTICIAS, agregados=(),
        referencia=date(2026, 1, 31), demonstracao=True,
    ))


@cache
def card_de_exemplo() -> str:
    return mark_safe(card.card_svg(_narrativa().compartilhavel, demonstracao=True))


def _explicacao(formacao: FatoDaFormacao) -> str:
    """A explicação de pertinência com os textos da 025."""
    return m_oportunidades.APARECE_PORQUE.format(
        formacoes=formacao.curso + m_oportunidades.NA_UNIDADE.format(unidade=formacao.unidade)
    )


def _oportunidades() -> tuple[OportunidadeDeExemplo, ...]:
    primeira, ultima = FORMACOES_FICTICIAS[0], FORMACOES_FICTICIAS[-1]
    oferecida = m_oportunidades.OFERECIDA_PELA_UNIDADE.format(unidade=ultima.unidade)
    return (
        OportunidadeDeExemplo(
            Categoria.CURSOS.label, "Especialização em Gestão de Obras",
            "Pós-graduação presencial na unidade Vitória, com aulas no período noturno.",
            _explicacao(ultima), oferecida,
        ),
        OportunidadeDeExemplo(
            Categoria.EVENTOS.label, "Encontro de egressos das engenharias e edificações",
            "Tarde de conversa com egressos e professores, no campus.",
            _explicacao(primeira), oferecida,
        ),
    )


@cache
def demonstracao_publica() -> dict:
    """Todas as peças da demonstração contam a mesma história (029 FR-010)."""
    from trajetoria.portal.inicio import formacoes_com_origem  # evita importação circular

    narrativa = _narrativa()
    registro = narrativa.secao("o_que_o_ifes_registra")
    primeira, ultima = FORMACOES_FICTICIAS[0], FORMACOES_FICTICIAS[-1]
    return {
        "sintese": [f.texto for f in registro.frases] if registro else [],
        "formacoes": formacoes_com_origem(narrativa),
        "card": card_de_exemplo(),
        "oportunidades": _oportunidades(),
        "primeira": primeira,
        "ultima": ultima,
        "contribuicao": {
            "forma": "Compartilhar experiência",
            "linha": f"{ultima.curso} · Unidade {ultima.unidade} · enviada em 07/10/2026",
            "situacao": f"A unidade {ultima.unidade} registrou contato em 09/10/2026.",
        },
    }

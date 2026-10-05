"""Gera os PNGs de referência do card editorial (021 T063; SC-015, item 9).

Script avulso, fora da suíte. Usa o pipeline real: `montar` → compartilhável → `card_svg` →
`png_de`. Dados fictícios. Na raiz do repositório:

    uv run python specs/021-minha-trajetoria-narrativa/evidencias/gerar_referencias.py
"""

import os
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from trajetoria.narrativa import card, rasterizacao  # noqa: E402
from trajetoria.narrativa.contrato import (  # noqa: E402
    METRICA_CURSO_UNIDADE_ANO,
    METRICA_UNIDADE_ANO,
    ContextoSelecionado,
    EntradaDaNarrativa,
    FatoDaFormacao,
)
from trajetoria.narrativa.montagem import montar  # noqa: E402

SAIDA = Path(__file__).resolve().parent
REFERENCIA = date(2026, 10, 5)
APURACAO = date(2026, 1, 31)
TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"


def formacao(curso, unidade, nivel, modalidade, ano):
    return FatoDaFormacao(curso=curso, unidade=unidade, nivel=nivel, modalidade=modalidade,
                          ano_conclusao=ano)


def par(unidade, ano, curso, por_curso=27, por_unidade=812):
    return (
        ContextoSelecionado(METRICA_CURSO_UNIDADE_ANO, unidade, ano, por_curso, APURACAO, 0, curso),
        ContextoSelecionado(METRICA_UNIDADE_ANO, unidade, ano, por_unidade, APURACAO, 0),
    )


def entrada(formacoes, nome, agregados=()):
    return EntradaDaNarrativa(nome, tuple(formacoes), tuple(agregados), REFERENCIA, True)


TADS_SERRA = formacao(TADS, "Serra", "Graduação", "Presencial", 2022)
CEFOR = formacao("Especialização em Informática na Educação", "Cefor", "Pós-graduação",
                 "A distância", 2025)
LONGOS = (
    "Especialização em Práticas Pedagógicas para Professores da Educação Profissional",
    TADS,
    "Mestrado Profissional em Educação Profissional e Tecnológica",
    "Especialização em Educação Profissional e Tecnológica Inclusiva",
    "Técnico em Administração",
    "Licenciatura em Letras Português",
    "Doutorado Profissional em Educação",
)
NOME_LONGO = "Maria Aparecida dos Santos Albuquerque de Oliveira Figueiredo"

# caso: (entrada, incluir o nome no card)
CASOS = {
    "ana-1-formacao-agregados": (entrada([TADS_SERRA], "Ana Exemplo", par("Serra", 2022, TADS)),
                                 False),
    "maria-2-formacoes-agregados-com-nome": (
        entrada([TADS_SERRA, CEFOR], "Maria Exemplo", par("Serra", 2022, TADS)), True),
    "maria-2-formacoes-agregados-sem-nome": (
        entrada([TADS_SERRA, CEFOR], "Maria Exemplo", par("Serra", 2022, TADS)), False),
    "diego-3-formacoes-sem-agregados": (entrada([
        formacao("Técnico em Química", "Vila Velha", "Técnico", "Presencial", 2012),
        formacao("Licenciatura em Química", "Vila Velha", "Graduação", "Presencial", 2017),
        formacao("Mestrado Profissional em Química", "Vila Velha", "Pós-graduação",
                 "Presencial", 2020),
    ], "Diego Exemplo"), True),
    "4-formacoes": (entrada([
        formacao("Técnico em Informática", "Serra", "Técnico", "Presencial", 2014),
        TADS_SERRA,
        CEFOR,
        formacao(LONGOS[2], "Vitória", "Pós-graduação", "Presencial", 2026),
    ], None), False),
    "pior-caso-mais-de-4-nomes-longos": (entrada(
        [formacao(curso, "Cachoeiro de Itapemirim", "Pós-graduação", "A distância", 2008 + 2 * i)
         for i, curso in enumerate(LONGOS)],
        NOME_LONGO, par("Cachoeiro de Itapemirim", 2008, LONGOS[0]),
    ), True),
    "unidade-sem-imagem-propria": (entrada(
        [formacao("Engenharia de Controle e Automação", "Linhares", "Graduação", "Presencial",
                  2019)],
        None, par("Linhares", 2019, "Engenharia de Controle e Automação", 41, 530),
    ), False),
}


def main():
    for caso, (e, com_nome) in CASOS.items():
        c = montar(e).compartilhavel
        nome = e.nome if com_nome else None
        composicao = card.compor(c, nome, True)
        png = rasterizacao.png_de(card.card_svg(c, nome=nome))
        if png is None:
            raise SystemExit("Rasterização indisponível.")
        (SAIDA / f"referencia-{caso}.png").write_bytes(png)
        print(f"referencia-{caso}.png: {composicao.exibidas} formação(ões) exibida(s), "
              f"destaques {'sim' if composicao.destaques else 'não'}, "
              f"abertura até y = {composicao.abertura}")


if __name__ == "__main__":
    main()

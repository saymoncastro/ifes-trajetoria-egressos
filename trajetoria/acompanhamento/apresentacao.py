"""Apresentação do acompanhamento da coleta (Feature 011; research R8 a R11; contracts/rotas.md).

Funções puras e textos operacionais: nada consulta o banco. As taxas são derivadas em
memória e nunca gravadas; o arredondamento é apresentação, não regra.

Linguagem: "Participações iniciadas" e "Participações concluídas" — nunca "questionários
integralmente respondidos" (006/DP-601) — e "iniciadas e não concluídas" fora da coleta,
sem "abandono" (005/DP-503). Os recortes agregados não têm supressão nem limiar
(DP-1101 aberta): a exposição produtiva dos recortes finos (curso, ano) DEVE revisitar
DP-1101 antes de ocorrer (010/DP-1001).
"""

import unicodedata
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from trajetoria.campanha.consultas import EstadoCampanha, FormaEncerramento

# --- Textos ------------------------------------------------------------------------------------

BANNER = (
    "Ambiente não produtivo de demonstração: a identificação é simulada por operador "
    "fictício, e os vínculos fictícios não representam designação institucional real. Este "
    "acompanhamento não está disponível para uso produtivo."
)

TEXTO_LISTA = (
    "Números calculados no momento da consulta. Elegíveis atuais é a população elegível "
    "atual, não o número de pessoas: cada formação concluída conta separadamente."
)
LISTA_VAZIA = "Nenhuma Campanha no escopo da sua atuação."
CONTAGEM_POR_FORMACAO = (
    "As contagens são de formações concluídas (Conclusões Acadêmicas), não de pessoas: cada "
    "formação concluída conta separadamente."
)
DEFINICOES = {
    "elegiveis": (
        "Formações concluídas que atendem hoje aos critérios da Campanha (população "
        "elegível atual)."
    ),
    "iniciadas": "Participações existentes nesta Campanha, inclusive as ainda sem respostas.",
    "concluidas": "Participações com conclusão registrada.",
    "nao_concluidas": "Participações iniciadas sem conclusão registrada.",
    "taxa_inicio": "Participações iniciadas ÷ elegíveis atuais.",
    "taxa_conclusao": "Participações concluídas ÷ elegíveis atuais.",
}
NAO_SE_APLICA = "não se aplica"
SEM_ELEGIVEIS = "Taxas não se aplicam: nenhuma formação elegível no momento."
INSTRUMENTO_NAO_PUBLICADO = "Instrumento ainda não publicado"
AVISO_PREPARACAO = "A coleta ainda não começou."
AVISO_COLETA = "Os números correspondem aos dados no momento da consulta."
AVISO_NUNCA_ABERTA = "Esta Campanha não chegou a entrar em coleta."
AVISO_COLETA_ENCERRADA = (
    "A coleta foi encerrada; as Participações não concluídas não podem mais ser concluídas."
)
AVISO_POPULACAO_ATUAL = (
    "A população elegível apresentada corresponde aos dados institucionais atuais e pode "
    "diferir da população existente quando a coleta foi encerrada."
)
SITUACAO_NUNCA_ABERTA = "Período encerrado — Campanha nunca aberta"
RECUSA_TITULO = "Acesso não permitido"
RECUSA_SEM_ATUACAO = (
    "Não há vínculo institucional ativo para este operador. Sem vínculo ativo, o "
    "acompanhamento da coleta não pode ser usado."
)
RECUSA_FORA_DO_ESCOPO = "Esta Campanha não está no escopo de acompanhamento da sua atuação."

_SITUACOES = {
    EstadoCampanha.EM_PREPARACAO: "Em preparação",
    EstadoCampanha.EM_COLETA: "Em coleta",
    EstadoCampanha.ENCERRADA: "Encerrada",
}
_FORMAS = {
    FormaEncerramento.EXPLICITA: "antecipadamente",
    FormaEncerramento.FIM_DO_PERIODO: "ao fim do período",
}

# --- Indicadores -------------------------------------------------------------------------------

_UMA_CASA = Decimal("0.1")


def _taxa(numerador: int, denominador: int) -> Decimal | None:
    """`None` com denominador zero: "não se aplica", nunca 0%. Sem teto (FR-038)."""
    if denominador == 0:
        return None
    return (Decimal(numerador) * 100 / Decimal(denominador)).quantize(_UMA_CASA, ROUND_HALF_UP)


@dataclass(frozen=True)
class Indicadores:
    """Contagens no escopo do operador (spec FR-030 a FR-035). Valor de leitura; nunca gravado."""

    elegiveis: int = 0
    iniciadas: int = 0
    concluidas: int = 0

    @property
    def nao_concluidas(self) -> int:
        return self.iniciadas - self.concluidas

    @property
    def taxa_inicio(self) -> Decimal | None:
        return _taxa(self.iniciadas, self.elegiveis)

    @property
    def taxa_conclusao(self) -> Decimal | None:
        return _taxa(self.concluidas, self.elegiveis)

    def __add__(self, outro: "Indicadores") -> "Indicadores":
        return Indicadores(
            self.elegiveis + outro.elegiveis,
            self.iniciadas + outro.iniciadas,
            self.concluidas + outro.concluidas,
        )


def percentual(taxa: Decimal | None) -> str | None:
    if taxa is None:
        return None
    return f"{taxa:.1f}".replace(".", ",") + "%"


# --- Ordem e rótulos ---------------------------------------------------------------------------


def _dobrado(texto: str) -> str:
    """Só para ordenar: sem caixa e sem diacríticos. Nunca agrupa valores."""
    decomposto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def _ordem_do_valor(valor) -> tuple:
    if valor is None:
        return (1,)
    if isinstance(valor, int):
        return (0, valor)
    return (0, _dobrado(valor), valor)


def chave_de_ordem(chave: tuple) -> tuple:
    """Ordem textual previsível (dobrada, depois exata), ano crescente, "não informado" por
    último em cada posição. Nunca usa indicador (FR-056)."""
    return tuple(_ordem_do_valor(valor) for valor in chave)


def rotulo_nao_concluidas(estado: EstadoCampanha) -> str:
    """Rótulo, não estado (FR-034)."""
    if estado is EstadoCampanha.EM_COLETA:
        return "Em andamento"
    return "Iniciadas e não concluídas"


def situacao(estado: EstadoCampanha) -> str:
    return _SITUACOES[estado]


def forma_de_encerramento(forma: FormaEncerramento) -> str:
    return _FORMAS[forma]


def numeros(indicadores: Indicadores) -> dict:
    """Os números de uma linha, com as taxas já em texto ("—" é decidido no template)."""
    return {
        "elegiveis": indicadores.elegiveis,
        "iniciadas": indicadores.iniciadas,
        "concluidas": indicadores.concluidas,
        "nao_concluidas": indicadores.nao_concluidas,
        "taxa_inicio": percentual(indicadores.taxa_inicio),
        "taxa_conclusao": percentual(indicadores.taxa_conclusao),
    }

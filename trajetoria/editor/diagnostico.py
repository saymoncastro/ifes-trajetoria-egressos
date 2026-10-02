"""Diagnóstico técnico de uma Versão em rascunho (US11; FR-066 a FR-075; research R5;
contracts/diagnostico.md §2).

Compõe, em memória, os resultados de duas capacidades que **já existem**, sem acrescentar
regra:

- **A — Estrutura válida**: `verificar_completude` da 002, as mesmas condições que a
  publicação aplica (002 FR-059);
- **B — Compatível com a jornada atual**: `secoes_nao_suportadas` da 006 (006 FR-016).

Guarda **todos** os problemas concretos — um por violação da 002 e um por Seção da 006 —
com o texto "onde + o que corrigir". A causa original fica em `causa`, para testes e
rastreabilidade, e nunca é exibida. Nada é gravado; não há estado de aprovação: o melhor
resultado é apenas "sem impedimentos técnicos conhecidos".
"""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from trajetoria.editor import mensagens
from trajetoria.editor.apresentacao import (
    Localizacao,
    localizador,
    rotulo_opcao,
    rotulo_secao,
)
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.regras import Motivo, verificar_completude
from trajetoria.participacao.percurso import secoes_nao_suportadas
from trajetoria.participacao.regras import Motivo as MotivoDaJornada


@dataclass(frozen=True)
class Problema:
    origem: str  # "estrutura" (A, 002) ou "jornada" (B, 006)
    causa: Enum  # motivo original; nunca exibido
    elemento_id: UUID
    elemento: Localizacao
    texto: str  # onde + o que corrigir


@dataclass(frozen=True)
class Diagnostico:
    estrutura: tuple[Problema, ...]
    jornada: tuple[Problema, ...]

    @property
    def estrutura_valida(self) -> bool:
        return not self.estrutura

    @property
    def compativel_com_jornada(self) -> bool:
        return not self.jornada

    @property
    def sem_impedimentos_conhecidos(self) -> bool:
        return self.estrutura_valida and self.compativel_com_jornada

    def textos_de(self, *elementos: UUID) -> list[str]:
        """Os problemas dos elementos, para as marcas na estrutura, na Seção e na Pergunta
        (uma Pergunta também mostra os das suas Opções)."""
        ids = set(elementos)
        return [p.texto for p in (*self.estrutura, *self.jornada) if p.elemento_id in ids]


# Só os motivos que `verificar_completude` devolve (mapa local, research R10).
_CORRIGIR = {
    Motivo.SEM_SECOES: mensagens.CORRIGIR_SEM_SECOES,
    Motivo.SECAO_SEM_PERGUNTAS: mensagens.CORRIGIR_SECAO_SEM_PERGUNTAS,
    Motivo.OPCOES_INSUFICIENTES: mensagens.CORRIGIR_OPCOES_INSUFICIENTES,
    Motivo.DESTINO_NAO_POSTERIOR: mensagens.CORRIGIR_DESTINO_NAO_POSTERIOR,
    Motivo.REFERENCIA_OUTRA_VERSAO: mensagens.CORRIGIR_REFERENCIA_OUTRA_VERSAO,
}


_DE_DESTINO = (Motivo.DESTINO_NAO_POSTERIOR, Motivo.REFERENCIA_OUTRA_VERSAO)


def _nomes(conteudo) -> dict[UUID, tuple[str, str]]:
    """Tipo e nome de cada elemento, para o início do texto do problema."""
    nomes = {conteudo.id: ("versao", "A Versão")}
    for i, secao in enumerate(conteudo.secoes, 1):
        nomes[secao.id] = ("secao", rotulo_secao(i, secao))
        for j, pergunta in enumerate(secao.perguntas, 1):
            nomes[pergunta.id] = (
                "pergunta",
                f"A Pergunta «{pergunta.texto}» (Pergunta {j} da Seção {i})",
            )
            for opcao in pergunta.opcoes:
                nomes[opcao.id] = ("opcao", f"O desvio da {rotulo_opcao(i, j, opcao)}")
    return nomes


def _texto(violacao, nomes) -> str:
    tipo, nome = nomes[violacao.elemento]
    if tipo == "secao":
        # Numa Seção, destino não posterior é sempre o do seu encaminhamento.
        nome = f"O encaminhamento da {nome}" if violacao.motivo in _DE_DESTINO else f"A {nome}"
    return _CORRIGIR[violacao.motivo].format(onde=nome)


def diagnosticar(versao, conteudo=None) -> Diagnostico:
    """Pré-condição: Versão em RASCUNHO (para publicada, nenhum diagnóstico é oferecido).
    `conteudo`: o `conteudo_da_versao(versao)` já lido por quem chama, se houver."""
    if conteudo is None:
        conteudo = conteudo_da_versao(versao)
    local = localizador(conteudo)
    nomes = _nomes(conteudo)
    estrutura = tuple(
        Problema("estrutura", v.motivo, v.elemento, local[v.elemento], _texto(v, nomes))
        for v in verificar_completude(versao)
    )
    jornada = tuple(
        Problema(
            "jornada",
            MotivoDaJornada.ESTRUTURA_NAO_SUPORTADA,
            secao.id,
            local[secao.id],
            f"{local[secao.id].rotulo}: {mensagens.INCOMPATIVEL_COM_A_JORNADA}",
        )
        for secao in secoes_nao_suportadas(conteudo)
    )
    return Diagnostico(estrutura, jornada)

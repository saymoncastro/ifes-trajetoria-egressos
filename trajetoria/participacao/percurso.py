"""Derivação do percurso de uma Participação (specs/006, contracts/percurso.md).

**Pureza**: regra de domínio sem I/O. Não acessa o ORM, não executa query, não chama
`conteudo_da_versao` (002) nem `respostas_atuais` (005), não conhece Campanha, Conclusão,
relógio ou outra Participação. Quem chama (`consultas.py`, `operacoes.py`) carrega os dados e
entrega:

- `conteudo`: a árvore imutável da Versão aplicada (`ConteudoVersao`, 002), reutilizada sem
  cópia;
- `respondidas`: `id` da Pergunta → `id` da Opção escolhida (escolha única) ou `None` (demais
  tipos), para cada Pergunta com Resposta atual.

A Seção é a unidade de navegação: toda Pergunta de uma Seção alcançada pertence ao percurso, e
a regra só decide para onde ir ao deixá-la (FR-010, FR-011). Só Perguntas das Seções
alcançadas são lidas, então uma Resposta fora do percurso é inativa por construção (FR-030).
A mesma Versão com as mesmas respostas produz sempre o mesmo resultado, em qualquer data
(FR-017).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from trajetoria.instrumento.conteudo import ConteudoPergunta, ConteudoSecao, ConteudoVersao
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada, Violacao

__all__ = [
    "Passagem",
    "Saida",
    "finalizada",
    "pendencias",
    "percorrer",
    "perguntas_do_percurso",
    "respondidas",
]


class Saida(Enum):
    """Destino que não é uma Seção."""

    FINALIZACAO = "finalizacao"  # o percurso termina ao deixar a Seção
    INDETERMINADA = "indeterminada"  # Pergunta com regra obrigatória ainda sem Resposta


@dataclass(frozen=True)
class Passagem:
    """Uma Seção do percurso determinado. Valor de leitura, nunca gravado."""

    secao: ConteudoSecao
    pendentes: tuple[UUID, ...]  # Perguntas obrigatórias da Seção sem Resposta, na ordem
    destino: UUID | Saida  # `id` da Seção seguinte ou Saida

    @property
    def satisfeita(self) -> bool:
        return not self.pendentes


def percorrer(
    conteudo: ConteudoVersao, respondidas: Mapping[UUID, UUID | None]
) -> tuple[Passagem, ...]:
    """O percurso determinado: da primeira Seção até a finalização ou até a Seção que ainda
    não pode ser deixada (a Seção atual). Nunca inclui Seção além dela (FR-014).

    Versão fora da capacidade desta feature (FR-016) é rejeitada antes de qualquer cálculo."""
    _exigir_suporte(conteudo)
    secoes = conteudo.secoes
    indice = {secao.id: i for i, secao in enumerate(secoes)}
    passagens = []
    i = 0
    while True:
        secao = secoes[i]
        pendentes = tuple(
            p.id for p in secao.perguntas if p.obrigatoria and p.id not in respondidas
        )
        destino = _destino(secoes, i, respondidas)
        passagens.append(Passagem(secao, pendentes, destino))
        if pendentes or isinstance(destino, Saida):
            return tuple(passagens)
        # A Versão aplicada é PUBLICADA: todo destino é posterior e o laço termina (FR-015).
        i = indice[destino]


def _com_regra(secao: ConteudoSecao) -> list[ConteudoPergunta]:
    return [p for p in secao.perguntas if any(o.regra for o in p.opcoes)]


def _exigir_suporte(conteudo: ConteudoVersao) -> None:
    """Seção com mais de uma Pergunta com regra está fora da capacidade de execução desta
    feature (006 FR-016; DP-604): nenhuma precedência entre regras é inventada. Verifica a
    Versão inteira, para que toda Participação da Campanha tenha o mesmo resultado. É
    limitação da execução, não do modelo de instrumento da 002."""
    violacoes = [
        Violacao(
            Motivo.ESTRUTURA_NAO_SUPORTADA,
            "secao",
            f"Seção {secao.id} tem {quantas} Perguntas com regra de navegação",
        )
        for secao in conteudo.secoes
        if (quantas := len(_com_regra(secao))) > 1
    ]
    if violacoes:
        raise ParticipacaoRejeitada(violacoes)


def _destino(secoes, i, respondidas) -> UUID | Saida:
    """Precedência de 006 FR-012 (002 FR-048 a FR-054), e nenhuma outra:

    1. Pergunta com regra respondida, Opção com regra → Seção da regra ou finalização;
    2. Pergunta com regra obrigatória sem Resposta → indeterminado;
    3. encaminhamento da Seção;
    4. Seção seguinte na ordem;
    5. finalização.

    A regra só é lida ao deixar a Seção: as demais Perguntas dela continuam no percurso."""
    secao = secoes[i]
    for pergunta in _com_regra(secao):  # no máximo uma (_exigir_suporte)
        if pergunta.id in respondidas:
            regra = _opcao_respondida(pergunta, respondidas[pergunta.id]).regra
            if regra is not None:
                return Saida.FINALIZACAO if regra.finaliza else regra.destino_secao_id
        elif pergunta.obrigatoria:
            return Saida.INDETERMINADA
    if secao.encaminhamento_id is not None:
        return secao.encaminhamento_id
    return secoes[i + 1].id if i + 1 < len(secoes) else Saida.FINALIZACAO


def _opcao_respondida(pergunta: ConteudoPergunta, opcao_id: UUID | None):
    """A Opção registrada para a Pergunta com regra. Opção ausente ou alheia só existe por
    escrita fora das operações; é rejeitada, com o motivo da 005, em vez de escolher um
    destino."""
    if opcao_id is None:
        motivo, detalhe = Motivo.VALOR_VAZIO, "sem Opção registrada"
    else:
        for opcao in pergunta.opcoes:
            if opcao.id == opcao_id:
                return opcao
        motivo, detalhe = Motivo.OPCAO_DE_OUTRA_PERGUNTA, "a Opção registrada não é desta Pergunta"
    raise ParticipacaoRejeitada(
        (Violacao(motivo, "pergunta", f"Pergunta {pergunta.id}: {detalhe}"),)
    )


def finalizada(passagens: tuple[Passagem, ...]) -> bool:
    """A última passagem está satisfeita e termina em finalização."""
    ultima = passagens[-1]
    return ultima.satisfeita and ultima.destino is Saida.FINALIZACAO


def perguntas_do_percurso(passagens: tuple[Passagem, ...]) -> frozenset[UUID]:
    """Todas as Perguntas das Seções do percurso — as que tornam uma Resposta ativa."""
    return frozenset(p.id for passagem in passagens for p in passagem.secao.perguntas)


def pendencias(passagens: tuple[Passagem, ...]) -> tuple[Violacao, ...]:
    """Uma `OBRIGATORIA_PENDENTE` por Pergunta obrigatória sem Resposta da Seção atual; vazio
    se a jornada está finalizada. Seções anteriores estão satisfeitas por construção, e as
    posteriores ainda não estão determinadas (research R8). Destino indeterminado não tem
    motivo próprio: a Pergunta com regra obrigatória vazia já é uma pendência."""
    if finalizada(passagens):
        return ()
    atual = passagens[-1]
    return tuple(
        Violacao(
            Motivo.OBRIGATORIA_PENDENTE,
            "pergunta",
            f"Pergunta {pergunta_id} obrigatória sem resposta na Seção {atual.secao.id}",
        )
        for pergunta_id in atual.pendentes
    )


def respondidas(respostas: Mapping) -> dict[UUID, UUID | None]:
    """Converte as Respostas atuais carregadas por quem chama (`respostas_atuais`, 005) no
    mapeamento que `percorrer` usa: Pergunta → Opção escolhida (escolha única) ou `None`. Só
    lê o atributo `opcao_id` já carregado; não faz I/O."""
    return {pergunta_id: r.opcao_id for pergunta_id, r in respostas.items()}

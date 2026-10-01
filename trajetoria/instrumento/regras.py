"""Vocabulário de rejeição do instrumento (contracts/operacoes.md, "Rejeição").

Separado de `operacoes.py` para que consumidores e testes importem `Motivo` sem importar
as operações.
"""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from trajetoria.instrumento.models import TipoPergunta, Versao


class Motivo(Enum):
    VERSAO_PUBLICADA = "versao_publicada"  # FR-016, FR-058 o
    REFERENCIA_OUTRA_VERSAO = "referencia_outra_versao"  # FR-058 a, g
    OPCAO_EM_TIPO_SEM_OPCOES = "opcao_em_tipo_sem_opcoes"  # FR-040, FR-058 b
    ESCALA_EM_TIPO_NAO_ESCALA = "escala_em_tipo_nao_escala"  # FR-058 c
    ESCALA_INVALIDA = "escala_invalida"  # FR-038, FR-058 d
    REGRA_EM_TIPO_INCOMPATIVEL = "regra_em_tipo_incompativel"  # FR-050, FR-058 e
    OPCAO_DE_OUTRA_PERGUNTA = "opcao_de_outra_pergunta"  # FR-058 f
    REGRA_JA_DEFINIDA = "regra_ja_definida"  # FR-052, FR-058 h
    POSICAO_OCUPADA = "posicao_ocupada"  # FR-047, FR-058 i
    ORDEM_INCOMPLETA = "ordem_incompleta"  # FR-045, FR-047
    POSICAO_INVALIDA = "posicao_invalida"  # FR-045
    TIPO_NAO_SUPORTADO = "tipo_nao_suportado"  # FR-034, FR-058 j
    TEXTO_VAZIO = "texto_vazio"  # FR-058 k
    DESIGNACAO_REPETIDA = "designacao_repetida"  # FR-006, FR-058 l
    OPCAO_REPETIDA = "opcao_repetida"  # FR-058 m
    COMPLEMENTO_REPETIDO = "complemento_repetido"  # FR-042, FR-058 n
    SECAO_COM_PERGUNTAS = "secao_com_perguntas"  # FR-061
    SECAO_REFERENCIADA = "secao_referenciada"  # FR-061
    SEM_SECOES = "sem_secoes"  # FR-059 a
    SECAO_SEM_PERGUNTAS = "secao_sem_perguntas"  # FR-059 b
    OPCOES_INSUFICIENTES = "opcoes_insuficientes"  # FR-059 c
    DESTINO_NAO_POSTERIOR = "destino_nao_posterior"  # FR-055, FR-059 d


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    elemento: UUID | None
    detalhe: str


class OperacaoRejeitada(Exception):
    """Operação rejeitada; nada foi gravado (FR-060)."""

    def __init__(self, violacoes: tuple[Violacao, ...]):
        if not violacoes:
            raise ValueError("OperacaoRejeitada exige ao menos uma violação")
        self.violacoes = tuple(violacoes)
        super().__init__(str(self))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)

    def __str__(self) -> str:
        return "; ".join(
            f"{v.motivo.name} ({v.elemento or '—'}): {v.detalhe}" if v.detalhe
            else f"{v.motivo.name} ({v.elemento or '—'})"
            for v in self.violacoes
        )


def verificar_completude(versao: Versao) -> tuple[Violacao, ...]:
    """Condições para publicar (FR-059), todas de uma vez e em ordem determinística:
    Seções por posição e, em cada uma, Perguntas e Opções por posição."""
    secoes = list(versao.secoes.order_by("posicao").prefetch_related("perguntas__opcoes"))
    if not secoes:
        return (Violacao(Motivo.SEM_SECOES, versao.id, "a Versão não tem Seções"),)
    posicao_da_secao = {s.id: s.posicao for s in secoes}

    violacoes = []

    def verificar_destino(origem: int, destino_id: UUID, elemento: UUID, de: str) -> None:
        # Destino sempre posterior: todo percurso avança e termina (FR-055, R15). Destino
        # fora da Versão só existe se algo escreveu fora das operações (FR-058 a, g).
        destino = posicao_da_secao.get(destino_id)
        if destino is None:
            violacoes.append(Violacao(Motivo.REFERENCIA_OUTRA_VERSAO, elemento, de))
        elif destino <= origem:
            violacoes.append(Violacao(Motivo.DESTINO_NAO_POSTERIOR, elemento, de))

    for secao in secoes:
        perguntas = sorted(secao.perguntas.all(), key=lambda p: p.posicao)
        if not perguntas:
            violacoes.append(
                Violacao(Motivo.SECAO_SEM_PERGUNTAS, secao.id, f"Seção {secao.posicao}")
            )
        if secao.encaminhamento_id:
            verificar_destino(secao.posicao, secao.encaminhamento_id, secao.id, "encaminhamento")
        for pergunta in perguntas:
            opcoes = sorted(pergunta.opcoes.all(), key=lambda o: o.posicao)
            escolha = pergunta.tipo in (TipoPergunta.ESCOLHA_UNICA, TipoPergunta.ESCOLHA_MULTIPLA)
            if escolha and len(opcoes) < 2:
                violacoes.append(
                    Violacao(Motivo.OPCOES_INSUFICIENTES, pergunta.id, f"{len(opcoes)} Opção(ões)")
                )
            for opcao in opcoes:
                if opcao.regra_destino_id:
                    verificar_destino(
                        secao.posicao, opcao.regra_destino_id, opcao.id, "regra de navegação"
                    )
    return tuple(violacoes)

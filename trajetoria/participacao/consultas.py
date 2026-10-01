"""Consultas de Participação e Resposta (contracts/consultas.md).

Nada aqui grava, calcula progresso, próxima Pergunta, obrigatoriedade ou conclusão, nem
monta modelo de tela (FR-050). Todas valem em qualquer estado da Campanha.

Origem dos dados: os valores das Respostas são declarados; o contexto acadêmico vem de
`participacao.conclusao` (institucional), lido e nunca copiado (FR-044).
"""

from datetime import datetime
from uuid import UUID

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.participacao.models import Participacao, Resposta

__all__ = [
    "admite_escrita",
    "localizar_participacao",
    "participacoes_da_conclusao",
    "respostas_atuais",
]


def localizar_participacao(
    campanha: Campanha, conclusao: ConclusaoAcademica
) -> Participacao | None:
    """A Participação do par, ou `None`. Nunca cria (FR-046)."""
    return Participacao.objects.filter(campanha=campanha, conclusao=conclusao).first()


def participacoes_da_conclusao(conclusao: ConclusaoAcademica) -> tuple[Participacao, ...]:
    """Todas as Participações da Conclusão, em ordem `(iniciada_em, id)`. A ordem é só
    determinística: nenhuma é "a atual" (FR-049)."""
    return tuple(Participacao.objects.filter(conclusao=conclusao).order_by("iniciada_em", "id"))


def admite_escrita(participacao: Participacao, *, agora: datetime | None = None) -> bool:
    """A Campanha está EM_COLETA no momento de referência (004). Não reavalia
    elegibilidade e não reserva nada: a escrita verifica de novo, sob bloqueio (FR-048)."""
    return estado(participacao.campanha, agora=agora) is EstadoCampanha.EM_COLETA


def respostas_atuais(participacao: Participacao) -> dict[UUID, Resposta]:
    """As Respostas atuais, indexadas pelo `id` da Pergunta. Pergunta ausente do dicionário
    = não respondida. O valor está na coluna do tipo (`opcao`, `opcoes`, `texto`,
    `escala`, mais `complemento` em escolha); `opcoes` vem na ordem do instrumento, não na
    de seleção (FR-047)."""
    respostas = (
        Resposta.objects.filter(participacao=participacao)
        .select_related("pergunta", "opcao")
        .prefetch_related("opcoes")
    )
    return {resposta.pergunta_id: resposta for resposta in respostas}

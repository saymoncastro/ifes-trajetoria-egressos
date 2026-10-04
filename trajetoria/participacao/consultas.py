"""Consultas de Participação e Resposta (005 contracts/consultas.md; 006 contracts/consultas.md).

Nada aqui grava, calcula progresso ou monta modelo de tela (005 FR-050; 006 FR-049). Todas
valem em qualquer estado da Campanha: o estado temporal é gate de criação, escrita e
conclusão, nunca de leitura (006 research R18).

A consulta da jornada carrega a Versão aplicada e as Respostas e entrega estruturas em
memória a `percurso.percorrer`, que é puro; o percurso é derivado, nunca gravado.

Origem dos dados: os valores das Respostas são declarados; o contexto acadêmico vem de
`participacao.conclusao` (institucional), lido e nunca copiado (FR-044).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Coalesce

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.instrumento.conteudo import ConteudoSecao, conteudo_da_versao
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.percurso import (
    Passagem,
    finalizada,
    pendencias,
    percorrer,
    perguntas_do_percurso,
    respondidas,
)
from trajetoria.participacao.regras import Violacao, coleta_nao_admitida

__all__ = [
    "SituacaoDaJornada",
    "atributo_efetivo",
    "conflito_pendente",
    "participacoes_oficiais",
    "situacao_analitica",
    "admite_escrita",
    "localizar_participacao",
    "participacoes_da_conclusao",
    "respostas_atuais",
    "situacao_da_jornada",
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
    """Não concluída (relida do banco; 006 FR-040) e Campanha EM_COLETA no momento de
    referência (004). Não reavalia elegibilidade e não reserva nada: a escrita verifica de
    novo, sob bloqueio (FR-048)."""
    gravada = Participacao.objects.select_related("campanha").filter(pk=participacao.pk).first()
    # Participação inexistente não admite escrita: as escritas a rejeitam (005 FR-052 c).
    return gravada is not None and _admite_escrita(gravada, agora)


def _admite_escrita(gravada: Participacao, agora: datetime | None) -> bool:
    """Regra única de "admite escrita". Concluída → falso **sem** consultar o estado da
    Campanha: a leitura de uma observação concluída não depende da data (006 R18)."""
    if gravada.concluida_em is not None:
        return False
    return estado(gravada.campanha, agora=agora) is EstadoCampanha.EM_COLETA


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


# --- Jornada (Feature 006) --------------------------------------------------------------------


@dataclass(frozen=True)
class SituacaoDaJornada:
    """Resposta única às perguntas de 006 FR-047. Valor de leitura, recalculado a cada
    consulta e nunca gravado (006 FR-052)."""

    participacao: Participacao
    concluida_em: datetime | None
    passagens: tuple[Passagem, ...]  # percurso determinado, na ordem
    finalizada: bool
    secao_atual: ConteudoSecao | None  # None ⇔ finalizada
    respostas: dict[UUID, Resposta]  # todas as atuais (005), ativas e inativas
    fora_do_percurso: frozenset[UUID]  # Perguntas com Resposta inativa
    impedimentos: tuple[Violacao, ...]  # o que impediria concluir agora
    admite_escrita: bool

    @property
    def pode_concluir(self) -> bool:
        return self.concluida_em is None and self.finalizada and not self.impedimentos


def situacao_da_jornada(
    participacao: Participacao, *, agora: datetime | None = None
) -> SituacaoDaJornada:
    """Reconstrói a jornada pela Versão histórica da Campanha e pelas Respostas preservadas.

    Para Participação concluída, não consulta o estado da Campanha nem usa `agora`: a mesma
    observação devolve o mesmo resultado em qualquer data (006 research R18). Para rascunho,
    `agora` só informa `admite_escrita` e `COLETA_NAO_ADMITIDA`. Estrutura não suportada é
    `ParticipacaoRejeitada` (006 FR-016).

    Participação e Respostas são lidas como um estado só: a linha da Participação recebe
    `FOR NO KEY UPDATE`, que espera uma conclusão ou escrita em andamento (elas a bloqueiam
    com `FOR UPDATE`) e não impede a inserção de Respostas por chave estrangeira. Sem isso,
    uma conclusão confirmada entre as duas leituras produziria um rascunho já sem as
    respostas inativas, ou uma concluída ainda com elas. Nada é gravado."""
    with transaction.atomic():
        participacao = (
            Participacao.objects.select_for_update(of=("self",), no_key=True)
            .select_related("campanha__versao")
            .get(pk=participacao.pk)
        )
        conteudo = conteudo_da_versao(participacao.campanha.versao)
        respostas = respostas_atuais(participacao)
    passagens = percorrer(conteudo, respondidas(respostas))
    escrita = _admite_escrita(participacao, agora)
    if participacao.concluida_em is not None:
        impedimentos = ()
    else:
        impedimentos = (() if escrita else (coleta_nao_admitida(),)) + pendencias(passagens)
    fim = finalizada(passagens)
    return SituacaoDaJornada(
        participacao=participacao,
        concluida_em=participacao.concluida_em,
        passagens=passagens,
        finalizada=fim,
        secao_atual=None if fim else passagens[-1].secao,
        respostas=respostas,
        fora_do_percurso=frozenset(respostas) - perguntas_do_percurso(passagens),
        impedimentos=impedimentos,
        admite_escrita=escrita,
    )


# 019: definição única das participações oficiais e da conclusão efetiva.
def conflito_pendente():
    return Q(formacao_declarada__validacao__conflito_detectado_na_validacao=True)


def participacoes_oficiais():
    confirmada = Q(
        formacao_declarada__validacao__resultado="CONFIRMADA",
        formacao_declarada__validacao__fora_da_abrangencia_na_validacao=False,
    )
    return Participacao.objects.filter(
        Q(conclusao__isnull=False) | (confirmada & ~conflito_pendente())
    ).annotate(
        conclusao_efetiva_id=Coalesce("conclusao_id", "formacao_declarada__validacao__conclusao_id")
    )


def atributo_efetivo(campo):
    return Coalesce(f"conclusao__{campo}", f"formacao_declarada__validacao__conclusao__{campo}")


def situacao_analitica(participacao):
    if participacao.conclusao_id:
        return "INSTITUCIONAL"
    decisao = getattr(participacao.formacao_declarada, "validacao", None)
    if decisao is None:
        return "DECLARADA_PENDENTE"
    if decisao.resultado == "NAO_CONFIRMADA":
        return "DECLARADA_NAO_CONFIRMADA"
    if decisao.fora_da_abrangencia_na_validacao:
        return "DECLARADA_FORA_DA_ABRANGENCIA"
    if decisao.conflito_detectado_na_validacao:
        return "DECLARADA_EM_CONFLITO"
    return "DECLARADA_VALIDADA"

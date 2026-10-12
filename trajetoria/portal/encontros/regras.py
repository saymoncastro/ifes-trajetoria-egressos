"""Regras puras do Encontro (031, incremento 1; data-model.md; research R4, R5, R7, R10).

Sem banco e sem relógio: o momento chega por parâmetro. Vocabulário de rejeição no padrão de
`oportunidades/regras.py` e `contribuicao/regras.py`.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from django.utils import timezone

from trajetoria.portal.models import (
    COMPLEMENTO_MAXIMO,
    ENCONTRO_DESCRICAO_MAXIMA,
    ENCONTRO_TITULO_MAXIMO,
    NOME_APRESENTACAO_MAXIMO,
    MotivoDeModeracao,
)
from trajetoria.portal.oportunidades.regras import endereco_invalido

ANTECEDENCIA_MINIMA = 2  # dias depois do envio (FR-002; H-3101)
ANTECEDENCIA_MAXIMA = 90
DURACAO_MAXIMA = timedelta(hours=3)
LIMITE_DE_ATIVOS = 3  # por organizador (clarify 3; H-3101)


class Situacao(Enum):
    """Situações do incremento 1 (FR-010, sem as de nova análise)."""

    EM_ANALISE = "em_analise"
    NAO_ANALISADO = "nao_analisado"
    PUBLICADO = "publicado"
    ENCERRADO = "encerrado"
    RECUSADO = "recusado"
    RETIRADO = "retirado"
    CANCELADO = "cancelado"


ATIVAS = frozenset({Situacao.EM_ANALISE, Situacao.PUBLICADO})


class Motivo(Enum):
    TITULO = "titulo"
    DESCRICAO = "descricao"
    NOME = "nome"
    DATA = "data"
    HORARIO = "horario"
    PUBLICO = "publico"
    LINK = "link"
    ORIGEM = "origem"  # a Conclusão não é da Pessoa
    TERMO = "termo"  # versão confirmada não é a vigente
    CIENCIA = "ciencia"
    LIMITE = "limite"  # três encontros ativos (clarify 3)
    MOTIVO = "motivo"
    COMPLEMENTO = "complemento"
    PROPRIO = "proprio"  # organizador confirmando o próprio encontro
    DUPLICADA = "duplicada"
    ESTADO = "estado"  # a situação não admite a ação (conflito)
    FORA_DO_ESCOPO = "fora_do_escopo"  # de outra Pessoa ou fora do escopo da moderação


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None


class EncontroRejeitado(Exception):
    """Operação rejeitada; nada foi gravado."""

    def __init__(self, violacoes):
        violacoes = tuple(violacoes)
        if not violacoes:
            raise ValueError("EncontroRejeitado exige ao menos uma violação")
        self.violacoes = violacoes
        super().__init__("; ".join(f"{v.motivo.name} ({v.campo or '—'})" for v in violacoes))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)


def situacao(encontro, agora: datetime) -> Situacao:
    """Ordem do data-model: cancelamento, retirada e recusa prevalecem; depois o relógio."""
    if encontro.cancelado_em is not None:
        return Situacao.CANCELADO
    if encontro.retirado_em is not None:
        return Situacao.RETIRADO
    if encontro.recusado_em is not None:
        return Situacao.RECUSADO
    if encontro.publicado_em is not None:
        return Situacao.ENCERRADO if agora >= encontro.termino else Situacao.PUBLICADO
    return Situacao.NAO_ANALISADO if agora >= encontro.inicio else Situacao.EM_ANALISE


def ativo(encontro, agora: datetime) -> bool:
    return situacao(encontro, agora) in ATIVAS


def normalizar_texto(valor) -> str:
    """Quebras de linha do navegador (CRLF) contam como uma, como no `maxlength`."""
    if not isinstance(valor, str):
        return ""
    return valor.replace("\r\n", "\n").replace("\r", "\n").strip()


def violacoes_de_texto(titulo: str, descricao: str, nome: str) -> list[Violacao]:
    violacoes = []
    for valor, maximo, motivo, campo in (
        (titulo, ENCONTRO_TITULO_MAXIMO, Motivo.TITULO, "titulo"),
        (descricao, ENCONTRO_DESCRICAO_MAXIMA, Motivo.DESCRICAO, "descricao"),
        (nome, NOME_APRESENTACAO_MAXIMO, Motivo.NOME, "nome"),
    ):
        if not valor or len(valor) > maximo:
            violacoes.append(Violacao(motivo, campo))
    return violacoes


def violacoes_de_horario(inicio: datetime | None, termino: datetime | None,
                         agora: datetime) -> list[Violacao]:
    """Data entre 2 e 90 dias depois do envio; mesmo dia; término depois do início; até 3 h
    (FR-002; research R4). Datas comparadas no fuso do projeto."""
    if inicio is None:
        return [Violacao(Motivo.DATA, "data")]
    violacoes = []
    hoje = timezone.localtime(agora).date()
    dia = timezone.localtime(inicio).date()
    if not (hoje + timedelta(days=ANTECEDENCIA_MINIMA)
            <= dia <= hoje + timedelta(days=ANTECEDENCIA_MAXIMA)):
        violacoes.append(Violacao(Motivo.DATA, "data"))
    if (termino is None or termino <= inicio or termino - inicio > DURACAO_MAXIMA
            or timezone.localtime(termino).date() != dia):
        violacoes.append(Violacao(Motivo.HORARIO, "termino"))
    return violacoes


def link_invalido(link: str) -> bool:
    """A validação mínima da 025 (FR-003; research R7). O endereço não é acessado."""
    return endereco_invalido(link) is not None


def violacoes_de_decisao(motivo, complemento: str) -> list[Violacao]:
    """Motivo da lista fechada; complemento até 300 e obrigatório em "outro" (FR-017)."""
    violacoes = []
    if motivo not in MotivoDeModeracao.values:
        violacoes.append(Violacao(Motivo.MOTIVO, "motivo"))
    if len(complemento) > COMPLEMENTO_MAXIMO or (
        motivo == MotivoDeModeracao.OUTRO and not complemento
    ):
        violacoes.append(Violacao(Motivo.COMPLEMENTO, "complemento"))
    return violacoes


# --- Visibilidade (FR-021, FR-024a; research R10) -------------------------------------------

class Quem(Enum):
    ORGANIZADOR = "organizador"
    MODERACAO = "moderacao"
    CONFIRMADO = "confirmado"  # Pessoa com confirmação ativa
    EGRESSO = "egresso"  # outra Pessoa com Conclusão
    SEM_CONCLUSAO = "sem_conclusao"  # sessão sem Conclusão Acadêmica
    ANONIMO = "anonimo"  # sem sessão de Pessoa


class Nivel(Enum):
    CONTEUDO = "conteudo"  # título, descrição, público, nome e origem
    SITUACAO = "situacao"  # só a situação, sem conteúdo
    INDISPONIVEL = "indisponivel"  # "Este encontro não está disponível"
    NEUTRA = "neutra"  # página sem sessão (FR-022)
    SO_PARA_EGRESSOS = "so_para_egressos"  # sessão sem Conclusão


_COM_CONTEUDO = {
    Situacao.EM_ANALISE: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.NAO_ANALISADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.RECUSADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.PUBLICADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO, Quem.EGRESSO},
    Situacao.RETIRADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.CANCELADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO},
    Situacao.ENCERRADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO},
}
_SO_A_SITUACAO = {Situacao.RETIRADO, Situacao.CANCELADO, Situacao.ENCERRADO}


def o_que_ver(atual: Situacao, quem: Quem) -> Nivel:
    """A tabela do FR-024a (clarify 1). "Confirmado" em cancelado ou encerrado é quem tinha
    confirmação ativa: depois do início ou do cancelamento, ninguém mais a cancela."""
    if quem is Quem.ANONIMO:
        return Nivel.NEUTRA
    if quem is Quem.SEM_CONCLUSAO:
        return Nivel.SO_PARA_EGRESSOS
    if quem in _COM_CONTEUDO[atual]:
        return Nivel.CONTEUDO
    return Nivel.SITUACAO if atual in _SO_A_SITUACAO else Nivel.INDISPONIVEL


def mostra_link(atual: Situacao, quem: Quem) -> bool:
    """O link só sai do servidor para quem confirmou, para o organizador e para a moderação,
    e só enquanto o encontro está publicado (FR-021; SC-002)."""
    return atual is Situacao.PUBLICADO and quem in {
        Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO
    }


def aceita_confirmacao(encontro, agora: datetime) -> bool:
    """Publicado e antes do início (FR-020, FR-023)."""
    return situacao(encontro, agora) is Situacao.PUBLICADO and agora < encontro.inicio

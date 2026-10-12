"""Operações de escrita dos encontros (031, incremento 1; data-model.md, "Transições").

Único caminho de escrita. Cada operação roda numa transação e revalida tudo no momento da
escrita; a linha existente é relida com `select_for_update` (research R8). Nada além do
Encontro e da Confirmação é gravado: nem Pessoa, nem Conclusão, nem contato.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NoReturn

from django.db import IntegrityError, transaction

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.portal.encontros import regras
from trajetoria.portal.encontros.governanca import escopo_da_decisao, modera
from trajetoria.portal.encontros.mensagens import VERSAO_DA_CIENCIA, VERSAO_DO_TERMO
from trajetoria.portal.encontros.regras import (
    EncontroRejeitado,
    Motivo,
    Situacao,
    Violacao,
)
from trajetoria.portal.models import CRITERIOS_DE_PUBLICO, Confirmacao, Encontro

__all__ = [
    "Proposta", "cancelar", "cancelar_participacao", "confirmar", "propor", "publicar",
    "recusar", "retirar",
]


@dataclass(frozen=True)
class Proposta:
    """O que o organizador informa (FR-002). O público usa `None` para critério ausente."""

    titulo: str
    descricao: str
    nome_apresentacao: str
    inicio: datetime | None
    termino: datetime | None
    publico_unidades: list[str] | None
    publico_niveis: list[str] | None
    publico_cursos: list[str] | None
    link: str
    conclusao_origem_id: object


def _rejeitar(motivo: Motivo, campo: str | None = None) -> NoReturn:
    raise EncontroRejeitado((Violacao(motivo, campo),))


def violacoes_da_proposta(proposta: Proposta, agora: datetime) -> list[Violacao]:
    """Tudo o que não depende do banco. Usada também pelo formulário, antes da confirmação."""
    violacoes = regras.violacoes_de_texto(
        proposta.titulo, proposta.descricao, proposta.nome_apresentacao
    )
    violacoes += regras.violacoes_de_horario(proposta.inicio, proposta.termino, agora)
    for campo in CRITERIOS_DE_PUBLICO:
        valores = getattr(proposta, campo)
        if valores is not None and (not valores or "" in valores):
            violacoes.append(Violacao(Motivo.PUBLICO, "publico"))
            break
    if regras.link_invalido(proposta.link):
        violacoes.append(Violacao(Motivo.LINK, "link"))
    return violacoes


@transaction.atomic
def propor(pessoa, proposta: Proposta, *, versao_do_termo: str, agora: datetime,
           id=None) -> Encontro:
    """Cria o Encontro "Em análise" (FR-001 a FR-006). A Conclusão de origem precisa ser da
    Pessoa; o termo confirmado precisa ser o vigente; no máximo três ativos (clarify 3).

    A Pessoa é travada (`select_for_update`) antes de contar os ativos: dois envios ao mesmo
    tempo não passam do limite (research R9). Travar não grava nada no núcleo. `id` fixo só
    serve à carga idempotente da demonstração."""
    Pessoa.objects.select_for_update().filter(pk=pessoa.pk).first()
    violacoes = violacoes_da_proposta(proposta, agora)
    conclusao = ConclusaoAcademica.objects.filter(
        pk=proposta.conclusao_origem_id, pessoa=pessoa
    ).first()
    if conclusao is None:
        violacoes.append(Violacao(Motivo.ORIGEM, "origem"))
    if violacoes:
        raise EncontroRejeitado(violacoes)
    if versao_do_termo != VERSAO_DO_TERMO:
        _rejeitar(Motivo.TERMO)
    ativos = sum(
        regras.ativo(e, agora) for e in Encontro.objects.filter(pessoa_id=pessoa.pk)
    )
    if ativos >= regras.LIMITE_DE_ATIVOS:
        _rejeitar(Motivo.LIMITE)
    return Encontro.objects.create(
        **({"id": id} if id else {}),
        pessoa_id=pessoa.pk,
        conclusao_origem_id=conclusao.pk,
        origem_curso=conclusao.curso or "",
        origem_unidade=conclusao.unidade or "",
        origem_ano=conclusao.ano_conclusao,
        nome_apresentacao=proposta.nome_apresentacao,
        titulo=proposta.titulo,
        descricao=proposta.descricao,
        inicio=proposta.inicio,
        termino=proposta.termino,
        publico_unidades=proposta.publico_unidades,
        publico_niveis=proposta.publico_niveis,
        publico_cursos=proposta.publico_cursos,
        link=proposta.link,
        versao_do_termo=versao_do_termo,
        enviado_em=agora,
    )


def _para_moderar(encontro_id, escopo) -> Encontro:
    encontro = Encontro.objects.select_for_update().filter(pk=encontro_id).first()
    if encontro is None or not modera(escopo, encontro):
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    return encontro


def _operador(operador) -> str:
    if not isinstance(operador, str) or not operador:
        raise TypeError("operador deve ser o identificador opaco do operador")
    return operador


@transaction.atomic
def publicar(encontro_id, *, operador: str, escopo, agora: datetime) -> Encontro:
    """Publicar é o ato de autorização (FR-015). Só "Em análise"; grava quem e por qual
    escopo decidiu (analyze F1)."""
    operador = _operador(operador)
    encontro = _para_moderar(encontro_id, escopo)
    if regras.situacao(encontro, agora) is not Situacao.EM_ANALISE:
        _rejeitar(Motivo.ESTADO)
    encontro.publicado_em, encontro.publicado_por = agora, operador
    encontro.publicado_por_escopo = escopo_da_decisao(escopo, encontro)
    encontro.save(update_fields=["publicado_em", "publicado_por", "publicado_por_escopo"])
    return encontro


def _decisao(motivo, complemento) -> str:
    complemento = regras.normalizar_texto(complemento)
    violacoes = regras.violacoes_de_decisao(motivo, complemento)
    if violacoes:
        raise EncontroRejeitado(violacoes)
    return complemento


@transaction.atomic
def recusar(encontro_id, *, operador: str, escopo, motivo, complemento, agora: datetime
            ) -> Encontro:
    """Recusa definitiva, com motivo (FR-017). Só "Em análise"."""
    operador = _operador(operador)
    complemento = _decisao(motivo, complemento)
    encontro = _para_moderar(encontro_id, escopo)
    if regras.situacao(encontro, agora) is not Situacao.EM_ANALISE:
        _rejeitar(Motivo.ESTADO)
    encontro.recusado_em, encontro.recusado_por = agora, operador
    encontro.motivo, encontro.complemento = motivo, complemento
    encontro.save(update_fields=["recusado_em", "recusado_por", "motivo", "complemento"])
    return encontro


@transaction.atomic
def retirar(encontro_id, *, operador: str, escopo, motivo, complemento, agora: datetime
            ) -> Encontro:
    """Retirada definitiva de um publicado, com motivo (FR-017). O link some na hora."""
    operador = _operador(operador)
    complemento = _decisao(motivo, complemento)
    encontro = _para_moderar(encontro_id, escopo)
    if regras.situacao(encontro, agora) is not Situacao.PUBLICADO:
        _rejeitar(Motivo.ESTADO)
    encontro.retirado_em, encontro.retirado_por = agora, operador
    encontro.motivo, encontro.complemento = motivo, complemento
    encontro.save(update_fields=["retirado_em", "retirado_por", "motivo", "complemento"])
    return encontro


@transaction.atomic
def cancelar(pessoa, encontro_id, *, agora: datetime) -> Encontro:
    """O organizador cancela, até o início, em análise ou publicado (FR-009). Definitivo."""
    encontro = (
        Encontro.objects.select_for_update().filter(pk=encontro_id, pessoa_id=pessoa.pk).first()
    )
    if encontro is None:
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    atual = regras.situacao(encontro, agora)
    if atual not in (Situacao.EM_ANALISE, Situacao.PUBLICADO) or agora >= encontro.inicio:
        _rejeitar(Motivo.ESTADO)
    encontro.cancelado_em = agora
    encontro.save(update_fields=["cancelado_em"])
    return encontro


@transaction.atomic
def confirmar(pessoa, encontro_id, *, versao_da_ciencia: str, agora: datetime,
              id=None) -> Confirmacao:
    """"Vou participar" (FR-020): publicado, antes do início, não pelo organizador, com a
    ciência vigente; uma ativa por pessoa. Quem chama garante que a Pessoa tem Conclusão."""
    encontro = Encontro.objects.select_for_update().filter(pk=encontro_id).first()
    if encontro is None:
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    if encontro.pessoa_id == pessoa.pk:
        _rejeitar(Motivo.PROPRIO)
    if not regras.aceita_confirmacao(encontro, agora):
        _rejeitar(Motivo.ESTADO)
    if versao_da_ciencia != VERSAO_DA_CIENCIA:
        _rejeitar(Motivo.CIENCIA)
    if encontro.confirmacoes.filter(pessoa_id=pessoa.pk, cancelada_em__isnull=True).exists():
        _rejeitar(Motivo.DUPLICADA)
    try:
        with transaction.atomic():  # a corrida de dois envios esbarra na unicidade
            return Confirmacao.objects.create(
                **({"id": id} if id else {}),
                encontro=encontro, pessoa_id=pessoa.pk,
                versao_da_ciencia=versao_da_ciencia, confirmada_em=agora,
            )
    except IntegrityError:
        _rejeitar(Motivo.DUPLICADA)


@transaction.atomic
def cancelar_participacao(pessoa, encontro_id, *, agora: datetime) -> Confirmacao:
    """A própria pessoa, até o início (FR-023). Confirmar de novo cria outra confirmação."""
    encontro = Encontro.objects.select_for_update().filter(pk=encontro_id).first()
    if encontro is None:
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    confirmacao = encontro.confirmacoes.filter(
        pessoa_id=pessoa.pk, cancelada_em__isnull=True
    ).first()
    if confirmacao is None or not regras.aceita_confirmacao(encontro, agora):
        _rejeitar(Motivo.ESTADO)
    confirmacao.cancelada_em = agora
    confirmacao.save(update_fields=["cancelada_em"])
    return confirmacao

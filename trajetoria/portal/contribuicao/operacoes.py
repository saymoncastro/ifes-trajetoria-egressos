"""Operações de escrita da Manifestação (026; plan R2, R5, R6, R11).

Único caminho de escrita: registrar (o egresso), retirar (o egresso) e registrar o contato
feito (o operador do escopo). Cada operação roda numa transação e revalida tudo no momento da
escrita; a linha existente é relida com `select_for_update`. Nada além da Manifestação é
gravado: nem `ContatoDaPessoa` (D-2602), nem Participação, nem a Oportunidade.
"""

from datetime import datetime
from typing import NoReturn

from django.db import IntegrityError, transaction

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.portal.contribuicao.governanca import recebe
from trajetoria.portal.contribuicao.mensagens import VERSAO_DA_CIENCIA
from trajetoria.portal.contribuicao.regras import (
    ManifestacaoRejeitada,
    Motivo,
    Violacao,
    email_da_contribuicao,
    normalizar_mensagem,
    violacoes_da_escolha,
)
from trajetoria.portal.models import Manifestacao

__all__ = ["registrar", "registrar_contato", "retirar"]


def _rejeitar(motivo: Motivo, campo: str | None = None) -> NoReturn:
    raise ManifestacaoRejeitada((Violacao(motivo, campo),))


@transaction.atomic
def registrar(pessoa, *, conclusao_id, forma, mensagem, email, versao_da_ciencia: str,
              agora: datetime, id=None) -> Manifestacao:
    """A Conclusão precisa ser da Pessoa (FR-013a); a versão confirmada precisa ser a vigente
    (FR-007); uma só ativa por forma e formação (FR-006). `id` fixo só serve a cargas
    idempotentes, como as manifestações fictícias da demonstração."""
    mensagem = normalizar_mensagem(mensagem)
    violacoes = violacoes_da_escolha(forma, mensagem)
    conclusao = ConclusaoAcademica.objects.filter(pk=conclusao_id, pessoa=pessoa).first()
    if conclusao is None:
        violacoes.append(Violacao(Motivo.FORMACAO, "formacao"))
    try:
        email = email_da_contribuicao(email)
    except ManifestacaoRejeitada as erro:
        violacoes += erro.violacoes
    if violacoes:
        raise ManifestacaoRejeitada(violacoes)
    if versao_da_ciencia != VERSAO_DA_CIENCIA:
        _rejeitar(Motivo.CIENCIA)
    ativa = Manifestacao.objects.filter(
        pessoa_id=pessoa.pk, conclusao_id=conclusao.pk, forma=forma, retirada_em__isnull=True
    )
    if ativa.exists():
        _rejeitar(Motivo.DUPLICADA, "forma")
    try:
        with transaction.atomic():  # a corrida de dois envios esbarra na unicidade (R6)
            return Manifestacao.objects.create(
                **({"id": id} if id else {}),
                pessoa_id=pessoa.pk, conclusao_id=conclusao.pk, unidade=conclusao.unidade or "",
                forma=forma, mensagem=mensagem, email=email,
                versao_da_ciencia=versao_da_ciencia, registrada_em=agora,
            )
    except IntegrityError:
        _rejeitar(Motivo.DUPLICADA, "forma")


@transaction.atomic
def retirar(pessoa, manifestacao_id, *, agora: datetime) -> Manifestacao:
    """Só a própria Pessoa, a qualquer momento (FR-005). Não é desfeita."""
    manifestacao = (
        Manifestacao.objects.select_for_update()
        .filter(pk=manifestacao_id, pessoa_id=pessoa.pk).first()
    )
    if manifestacao is None:
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    if manifestacao.retirada_em is not None:
        _rejeitar(Motivo.ESTADO)
    manifestacao.retirada_em = agora
    manifestacao.save(update_fields=["retirada_em"])
    return manifestacao


@transaction.atomic
def registrar_contato(manifestacao_id, *, operador: str, escopo, agora: datetime) -> Manifestacao:
    """O marco "contato feito" (D-2601; FR-005a): só no escopo, só ativa, uma única vez."""
    if not isinstance(operador, str) or not operador:
        raise TypeError("operador deve ser o identificador opaco do operador")
    manifestacao = Manifestacao.objects.select_for_update().filter(pk=manifestacao_id).first()
    if manifestacao is None or not recebe(escopo, manifestacao.unidade):
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    if manifestacao.retirada_em is not None or manifestacao.contato_registrado_em is not None:
        _rejeitar(Motivo.ESTADO)
    manifestacao.contato_registrado_em, manifestacao.contato_registrado_por = agora, operador
    manifestacao.save(update_fields=["contato_registrado_em", "contato_registrado_por"])
    return manifestacao

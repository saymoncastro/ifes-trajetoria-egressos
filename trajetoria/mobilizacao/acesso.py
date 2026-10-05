"""Autorização dos Lotes (Feature 020, FR-036/FR-037; research R10).

Cada operação revalida no seu próprio momento: vínculos ativos, capacidade, escopo e
visibilidade da Campanha (011) e do Lote. Nada vem do cliente além dos identificadores.
Interpretação local reversível, **só demonstração** (DP-2001); o envio real continua
bloqueado pelos Gates A e B.
"""

from dataclasses import dataclass
from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect

from trajetoria.acompanhamento.acesso import ESCOLHA_DE_OPERADOR, Atuacao, recusa
from trajetoria.acompanhamento.consultas import campanhas_visiveis
from trajetoria.campanha.models import Campanha
from trajetoria.demonstracao.operador import operador_em_uso, operador_ficticio
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.regras import (
    escopo_de_acompanhamento,
    pode_consultar_lotes,
    pode_consultar_rascunho,
    pode_enviar_lote,
    pode_preparar_lote,
)
from trajetoria.mobilizacao.models import LoteDeMobilizacao


class RecusaDeLote(Exception):
    """Somente categoria fixa e status; nunca dado pessoal nem texto de exceção externa."""

    def __init__(self, categoria="sem_autorizacao", status=403):
        self.categoria = categoria
        self.status = status
        super().__init__(categoria)


@dataclass(frozen=True)
class Contexto:
    operador: str
    escopo: object
    atuacao: Atuacao
    preparar: bool
    enviar: bool


def contexto_do_operador(operador) -> Contexto:
    if not settings.TRAJETORIA_DEMONSTRACAO:
        raise RecusaDeLote("modo_desligado", 404)
    if operador_ficticio(operador) is None:
        raise RecusaDeLote()
    vinculos = vinculos_ativos(operador)
    escopo = escopo_de_acompanhamento(vinculos)
    if not pode_consultar_lotes(vinculos) or escopo is None:
        raise RecusaDeLote()
    return Contexto(
        operador,
        escopo,
        Atuacao(tuple(v.rotulo_de_atuacao for v in vinculos), pode_consultar_rascunho(vinculos)),
        preparar=pode_preparar_lote(vinculos),
        enviar=pode_enviar_lote(vinculos),
    )


def campanha_autorizada(campanha_id, contexto) -> Campanha:
    campanha = campanhas_visiveis(contexto.escopo).filter(pk=campanha_id).first()
    if campanha is None:
        if not Campanha.objects.filter(pk=campanha_id).exists():
            raise RecusaDeLote("inexistente", 404)
        raise RecusaDeLote("fora_do_escopo", 403)
    return campanha


def lote_visivel(lote, escopo) -> bool:
    """Institucional vê todos. CSAEG vê só Lotes cujo filtro de unidades está contido nas
    suas; Lote sem filtro de unidade é institucional (FR-037)."""
    if escopo.institucional:
        return True
    return lote.unidades is not None and set(lote.unidades) <= set(escopo.unidades)


def lotes_visiveis(campanha, escopo):
    lotes = LoteDeMobilizacao.objects.filter(campanha=campanha)
    if escopo.institucional:
        return lotes
    return lotes.filter(unidades__isnull=False, unidades__contained_by=sorted(escopo.unidades))


def lote_autorizado(campanha, lote_id, contexto) -> LoteDeMobilizacao:
    lote = LoteDeMobilizacao.objects.filter(pk=lote_id, campanha=campanha).first()
    if lote is None:
        raise RecusaDeLote("inexistente", 404)
    if not lote_visivel(lote, contexto.escopo):
        raise RecusaDeLote("fora_do_escopo", 403)
    return lote


def lotes(view):
    """Barreira externa das rotas de Lote, relida a cada pedido (marcador `lotes`)."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise Http404
        operador = operador_em_uso(request)
        if operador is None:
            return redirect(ESCOLHA_DE_OPERADOR)
        try:
            contexto = contexto_do_operador(operador)
        except RecusaDeLote:
            return recusa(request, "Lotes de mobilização não estão disponíveis para esta atuação.")
        request.lotes = contexto
        request.atuacao = contexto.atuacao
        return view(request, *args, **kwargs)

    envolvida.lotes = True
    return envolvida

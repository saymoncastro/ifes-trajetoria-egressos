"""Operações de escrita da Oportunidade (025; data-model.md, "Operações"; research R5).

Único caminho de escrita. Cada operação roda numa transação, relê a linha com
`select_for_update` e revalida estado e escopo no momento da escrita: um estado que mudou
entre a exibição e a confirmação vira `Motivo.ESTADO`, que a view mostra como conflito
(FR-034). Nada além da Oportunidade é gravado (FR-037).
"""

import hashlib
from datetime import date, datetime
from typing import NoReturn

from django.db import transaction
from django.utils import timezone

from trajetoria.portal.models import (
    CRITERIOS_DE_PUBLICO,
    RESUMO_MAXIMO,
    TITULO_MAXIMO,
    Categoria,
    Oportunidade,
)
from trajetoria.portal.oportunidades.governanca import administra
from trajetoria.portal.oportunidades.regras import (
    EDITAVEIS,
    RETIRAVEIS,
    Estado,
    Motivo,
    OportunidadeRejeitada,
    Violacao,
    endereco_invalido,
    estado,
)

__all__ = ["assinatura", "cadastrar", "editar", "publicar", "retirar"]

CAMPOS_DE_CONTEUDO = (
    "titulo", "resumo", "categoria", "unidade_responsavel", "endereco", "inicio", "fim",
    *CRITERIOS_DE_PUBLICO,
)


def assinatura(oportunidade) -> str:
    """Resumo do conteúdo e dos momentos gravados. A edição o leva do formulário à gravação:
    se outro operador mudou a oportunidade nesse meio-tempo, a gravação vira conflito, em
    vez de desfazer em silêncio a mudança dele (FR-034; code review do PR #49)."""
    campos = (*CAMPOS_DE_CONTEUDO, "publicada_em", "retirada_em")
    texto = repr(tuple(getattr(oportunidade, campo) for campo in campos))
    return hashlib.sha256(texto.encode()).hexdigest()


def _rejeitar(motivo: Motivo, campo: str | None = None, detalhe: str = "") -> NoReturn:
    raise OportunidadeRejeitada((Violacao(motivo, campo, detalhe),))


def _exigir_operador(operador: str) -> None:
    if not isinstance(operador, str) or not operador:
        raise TypeError("operador deve ser o identificador opaco do operador")


def _publico(valores) -> list[str] | None:
    """Lista vazia ou ausente = critério ausente (`NULL`); nunca `[]` (FR-007)."""
    if not valores:
        return None
    return list(dict.fromkeys(valores))


def _conteudo(dados: dict, escopo, *, publicada: bool, hoje: date) -> dict:
    """Valida e normaliza o conteúdo (FR-002 a FR-007, FR-026, FR-029). Junta todas as
    violações para a tela mostrar cada erro no seu campo."""
    violacoes = []
    titulo = (dados.get("titulo") or "").strip()
    resumo = (dados.get("resumo") or "").strip()
    if not 1 <= len(titulo) <= TITULO_MAXIMO:
        violacoes.append(Violacao(Motivo.TITULO, "titulo", "1 a 120 caracteres"))
    if not 1 <= len(resumo) <= RESUMO_MAXIMO:
        violacoes.append(Violacao(Motivo.RESUMO, "resumo", "1 a 300 caracteres"))
    if dados.get("categoria") not in Categoria.values:
        violacoes.append(Violacao(Motivo.CATEGORIA, "categoria", "fora da lista"))
    unidade = dados.get("unidade_responsavel") or ""
    if not administra(escopo, unidade):
        violacoes.append(
            Violacao(Motivo.UNIDADE_FORA_DO_ESCOPO, "unidade_responsavel", "fora do escopo")
        )
    endereco = (dados.get("endereco") or "").strip()
    if endereco_invalido(endereco):
        violacoes.append(Violacao(Motivo.ENDERECO, "endereco", "forma recusada"))
    inicio, fim = dados.get("inicio"), dados.get("fim")
    if not isinstance(inicio, date) or not isinstance(fim, date) or inicio > fim:
        violacoes.append(Violacao(Motivo.PERIODO_INVERTIDO, "fim", "início depois do fim"))
    elif publicada and fim < hoje:
        violacoes.append(Violacao(Motivo.FIM_ANTES_DE_HOJE, "fim", "fim antes de hoje"))
    publico = {campo: _publico(dados.get(campo)) for campo in CRITERIOS_DE_PUBLICO}
    for campo, valores in publico.items():
        if valores and any(not isinstance(v, str) or not v for v in valores):
            violacoes.append(Violacao(Motivo.PUBLICO, campo, "valor vazio"))
    if violacoes:
        raise OportunidadeRejeitada(violacoes)
    return {
        "titulo": titulo, "resumo": resumo, "categoria": dados["categoria"],
        "unidade_responsavel": unidade, "endereco": endereco, "inicio": inicio, "fim": fim,
        **publico,
    }


def _bloquear(oportunidade_id, escopo) -> Oportunidade:
    oportunidade = Oportunidade.objects.select_for_update().filter(pk=oportunidade_id).first()
    if oportunidade is None or not administra(escopo, oportunidade.unidade_responsavel):
        _rejeitar(Motivo.FORA_DO_ESCOPO)
    return oportunidade


@transaction.atomic
def cadastrar(dados: dict, *, operador: str, escopo, hoje: date, id=None) -> Oportunidade:
    """Cria em Rascunho (FR-028). O operador não é gravado no cadastro (FR-033). `id` fixo
    só serve a cargas idempotentes, como o catálogo da demonstração (research R4)."""
    _exigir_operador(operador)
    conteudo = _conteudo(dados, escopo, publicada=False, hoje=hoje)
    return Oportunidade.objects.create(**({"id": id} if id else {}), **conteudo)


@transaction.atomic
def editar(oportunidade_id, dados: dict, *, operador: str, escopo, hoje: date,
           versao: str | None = None) -> Oportunidade:
    """Rascunho, Agendada ou Em divulgação (FR-029). Publicada continua publicada; o fim
    nunca fica antes de hoje (encerrar antes do prazo é retirar). Com `versao`, recusa se o
    conteúdo mudou desde a leitura (conflito)."""
    _exigir_operador(operador)
    oportunidade = _bloquear(oportunidade_id, escopo)
    if estado(oportunidade, hoje) not in EDITAVEIS:
        _rejeitar(Motivo.ESTADO)
    if versao is not None and versao != assinatura(oportunidade):
        _rejeitar(Motivo.ESTADO, None, "conteúdo alterado por outro operador")
    publicada = oportunidade.publicada_em is not None
    for campo, valor in _conteudo(dados, escopo, publicada=publicada, hoje=hoje).items():
        setattr(oportunidade, campo, valor)
    oportunidade.save(update_fields=list(CAMPOS_DE_CONTEUDO))
    return oportunidade


@transaction.atomic
def publicar(oportunidade_id, *, operador: str, escopo, agora: datetime) -> Oportunidade:
    """Único ato que autoriza a divulgação (FR-030). Só a partir de Rascunho."""
    _exigir_operador(operador)
    oportunidade = _bloquear(oportunidade_id, escopo)
    hoje = timezone.localdate(agora)
    if estado(oportunidade, hoje) is not Estado.RASCUNHO:
        _rejeitar(Motivo.ESTADO)
    if oportunidade.fim < hoje:
        _rejeitar(Motivo.FIM_ANTES_DE_HOJE, "fim", "fim já passou")
    oportunidade.publicada_em, oportunidade.publicada_por = agora, operador
    oportunidade.save(update_fields=["publicada_em", "publicada_por"])
    return oportunidade


@transaction.atomic
def retirar(oportunidade_id, *, operador: str, escopo, agora: datetime) -> Oportunidade:
    """Definitiva e imediata (FR-031). Rascunho retirado é descarte."""
    _exigir_operador(operador)
    oportunidade = _bloquear(oportunidade_id, escopo)
    if estado(oportunidade, timezone.localdate(agora)) not in RETIRAVEIS:
        _rejeitar(Motivo.ESTADO)
    oportunidade.retirada_em, oportunidade.retirada_por = agora, operador
    oportunidade.save(update_fields=["retirada_em", "retirada_por"])
    return oportunidade

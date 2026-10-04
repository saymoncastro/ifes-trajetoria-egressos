"""Operações de escrita de Campanha (contracts/operacoes.md).

Único caminho de escrita suportado (research R10). Toda operação roda numa transação e
bloqueia a linha da Campanha antes de verificar. A imutabilidade é controlada só pela
primeira abertura (`aberta_em`), nunca pelo estado temporal: Campanha nunca aberta é
editável e removível mesmo com período expirado (FR-043, FR-044).

Argumento de tipo errado é erro de programação: levanta `TypeError` antes de qualquer
verificação de domínio. Valor inválido para o domínio levanta `CampanhaRejeitada`.

As operações gravam numa cópia relida sob bloqueio e copiam os campos gravados para a
instância recebida, que é devolvida: quem segue usando a Campanha vê o estado gravado.
"""

from collections.abc import Iterable
from datetime import date, datetime
from enum import Enum
from typing import NoReturn

from django.db import transaction

from trajetoria.campanha.consultas import (
    EstadoCampanha,
    estado,
    impedimentos_de_abertura,
    momento_de_referencia,
)
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.regras import CampanhaRejeitada, Motivo, Violacao
from trajetoria.instrumento.models import Versao

__all__ = [
    "SituacaoAbertura",
    "SituacaoEncerramento",
    "abrir",
    "alterar_campanha",
    "criar_campanha",
    "definir_criterios",
    "definir_periodo",
    "encerrar",
    "remover_campanha",
    "violacoes_de_periodo",
]

_ANO_MAXIMO = 32767  # limite de PositiveSmallIntegerField

# Sentinela de "não informado" em `alterar_campanha`.
_MANTER = object()


def _rejeitar(motivo: Motivo, campo: str | None, detalhe: str) -> NoReturn:
    raise CampanhaRejeitada((Violacao(motivo, campo, detalhe),))


def _bloquear(campanha: Campanha) -> Campanha:
    return Campanha.objects.select_for_update().get(pk=campanha.pk)


def _sincronizar(recebida: Campanha, gravada: Campanha, campos) -> Campanha:
    for campo in campos:
        setattr(recebida, campo, getattr(gravada, campo))
    return recebida


def _bloquear_nunca_aberta(campanha: Campanha) -> Campanha:
    """Bloqueia e exige que a Campanha nunca tenha sido aberta. Não consulta o estado nem o
    relógio: a fronteira histórica é a primeira abertura (FR-043)."""
    campanha = _bloquear(campanha)
    if campanha.aberta_em is not None:
        _rejeitar(Motivo.CAMPANHA_JA_ABERTA, None, "Campanha já aberta não pode ser alterada")
    return campanha


def _exigir_str(valor) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"nome deve ser str, não {type(valor).__name__}")
    return valor


def _nome(valor) -> str:
    # Gravado como recebido, sem strip().
    if not _exigir_str(valor).strip():
        _rejeitar(Motivo.NOME_VAZIO, "nome", "nome vazio")
    return valor


def _data(valor, nome: str) -> date | None:
    # datetime é subclasse de date e não é data civil.
    if valor is not None and (not isinstance(valor, date) or isinstance(valor, datetime)):
        raise TypeError(f"{nome} deve ser date ou None, não {type(valor).__name__}")
    return valor


def _versao(valor) -> Versao:
    if not isinstance(valor, Versao):
        raise TypeError(f"versao deve ser Versao, não {type(valor).__name__}")
    return valor


# --- Preparação -----------------------------------------------------------------------


def criar_campanha(nome: str, versao: Versao) -> Campanha:
    """Nasce EM_PREPARACAO, sem período e sem critérios (população ampla). A Versão pode
    estar em qualquer estado e não é alterada (FR-006, FR-007)."""
    nome, versao = _nome(nome), _versao(versao)
    return Campanha.objects.create(nome=nome, versao=versao)


def alterar_campanha(campanha: Campanha, *, nome=_MANTER, versao=_MANTER) -> Campanha:
    # Tipos antes do bloqueio, como em definir_*; o domínio depois.
    if nome is not _MANTER:
        _exigir_str(nome)
    if versao is not _MANTER:
        _versao(versao)
    with transaction.atomic():
        gravada = _bloquear_nunca_aberta(campanha)
        campos = []
        if nome is not _MANTER:
            gravada.nome = _nome(nome)
            campos.append("nome")
        if versao is not _MANTER:
            gravada.versao = versao
            campos.append("versao")
        gravada.save(update_fields=campos)
    return _sincronizar(campanha, gravada, campos)


def violacoes_de_periodo(inicio: date | None, fim: date | None) -> tuple[Violacao, ...]:
    """Regra única de período válido (FR-012), pura e sem gravar. `definir_periodo` a aplica
    sob bloqueio; a gestão da 017 a consulta quando ainda não há Campanha a quem aplicá-la."""
    inicio, fim = _data(inicio, "inicio"), _data(fim, "fim")
    if inicio is None or fim is None:
        ausente = "inicio" if inicio is None else "fim"
        return (Violacao(Motivo.PERIODO_INCOMPLETO, ausente, "o período exige as duas datas"),)
    if inicio > fim:
        return (Violacao(Motivo.PERIODO_INVERTIDO, "inicio", f"{inicio} é posterior a {fim}"),)
    return ()


def definir_periodo(campanha: Campanha, inicio: date | None, fim: date | None) -> Campanha:
    """Datas civis, ambas incluídas; sem período padrão (FR-011–FR-014). Pode corrigir o
    período de Campanha nunca aberta e expirada: isso não é reabertura (FR-039)."""
    inicio, fim = _data(inicio, "inicio"), _data(fim, "fim")
    with transaction.atomic():
        gravada = _bloquear_nunca_aberta(campanha)
        if violacoes := violacoes_de_periodo(inicio, fim):
            raise CampanhaRejeitada(violacoes)
        gravada.inicio, gravada.fim = inicio, fim
        gravada.save(update_fields=["inicio", "fim"])
    return _sincronizar(campanha, gravada, ["inicio", "fim"])


def _ano(valor, campo: str, violacoes: list[Violacao]) -> int | None:
    # bool é subclasse de int e não é ano.
    if valor is None:
        return None
    if type(valor) is not int or not 0 < valor <= _ANO_MAXIMO:
        violacoes.append(Violacao(Motivo.ANO_INVALIDO, campo, f"ano {valor!r}"))
        return None
    return valor


def _conjunto(valor, campo: str, violacoes: list[Violacao]) -> list[str] | None:
    """`None` = critério não definido. Coleção vazia é inválida, nunca equivalente a `None`.
    Os textos ficam intactos, sem duplicatas e em ordem estável (research R11)."""
    if valor is None:
        return None
    if isinstance(valor, str) or not isinstance(valor, Iterable):
        raise TypeError(f"{campo} deve ser uma coleção de str, não {type(valor).__name__}")
    valores = list(valor)
    if not all(isinstance(v, str) for v in valores):
        raise TypeError(f"{campo} deve conter apenas str")
    if not valores:
        violacoes.append(Violacao(Motivo.CONJUNTO_VAZIO, campo, "conjunto sem valores"))
        return None
    if any(not v.strip() for v in valores):
        violacoes.append(Violacao(Motivo.VALOR_VAZIO, campo, "valor vazio no conjunto"))
        return None
    return sorted(set(valores))


def definir_criterios(
    campanha: Campanha,
    *,
    ano_minimo=None,
    ano_maximo=None,
    unidades=None,
    niveis=None,
    modalidades=None,
    formas_oferta=None,
) -> Campanha:
    """Substitui a definição inteira de critérios; `None` = critério não definido. Sem
    argumentos, a população volta a ser ampla. Rejeita com todas as violações (FR-023)."""
    violacoes: list[Violacao] = []
    criterios = {
        "ano_minimo": _ano(ano_minimo, "ano_minimo", violacoes),
        "ano_maximo": _ano(ano_maximo, "ano_maximo", violacoes),
        "unidades": _conjunto(unidades, "unidades", violacoes),
        "niveis": _conjunto(niveis, "niveis", violacoes),
        "modalidades": _conjunto(modalidades, "modalidades", violacoes),
        "formas_oferta": _conjunto(formas_oferta, "formas_oferta", violacoes),
    }
    minimo, maximo = criterios["ano_minimo"], criterios["ano_maximo"]
    if minimo is not None and maximo is not None and minimo > maximo:
        violacoes.append(
            Violacao(Motivo.ANOS_INVERTIDOS, "ano_minimo", f"{minimo} é maior que {maximo}")
        )
    with transaction.atomic():
        gravada = _bloquear_nunca_aberta(campanha)
        if violacoes:
            raise CampanhaRejeitada(violacoes)
        for campo, valor in criterios.items():
            setattr(gravada, campo, valor)
        gravada.save(update_fields=list(criterios))
    return _sincronizar(campanha, gravada, criterios)


def remover_campanha(campanha: Campanha) -> None:
    with transaction.atomic():
        _bloquear_nunca_aberta(campanha).delete()


# --- Ciclo de vida --------------------------------------------------------------------


class SituacaoAbertura(Enum):
    ABERTA = "aberta"  # transição feita agora; aberta_em registrado
    JA_EM_COLETA = "ja_em_coleta"  # já aberta; nada mudou (FR-037)
    JA_ENCERRADA = "ja_encerrada"  # aberta e já encerrada; nada mudou (FR-037)


def abrir(campanha: Campanha, *, agora: datetime | None = None) -> SituacaoAbertura:
    """Inicia a coleta e fixa a Campanha. Exige Versão PUBLICADA, período definido e data de
    referência dentro do período; rejeita com todas as condições não satisfeitas (FR-036).
    Nunca publica a Versão (FR-009) e nunca agenda nada (FR-042)."""
    agora = momento_de_referencia(agora)
    recebida = campanha
    with transaction.atomic():
        campanha = _bloquear(campanha)
        if campanha.aberta_em is not None:
            _sincronizar(recebida, campanha, ["aberta_em", "encerrada_em"])
            if estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA:
                return SituacaoAbertura.JA_ENCERRADA
            return SituacaoAbertura.JA_EM_COLETA
        violacoes = impedimentos_de_abertura(campanha, agora=agora)
        if violacoes:
            raise CampanhaRejeitada(violacoes)
        campanha.aberta_em = agora
        campanha.save(update_fields=["aberta_em"])
    _sincronizar(recebida, campanha, ["aberta_em"])
    return SituacaoAbertura.ABERTA


class SituacaoEncerramento(Enum):
    ENCERRADA = "encerrada"  # encerramento explícito feito agora; encerrada_em registrado
    JA_ENCERRADA = "ja_encerrada"  # aberta e já encerrada; nada mudou (FR-040)


def encerrar(campanha: Campanha, *, agora: datetime | None = None) -> SituacaoEncerramento:
    """Encerramento antecipado explícito, só para Campanha aberta. Campanha nunca aberta é
    rejeitada sem gravar nada, mesmo se já ENCERRADA pelo tempo (FR-040)."""
    agora = momento_de_referencia(agora)
    recebida = campanha
    with transaction.atomic():
        campanha = _bloquear(campanha)
        if campanha.aberta_em is None:
            _rejeitar(Motivo.CAMPANHA_NUNCA_ABERTA, None, "Campanha nunca aberta")
        if agora < campanha.aberta_em:
            _rejeitar(
                Motivo.ANTES_DA_ABERTURA,
                None,
                f"encerramento em {agora} anterior à abertura em {campanha.aberta_em}",
            )
        _sincronizar(recebida, campanha, ["aberta_em", "encerrada_em"])
        # encerrada_em é gravado uma única vez, mesmo consultado com `agora` anterior a ele.
        if (
            campanha.encerrada_em is not None
            or estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA
        ):
            return SituacaoEncerramento.JA_ENCERRADA
        campanha.encerrada_em = agora
        campanha.save(update_fields=["encerrada_em"])
    _sincronizar(recebida, campanha, ["encerrada_em"])
    return SituacaoEncerramento.ENCERRADA

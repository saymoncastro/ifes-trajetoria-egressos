"""Seleção do Lote, comum à prévia e à confirmação (Feature 020, FR-017; research R5).

Ordem obrigatória:

1. Conclusões na abrangência da Campanha — só `populacao_no_momento` (004); nenhuma regra
   de elegibilidade é reimplementada aqui;
2. escopo do operador (unidade da Conclusão; CSAEG nunca seleciona por outra unidade);
3. filtros do Lote, sobre a Conclusão;
4. Pessoas distintas pela identidade interna — nunca por nome ou e-mail;
5. exclusão das Pessoas já abordadas nesta Campanha (FR-024);
6. contato pela política determinística (FR-008).

Nada aqui grava. Filtros só existem no Lote, nunca na Campanha (017 FR-024; ADR 0004).
"""

from dataclasses import dataclass

from django.db.models import Q

from trajetoria.campanha.consultas import populacao_no_momento
from trajetoria.contato.politica import contato_utilizavel
from trajetoria.mobilizacao.models import MembroDoLote, SituacaoDoMembro


class FiltrosInvalidos(ValueError):
    """Categoria fixa; nunca carrega valor recebido."""

    def __init__(self):
        super().__init__("filtros_invalidos")


def _texto(valor):
    if valor is None:
        return None
    if not isinstance(valor, str) or any(c in valor for c in "\r\n\x00"):
        raise FiltrosInvalidos
    valor = valor.strip()
    return valor or None


def _ano(valor):
    if valor in (None, ""):
        return None
    try:
        ano = int(valor)
    except (TypeError, ValueError):
        raise FiltrosInvalidos from None
    if not 1900 <= ano <= 2999:
        raise FiltrosInvalidos
    return ano


@dataclass(frozen=True)
class Filtros:
    """Todos opcionais. `unidades` vazio equivale a sem filtro (`None`)."""

    unidades: tuple[str, ...] | None = None
    nivel: str | None = None
    ano_minimo: int | None = None
    ano_maximo: int | None = None
    curso: str | None = None

    @classmethod
    def de(cls, *, unidades=(), nivel=None, ano_minimo=None, ano_maximo=None, curso=None):
        limpas = tuple(sorted({u for u in (_texto(u) for u in unidades or ()) if u}))
        filtros = cls(
            unidades=limpas or None,
            nivel=_texto(nivel),
            ano_minimo=_ano(ano_minimo),
            ano_maximo=_ano(ano_maximo),
            curso=_texto(curso),
        )
        if (
            filtros.ano_minimo is not None
            and filtros.ano_maximo is not None
            and filtros.ano_minimo > filtros.ano_maximo
        ):
            raise FiltrosInvalidos
        return filtros

    @property
    def vazio(self) -> bool:
        return all(getattr(self, c) is None for c in self.__dataclass_fields__)

    def condicao(self) -> Q:
        condicao = Q()
        if self.unidades is not None:
            condicao &= Q(unidade__in=self.unidades)
        if self.nivel is not None:
            condicao &= Q(nivel=self.nivel)
        if self.ano_minimo is not None:
            condicao &= Q(ano_conclusao__gte=self.ano_minimo)
        if self.ano_maximo is not None:
            condicao &= Q(ano_conclusao__lte=self.ano_maximo)
        if self.curso is not None:
            condicao &= Q(curso=self.curso)  # igualdade textual (010/DP-1005)
        return condicao


@dataclass(frozen=True)
class Selecao:
    conclusoes: int
    pessoas: tuple[tuple[object, object], ...]  # (pessoa_id, ContatoDaPessoa | None)
    excluidas: int

    @property
    def com_contato(self) -> int:
        return sum(contato is not None for _, contato in self.pessoas)

    @property
    def sem_contato(self) -> int:
        return len(self.pessoas) - self.com_contato


def ja_abordadas(campanha):
    """Pessoas com membro desta Campanha em situação que não seja `SEM_CONTATO` (FR-024)."""
    return MembroDoLote.objects.filter(campanha=campanha).exclude(
        situacao=SituacaoDoMembro.SEM_CONTATO
    ).values("pessoa_id")


def selecionar(campanha, escopo, filtros: Filtros, agora) -> Selecao:
    conclusoes = populacao_no_momento(campanha)
    if not escopo.institucional:
        conclusoes = conclusoes.filter(unidade__in=sorted(escopo.unidades))
    conclusoes = conclusoes.filter(filtros.condicao())
    todas = sorted(set(conclusoes.values_list("pessoa_id", flat=True)), key=str)
    abordadas = set(ja_abordadas(campanha).values_list("pessoa_id", flat=True))
    elegiveis = [p for p in todas if p not in abordadas]
    return Selecao(
        conclusoes=conclusoes.count(),
        pessoas=tuple((p, contato_utilizavel(p, agora)) for p in elegiveis),
        excluidas=len(todas) - len(elegiveis),
    )

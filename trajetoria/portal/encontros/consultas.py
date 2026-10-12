"""Leituras dos encontros (031, incremento 1; research R6, R8, R10). Nada grava.

A pertinência é a da 025 (`satisfaz` e `explicacao`), aplicada ao Encontro, que usa os mesmos
nomes de critério. A descoberta não lê Resposta, Formação Declarada, contato nem nome.
"""

from dataclasses import dataclass
from datetime import datetime

from django.utils import timezone

from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.governanca import modera
from trajetoria.portal.encontros.regras import Quem
from trajetoria.portal.models import Categoria, Encontro
from trajetoria.portal.oportunidades.consultas import itens_da_pessoa
from trajetoria.portal.oportunidades.pertinencia import explicacao, satisfaz


@dataclass(frozen=True)
class Item:
    encontro: Encontro
    explicacao: str


def publicados_em_curso(agora: datetime):
    """Publicados, sem decisão contrária nem cancelamento, antes do término (FR-011)."""
    return Encontro.objects.filter(
        publicado_em__isnull=False, recusado_em__isnull=True, retirado_em__isnull=True,
        cancelado_em__isnull=True, termino__gt=agora,
    ).order_by("inicio", "titulo", "id")


def pertinentes(pessoa, agora: datetime) -> list[Item]:
    """Os encontros que aparecem na lista da Pessoa, pela data (FR-011 a FR-013). Sem
    Conclusão, nada."""
    conclusoes = tuple(pessoa.conclusoes.all())
    if not conclusoes:
        return []
    itens = []
    for encontro in publicados_em_curso(agora):
        if not encontro.tem_publico:
            itens.append(Item(encontro, m.ABERTO_A_TODOS))
            continue
        formacoes = tuple(c for c in conclusoes if satisfaz(encontro, c))
        if formacoes:
            itens.append(Item(encontro, explicacao(encontro, formacoes)))
    return itens


def explicacao_para(pessoa, encontro) -> str | None:
    """A explicação da pertinência, ou `None` se o encontro não é para a formação da Pessoa
    (ela chegou pelo endereço; H-3108)."""
    if not encontro.tem_publico:
        return m.ABERTO_A_TODOS
    formacoes = tuple(c for c in pessoa.conclusoes.all() if satisfaz(encontro, c))
    return explicacao(encontro, formacoes) if formacoes else None


def eventos_do_ifes(pessoa, agora: datetime) -> list:
    """Itens A: as oportunidades pertinentes da categoria Eventos, na ordem da 025."""
    itens = itens_da_pessoa(pessoa, timezone.localdate(agora))
    return [i for i in itens if i.oportunidade.categoria == Categoria.EVENTOS]


def do_organizador(pessoa):
    return Encontro.objects.filter(pessoa_id=pessoa.pk).order_by("-enviado_em", "id")


def do_escopo(escopo) -> list[Encontro]:
    """Os encontros que o escopo modera (research R8). O volume da demonstração permite filtrar
    em Python, com a mesma regra que autoriza a ação."""
    return [e for e in Encontro.objects.order_by("inicio", "titulo", "id") if modera(escopo, e)]


def confirmacao_ativa(pessoa, encontro):
    if pessoa is None:
        return None
    return encontro.confirmacoes.filter(pessoa_id=pessoa.pk, cancelada_em__isnull=True).first()


def quantas_confirmaram(encontro) -> int:
    """Só para o organizador e a moderação (FR-025). Nunca quem."""
    return encontro.confirmacoes.filter(cancelada_em__isnull=True).count()


def quem_e(pessoa, encontro, *, com_conclusao: bool) -> Quem:
    """Quem a Pessoa é diante deste encontro (research R10). A moderação tem telas próprias."""
    if pessoa is None:
        return Quem.ANONIMO
    if not com_conclusao:
        return Quem.SEM_CONCLUSAO
    if encontro.pessoa_id == pessoa.pk:
        return Quem.ORGANIZADOR
    if confirmacao_ativa(pessoa, encontro) is not None:
        return Quem.CONFIRMADO
    return Quem.EGRESSO

"""Carga do contexto da trajetória (Feature 021, P2; contracts/contexto-da-trajetoria.md).

Separada da incorporação (001): nunca é chamada por ela, pelo acesso (018), pela declaração
(019) nem pela view da narrativa (FR-071, FR-008). A consulta à fonte acontece fora da
transação; indisponibilidade não grava nada e não se propaga (FR-062). Nada é atualizado:
complemento diferente e agregado com valor diferente na mesma chave são só sinalizados, sem
valores pessoais (FR-048, FR-057).
"""

import logging
from dataclasses import dataclass
from enum import Enum

from django.db import transaction

from trajetoria.contexto_trajetoria.models import (
    ComplementoDaConclusao,
    ContextoInstitucionalAgregado,
)
from trajetoria.fonte_academica.contexto_da_trajetoria import ContextoIndisponivel

logger = logging.getLogger("trajetoria.contexto_trajetoria")


class SituacaoDaCarga(Enum):
    CARREGADO = "carregado"
    INDISPONIVEL = "indisponivel"
    SEM_CONCLUSOES = "sem_conclusoes"


@dataclass(frozen=True)
class Sinal:
    """Divergência sinalizada; `referencia` é id externo ou recorte, nunca dado pessoal."""

    tipo: str
    fonte: str
    referencia: str
    campos: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoDaCarga:
    situacao: SituacaoDaCarga
    complementos_criados: int = 0
    agregados_criados: int = 0
    sinais: tuple[Sinal, ...] = ()


def carregar_contexto(fonte_de_contexto, pessoa) -> ResultadoDaCarga:
    codigo = fonte_de_contexto.codigo
    conclusoes = {c.id_externo: c for c in pessoa.conclusoes.filter(fonte=codigo)}
    if not conclusoes:
        return ResultadoDaCarga(SituacaoDaCarga.SEM_CONCLUSOES)
    try:
        resposta = fonte_de_contexto.obter_contexto(tuple(sorted(conclusoes)))
    except ContextoIndisponivel:
        logger.warning("Contexto da trajetória indisponível na fonte %s", codigo)
        return ResultadoDaCarga(SituacaoDaCarga.INDISPONIVEL)

    sinais: list[Sinal] = []
    complementos = agregados = 0
    with transaction.atomic():
        for na_fonte in resposta.complementos:
            conclusao = conclusoes.get(na_fonte.id_externo_conclusao)
            if conclusao is None:  # não pedida, ou de outra Pessoa: ignorado
                continue
            gravado, criado = ComplementoDaConclusao.objects.get_or_create(
                conclusao=conclusao,
                defaults={
                    "ano_ingresso": na_fonte.ano_ingresso,
                    "data_ingresso": na_fonte.data_ingresso,
                },
            )
            if criado:
                complementos += 1
                continue
            campos = tuple(
                campo for campo in ("ano_ingresso", "data_ingresso")
                if getattr(gravado, campo) != getattr(na_fonte, campo)
            )
            if campos:
                sinais.append(Sinal("complemento_diferente", codigo, conclusao.id_externo, campos))
        for na_fonte in resposta.agregados:
            gravado, criado = ContextoInstitucionalAgregado.objects.get_or_create(
                fonte=codigo,
                metrica=na_fonte.metrica.value,
                curso=na_fonte.curso,
                unidade=na_fonte.unidade,
                ano=na_fonte.ano,
                apurado_em=na_fonte.apurado_em,
                defaults={"valor": na_fonte.valor},
            )
            if criado:
                agregados += 1
            elif gravado.valor != na_fonte.valor:
                recorte = " · ".join(
                    str(v) for v in (na_fonte.metrica.value, na_fonte.curso, na_fonte.unidade,
                                     na_fonte.ano, na_fonte.apurado_em.isoformat())
                    if v is not None
                )
                sinais.append(Sinal("agregado_divergente", codigo, recorte, ("valor",)))
        transaction.on_commit(lambda: _registrar(sinais))
    return ResultadoDaCarga(SituacaoDaCarga.CARREGADO, complementos, agregados, tuple(sinais))


def _registrar(sinais) -> None:
    for sinal in sinais:
        logger.warning(
            "Divergência %s em %s:%s (campos: %s)",
            sinal.tipo, sinal.fonte, sinal.referencia, ", ".join(sinal.campos) or "—",
        )

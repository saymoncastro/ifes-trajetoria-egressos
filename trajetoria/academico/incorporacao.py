"""Incorporação de uma Pessoa e de suas Conclusões a partir de uma fonte acadêmica.

Contrato: specs/001-nucleo-academico-fonte-simulada/contracts/incorporacao.md. A fonte é
recebida como argumento; o núcleo conhece apenas o contrato da fronteira.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from django.db import transaction

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.contrato import (
    ConclusaoNaFonte,
    FonteAcademica,
    PessoaEncontrada,
)

logger = logging.getLogger("trajetoria.academico")


class SituacaoIncorporacao(Enum):
    INCORPORADA = "incorporada"
    SEM_CONCLUSAO_ELEGIVEL = "sem_conclusao_elegivel"
    PESSOA_INEXISTENTE = "pessoa_inexistente"


class TipoDivergencia(Enum):
    ATRIBUTOS_DIFERENTES = "atributos_diferentes"
    CONCLUSAO_DE_OUTRA_PESSOA = "conclusao_de_outra_pessoa"
    AUSENTE_NA_FONTE = "ausente_na_fonte"


@dataclass(frozen=True)
class Divergencia:
    """Diferença entre o já incorporado e o que a fonte devolveu agora. Só é sinalizada:
    nada é alterado e nada sobre ela é persistido (FR-033; DP-005, DP-006)."""

    tipo: TipoDivergencia
    registro: Literal["pessoa", "conclusao"]
    fonte: str
    id_externo: str
    campos: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoIncorporacao:
    situacao: SituacaoIncorporacao
    pessoa: Pessoa | None = None
    pessoa_criada: bool = False
    conclusoes_criadas: tuple[ConclusaoAcademica, ...] = ()
    conclusoes_existentes: tuple[ConclusaoAcademica, ...] = ()
    divergencias: tuple[Divergencia, ...] = ()


def incorporar_pessoa(fonte: FonteAcademica, id_externo_pessoa: str) -> ResultadoIncorporacao:
    """Incorpora a Pessoa e suas conclusões reconhecidas. Idempotente: a deduplicação usa
    só (fonte, id_externo). Nunca atualiza nem remove."""
    # Consulta antes de abrir a transação: uma falha da fonte não chega a escrever nada.
    resposta = fonte.obter_pessoa(id_externo_pessoa)

    if isinstance(resposta, PessoaEncontrada):
        with transaction.atomic():
            resultado = _incorporar(fonte.codigo, resposta)
    else:
        resultado = _pessoa_inexistente(fonte.codigo, resposta.id_externo)
    for divergencia in resultado.divergencias:
        _registrar(divergencia)
    return resultado


def _incorporar(codigo: str, resposta: PessoaEncontrada) -> ResultadoIncorporacao:
    divergencias: list[Divergencia] = []
    pessoa = Pessoa.objects.filter(fonte=codigo, id_externo=resposta.id_externo).first()
    if pessoa is not None and pessoa.nome != resposta.nome:
        divergencias.append(
            Divergencia(
                TipoDivergencia.ATRIBUTOS_DIFERENTES, "pessoa", codigo, pessoa.id_externo,
                ("nome",),
            )
        )

    ja_incorporadas = {
        c.id_externo: c
        for c in ConclusaoAcademica.objects.filter(
            fonte=codigo, id_externo__in=[c.id_externo for c in resposta.conclusoes]
        )
    }
    novas: list[ConclusaoNaFonte] = []
    existentes: list[ConclusaoAcademica] = []
    for na_fonte in resposta.conclusoes:
        incorporada = ja_incorporadas.get(na_fonte.id_externo)
        if incorporada is None:
            novas.append(na_fonte)
        elif pessoa is None or incorporada.pessoa_id != pessoa.id:
            # Não reatribui nem duplica.
            divergencias.append(
                Divergencia(
                    TipoDivergencia.CONCLUSAO_DE_OUTRA_PESSOA, "conclusao", codigo,
                    na_fonte.id_externo,
                )
            )
        else:
            campos = tuple(
                campo for campo, valor in _contexto(na_fonte).items()
                if getattr(incorporada, campo) != valor
            )
            if campos:
                divergencias.append(
                    Divergencia(
                        TipoDivergencia.ATRIBUTOS_DIFERENTES, "conclusao", codigo,
                        na_fonte.id_externo, campos,
                    )
                )
            existentes.append(incorporada)

    if pessoa is not None:
        presentes = [c.id_externo for c in resposta.conclusoes]
        for ausente in pessoa.conclusoes.filter(fonte=codigo).exclude(id_externo__in=presentes):
            divergencias.append(
                Divergencia(
                    TipoDivergencia.AUSENTE_NA_FONTE, "conclusao", codigo, ausente.id_externo
                )
            )
    elif not novas:
        # Sem conclusão que possa ser associada a ela (nenhuma reconhecida, ou todas já de
        # outras Pessoas): a Pessoa não é materializada (FR-039).
        return ResultadoIncorporacao(
            SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL, divergencias=tuple(divergencias)
        )

    pessoa_criada = False
    if pessoa is None:
        pessoa, pessoa_criada = Pessoa.objects.get_or_create(
            fonte=codigo, id_externo=resposta.id_externo, defaults={"nome": resposta.nome}
        )
    criadas = []
    for na_fonte in novas:
        conclusao, _ = ConclusaoAcademica.objects.get_or_create(
            fonte=codigo,
            id_externo=na_fonte.id_externo,
            defaults={"pessoa": pessoa, **_contexto(na_fonte)},
        )
        criadas.append(conclusao)

    # Pessoa já incorporada que a fonte agora devolve sem conclusões: as ausências já
    # foram sinalizadas acima, e nada foi alterado.
    situacao = (
        SituacaoIncorporacao.INCORPORADA
        if resposta.conclusoes
        else SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL
    )
    return ResultadoIncorporacao(
        situacao,
        pessoa=pessoa,
        pessoa_criada=pessoa_criada,
        conclusoes_criadas=tuple(criadas),
        conclusoes_existentes=tuple(existentes),
        divergencias=tuple(divergencias),
    )


def _pessoa_inexistente(codigo: str, id_externo: str) -> ResultadoIncorporacao:
    # Se já foi incorporada, a ausência é sinalizada; nada é removido.
    pessoa = Pessoa.objects.filter(fonte=codigo, id_externo=id_externo).first()
    divergencias = (
        (Divergencia(TipoDivergencia.AUSENTE_NA_FONTE, "pessoa", codigo, id_externo),)
        if pessoa is not None
        else ()
    )
    return ResultadoIncorporacao(
        SituacaoIncorporacao.PESSOA_INEXISTENTE, pessoa=pessoa, divergencias=divergencias
    )


def _contexto(conclusao: ConclusaoNaFonte) -> dict:
    return {
        "curso": conclusao.curso,
        "unidade": conclusao.unidade,
        "nivel": conclusao.nivel,
        "modalidade": conclusao.modalidade,
        "forma_oferta": conclusao.forma_oferta,
        "ano_conclusao": conclusao.ano_conclusao,
        "data_conclusao": conclusao.data_conclusao,
    }


def _registrar(divergencia: Divergencia) -> None:
    # Só identificadores e nomes de campos: nunca valores pessoais (Princípio XVI).
    logger.warning(
        "Divergência %s em %s %s:%s (campos: %s)",
        divergencia.tipo.name,
        divergencia.registro,
        divergencia.fonte,
        divergencia.id_externo,
        ", ".join(divergencia.campos) or "—",
    )

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
    CAMPOS_DE_CONTEXTO,
    ConclusaoNaFonte,
    FonteAcademica,
    PessoaEncontrada,
    PessoaInexistente,
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

    with transaction.atomic():
        resultado = incorporar_encontrada(fonte.codigo, resposta)
    registrar_divergencias(resultado)
    return resultado


def registrar_divergencias(resultado: ResultadoIncorporacao) -> None:
    """Registra as divergências de uma incorporação, sem valores pessoais. Quem compõe a
    incorporação numa transação própria chama depois do commit."""
    for divergencia in resultado.divergencias:
        _registrar(divergencia)


def incorporar_encontrada(codigo, resposta) -> ResultadoIncorporacao:
    """Incorpora uma resposta já obtida, na transação do chamador; não registra logs."""
    if isinstance(resposta, PessoaEncontrada):
        return _incorporar(codigo, resposta)
    if isinstance(resposta, PessoaInexistente):
        return _pessoa_inexistente(codigo, resposta.id_externo)
    # Resposta fora do contrato é erro de integração, nunca "inexistente" (FR-025).
    raise TypeError(f"resposta fora do contrato: {type(resposta).__name__}")


def _incorporar(codigo: str, resposta: PessoaEncontrada) -> ResultadoIncorporacao:
    pessoa = Pessoa.objects.filter(fonte=codigo, id_externo=resposta.id_externo).first()
    ja_incorporadas = {
        c.id_externo: c
        for c in ConclusaoAcademica.objects.filter(
            fonte=codigo, id_externo__in=[c.id_externo for c in resposta.conclusoes]
        )
    }

    if pessoa is None and all(c.id_externo in ja_incorporadas for c in resposta.conclusoes):
        # Sem conclusão que possa ser associada a ela (nenhuma reconhecida, ou todas já de
        # outras Pessoas): a Pessoa não é materializada (FR-039).
        divergencias = tuple(
            _comparar(codigo, None, ja_incorporadas[c.id_externo], c) for c in resposta.conclusoes
        )
        return ResultadoIncorporacao(
            SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL, divergencias=divergencias
        )

    pessoa_criada = False
    if pessoa is None:
        pessoa, pessoa_criada = Pessoa.objects.get_or_create(
            fonte=codigo, id_externo=resposta.id_externo, defaults={"nome": resposta.nome}
        )
    divergencias: list[Divergencia] = []
    # Também cobre a Pessoa criada por outra transação entre a leitura e o get_or_create.
    if not pessoa_criada and pessoa.nome != resposta.nome:
        divergencias.append(
            Divergencia(
                TipoDivergencia.ATRIBUTOS_DIFERENTES, "pessoa", codigo, pessoa.id_externo,
                ("nome",),
            )
        )

    criadas: list[ConclusaoAcademica] = []
    existentes: list[ConclusaoAcademica] = []
    for na_fonte in resposta.conclusoes:
        incorporada = ja_incorporadas.get(na_fonte.id_externo)
        if incorporada is None:
            incorporada, criada = ConclusaoAcademica.objects.get_or_create(
                fonte=codigo,
                id_externo=na_fonte.id_externo,
                defaults={"pessoa": pessoa, **_contexto(na_fonte)},
            )
            if criada:
                criadas.append(incorporada)
                continue
        # Já existia, inclusive se criada por outra transação depois da leitura acima.
        if divergencia := _comparar(codigo, pessoa, incorporada, na_fonte):
            divergencias.append(divergencia)
        if incorporada.pessoa_id == pessoa.id:
            existentes.append(incorporada)

    if not pessoa_criada:
        presentes = [c.id_externo for c in resposta.conclusoes]
        for ausente in pessoa.conclusoes.filter(fonte=codigo).exclude(id_externo__in=presentes):
            divergencias.append(
                Divergencia(
                    TipoDivergencia.AUSENTE_NA_FONTE, "conclusao", codigo, ausente.id_externo
                )
            )

    # Pessoa já incorporada que a fonte agora devolve sem conclusões: as ausências foram
    # sinalizadas acima, e nada foi alterado.
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


def _comparar(
    codigo: str,
    pessoa: Pessoa | None,
    incorporada: ConclusaoAcademica,
    na_fonte: ConclusaoNaFonte,
) -> Divergencia | None:
    """Compara uma conclusão já incorporada com a devolvida agora; não altera nada."""
    if pessoa is None or incorporada.pessoa_id != pessoa.id:
        # Não reatribui nem duplica.
        return Divergencia(
            TipoDivergencia.CONCLUSAO_DE_OUTRA_PESSOA, "conclusao", codigo, na_fonte.id_externo
        )
    campos = tuple(
        campo for campo, valor in _contexto(na_fonte).items()
        if getattr(incorporada, campo) != valor
    )
    if campos:
        return Divergencia(
            TipoDivergencia.ATRIBUTOS_DIFERENTES, "conclusao", codigo, na_fonte.id_externo,
            campos,
        )
    return None


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
    return {campo: getattr(conclusao, campo) for campo in CAMPOS_DE_CONTEXTO}


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

"""Incorporação de uma Pessoa e de suas Conclusões a partir de uma fonte acadêmica.

Contrato: specs/001-nucleo-academico-fonte-simulada/contracts/incorporacao.md. A fonte é
recebida como argumento; o núcleo conhece apenas o contrato da fronteira.
"""

from dataclasses import dataclass
from enum import Enum

from django.db import transaction

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.contrato import (
    ConclusaoNaFonte,
    FonteAcademica,
    PessoaEncontrada,
)


class SituacaoIncorporacao(Enum):
    INCORPORADA = "incorporada"
    SEM_CONCLUSAO_ELEGIVEL = "sem_conclusao_elegivel"
    PESSOA_INEXISTENTE = "pessoa_inexistente"


@dataclass(frozen=True)
class ResultadoIncorporacao:
    situacao: SituacaoIncorporacao
    pessoa: Pessoa | None = None
    pessoa_criada: bool = False
    conclusoes_criadas: tuple[ConclusaoAcademica, ...] = ()
    conclusoes_existentes: tuple[ConclusaoAcademica, ...] = ()


def incorporar_pessoa(fonte: FonteAcademica, id_externo_pessoa: str) -> ResultadoIncorporacao:
    """Incorpora a Pessoa e suas conclusões reconhecidas. Idempotente: a deduplicação usa
    só (fonte, id_externo). Nunca atualiza nem remove."""
    # Consulta antes de abrir a transação: uma falha da fonte não chega a escrever nada.
    resposta = fonte.obter_pessoa(id_externo_pessoa)

    if not isinstance(resposta, PessoaEncontrada):
        return ResultadoIncorporacao(SituacaoIncorporacao.PESSOA_INEXISTENTE)

    if not resposta.conclusoes:
        # Pessoa sem conclusão elegível não é materializada (FR-039).
        return ResultadoIncorporacao(SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL)

    with transaction.atomic():
        pessoa, pessoa_criada = Pessoa.objects.get_or_create(
            fonte=fonte.codigo,
            id_externo=resposta.id_externo,
            defaults={"nome": resposta.nome},
        )
        criadas, existentes = [], []
        for conclusao_na_fonte in resposta.conclusoes:
            conclusao, criada = ConclusaoAcademica.objects.get_or_create(
                fonte=fonte.codigo,
                id_externo=conclusao_na_fonte.id_externo,
                defaults={"pessoa": pessoa, **_contexto(conclusao_na_fonte)},
            )
            (criadas if criada else existentes).append(conclusao)

    return ResultadoIncorporacao(
        SituacaoIncorporacao.INCORPORADA,
        pessoa=pessoa,
        pessoa_criada=pessoa_criada,
        conclusoes_criadas=tuple(criadas),
        conclusoes_existentes=tuple(existentes),
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

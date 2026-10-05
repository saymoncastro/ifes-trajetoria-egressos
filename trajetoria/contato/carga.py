"""Carga de contatos da fonte (Feature 020; contracts/fonte-de-contatos.md; research R2, R3).

Separada da incorporação (001): nunca é chamada por ela, pelo acesso (018), pela declaração
(019) nem pela narrativa (021). A consulta à fonte acontece fora da transação;
indisponibilidade não grava nada e não se confunde com "sem e-mail".

Uma **observação** é a lista ordenada de e-mails válidos que a fonte informou num momento.
Só é gravada quando difere da última gravada para a mesma Pessoa e fonte (idempotência
por observação, não por valor, para preservar a ordem do adaptador). Lista vazia não grava
nem apaga. Nada é atualizado nem removido. Logs só com categoria e código da fonte.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from django.db import transaction
from django.utils import timezone

from trajetoria.contato.endereco import EnderecoInvalido, normalizar_email
from trajetoria.contato.models import Canal, ContatoDaPessoa, Origem
from trajetoria.fonte_academica.contatos_da_fonte import ContatosIndisponiveis

logger = logging.getLogger("trajetoria.contato")


class SituacaoDaCarga(Enum):
    CARREGADO = "carregado"
    INALTERADO = "inalterado"
    SEM_EMAIL = "sem_email"
    INDISPONIVEL = "indisponivel"


@dataclass(frozen=True)
class ResultadoDaCarga:
    situacao: SituacaoDaCarga
    gravados: int = 0
    ignorados_invalidos: int = 0


def _ultima_observacao(pessoa, fonte) -> tuple[str, ...]:
    registros = ContatoDaPessoa.objects.filter(
        pessoa=pessoa, origem=Origem.FONTE_ACADEMICA, fonte=fonte
    )
    ultima = registros.order_by("-obtido_em").values_list("obtido_em", flat=True).first()
    if ultima is None:
        return ()
    return tuple(
        registros.filter(obtido_em=ultima).order_by("posicao").values_list("valor", flat=True)
    )


def carregar_contatos(fonte, pessoa, *, agora=None) -> ResultadoDaCarga:
    codigo = fonte.codigo
    try:
        recebidos = fonte.obter_emails(pessoa.id_externo)
    except ContatosIndisponiveis:
        logger.warning("Contatos indisponíveis na fonte %s", codigo)
        return ResultadoDaCarga(SituacaoDaCarga.INDISPONIVEL)

    validos, invalidos = [], 0
    for valor in recebidos:
        try:
            normalizado = normalizar_email(valor)
        except EnderecoInvalido:
            invalidos += 1
            continue
        if normalizado not in validos:
            validos.append(normalizado)
    if invalidos:
        logger.warning("Contato inválido ignorado na fonte %s (%d)", codigo, invalidos)
    if not validos:
        return ResultadoDaCarga(SituacaoDaCarga.SEM_EMAIL, ignorados_invalidos=invalidos)

    agora = agora or timezone.now()
    with transaction.atomic():
        if _ultima_observacao(pessoa, codigo) == tuple(validos):
            return ResultadoDaCarga(SituacaoDaCarga.INALTERADO, ignorados_invalidos=invalidos)
        ContatoDaPessoa.objects.bulk_create(
            ContatoDaPessoa(
                pessoa=pessoa,
                canal=Canal.EMAIL,
                valor=valor,
                origem=Origem.FONTE_ACADEMICA,
                fonte=codigo,
                posicao=posicao,
                obtido_em=agora,
            )
            for posicao, valor in enumerate(validos)
        )
    return ResultadoDaCarga(SituacaoDaCarga.CARREGADO, len(validos), invalidos)

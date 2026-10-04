"""Verificação uniforme, sem fonte externa nem escrita de domínio."""

import hmac
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from django.utils import timezone

from trajetoria.acesso import limitacao
from trajetoria.acesso.chaves import (
    ChavesInvalidas,
    chave_de_origem,
    chaves_de_acesso,
    identificador_cpf,
    verificador,
)
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.acesso.normalizacao import normalizar_cpf, normalizar_data

logger = logging.getLogger("trajetoria.acesso")


@dataclass(frozen=True)
class Confirmada:
    pessoa: object
    versao_material: object


@dataclass(frozen=True)
class NaoConfirmada:
    pass


class CausaIndisponibilidade(Enum):
    CHAVE_NAO_CONFIGURADA = "chave_nao_configurada"
    LIMITE_TEMPORARIO = "limite_temporario"
    FALHA_TECNICA = "falha_tecnica"


@dataclass(frozen=True)
class Indisponivel:
    causa: CausaIndisponibilidade
    espera_ate: object = None


@dataclass(frozen=True)
class FormatoInvalido:
    campos: tuple[str, ...]


def verificar(cpf_texto, data_texto, origem, *, agora):
    try:
        # A origem precisa de uma chave válida para nunca ir ao cache em claro.
        # Configuração ausente ainda permite orientar erros de formato, sem cache.
        try:
            chaves = chaves_de_acesso()
        except ChavesInvalidas:
            campos = _campos_invalidos(cpf_texto, data_texto, agora)
            if campos:
                return FormatoInvalido(campos)
            logger.warning("CHAVE_NAO_CONFIGURADA")
            return Indisponivel(CausaIndisponibilidade.CHAVE_NAO_CONFIGURADA)
        origem_derivada = "acesso:origem:" + chave_de_origem(origem, chaves)
        if ate := limitacao.em_espera(origem_derivada, agora):
            return Indisponivel(CausaIndisponibilidade.LIMITE_TEMPORARIO, ate)
        limitacao.registrar("origem", origem_derivada, agora)
        campos = _campos_invalidos(cpf_texto, data_texto, agora)
        if campos:
            return FormatoInvalido(campos)
        cpf = normalizar_cpf(cpf_texto)
        data = normalizar_data(data_texto, timezone.localdate(agora))
        identificador = identificador_cpf(cpf, chaves)
        procurado = verificador(cpf, data, chaves)
        chave_cpf = "acesso:cpf:" + identificador
        # Uma verificação por CPF de cada vez: tentativas simultâneas não escapam da conta.
        if not limitacao.travar(chave_cpf):
            logger.info("LIMITE_TEMPORARIO (verificação simultânea)")
            return Indisponivel(
                CausaIndisponibilidade.LIMITE_TEMPORARIO, agora + timedelta(seconds=1)
            )
        try:
            if ate := limitacao.em_espera(chave_cpf, agora):
                return Indisponivel(CausaIndisponibilidade.LIMITE_TEMPORARIO, ate)
            materiais = list(
                MaterialDeVerificacao.objects.filter(
                    identificador_cpf=identificador
                ).select_related("pessoa")
            )
            unico = materiais[0] if len(materiais) == 1 else None
            esperado = unico.verificador if unico and unico.verificador else "0" * 64
            confere = hmac.compare_digest(procurado, esperado)
            if unico is not None and unico.verificador is not None and confere:
                limitacao.zerar(chave_cpf)
                limitacao.estornar(origem_derivada)
                return Confirmada(unico.pessoa, unico.atualizado_em)
            limitacao.registrar("cpf", chave_cpf, agora)
            return NaoConfirmada()
        finally:
            limitacao.liberar(chave_cpf)
    except Exception as erro:
        logger.warning("FALHA_TECNICA (%s)", type(erro).__name__)
        return Indisponivel(CausaIndisponibilidade.FALHA_TECNICA)


def _campos_invalidos(cpf, data, agora):
    return tuple(
        campo
        for campo, invalido in (
            ("cpf", normalizar_cpf(cpf) is None),
            ("data_nascimento", normalizar_data(data, timezone.localdate(agora)) is None),
        )
        if invalido
    )

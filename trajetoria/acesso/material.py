"""Importação atômica do material; única fronteira de escrita (018 R5/R6)."""

import logging
from dataclasses import dataclass
from enum import Enum

from django.db import transaction
from django.utils import timezone

from trajetoria.academico.incorporacao import incorporar_encontrada, registrar_divergencias
from trajetoria.acesso.chaves import chaves_de_acesso, identificador_cpf, verificador
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.acesso.normalizacao import cpf_utilizavel
from trajetoria.fonte_academica.contrato import PessoaEncontrada

logger = logging.getLogger("trajetoria.acesso")


class TipoSinal(Enum):
    CPF_INUTILIZAVEL = "cpf_inutilizavel"
    ALTERADO = "alterado"
    AUSENTE_NA_FONTE = "ausente_na_fonte"
    COLISAO = "colisao"


@dataclass(frozen=True)
class SinalDoMaterial:
    tipo: TipoSinal
    campos: tuple[str, ...] = ()


def registrar_material(pessoa, cpf, data, chaves, agora):
    antigo = MaterialDeVerificacao.objects.select_for_update().filter(pessoa=pessoa).first()
    sinais = []
    if not cpf_utilizavel(cpf):
        if cpf is not None:
            sinais.append(SinalDoMaterial(TipoSinal.CPF_INUTILIZAVEL))
        elif antigo:
            sinais.append(SinalDoMaterial(TipoSinal.AUSENTE_NA_FONTE, ("cpf",)))
        return sinais
    identificador = identificador_cpf(cpf, chaves)
    novo_verificador = verificador(cpf, data, chaves) if data is not None else None
    if antigo is None:
        antigo = MaterialDeVerificacao.objects.create(
            pessoa=pessoa,
            identificador_cpf=identificador,
            verificador=novo_verificador,
            atualizado_em=agora,
        )
    else:
        mudou_cpf = antigo.identificador_cpf != identificador
        if mudou_cpf:
            antigo.identificador_cpf = identificador
            antigo.verificador = novo_verificador
            sinais.append(SinalDoMaterial(TipoSinal.ALTERADO, ("cpf",)))
        elif data is not None and antigo.verificador != novo_verificador:
            antigo.verificador = novo_verificador
            sinais.append(SinalDoMaterial(TipoSinal.ALTERADO, ("data_nascimento",)))
        elif data is None and antigo.verificador is not None:
            # Só é ausência o que já esteve presente; material sem data não sinaliza a cada carga.
            sinais.append(SinalDoMaterial(TipoSinal.AUSENTE_NA_FONTE, ("data_nascimento",)))
        if any(s.tipo == TipoSinal.ALTERADO for s in sinais):
            antigo.atualizado_em = agora
            antigo.save(update_fields=("identificador_cpf", "verificador", "atualizado_em"))
    if (
        MaterialDeVerificacao.objects.filter(identificador_cpf=identificador)
        .exclude(pessoa=pessoa)
        .exists()
    ):
        sinais.append(SinalDoMaterial(TipoSinal.COLISAO))
    return sinais


def incorporar_com_material(fonte, id_externo):
    chaves = chaves_de_acesso()
    resposta = fonte.obter_pessoa(id_externo)
    with transaction.atomic():
        resultado = incorporar_encontrada(fonte.codigo, resposta)
        sinais = []
        if resultado.pessoa is not None and isinstance(resposta, PessoaEncontrada):
            sinais = registrar_material(
                resultado.pessoa, resposta.cpf, resposta.data_nascimento, chaves, timezone.now()
            )

        # O preparo pode abrir uma transação externa: logs só após o commit dela.
        def registrar():
            registrar_divergencias(resultado)
            for sinal in sinais:
                logger.warning(
                    "Material %s em %s:%s (campos: %s)",
                    sinal.tipo.name,
                    fonte.codigo,
                    id_externo,
                    ", ".join(sinal.campos) or "—",
                )

        transaction.on_commit(registrar)
    return resultado

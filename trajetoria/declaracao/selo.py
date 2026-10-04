"""Credenciais transitórias e dados de consulta autenticados, com chaves independentes.

O selo transitório (chave A) é da 018 (`acesso.transito`); aqui ficam o selo de início, que
usa a mesma chave, e os dados persistidos para consulta ao acervo (chave B). Toda operação da
019 valida as duas chaves juntas: B nunca pode ser igual a A nem a outra chave do sistema.
"""

import json
from datetime import date
from uuid import UUID, uuid4

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from trajetoria.acesso import transito
from trajetoria.acesso.transito import ChaveIndisponivel, SeloInvalido, selar_transito

__all__ = [
    "ChaveIndisponivel",
    "SeloInvalido",
    "abrir_consulta",
    "abrir_inicio",
    "abrir_transito",
    "selar_consulta",
    "selar_inicio",
    "selar_transito",
    "validar_chaves",
]


def validar_chaves():
    a = transito.chave_do_selo()
    b = settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO
    outras = (
        settings.TRAJETORIA_CHAVE_SELO_DECLARACAO,
        settings.SECRET_KEY,
        settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO,
        settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO,
        settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO,
    )
    try:
        if not isinstance(b, str) or not b or b in outras:
            raise ValueError
        return a, Fernet(b)
    except (TypeError, ValueError):
        raise ChaveIndisponivel("Dados temporariamente indisponíveis.") from None


def abrir_transito(token, agora):
    validar_chaves()
    cpf, data, _ = transito.abrir(token, "transito", agora)
    return cpf, data


def selar_inicio(cpf11, data, dados):
    validar_chaves()
    return transito.selar("inicio", cpf11, data, dados=dados, chave=str(uuid4()))


def abrir_inicio(token, agora):
    validar_chaves()
    cpf, data, conteudo = transito.abrir(token, "inicio", agora)
    try:
        return cpf, data, conteudo["dados"], UUID(conteudo["chave"])
    except (ValueError, KeyError, TypeError):
        raise SeloInvalido("Confirme os dados novamente.") from None


def selar_consulta(declaracao_id, cpf11, data):
    _, b = validar_chaves()
    conteudo = dict(p="acervo", cpf=cpf11, data=data.isoformat(), formacao=str(declaracao_id))
    return b.encrypt(json.dumps(conteudo).encode()).decode()


def abrir_consulta(dados):
    _, b = validar_chaves()
    try:
        claro = json.loads(b.decrypt(dados.selado.encode()))
        if claro["p"] != "acervo" or claro.get("formacao") != str(dados.formacao_id):
            raise ValueError
        return claro["cpf"], date.fromisoformat(claro["data"])
    except (InvalidToken, ValueError, TypeError, KeyError, AttributeError):
        raise SeloInvalido("Dados indisponíveis.") from None

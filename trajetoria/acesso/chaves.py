"""Derivações HMAC com segredos independentes (018 R3)."""

import hashlib
import hmac
from dataclasses import dataclass, field

from django.conf import settings


class ChavesInvalidas(Exception):
    """Configuração inadequada, sem incluir valores."""


@dataclass(frozen=True)
class Chaves:
    localizacao: str = field(repr=False)
    verificacao: str = field(repr=False)


def chaves_de_acesso():
    a = settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO
    b = settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO
    outras = (settings.SECRET_KEY, settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO)
    if any(not isinstance(k, str) or len(k) < 32 or k in outras for k in (a, b)) or a == b:
        raise ChavesInvalidas("Chaves de acesso não configuradas adequadamente.")
    return Chaves(a, b)


def _hmac(chave, mensagem):
    return hmac.new(chave.encode(), mensagem.encode(), hashlib.sha256).hexdigest()


def identificador_cpf(cpf11, chaves):
    return _hmac(chaves.localizacao, "cpf:" + cpf11)


def verificador(cpf11, data, chaves):
    return _hmac(chaves.verificacao, f"cpf-nascimento:{cpf11}:{data.isoformat()}")


def chave_de_origem(endereco, chaves):
    return _hmac(chaves.localizacao, "origem:" + endereco)

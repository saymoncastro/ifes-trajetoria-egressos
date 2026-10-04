"""Selo transitório do resultado `NAO_CONFIRMADA` (018 FR-035; 019 R5, R6).

É o ponto de saída da 018: CPF e data viajam cifrados, com finalidade e validade, só no
corpo de POST, e nunca vão para sessão, banco, URL ou log. Chave própria (A), distinta das
chaves de acesso, da pseudonimização e do framework. Quem consome o selo (a 019) depende
deste módulo, e nunca o contrário.
"""

import json
from datetime import date

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.utils import timezone


class ChaveIndisponivel(Exception):
    """Configuração inadequada, sem incluir valores."""


class SeloInvalido(Exception):
    """Vencido, adulterado ou de outra finalidade; nunca diz qual."""


def chave_do_selo():
    a = settings.TRAJETORIA_CHAVE_SELO_DECLARACAO
    outras = (
        settings.SECRET_KEY,
        settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO,
        settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO,
        settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO,
    )
    try:
        if not isinstance(a, str) or not a or a in outras:
            raise ValueError
        return Fernet(a)
    except (TypeError, ValueError):
        raise ChaveIndisponivel("Dados temporariamente indisponíveis.") from None


def selar(finalidade, cpf11, data, **campos):
    conteudo = dict(p=finalidade, cpf=cpf11, data=data.isoformat(), **campos)
    return chave_do_selo().encrypt_at_time(
        json.dumps(conteudo).encode(), int(timezone.now().timestamp())
    ).decode()


def abrir(token, finalidade, agora):
    """Devolve `(cpf11, data, conteudo)` de um selo válido, dentro da validade."""
    chave = chave_do_selo()
    try:
        claro = chave.decrypt_at_time(
            token.encode(),
            ttl=int(settings.TRAJETORIA_SELO_DECLARACAO_VALIDADE.total_seconds()),
            current_time=int(agora.timestamp()),
        )
        dados = json.loads(claro)
        if dados["p"] != finalidade:
            raise ValueError
        return dados["cpf"], date.fromisoformat(dados["data"]), dados
    except (InvalidToken, ValueError, TypeError, KeyError, AttributeError):
        raise SeloInvalido("Confirme os dados novamente.") from None


def selar_transito(cpf11, data):
    return selar("transito", cpf11, data)

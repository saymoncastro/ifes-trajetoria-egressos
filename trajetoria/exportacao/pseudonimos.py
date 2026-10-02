"""Pseudônimos analíticos (spec FR-026 a FR-029; research R5).

HMAC-SHA-256 com chave dedicada sobre `"<domínio>:<identificador interno>"`, em hexadecimal.
O domínio separa Conclusão e Pessoa: o mesmo UUID nunca dá o mesmo pseudônimo nos dois.
Estável enquanto a mesma chave vigorar; trocá-la rompe a ligação com exportações
anteriores. Nada é persistido nem registrado: nem a chave, nem os pseudônimos, nem a
correspondência — o cálculo é refeito a cada exportação.
"""

import hashlib
import hmac
from uuid import UUID

from django.conf import settings

from trajetoria.exportacao.regras import ExportacaoRecusada, Motivo

DOMINIOS = ("conclusao", "pessoa")
_TAMANHO_MINIMO = 32  # salvaguarda contra chave trivial; hipótese (research R5)


def chave_de_pseudonimizacao() -> str:
    """A chave configurada, validada antes de qualquer leitura de linha."""
    chave = settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO
    if not chave:
        raise ExportacaoRecusada(Motivo.CHAVE_AUSENTE)
    if len(chave) < _TAMANHO_MINIMO or chave == settings.SECRET_KEY:
        raise ExportacaoRecusada(Motivo.CHAVE_INADEQUADA)
    return chave


def pseudonimo(dominio: str, identificador: UUID, chave: str) -> str:
    if dominio not in DOMINIOS:
        raise ValueError(f"domínio de pseudônimo desconhecido: {dominio}")
    mensagem = f"{dominio}:{identificador}".encode()
    return hmac.new(chave.encode(), mensagem, hashlib.sha256).hexdigest()

"""Contadores transitórios com esperas limitadas; apenas chaves derivadas.

A janela é fixa a partir da primeira contagem: tráfego contínuo (um laboratório atrás do
mesmo endereço) não prolonga a punição indefinidamente. O incremento é atômico
(`add` + `incr`) e a verificação de cada CPF é serializada por uma trava, para que
requisições simultâneas não escapem da contagem. Em produção, o cache precisa ser
compartilhado entre processos (DP-1803).
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import caches

ORIGEM, CPF = "origem", "cpf"
# Tempo máximo de uma verificação; a trava expira sozinha se o processo morrer.
_DURACAO_DA_TRAVA = 10
logger = logging.getLogger("trajetoria.acesso")


def _cache():
    return caches["acesso"]


def em_espera(chave, agora):
    ate = _cache().get(chave + ":ate")
    return ate if ate and ate > agora else None


def registrar(tipo, chave, agora):
    if em_espera(chave, agora):
        return
    cache = _cache()
    config = settings.TRAJETORIA_ACESSO_LIMITES
    regra = config[tipo]
    janela = regra["janela"]
    inicio = cache.get(chave + ":inicio")
    if inicio is not None and inicio + timedelta(seconds=janela) <= agora:
        zerar(chave)  # janela encerrada: nova contagem
        inicio = None
    if inicio is None:
        # `add` só grava se ninguém gravou antes; o início vale o que estiver no cache.
        cache.add(chave + ":inicio", agora, janela)
        inicio = cache.get(chave + ":inicio") or agora
    cache.add(chave + ":n", 0, janela)
    try:
        n = cache.incr(chave + ":n")
    except ValueError:  # expirou entre o `add` e o `incr`
        cache.set(chave + ":n", 1, janela)
        n = 1
    if n > regra["livres"]:
        k = n - regra["livres"] - 1
        # Limitar o expoente evita trabalho ilimitado depois de muitas tentativas.
        segundos = min(
            config["espera_base"] * config["fator"] ** min(k, 20), config["espera_maxima"]
        )
        # A espera nunca ultrapassa a janela: o fim dela sempre devolve a origem ou o CPF.
        ate = min(agora + timedelta(seconds=segundos), inicio + timedelta(seconds=janela))
        cache.set(chave + ":ate", ate, janela)
        logger.info("LIMITE_TEMPORARIO (%s)", tipo)


def estornar(chave):
    """Desconta uma contagem: confirmação bem-sucedida não pune a origem."""
    cache = _cache()
    try:
        if cache.decr(chave + ":n") < 0:
            cache.incr(chave + ":n")
    except ValueError:  # nada contado (ou já expirado)
        pass


def zerar(chave):
    _cache().delete_many([chave + ":inicio", chave + ":n", chave + ":ate"])


def travar(chave):
    """Reserva a verificação desta chave; `False` se outra estiver em andamento."""
    return _cache().add(chave + ":trava", True, _DURACAO_DA_TRAVA)


def liberar(chave):
    _cache().delete(chave + ":trava")

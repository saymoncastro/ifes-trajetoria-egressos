"""Operações do estado técnico do vídeo (Feature 022; data-model §3.1 e §3.2).

- `solicitar` registra o pedido e nunca duplica (FR-032).
- `processar_proximo` renderiza um pedido por vez, fora da transação, e só grava o
  resultado se a linha continuar como estava quando o render começou (analyze U2).
- `limpar` descarta o que venceu e marca como falha o travado ou o esquecido sem
  processador. Roda no processador, a cada pedido e, no máximo a cada 30 s por processo,
  nas leituras: nenhuma composição com nome fica guardada sem prazo (FR-029; analyze P1),
  sem que cada consulta de estado ou pedido `Range` vire três escritas no banco.

Os prazos dos estados intermediários derivam do tempo máximo de render: um render em
andamento nunca é dado como travado nem apagado por uma leitura concorrente.

Nada aqui escreve em dado de domínio (FR-033). Os logs só têm fatos técnicos (FR-027).
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from trajetoria.narrativa.composicao import chave_da_composicao
from trajetoria.video import mensagens, renderizador
from trajetoria.video.models import GeracaoDeVideo as G

logger = logging.getLogger("trajetoria.video")

SEM_PROCESSADOR = timedelta(minutes=10)
INTERVALO_DA_LIMPEZA = timedelta(seconds=30)
_MARGEM = timedelta(minutes=1)
_ultima_limpeza = None
NENHUM, PREPARANDO, PRONTO, FALHOU = "nenhum", "preparando", "pronto", "falhou"
_EXIBIDO = {G.SOLICITADO: PREPARANDO, G.PROCESSANDO: PREPARANDO, G.PRONTO: PRONTO,
            G.FALHOU: FALHOU}


def travado() -> timedelta:
    """Depois disso, um PROCESSANDO é dado como abandonado (processador morto no meio)."""
    return max(
        timedelta(minutes=5),
        timedelta(seconds=settings.TRAJETORIA_VIDEO_TEMPO_MAXIMO) + _MARGEM,
    )


def _expira(momento, minimo=timedelta(0)):
    """Retenção, mas nunca antes do fim da janela do estado (pedido ou render em curso)."""
    return momento + max(settings.TRAJETORIA_VIDEO_RETENCAO, minimo)


def limpar() -> None:
    global _ultima_limpeza
    agora = timezone.now()
    _ultima_limpeza = agora
    G.objects.filter(expira_em__lt=agora).delete()
    falha = {"estado": G.FALHOU, "composicao": None, "concluido_em": agora,
             "expira_em": _expira(agora)}
    G.objects.filter(estado=G.PROCESSANDO, iniciado_em__lt=agora - travado()).update(
        motivo="tempo_esgotado", **falha
    )
    G.objects.filter(estado=G.SOLICITADO, solicitado_em__lt=agora - SEM_PROCESSADOR).update(
        motivo="sem_processador", **falha
    )


def _limpar_se_preciso() -> None:
    """Nas leituras, no máximo uma limpeza por intervalo e por processo. O relógio que volta
    (`abs`) também limpa."""
    agora = timezone.now()
    if _ultima_limpeza is None or abs(agora - _ultima_limpeza) >= INTERVALO_DA_LIMPEZA:
        limpar()


def solicitar(composicao: dict) -> None:
    limpar()
    chave = chave_da_composicao(composicao)
    agora = timezone.now()
    campos = {
        "template": composicao["template"], "estado": G.SOLICITADO, "composicao": composicao,
        "video": None, "tamanho": None, "motivo": "", "solicitado_em": agora,
        "iniciado_em": None, "concluido_em": None,
        "expira_em": _expira(agora, SEM_PROCESSADOR + _MARGEM),
    }
    with transaction.atomic():
        # Só o estado: o vídeo pronto (~1 MB) não precisa sair do banco aqui.
        linha = G.objects.select_for_update().filter(chave=chave).only("pk", "estado").first()
        if linha is None:
            try:
                with transaction.atomic():
                    G.objects.create(chave=chave, **campos)
            except IntegrityError:
                pass  # Outro pedido simultâneo criou a mesma chave: nada a fazer (FR-032).
        elif linha.estado == G.FALHOU:
            G.objects.filter(pk=linha.pk).update(**campos)


def estado_para(chave: str) -> str:
    _limpar_se_preciso()
    estado = G.objects.filter(chave=chave).values_list("estado", flat=True).first()
    return _EXIBIDO.get(estado, NENHUM)


def video_pronto(chave: str) -> bytes | None:
    _limpar_se_preciso()
    video = (
        G.objects.filter(chave=chave, estado=G.PRONTO).values_list("video", flat=True).first()
    )
    return bytes(video) if video is not None else None


def processar_proximo() -> bool:
    """Um pedido, o mais antigo. Devolve se houve trabalho."""
    limpar()
    agora = timezone.now()
    with transaction.atomic():
        linha = (
            G.objects.select_for_update(skip_locked=True)
            .filter(estado=G.SOLICITADO)
            .order_by("solicitado_em", "id")
            .first()
        )
        if linha is None:
            return False
        composicao = linha.composicao
        G.objects.filter(pk=linha.pk).update(
            estado=G.PROCESSANDO, iniciado_em=agora, expira_em=_expira(agora, travado() + _MARGEM)
        )
    try:
        video = renderizador.renderizar(composicao)
        resultado = {"estado": G.PRONTO, "video": video, "tamanho": len(video)}
    except renderizador.FalhaDeRenderizacao as falha:
        resultado = {"estado": G.FALHOU, "motivo": falha.motivo}
    except Exception:
        # O processador continua vivo; só o fato técnico vai para o log.
        logger.exception("video: erro inesperado na geração")
        resultado = {"estado": G.FALHOU, "motivo": "erro_inesperado"}
    fim = timezone.now()
    gravadas = G.objects.filter(pk=linha.pk, estado=G.PROCESSANDO, iniciado_em=agora).update(
        composicao=None, concluido_em=fim, expira_em=_expira(fim), **resultado
    )
    if not gravadas:
        logger.warning("video: resultado descartado")
    return True


def bloco(composicao: dict | None, sufixo: str) -> dict:
    """Contexto do bloco #video na página da 021 (contracts/rotas.md)."""
    if composicao is None:
        return {"disponivel": False}
    return {
        "disponivel": True,
        "estado": estado_para(chave_da_composicao(composicao)),
        "sufixo": sufixo,
        "textos": mensagens,
    }

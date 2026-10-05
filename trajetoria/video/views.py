"""Rotas do vídeo (Feature 022; contracts/rotas.md).

Camada fina. A composição é recalculada pela sessão a cada requisição, com a regra de acesso
e de nome da 021; a chave nunca vem do cliente nem sai para ele (FR-025). A entrega do MP4
trata um único intervalo `Range`, que o Safari do iOS exige para reproduzir (research R8).
"""

import re
from functools import wraps

from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from trajetoria.narrativa.composicao import ComposicaoImpossivel, chave_da_composicao
from trajetoria.narrativa.views import Redirecionar, composicao_da_sessao
from trajetoria.video import mensagens, operacoes, renderizador

_INTERVALO = re.compile(r"^bytes=(\d*)-(\d*)$")


def _da_sessao(quer_nome):
    def decorador(view):
        @wraps(view)
        def envolvida(request):
            try:
                composicao, sufixo = composicao_da_sessao(request, quer_nome(request))
            except Redirecionar as r:
                return redirect(r.destino)
            except ComposicaoImpossivel as erro:
                raise Http404 from erro
            return view(request, composicao, sufixo)

        return envolvida

    return decorador


def _nome_no_get(request) -> bool:
    return request.GET.get("nome") == "1"


@require_POST
@never_cache
@_da_sessao(lambda request: request.POST.get("nome") == "1")
def solicitar_video(request, composicao, sufixo):
    if renderizador.disponivel():
        operacoes.solicitar(composicao)
    resposta = HttpResponseRedirect(f"/minha-trajetoria/{sufixo}#video")
    resposta.status_code = 303
    return resposta


def _intervalo(cabecalho: str | None, total: int):
    """(início, fim) de um único intervalo; "invalido" → 416; None → arquivo inteiro."""
    achado = _INTERVALO.match(cabecalho.strip()) if cabecalho else None
    if achado is None or achado[1] == achado[2] == "":
        return None
    if achado[1] == "":
        sufixo = int(achado[2])
        if sufixo == 0:
            return "invalido"
        inicio, fim = max(0, total - sufixo), total - 1
    else:
        inicio = int(achado[1])
        fim = min(int(achado[2]), total - 1) if achado[2] else total - 1
    if inicio >= total or inicio > fim:
        return "invalido"
    return inicio, fim


@require_GET
@never_cache
@_da_sessao(_nome_no_get)
def video_mp4(request, composicao, sufixo):
    dados = operacoes.video_pronto(chave_da_composicao(composicao))
    if dados is None:
        raise Http404
    total = len(dados)
    intervalo = _intervalo(request.headers.get("Range"), total)
    if intervalo == "invalido":
        resposta = HttpResponse(status=416)
        resposta["Content-Range"] = f"bytes */{total}"
    elif intervalo is None:
        resposta = HttpResponse(dados, content_type="video/mp4")
    else:
        inicio, fim = intervalo
        resposta = HttpResponse(dados[inicio:fim + 1], content_type="video/mp4", status=206)
        resposta["Content-Range"] = f"bytes {inicio}-{fim}/{total}"
    resposta["Accept-Ranges"] = "bytes"
    resposta["Content-Disposition"] = f'inline; filename="{mensagens.ARQUIVO}"'
    return resposta


@require_GET
@never_cache
@_da_sessao(_nome_no_get)
def estado_video(request, composicao, sufixo):
    return JsonResponse({"estado": operacoes.estado_para(chave_da_composicao(composicao))})

"""Views do Portal (024; contracts/rotas.md). Cada entrada tem destino fixo: nenhum valor do
cliente decide para onde a pessoa vai (FR-006). Nada aqui grava, salvo a sessão que a
identificação da 018 estabelece (FR-029)."""

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.acesso.views import identificar
from trajetoria.declaracao.sessao import declaracoes_em_uso
from trajetoria.portal import mensagens
from trajetoria.portal.inicio import montar_inicio

TITULO_ENTRADA = "Confirme seus dados para entrar no Portal do Egresso"
_PRODUTO = {"produto": mensagens.PRODUTO, "produto_subtitulo": mensagens.PRODUTO_SUBTITULO}


def _ir(destino: str) -> HttpResponse:
    return HttpResponse(status=303, headers={"Location": destino})


def _destino_com_sujeito(request) -> str | None:
    if pessoa_em_uso(request) is not None:
        return "/inicio/"
    if declaracoes_em_uso(request) is not None:
        return "/declaracao/"
    return None


@require_GET
def entrada(request):
    """A raiz com o Portal ligado (FR-005): acesso espontâneo."""
    return _ir(_destino_com_sujeito(request) or "/entrar/")


@never_cache
@require_http_methods(["GET", "POST"])
def entrar(request):
    """Identificação pelo Portal: a mesma da 018, confirmada leva ao Início (FR-002, FR-003).
    Com sujeito, não há formulário: vai direto ao seu lugar (FR-004)."""
    if request.method == "GET" and (destino := _destino_com_sujeito(request)):
        return _ir(destino)
    return identificar(
        request,
        destino="/inicio/",
        acao="/entrar/",
        titulo=TITULO_ENTRADA,
        rotulo=mensagens.ROTULO_ENTRADA,
        continuar=None,
        aviso_de_envio=False,
        contexto=_PRODUTO,
    )


@never_cache
@require_GET
def inicio(request):
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        if declaracoes_em_uso(request) is not None:
            return _ir("/declaracao/")
        # 023 FR-001: com aviso quando a sessão acabou de expirar (FR-007).
        return _ir("/entrar/?aviso=sessao" if getattr(request, "_sessao_expirada", False)
                   else "/entrar/")
    contexto = montar_inicio(pessoa, timezone.localdate(), settings.TRAJETORIA_DEMONSTRACAO)
    contexto.update(_PRODUTO)
    return render(request, "portal/inicio.html", contexto)

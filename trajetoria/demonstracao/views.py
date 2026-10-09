"""Compatibilidade da entrada antiga e seleção do operador fictício, inalterada."""

from collections.abc import Callable

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from trajetoria.demonstracao.operador import (
    OPERADORES_FICTICIOS,
    esquecer_operador,
    operador_em_uso,
    operador_ficticio,
    usar_operador,
)
from trajetoria.governanca.consultas import vinculos_ativos


@require_GET
def entrada(request):
    return redirect("/acesso/", permanent=True)


# --- Operador fictício do editor (010) --------------------------------------------------------


# Destinos fechados depois da escolha (011 research R13): nunca um endereço vindo do cliente.
# O mapa é um ponto de extensão neutro (025 research R3): outro módulo pode registrar uma
# chave com um predicado de ativação, avaliado a cada pedido.
_DESTINOS: dict[str, tuple[str, Callable[[], bool]]] = {
    "acompanhamento": ("/acompanhamento/", lambda: True),
}


def registrar_destino(chave: str, endereco: str, ativo: Callable[[], bool] = lambda: True):
    """Acrescenta um destino fechado. `endereco` é fixo; `ativo()` decide, no pedido, se a
    chave é aceita. Chave inativa é tratada como desconhecida."""
    _DESTINOS[chave] = (endereco, ativo)


def _destino(chave: str | None) -> str | None:
    registro = _DESTINOS.get(chave)
    if registro is None or not registro[1]():
        return None
    return registro[0]


@require_GET
def operadores(request):
    em_uso = operador_em_uso(request)
    destino = request.GET.get("destino")
    lista = [
        {
            "identificador": operador.identificador,
            "rotulo": operador.rotulo,
            "atuacoes": [v.rotulo_de_atuacao for v in vinculos_ativos(operador.identificador)],
            "em_uso": operador.identificador == em_uso,
        }
        for operador in OPERADORES_FICTICIOS
    ]
    rotulo_em_uso = next((o["rotulo"] for o in lista if o["em_uso"]), None)
    return render(
        request,
        "demonstracao/operador.html",
        {
            "operadores": lista,
            "rotulo_em_uso": rotulo_em_uso,
            "destino": destino if _destino(destino) else None,
        },
    )


@require_POST
def escolher_operador(request):
    operador = operador_ficticio(request.POST.get("operador"))
    if operador is None:
        raise Http404
    # Destino fechado: editor (padrão) ou um destino registrado e ativo; nunca um endereço
    # vindo do cliente.
    resposta = redirect(_destino(request.POST.get("destino")) or "/editor/")
    usar_operador(resposta, operador)
    return resposta


@require_POST
def encerrar_operador(request):
    resposta = redirect("/demonstracao/operador/")
    esquecer_operador(resposta)
    return resposta

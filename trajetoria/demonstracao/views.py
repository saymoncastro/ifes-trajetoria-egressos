"""Telas do adaptador de demonstração: escolher e encerrar a Pessoa fictícia (008;
contracts/rotas.md, "Demonstração") e o operador fictício do editor (010;
contracts/demonstracao-operador.md) e do acompanhamento da coleta (011). Nada de domínio é
criado ou alterado (FR-009)."""

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from trajetoria.demonstracao.entrada import (
    esquecer,
    pessoa_de_demonstracao,
    pessoas_de_demonstracao,
    usar,
)
from trajetoria.demonstracao.operador import (
    OPERADORES_FICTICIOS,
    esquecer_operador,
    operador_em_uso,
    operador_ficticio,
    usar_operador,
)
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.interface.apresentacao import resumo_da_formacao


@require_GET
def entrada(request):
    pessoas = [
        {
            "pk": pessoa.pk,
            "nome": pessoa.nome or "Pessoa fictícia sem nome informado",
            "resumos": [r for c in pessoa.conclusoes.all() if (r := resumo_da_formacao(c))],
        }
        for pessoa in pessoas_de_demonstracao()
    ]
    return render(request, "demonstracao/entrada.html", {"pessoas": pessoas})


@require_POST
def escolher(request):
    pessoa = pessoa_de_demonstracao(request.POST.get("pessoa"))
    if pessoa is None:
        raise Http404
    resposta = redirect("/formacoes/")
    usar(resposta, pessoa)
    return resposta


@require_POST
def encerrar(request):
    resposta = redirect("/demonstracao/")
    esquecer(resposta)
    return resposta


# --- Operador fictício do editor (010) --------------------------------------------------------


# Destinos fechados depois da escolha (011 research R13): nunca um endereço vindo do cliente.
_DESTINOS = {"acompanhamento": "/acompanhamento/"}


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
            "destino": destino if destino in _DESTINOS else None,
        },
    )


@require_POST
def escolher_operador(request):
    operador = operador_ficticio(request.POST.get("operador"))
    if operador is None:
        raise Http404
    # Destino fechado: editor (padrão) ou acompanhamento; sem endereço vindo do cliente.
    resposta = redirect(_DESTINOS.get(request.POST.get("destino"), "/editor/"))
    usar_operador(resposta, operador)
    return resposta


@require_POST
def encerrar_operador(request):
    resposta = redirect("/demonstracao/operador/")
    esquecer_operador(resposta)
    return resposta

"""Telas do adaptador de demonstração: escolher e encerrar (contracts/rotas.md,
"Demonstração"). Nada de domínio é criado ou alterado (FR-009)."""

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from trajetoria.demonstracao.entrada import (
    esquecer,
    pessoa_de_demonstracao,
    pessoas_de_demonstracao,
    usar,
)
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

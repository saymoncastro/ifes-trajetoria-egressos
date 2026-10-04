"""Entrada administrativa de confirmação de dados, somente no modo fictício."""

from math import ceil

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from trajetoria.acesso import mensagens
from trajetoria.acesso.demonstracao import painel
from trajetoria.acesso.formularios import EntradaForm
from trajetoria.acesso.normalizacao import normalizar_cpf, normalizar_data
from trajetoria.acesso.sessao import encerrar, estabelecer
from trajetoria.acesso.transito import ChaveIndisponivel, selar_transito
from trajetoria.acesso.verificacao import (
    CausaIndisponibilidade,
    Confirmada,
    FormatoInvalido,
    Indisponivel,
    NaoConfirmada,
    verificar,
)
from trajetoria.demonstracao.base import base_somente_simulada


@never_cache
@require_http_methods(["GET", "POST"])
def entrada(request):
    if not base_somente_simulada():
        return render(
            request,
            "acesso/entrada.html",
            {"base_indevida": mensagens.BASE_INDEVIDA, "prefixo_titulo": "Erro: "},
            status=422,
        )
    form = EntradaForm(request.POST if request.method == "POST" else None)
    aviso = None
    status = 200
    espera = None
    selo = None
    if request.method == "POST":
        form.is_valid()
        agora = timezone.now()
        resultado = verificar(
            form.cleaned_data["cpf"],
            form.cleaned_data["data_nascimento"],
            request.META.get("REMOTE_ADDR", ""),
            agora=agora,
        )
        if isinstance(resultado, Confirmada):
            estabelecer(request, resultado, agora)
            return HttpResponse(status=303, headers={"Location": "/formacoes/"})
        if isinstance(resultado, NaoConfirmada):
            aviso = mensagens.NAO_CONFIRMADA
            try:
                selo = selar_transito(normalizar_cpf(form.cleaned_data["cpf"]),
                    normalizar_data(form.cleaned_data["data_nascimento"],timezone.localdate(agora)))
            except ChaveIndisponivel:
                pass
        elif isinstance(resultado, FormatoInvalido):
            for campo in resultado.campos:
                form.add_error(campo, mensagens.ERROS[campo])
                form.fields[campo].widget.attrs.update(
                    {"aria-invalid": "true", "aria-describedby": f"dica-{campo} erro-{campo}"}
                )
        elif isinstance(resultado, Indisponivel):
            if resultado.causa == CausaIndisponibilidade.LIMITE_TEMPORARIO:
                status = 429
                aviso = mensagens.ESPERA
                espera = max(1, ceil((resultado.espera_ate - agora).total_seconds()))
            else:
                status = 503
                aviso = mensagens.INDISPONIVEL
    resposta = render(
        request,
        "acesso/entrada.html",
        {
            "form": form,
            "selo_declaracao": selo,
            "painel": painel(),
            "aviso": aviso,
            "prefixo_titulo": "Erro: " if form.errors else "",
            "conferir": mensagens.CONFERIR if aviso == mensagens.NAO_CONFIRMADA else None,
        },
        status=status,
    )
    if espera is not None:
        resposta["Retry-After"] = str(espera)
    return resposta


@never_cache
@require_POST
def sair(request):
    encerrar(request)
    return HttpResponse(status=303, headers={"Location": "/acesso/"})

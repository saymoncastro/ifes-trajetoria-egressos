"""Telas exclusivamente administrativas da demonstração, sem persistência."""

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from trajetoria.acompanhamento.acesso import recusa
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.comunicacao.acesso import RecusaComunicacao, campanha_autorizada, comunicacao
from trajetoria.comunicacao.consultas import publico_atual
from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.operacoes import simular_comunicacao

BANNER = "Demonstração local com contatos fictícios; nenhum envio real."


def erro(request, recusa_):
    if recusa_.status == 404:
        raise Http404
    if recusa_.status == 403:
        return recusa(request, "Comunicação não autorizada para esta atuação ou escopo.")
    resposta = render(
        request,
        "comunicacao/resultado.html",
        {
            "banner": BANNER,
            "atuacao": request.atuacao,
            "erro": "Preparação recusada. Zero mensagens submetidas.",
        },
        status=recusa_.status,
    )
    resposta["Cache-Control"] = "no-store"
    return resposta


def contexto(request, campanha, agora):
    return {
        "banner": BANNER,
        "atuacao": request.atuacao,
        "campanha": campanha,
        "momento": timezone.localtime(agora),
        "trilha": [
            ("Campanhas", "/acompanhamento/"),
            (campanha.nome, f"/acompanhamento/campanhas/{campanha.pk}/"),
            ("Comunicação simulada", None),
        ],
        "situacao": estado(campanha, agora=agora).name.replace("_", " "),
        "pode_simular": estado(campanha, agora=agora) != EstadoCampanha.ENCERRADA,
    }


@comunicacao
@require_GET
def preparar(request, campanha):
    try:
        visivel = campanha_autorizada(campanha, request.comunicacao)
        agora = timezone.now()
        publico = publico_atual(visivel, request.comunicacao.escopo)
        representante = next((i for i in publico.itens if i.contato), None)
        convite = renderizar_convite(
            representante.pessoa.nome if representante else None,
            visivel.nome,
            settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO,
        )
    except RecusaComunicacao as exc:
        return erro(request, exc)
    except Exception:
        return erro(request, RecusaComunicacao("falha_preparacao", 422))
    resposta = render(
        request,
        "comunicacao/comunicacao.html",
        {
            **contexto(request, visivel, agora),
            "totais": publico.totais,
            "convite": convite,
            "destinatario": representante.contato if representante else None,
        },
    )
    resposta["Cache-Control"] = "no-store"
    return resposta


@comunicacao
@require_POST
def simular(request, campanha):
    try:
        visivel = campanha_autorizada(campanha, request.comunicacao)
        resultado = simular_comunicacao(campanha, request.comunicacao.operador)
    except RecusaComunicacao as exc:
        if exc.status == 409:
            resposta = render(
                request,
                "comunicacao/resultado.html",
                {
                    **contexto(request, visivel, timezone.now()),
                    "erro": "Campanha encerrada. Simulação recusada; zero mensagens submetidas.",
                },
                status=409,
            )
            resposta["Cache-Control"] = "no-store"
            return resposta
        return erro(request, exc)
    except Exception:
        resposta = render(
            request,
            "comunicacao/resultado.html",
            {
                "banner": BANNER,
                "atuacao": request.atuacao,
                "erro": "Falha inesperada. Não foi possível confirmar o resultado do transporte.",
            },
            status=500,
        )
        resposta["Cache-Control"] = "no-store"
        return resposta
    # Coleção individual nunca entra no contexto do template.
    resposta = render(
        request,
        "comunicacao/resultado.html",
        {
            **contexto(request, visivel, resultado.momento),
            "totais": resultado.totais,
            "interrompida": resultado.interrompida,
        },
        status=500 if resultado.interrompida else 200,
    )
    resposta["Cache-Control"] = "no-store"
    return resposta

"""Telas exclusivamente administrativas da demonstração, sem persistência."""

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import recusa
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.comunicacao.acesso import RecusaComunicacao, campanha_autorizada, comunicacao
from trajetoria.comunicacao.consultas import publico_atual
from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.operacoes import simular_comunicacao

BANNER = "Demonstração local com contatos fictícios; nenhum envio real."
RECUSAS = {
    "conteudo_inseguro": (
        "Preparação recusada: o nome da Campanha ou de uma Pessoa contém link ou marcação "
        "não permitidos no convite. Zero mensagens submetidas."
    ),
}


def pagina(request, template, dados, status=200):
    """Toda resposta da 016 é transitória: nunca guardada em cache."""
    resposta = render(
        request,
        template,
        {"banner": BANNER, "atuacao": request.atuacao, **dados},
        status=status,
    )
    resposta["Cache-Control"] = "no-store"
    return resposta


def erro(request, recusa_):
    if recusa_.status == 404:
        raise Http404
    if recusa_.status == 403:
        return recusa(request, "Comunicação não autorizada para esta atuação ou escopo.")
    texto = RECUSAS.get(recusa_.categoria, "Preparação recusada. Zero mensagens submetidas.")
    return pagina(request, "comunicacao/resultado.html", {"erro": texto}, recusa_.status)


def contexto(campanha, agora):
    situacao = estado(campanha, agora=agora)
    return {
        "campanha": campanha,
        "momento": timezone.localtime(agora),
        "trilha": [
            ("Campanhas", "/acompanhamento/"),
            (campanha.nome, f"/acompanhamento/campanhas/{campanha.pk}/"),
            ("Comunicação simulada", None),
        ],
        "situacao": ap.situacao(situacao),
        "pode_simular": situacao != EstadoCampanha.ENCERRADA,
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
    return pagina(
        request,
        "comunicacao/comunicacao.html",
        {
            **contexto(visivel, agora),
            "totais": publico.totais,
            "convite": convite,
            "destinatario": representante.contato if representante else None,
        },
    )


@comunicacao
@require_POST
def simular(request, campanha):
    # A operação autoriza operador e Campanha por conta própria (R2); a view não repete.
    try:
        resultado = simular_comunicacao(campanha, request.comunicacao.operador)
    except RecusaComunicacao as exc:
        if exc.status != 409:
            return erro(request, exc)
        visivel = campanha_autorizada(campanha, request.comunicacao)
        return pagina(
            request,
            "comunicacao/resultado.html",
            {
                **contexto(visivel, timezone.now()),
                "erro": "Campanha encerrada. Simulação recusada; zero mensagens submetidas.",
            },
            409,
        )
    except Exception:
        return pagina(
            request,
            "comunicacao/resultado.html",
            {"erro": "Falha inesperada. Não foi possível confirmar o resultado do transporte."},
            500,
        )
    # Coleção individual nunca entra no contexto do template.
    return pagina(
        request,
        "comunicacao/resultado.html",
        {
            **contexto(resultado.campanha, resultado.momento),
            "totais": resultado.totais,
            "interrompida": resultado.interrompida,
        },
        500 if resultado.interrompida else 200,
    )

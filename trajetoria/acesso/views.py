"""Entrada administrativa de confirmação de dados, somente no modo fictício."""

from math import ceil

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from trajetoria.acesso import mensagens, pendente
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

TITULO = "Confirme seus dados para acessar a pesquisa"
CONTINUAR = ("Continuar para suas formações", "/formacoes/")


@never_cache
@require_http_methods(["GET", "POST"])
def entrada(request):
    """Entrada do convite (018; 016 FR-021; 018 FR-053): confirmada, segue para a escolha de
    formações. Outras entradas usam a mesma identificação com destino fixo próprio (024)."""
    return identificar(request, destino="/formacoes/", acao="/acesso/")


def identificar(
    request,
    *,
    destino: str,
    acao: str,
    titulo: str = TITULO,
    rotulo: str | None = None,
    continuar: tuple[str, str] | None = CONTINUAR,
    aviso_de_envio: bool = True,
    contexto: dict | None = None,
):
    """A identificação da 018 com destino fixo por quem chama (024 research R3; FR-006):
    nenhum valor do cliente decide para onde a Pessoa confirmada vai. `acao` é o endereço do
    formulário; `aviso_de_envio=False` suprime a frase do envio guardado, que só é verdadeira
    no caminho que leva à escolha de formações (024 FR-007). Este módulo não conhece quem o
    chama; `contexto` só acrescenta apresentação (por exemplo, o nome do produto)."""
    # Marca antes de qualquer leitura de sessão (faixa, navegação): um POST sem confirmação
    # não pode renovar nem descartar a sessão anterior, qualquer que seja o endereço (018).
    request._post_de_entrada = request.method == "POST"
    if not base_somente_simulada():
        return render(
            request,
            "acesso/entrada.html",
            {"base_indevida": mensagens.BASE_INDEVIDA, "prefixo_titulo": "Erro: ",
             "titulo": titulo, "rotulo": rotulo, **(contexto or {})},
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
            return HttpResponse(status=303, headers={"Location": destino})
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
            "chegada": _chegada(request, aviso_de_envio) if request.method == "GET" else (),
            "acao": acao,
            "titulo": titulo,
            "rotulo": rotulo,
            "continuar": continuar,
            **(contexto or {}),
            # 023 FR-022: depois de uma tentativa que falhou, nada de "Continuar para suas
            # formações" de uma sessão anterior.
            "tentativa_falhou": request.method == "POST",
            "passos": (mensagens.PASSO_CONFERIR, mensagens.PASSO_INFORMAR),
            "form": form,
            "selo_declaracao": selo,
            "painel": painel(),
            "aviso": aviso,
            "prefixo_titulo": "Erro: " if form.errors else "",
            "conferir": aviso == mensagens.NAO_CONFIRMADA,
        },
        status=status,
    )
    if espera is not None:
        resposta["Retry-After"] = str(espera)
    return resposta


def _chegada(request, aviso_de_envio=True):
    """Aviso de chegada por código de lista fechada (023 FR-001, FR-003, FR-030). A frase do
    envio guardado só aparece se o envio pendente existe e vale (regra de verdade)."""
    codigo = request.GET.get("aviso")
    if codigo == "sessao":
        frases = [mensagens.SESSAO_ENCERRADA]
        if aviso_de_envio and pendente.ler(request) is not None:
            frases.append(mensagens.ENVIO_GUARDADO)
        return tuple(frases)
    if codigo == "selo":
        return (mensagens.SELO_VENCIDO,)
    return ()


@never_cache
@require_POST
def sair(request):
    encerrar(request)
    return HttpResponse(status=303, headers={"Location": "/acesso/"})

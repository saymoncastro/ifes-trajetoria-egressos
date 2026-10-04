"""Autorização do acompanhamento da coleta (Feature 011; research R12; contracts/rotas.md).

As views de leitura usam `@acompanhamento`; a escrita da 017 usa `@gestao`.
DP-402 aberta: interpretação C1 restrita à demonstração. Ambos são os mais externos.
A cada requisição, **antes** de
qualquer consulta de Campanha, Conclusão ou Participação:

1. identificação e vínculos ativos: `vinculos_do_operador_em_uso`, o mesmo ponto único do
   editor (adaptador de demonstração da 010; DP-1001). Sem operador → escolha de operador
   fictício com destino fechado `acompanhamento`;
2. `pode_acompanhar_coleta` (CPAEG ou CSAEG ativo); falso → recusa;
3. `escopo_de_acompanhamento`: institucional ou as unidades dos vínculos CSAEG.

A view recebe `request.escopo` e `request.atuacao`. Nunca consulta privilégio técnico nem o
modo de demonstração (010 FR-005, FR-067): fora do modo, o middleware da 008 já respondeu 404.
"""

from dataclasses import dataclass
from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.demonstracao.operador import vinculos_do_operador_em_uso
from trajetoria.governanca.regras import (
    escopo_de_acompanhamento,
    pode_acompanhar_coleta,
    pode_consultar_rascunho,
    pode_gerir_campanha,
    pode_validar_formacao,
)

ESCOLHA_DE_OPERADOR = "/demonstracao/operador/?destino=acompanhamento"


@dataclass(frozen=True)
class Atuacao:
    """O que as páginas sabem do operador: rótulos das atuações e se consulta rascunhos (010).
    Nunca o identificador."""

    rotulos: tuple[str, ...]
    consultar_rascunho: bool
    gerir_campanha: bool = False
    validar_formacao: bool = False


def recusa(request, texto: str):
    """Página 403 em linguagem operacional, sem nenhum dado de Campanha."""
    return render(
        request,
        "acompanhamento/recusa.html",
        {
            "banner": ap.BANNER,
            "atuacao": getattr(request, "atuacao", None),
            "titulo": ap.RECUSA_TITULO,
            "texto": texto,
        },
        status=403,
    )


def acompanhamento(view):
    @wraps(view)
    def envolvida(request, *args, **kwargs):
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect(ESCOLHA_DE_OPERADOR)
        if not pode_acompanhar_coleta(vinculos):
            return recusa(request, ap.RECUSA_SEM_ATUACAO)
        request.vinculos = vinculos
        request.escopo = escopo_de_acompanhamento(vinculos)
        request.atuacao = Atuacao(
            rotulos=tuple(v.rotulo_de_atuacao for v in vinculos),
            consultar_rascunho=pode_consultar_rascunho(vinculos),
            gerir_campanha=pode_gerir_campanha(vinculos),
            validar_formacao=pode_validar_formacao(vinculos),
        )
        return view(request, *args, **kwargs)

    envolvida.acompanhamento = True
    return envolvida


def gestao(view):
    """Barreira externa da 017: demonstração e CPAEG, relidos a cada pedido.

    Interpretação C1, restrita à demonstração; DP-402 permanece aberta.
    """

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise Http404
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect(ESCOLHA_DE_OPERADOR)
        if not pode_gerir_campanha(vinculos):
            return recusa(request, "A gestão de Campanhas não está disponível para esta atuação.")
        request.atuacao = Atuacao(
            tuple(v.rotulo_de_atuacao for v in vinculos),
            pode_consultar_rascunho(vinculos),
            gerir_campanha=True,
        )
        return view(request, *args, **kwargs)

    envolvida.gestao = True
    return envolvida

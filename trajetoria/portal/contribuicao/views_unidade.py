"""Telas da unidade que recebe (026 US3; FR-009, FR-010; plan R12).

Padrão da curadoria da 025: barreira relida a cada pedido, escrita só pelas operações,
confirmação explícita, estado que mudou vira conflito (409) e registro fora do escopo é 404
(não revela que existe). Sem Django admin. O contato com o egresso acontece fora do sistema;
aqui só se registra o marco "contato feito" (D-2601).
"""

from functools import wraps

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import Atuacao, recusa
from trajetoria.demonstracao.operador import operador_em_uso, vinculos_do_operador_em_uso
from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.consultas import ativas_do_escopo, descrever
from trajetoria.portal.contribuicao.formularios import formacao_em_texto
from trajetoria.portal.contribuicao.governanca import (
    escopo_de_recebimento,
    pode_receber_contribuicoes,
    recebe,
)
from trajetoria.portal.contribuicao.planilha import csv_da_unidade
from trajetoria.portal.contribuicao.regras import ManifestacaoRejeitada, Motivo
from trajetoria.portal.models import Forma, Manifestacao

LISTA = "/curadoria/contribuicoes/"
DESTINO = "contribuicoes"  # destino registrado da escolha de operador (portal/apps.py)
ESCOLHA_DE_OPERADOR = f"/demonstracao/operador/?destino={DESTINO}"


def unidade(view):
    """Demonstração, operador e competência, relidos a cada pedido. O identificador do
    operador nunca vai ao template."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise Http404
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect(ESCOLHA_DE_OPERADOR)
        if not pode_receber_contribuicoes(vinculos):
            return recusa(request, m.UNIDADE_RECUSA, destino_operador=DESTINO)
        request.escopo = escopo_de_recebimento(vinculos)
        request.atuacao = Atuacao(tuple(v.rotulo_de_atuacao for v in vinculos), False)
        return view(request, *args, **kwargs)

    return envolvida


def _pagina(request, template, *, titulo, status=200, **contexto):
    trilha = [(m.UNIDADE_TITULO, None)] if template == "lista" else [
        (m.UNIDADE_TITULO, LISTA), (titulo, None)
    ]
    return render(
        request,
        f"portal/contribuicao/unidade/{template}.html",
        {"banner": ap.BANNER, "atuacao": request.atuacao, "trilha": trilha, "titulo": titulo,
         "destino_operador": DESTINO, "m": m, **contexto},
        status=status,
    )


def _data(momento) -> str:
    return timezone.localtime(momento).strftime("%d/%m/%Y")


def _situacao(manifestacao) -> str:
    if manifestacao.contato_registrado_em is None:
        return m.SEM_CONTATO
    return m.CONTATO_EM.format(data=_data(manifestacao.contato_registrado_em))


@unidade
@require_GET
@never_cache
def lista(request):
    linhas = [
        {
            "manifestacao": d.manifestacao,
            "recebida_em": _data(d.manifestacao.registrada_em),
            "nome": d.nome or m.SEM_NOME,
            "forma": Forma(d.manifestacao.forma).label,
            "formacao": formacao_em_texto(d.conclusao),
            "situacao": _situacao(d.manifestacao),
            "pode_registrar": d.manifestacao.contato_registrado_em is None,
        }
        for d in descrever(ativas_do_escopo(request.escopo), com_nome=True)
    ]
    aviso = m.CONTATO_AVISO if request.GET.get("aviso") == "contato" else None
    return _pagina(request, "lista", titulo=m.UNIDADE_TITULO, linhas=linhas, aviso=aviso)


@unidade
@require_GET
@never_cache
def exportar(request):
    """FR-010: só as ativas do escopo; sem CPF nem data de nascimento."""
    conteudo = csv_da_unidade(descrever(ativas_do_escopo(request.escopo), com_nome=True))
    return HttpResponse(conteudo, content_type="text/csv; charset=utf-8", headers={
        "Content-Disposition": 'attachment; filename="contribuicoes-recebidas.csv"',
    })


def _conflito(request):
    return _pagina(request, "conflito", titulo=m.CONFLITO_TITULO, status=409)


@unidade
@require_http_methods(["GET", "POST"])
@never_cache
def contato(request, pk):
    """Confirmação e registro do marco "contato feito" (FR-005a), uma única vez."""
    manifestacao = Manifestacao.objects.filter(pk=pk).first()
    if manifestacao is None or not recebe(request.escopo, manifestacao.unidade):
        raise Http404
    if not manifestacao.ativa or manifestacao.contato_registrado_em is not None:
        return _conflito(request)
    if request.method == "POST":
        try:
            operacoes.registrar_contato(pk, operador=operador_em_uso(request),
                                        escopo=request.escopo, agora=timezone.now())
        except ManifestacaoRejeitada as erro:
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            return _conflito(request)
        return redirect(f"{LISTA}?aviso=contato")
    (d,) = descrever([manifestacao], com_nome=True)
    return _pagina(
        request, "contato", titulo=m.REGISTRAR_CONTATO,
        subtitulo=f"{d.nome or m.SEM_NOME} · {Forma(manifestacao.forma).label}",
        texto=m.CONTATO_TEXTO.format(destino=m.destino(manifestacao.unidade)),
    )

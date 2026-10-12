"""Telas de quem descobre e participa (031 US3, US5, US6; contracts/rotas.md).

A página do encontro decide o que mostrar só por `regras.o_que_ver` e o link só por
`regras.mostra_link` (FR-021, FR-024a; research R10): o link nunca entra no contexto de quem
não pode vê-lo. Sem sessão, a página é neutra (FR-022). As únicas escritas são as de
`operacoes`: confirmar e cancelar a confirmação. Destinos fixos (024 FR-006).
"""

from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal.destinos import sem_pessoa
from trajetoria.portal.encontros import consultas, operacoes, regras
from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.apresentacao import (
    apresentar,
    confirmacoes,
    data,
    hora,
    quem_analisa,
    quem_moderou,
)
from trajetoria.portal.encontros.regras import EncontroRejeitado, Motivo, Nivel, Quem, Situacao
from trajetoria.portal.models import Encontro

ENCONTROS = "/encontros/"


def _ir(destino: str) -> HttpResponse:
    return HttpResponse(status=303, headers={"Location": destino})


def egresso(view):
    """Pessoa identificada pela 018 e com ao menos uma Conclusão (FR-001, FR-020)."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        pessoa = pessoa_em_uso(request)
        if pessoa is None:
            return sem_pessoa(request)
        if not elegivel(pessoa):
            raise Http404
        return view(request, pessoa, *args, **kwargs)

    return envolvida


def _encontro_ou_404(pk) -> Encontro:
    encontro = Encontro.objects.filter(pk=pk).first()
    if encontro is None:
        raise Http404
    return encontro


@never_cache
@require_GET
@egresso
def encontros(request, pessoa):
    """Dois grupos: propostos por egressos, pela data; eventos do Ifes, na ordem da 025
    (FR-013). Nenhum ranking; consultar não grava."""
    agora = timezone.now()
    propostos = [
        {**apresentar(i.encontro), "explicacao": i.explicacao}
        for i in consultas.pertinentes(pessoa, agora)
    ]
    eventos = consultas.eventos_do_ifes(pessoa, agora)
    return render(request, "portal/encontros/lista.html", {
        "m": m, "propostos": propostos, "eventos": eventos,
    })


def _pagina(request, template, contexto, status=200):
    return render(request, f"portal/encontros/{template}.html", {"m": m, **contexto},
                  status=status)


@never_cache
@require_GET
def pagina(request, pk):
    """A página do encontro, por situação e por quem vê (FR-024a)."""
    encontro = _encontro_ou_404(pk)
    pessoa = pessoa_em_uso(request)
    agora = timezone.now()
    quem = consultas.quem_e(pessoa, encontro,
                            com_conclusao=pessoa is not None and elegivel(pessoa))
    atual = regras.situacao(encontro, agora)
    nivel = regras.o_que_ver(atual, quem)
    if nivel is Nivel.NEUTRA:
        return _pagina(request, "neutra", {"texto": m.NEUTRA_TEXTO, "com_acao": True})
    if nivel is Nivel.SO_PARA_EGRESSOS:
        return _pagina(request, "neutra", {"texto": m.SO_PARA_EGRESSOS, "com_acao": False})
    if nivel is Nivel.INDISPONIVEL:
        return _pagina(request, "situacao", {
            "titulo": m.INDISPONIVEL_TITULO, "texto": m.INDISPONIVEL_TEXTO,
        }, status=404)
    if nivel is Nivel.SITUACAO:
        return _pagina(request, "situacao", _so_a_situacao(encontro, atual))
    mostrar_link = regras.mostra_link(atual, quem)
    contexto = {
        "e": apresentar(encontro, mostrar_link=mostrar_link),
        "quem": quem.value, "situacao": atual.value,
        "aviso": m.AVISOS.get(request.GET.get("aviso")),
        "endereco": request.build_absolute_uri(f"{ENCONTROS}{encontro.pk}/"),
    }
    if quem is Quem.ORGANIZADOR:
        contexto |= _do_organizador(encontro, atual, agora)
    else:
        contexto |= _de_quem_participa(pessoa, encontro, atual, quem, agora)
    return _pagina(request, "pagina", contexto)


def _so_a_situacao(encontro, atual) -> dict:
    if atual is Situacao.RETIRADO:
        return {"titulo": m.RETIRADO, "texto": m.RETIRADO_TEXTO}
    if atual is Situacao.CANCELADO:
        return {"titulo": m.CANCELADO,
                "texto": m.CANCELADO_TEXTO.format(data=data(encontro.cancelado_em))}
    return {"titulo": m.ENCERRADO,
            "texto": m.ENCERRADO_TEXTO.format(data=data(encontro.termino),
                                              hora=hora(encontro.termino))}


def _situacao_em_texto(encontro, atual) -> str:
    if atual is Situacao.EM_ANALISE:
        return m.EM_ANALISE.format(quem=quem_analisa(encontro), data=data(encontro.enviado_em))
    if atual is Situacao.NAO_ANALISADO:
        return m.NAO_ANALISADO
    if atual is Situacao.PUBLICADO:
        return m.PUBLICADO.format(data=data(encontro.publicado_em),
                                  quem=quem_moderou(encontro.publicado_por_escopo))
    if atual is Situacao.RECUSADO:
        return m.RECUSADO.format(quem=quem_analisa(encontro), data=data(encontro.recusado_em))
    if atual is Situacao.RETIRADO:
        return m.RETIRADO
    if atual is Situacao.CANCELADO:
        return m.CANCELADO
    return m.ENCERRADO


def _do_organizador(encontro, atual, agora) -> dict:
    pode_cancelar = (atual in (Situacao.EM_ANALISE, Situacao.PUBLICADO)
                     and agora < encontro.inicio)
    contexto = {
        "situacao_texto": _situacao_em_texto(encontro, atual),
        "pode_cancelar": pode_cancelar,
        "em_analise": atual is Situacao.EM_ANALISE,
    }
    if encontro.publicado_em is not None:
        contexto["contagem"] = confirmacoes(consultas.quantas_confirmaram(encontro))
    if encontro.motivo:
        contexto["motivo"] = encontro.get_motivo_display()
        contexto["complemento"] = encontro.complemento
    return contexto


def _de_quem_participa(pessoa, encontro, atual, quem, agora) -> dict:
    confirmacao = consultas.confirmacao_ativa(pessoa, encontro)
    explicacao = consultas.explicacao_para(pessoa, encontro)
    return {
        "explicacao": explicacao,
        "fora_do_publico": explicacao is None,
        "confirmacao": confirmacao,
        "confirmada_em_texto": (m.CONFIRMADO_EM.format(data=data(confirmacao.confirmada_em))
                                if confirmacao else ""),
        "aceita": regras.aceita_confirmacao(encontro, agora),
        "ciencia": m.CIENCIA,
        "ciencia_versao": m.CIENCIA_VERSAO.format(versao=m.VERSAO_DA_CIENCIA),
        "versao": m.VERSAO_DA_CIENCIA,
        "encerrado": atual is Situacao.ENCERRADO,
        "cancelado": atual is Situacao.CANCELADO,
    }


def _conflito(request):
    return _pagina(request, "conflito", {"titulo": m.CONFLITO_TITULO, "texto": m.CONFLITO},
                   status=409)


@never_cache
@require_POST
@egresso
def participar(request, pessoa, pk):
    """"Vou participar" (FR-020). Volta à página, que passa a mostrar o link."""
    encontro = _encontro_ou_404(pk)
    try:
        operacoes.confirmar(pessoa, encontro.pk, versao_da_ciencia=request.POST.get("versao", ""),
                            agora=timezone.now())
    except EncontroRejeitado as erro:
        if Motivo.FORA_DO_ESCOPO in erro.motivos:
            raise Http404 from None
        return _conflito(request)
    return _ir(f"{ENCONTROS}{encontro.pk}/?aviso=confirmado")


@never_cache
@require_http_methods(["GET", "POST"])
@egresso
def cancelar_participacao(request, pessoa, pk):
    """Confirmação e cancelamento da própria participação, até o início (FR-023)."""
    encontro = _encontro_ou_404(pk)
    agora = timezone.now()
    if (consultas.confirmacao_ativa(pessoa, encontro) is None
            or not regras.aceita_confirmacao(encontro, agora)):
        return _ir(f"{ENCONTROS}{encontro.pk}/")
    if request.method == "POST":
        try:
            operacoes.cancelar_participacao(pessoa, encontro.pk, agora=agora)
        except EncontroRejeitado:
            return _conflito(request)
        return _ir(f"{ENCONTROS}{encontro.pk}/?aviso=participacao_cancelada")
    return _pagina(request, "cancelar_participacao", {"e": apresentar(encontro)})

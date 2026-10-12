"""Telas de quem propõe (031 US1, US4; contracts/rotas.md; protótipos o1 a o10).

Proposta em duas telas, sem estado em sessão: formulário → "Confira e envie" (campos
reenviados e revalidados) → página do encontro "Em análise". Erro volta ao formulário com o
que a pessoa digitou (FR-007). Escritas só por `operacoes`: propor e cancelar.
"""

from types import SimpleNamespace

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.portal.barreiras import egresso
from trajetoria.portal.destinos import ir
from trajetoria.portal.encontros import consultas, operacoes, regras
from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.apresentacao import (
    apresentar,
    confirmacoes,
    situacao_em_texto,
)
from trajetoria.portal.encontros.formularios import (
    ANCORAS,
    erros_das_violacoes,
    formacao_em_texto,
    ler,
    opcoes,
)
from trajetoria.portal.encontros.regras import EncontroRejeitado, Motivo, Situacao
from trajetoria.portal.encontros.views_egresso import ENCONTROS
from trajetoria.portal.oportunidades.consultas import opcoes_de_publico

SEUS = "/encontros/seus/"




def _conclusoes(pessoa) -> list:
    return list(pessoa.conclusoes.all())


def _ativos(pessoa, agora) -> int:
    return sum(regras.ativo(e, agora) for e in consultas.do_organizador(pessoa))


def _formulario(request, pessoa, campos=None, erros=None, status=200):
    erros = erros or {}
    agora = timezone.now()
    return render(request, "portal/encontros/propor.html", {
        "m": m, "erros": erros,
        "resumo_erros": [{"ancora": ANCORAS.get(c, c), "texto": t} for c, t in erros.items()],
        **opcoes(campos, _conclusoes(pessoa), opcoes_de_publico(), agora),
    }, status=status)


def _confira(request, lida, conclusoes, erros=None, status=200):
    p = lida.proposta
    origem = next(c for c in conclusoes if c.pk == p.conclusao_origem_id)
    previa = SimpleNamespace(  # o mesmo objeto que a apresentação usa, sem gravar nada
        pk=None, titulo=p.titulo, descricao=p.descricao, inicio=p.inicio, termino=p.termino,
        nome_apresentacao=p.nome_apresentacao, origem_curso=origem.curso or "",
        origem_unidade=origem.unidade or "", origem_ano=origem.ano_conclusao,
        publico_unidades=p.publico_unidades, publico_niveis=p.publico_niveis,
        publico_cursos=p.publico_cursos, publicado_em=None, publicado_por_escopo=None,
        tem_publico=any(v is not None for v in (p.publico_unidades, p.publico_niveis,
                                                p.publico_cursos)),
    )
    e = apresentar(previa)
    unidade_unica = p.publico_unidades is not None and len(p.publico_unidades) == 1
    return render(request, "portal/encontros/confira.html", {
        "m": m, "e": e, "campos": lida.campos, "erros": erros or {},
        "quem_analisa": (m.QUEM_ANALISA_UNIDADE.format(unidade=p.publico_unidades[0])
                         if unidade_unica else m.QUEM_ANALISA_CPAEG),
        "link": p.link, "origem": formacao_em_texto(origem),
        "termo": m.TERMO, "versao": m.VERSAO_DO_TERMO,
        "termo_versao": m.TERMO_VERSAO.format(versao=m.VERSAO_DO_TERMO),
    }, status=status)


@never_cache
@require_http_methods(["GET", "POST"])
@egresso
def propor(request, pessoa):
    """Formulário (FR-002 a FR-005, FR-007). POST válido mostra "Confira e envie"."""
    agora = timezone.now()
    if request.method == "GET":
        if _ativos(pessoa, agora) >= regras.LIMITE_DE_ATIVOS:
            return _formulario(request, pessoa, erros={"limite": m.ERROS["limite"]})
        return _formulario(request, pessoa)
    conclusoes = _conclusoes(pessoa)
    lida, erros = ler(request.POST, conclusoes, opcoes_de_publico(), agora)
    if "voltar" in request.POST:
        return _formulario(request, pessoa, lida.campos)
    if not erros and _ativos(pessoa, agora) >= regras.LIMITE_DE_ATIVOS:
        erros["limite"] = m.ERROS["limite"]
    if erros:
        return _formulario(request, pessoa, lida.campos, erros, status=422)
    return _confira(request, lida, conclusoes)


@never_cache
@require_POST
@egresso
def enviar(request, pessoa):
    """Grava (FR-006): a proposta revalidada, com a versão do termo lida."""
    agora = timezone.now()
    conclusoes = _conclusoes(pessoa)
    lida, erros = ler(request.POST, conclusoes, opcoes_de_publico(), agora)
    if erros:
        return _formulario(request, pessoa, lida.campos, erros, status=422)
    try:
        encontro = operacoes.propor(pessoa, lida.proposta,
                                    versao_do_termo=request.POST.get("versao", ""), agora=agora)
    except EncontroRejeitado as erro:
        if Motivo.TERMO in erro.motivos:
            return _confira(request, lida, conclusoes, erros={"termo": m.ERROS["termo"]},
                            status=409)
        if Motivo.LIMITE in erro.motivos:
            return _formulario(request, pessoa, lida.campos,
                               {"limite": m.ERROS["limite"]}, status=409)
        return _formulario(request, pessoa, lida.campos,
                           erros_das_violacoes(erro.violacoes, agora), status=422)
    return ir(f"{ENCONTROS}{encontro.pk}/?aviso=enviado")


def _linha(encontro, agora) -> dict:
    texto = situacao_em_texto(encontro, regras.situacao(encontro, agora))
    linha = {"e": apresentar(encontro), "situacao": texto}
    if encontro.publicado_em is not None:
        linha["contagem"] = confirmacoes(encontro.n_confirmacoes)
    if encontro.motivo:
        linha["motivo"] = encontro.get_motivo_display()
    return linha


@never_cache
@require_GET
@egresso
def seus(request, pessoa):
    """Seus encontros, com a quantidade de confirmações e nunca quem (FR-025)."""
    agora = timezone.now()
    return render(request, "portal/encontros/seus.html", {
        "m": m, "linhas": [_linha(e, agora) for e in consultas.do_organizador(pessoa)],
        "aviso": m.AVISOS.get(request.GET.get("aviso")),
    })


@never_cache
@require_http_methods(["GET", "POST"])
@egresso
def cancelar(request, pessoa, pk):
    """Confirmação e cancelamento pelo organizador, até o início (FR-009)."""
    encontro = consultas.do_organizador(pessoa).filter(pk=pk).first()
    if encontro is None:
        raise Http404
    agora = timezone.now()
    atual = regras.situacao(encontro, agora)
    if atual not in (Situacao.EM_ANALISE, Situacao.PUBLICADO) or agora >= encontro.inicio:
        return ir(f"{ENCONTROS}{pk}/")
    if request.method == "POST":
        try:
            operacoes.cancelar(pessoa, pk, agora=agora)
        except EncontroRejeitado:
            return render(request, "portal/encontros/conflito.html",
                          {"m": m, "titulo": m.CONFLITO_TITULO, "texto": m.CONFLITO}, status=409)
        return ir(f"{SEUS}?aviso=cancelado")
    return render(request, "portal/encontros/cancelar.html", {"m": m, "e": apresentar(encontro)})

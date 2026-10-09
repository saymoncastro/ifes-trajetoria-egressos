"""Telas do egresso (026 US1, US2; plan, "Rotas"; R11).

Três telas até o envio, sem JavaScript e sem estado em sessão: escolha → confirmação com o
texto de ciência e o e-mail → detalhe da manifestação gravada. Destinos fixos; nenhum valor do
cliente decide para onde a pessoa vai (024 FR-006). Sem Conclusão, a contribuição não existe
(404; FR-011). Manifestação de outra Pessoa também é 404. As únicas escritas são as de
`operacoes`: registrar e retirar.
"""

from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.declaracao.sessao import declaracoes_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.consultas import (
    conclusoes_de_referencia,
    da_pessoa,
    da_pessoa_ou_none,
    descrever,
)
from trajetoria.portal.contribuicao.formularios import (
    Escolha,
    formacao_em_texto,
    ler_escolha,
    opcoes,
)
from trajetoria.portal.contribuicao.regras import (
    ManifestacaoRejeitada,
    Motivo,
    Situacao,
    situacao,
)
from trajetoria.portal.models import Forma

LISTA = "/contribuicoes/"
_ANCORAS = {
    "forma": "campo-forma", "formacao": "campo-formacao", "mensagem": "mensagem",
    "email": "email", "ciencia": "o-que-acontece",
}


def _ir(destino: str) -> HttpResponse:
    return HttpResponse(status=303, headers={"Location": destino})


def egresso(view):
    """Pessoa identificada pela 018 e com ao menos uma Conclusão Acadêmica (D-2603)."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        pessoa = pessoa_em_uso(request)
        if pessoa is None:
            if declaracoes_em_uso(request) is not None:
                return _ir("/declaracao/")
            return _ir("/entrar/?aviso=sessao" if getattr(request, "_sessao_expirada", False)
                       else "/entrar/")
        if not elegivel(pessoa):
            raise Http404
        return view(request, pessoa, *args, **kwargs)

    return envolvida


def _data(momento) -> str:
    return timezone.localtime(momento).strftime("%d/%m/%Y")


def _resumo_de_erros(erros: dict) -> list[dict]:
    return [{"ancora": _ANCORAS[campo], "texto": texto} for campo, texto in erros.items()]


def _escolha(request, escolha: Escolha | None, conclusoes, *, erros=None, status=200):
    erros = erros or {}
    return render(request, "portal/contribuicao/escolha.html", {
        "m": m, "erros": erros, "resumo_erros": _resumo_de_erros(erros),
        "mensagem": escolha.mensagem if escolha else "", **opcoes(escolha, conclusoes),
    }, status=status)


def _resumo(forma: str, conclusao, unidade: str, mensagem: str) -> list[tuple[str, str]]:
    linhas = [
        (m.RESUMO_FORMA, Forma(forma).label),
        (m.RESUMO_FORMACAO, formacao_em_texto(conclusao)),
        (m.RESUMO_DESTINO, m.destino(unidade, inicio=True)),
    ]
    if mensagem:
        linhas.append((m.RESUMO_MENSAGEM, mensagem))
    return linhas


def _confirmacao(request, escolha: Escolha, *, email="", erros=None, status=200):
    erros = erros or {}
    unidade = escolha.conclusao.unidade or ""
    return render(request, "portal/contribuicao/confirmar.html", {
        "m": m, "erros": erros, "resumo_erros": _resumo_de_erros(erros),
        "resumo": _resumo(escolha.forma, escolha.conclusao, unidade, escolha.mensagem),
        "ciencia": m.ciencia(unidade), "versao": m.VERSAO_DA_CIENCIA,
        "versao_texto": m.VERSAO_TEXTO.format(versao=m.VERSAO_DA_CIENCIA),
        "escolha": escolha, "formacao": str(escolha.conclusao.pk), "email": email,
    }, status=status)


def _ativa(pessoa, escolha: Escolha) -> bool:
    return da_pessoa(pessoa).filter(
        conclusao_id=escolha.conclusao.pk, forma=escolha.forma, retirada_em__isnull=True
    ).exists()


@never_cache
@require_http_methods(["GET", "POST"])
@egresso
def contribuir(request, pessoa):
    """Escolha (tela 1). O POST válido mostra a confirmação (tela 2); "Voltar e alterar" da
    confirmação volta aqui com as escolhas mantidas."""
    conclusoes = conclusoes_de_referencia(pessoa)
    if request.method == "GET":
        return _escolha(request, None, conclusoes)
    escolha, erros = ler_escolha(request.POST, conclusoes)
    if "voltar" in request.POST:
        return _escolha(request, escolha, conclusoes)
    if not erros and _ativa(pessoa, escolha):
        erros["forma"] = m.ERROS["duplicada"]
    if erros:
        return _escolha(request, escolha, conclusoes, erros=erros, status=422)
    return _confirmacao(request, escolha)


@never_cache
@require_POST
@egresso
def confirmar(request, pessoa):
    """Grava (FR-001, FR-004, FR-007) e leva ao detalhe (tela 3). Erro de e-mail mantém as
    escolhas; uma escolha inválida ou já ativa volta à tela 1."""
    conclusoes = conclusoes_de_referencia(pessoa)
    escolha, erros = ler_escolha(request.POST, conclusoes)
    if erros:
        return _escolha(request, escolha, conclusoes, erros=erros, status=422)
    email = request.POST.get("email", "")
    try:
        manifestacao = operacoes.registrar(
            pessoa, conclusao_id=escolha.conclusao.pk, forma=escolha.forma,
            mensagem=escolha.mensagem, email=email,
            versao_da_ciencia=request.POST.get("versao", ""), agora=timezone.now(),
        )
    except ManifestacaoRejeitada as erro:
        if Motivo.DUPLICADA in erro.motivos:
            return _escolha(request, escolha, conclusoes,
                            erros={"forma": m.ERROS["duplicada"]}, status=409)
        if Motivo.EMAIL in erro.motivos:
            return _confirmacao(request, escolha, email=email,
                                erros={"email": m.ERROS["email"]}, status=422)
        if Motivo.CIENCIA in erro.motivos:
            return _confirmacao(request, escolha, email=email,
                                erros={"ciencia": m.ERROS["ciencia"]}, status=409)
        raise
    return _ir(f"{LISTA}{manifestacao.pk}/?aviso=enviada")


def _situacao(manifestacao, *, na_lista: bool = False) -> tuple[str, str]:
    """Texto e classe da situação (FR-005a, FR-013). Na lista, a data de envio já está na
    linha de cima."""
    atual = situacao(manifestacao)
    if atual is Situacao.RETIRADA:
        return m.SITUACAO_RETIRADA.format(data=_data(manifestacao.retirada_em)), "retirada"
    if atual is Situacao.CONTATO_REGISTRADO:
        texto = m.SITUACAO_CONTATO.format(
            destino=m.destino(manifestacao.unidade, inicio=True),
            data=_data(manifestacao.contato_registrado_em),
        )
        return texto, "marco"
    if na_lista:
        return m.SITUACAO_ENVIADA_NA_LISTA, "enviada"
    return m.SITUACAO_ENVIADA.format(data=_data(manifestacao.registrada_em)), "enviada"


def _linha(d) -> str:
    """Formação, quem recebe e data, numa linha (lista e retirada)."""
    curso = d.conclusao.curso if d.conclusao else None
    return m.LINHA_DA_LISTA.format(
        formacao=curso or m.FORMACAO_NAO_ENCONTRADA,
        quem_recebe=m.quem_recebe(d.manifestacao.unidade),
        data=_data(d.manifestacao.registrada_em),
    )


@never_cache
@require_GET
@egresso
def contribuicoes(request, pessoa):
    """Suas contribuições (FR-013)."""
    itens = []
    for d in descrever(da_pessoa(pessoa)):
        texto, classe = _situacao(d.manifestacao, na_lista=True)
        itens.append({
            "manifestacao": d.manifestacao,
            "forma": Forma(d.manifestacao.forma).label,
            "linha": _linha(d),
            "situacao": texto, "classe": classe,
        })
    return render(request, "portal/contribuicao/lista.html", {
        "m": m, "itens": itens, "aviso": m.AVISOS.get(request.GET.get("aviso")),
    })


def _da_pessoa_ou_404(pessoa, pk):
    manifestacao = da_pessoa_ou_none(pessoa, pk)
    if manifestacao is None:
        raise Http404
    return manifestacao


@never_cache
@require_GET
@egresso
def detalhe(request, pessoa, pk):
    """O que enviou, para quem, o que acontece depois e a situação (US1.4, US2)."""
    manifestacao = _da_pessoa_ou_404(pessoa, pk)
    (d,) = descrever([manifestacao])
    texto, classe = _situacao(manifestacao)
    vigente = manifestacao.versao_da_ciencia == m.VERSAO_DA_CIENCIA
    return render(request, "portal/contribuicao/detalhe.html", {
        "m": m, "manifestacao": manifestacao, "situacao": texto, "classe": classe,
        "aviso": m.AVISOS.get(request.GET.get("aviso")),
        "resumo": _resumo(manifestacao.forma, d.conclusao, manifestacao.unidade,
                          manifestacao.mensagem),
        "ciencia": m.ciencia(manifestacao.unidade) if vigente else None,
        "versao_texto": m.VERSAO_TEXTO.format(versao=manifestacao.versao_da_ciencia),
    })


@never_cache
@require_http_methods(["GET", "POST"])
@egresso
def retirar(request, pessoa, pk):
    """Confirmação e retirada (FR-005). Já retirada: volta ao detalhe, que mostra a data."""
    manifestacao = _da_pessoa_ou_404(pessoa, pk)
    if not manifestacao.ativa:
        return _ir(f"{LISTA}{pk}/")
    if request.method == "POST":
        try:
            operacoes.retirar(pessoa, pk, agora=timezone.now())
        except ManifestacaoRejeitada as erro:
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            return _ir(f"{LISTA}{pk}/")
        return _ir(f"{LISTA}?aviso=retirada")
    (d,) = descrever([manifestacao])
    return render(request, "portal/contribuicao/retirar.html", {
        "m": m, "manifestacao": manifestacao, "forma": Forma(manifestacao.forma).label,
        "linha": _linha(d),
        "texto": m.RETIRAR_TEXTO.format(da_unidade=m.da_unidade(manifestacao.unidade)),
    })

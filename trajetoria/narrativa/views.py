"""Página "Minha trajetória no Ifes" e o card (Feature 021; contracts/rotas.md).

Camada fina: a narrativa vem de `montagem.montar`, os fatos de `consultas`, o card de
`card` e o PNG de `rasterizacao`. Nenhuma view grava nada (FR-008). Sem Pessoa na sessão
(018), vai para `/acesso/`; sem Participação concluída institucional, para `/formacoes/`,
sem mencionar a narrativa (FR-002). O nome só entra no card com `nome=1` (FR-034).
"""

from functools import wraps

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.narrativa import card, catalogo, consultas, rasterizacao
from trajetoria.narrativa.montagem import montar

ARQUIVO = "minha-trajetoria-ifes"


class _Redirecionar(Exception):
    def __init__(self, destino):
        self.destino = destino


def _pessoa_e_narrativa(request):
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        raise _Redirecionar("/acesso/")
    if not consultas.elegivel(pessoa):
        raise _Redirecionar("/formacoes/")
    entrada = consultas.entrada_da_pessoa(
        pessoa, timezone.localdate(), settings.TRAJETORIA_DEMONSTRACAO
    )
    return pessoa, montar(entrada)


def _nome_escolhido(request, pessoa) -> str | None:
    return pessoa.nome if request.GET.get("nome") == "1" and pessoa.nome else None


def _svg(request, pessoa, narrativa) -> str:
    return card.card_svg(
        narrativa.compartilhavel,
        nome=_nome_escolhido(request, pessoa),
        demonstracao=settings.TRAJETORIA_DEMONSTRACAO,
    )


def _respondendo(view):
    @wraps(view)
    def envolvida(request):
        try:
            return view(request, *_pessoa_e_narrativa(request))
        except _Redirecionar as r:
            return redirect(r.destino)

    return envolvida


def _itens(secao):
    """Frases sem formação (abertura) e, na ordem, as frases de cada formação."""
    abertura = [f for f in secao.frases if f.formacao is None]
    indices = sorted({f.formacao for f in secao.frases if f.formacao is not None})
    return abertura, [[f for f in secao.frases if f.formacao == i] for i in indices]


@require_GET
@never_cache
@_respondendo
def minha_trajetoria(request, pessoa, narrativa):
    secoes = []
    for secao in narrativa.secoes:
        abertura, itens = (
            _itens(secao) if secao.chave == "trajetoria_academica" else (list(secao.frases), [])
        )
        secoes.append(
            {"chave": secao.chave, "titulo": secao.titulo, "abertura": abertura, "itens": itens}
        )
    nome = _nome_escolhido(request, pessoa)
    sufixo = "?nome=1" if nome else ""
    png = rasterizacao.rasterizacao_disponivel()
    return render(
        request,
        "narrativa/minha_trajetoria.html",
        {
            "titulo": catalogo.TITULO,
            "titulo_do_card": catalogo.TITULO_DO_CARD,
            "secoes": secoes,
            "card": {
                "png": png,
                "arquivo": f"/minha-trajetoria/card.{'png' if png else 'svg'}{sufixo}",
                "nome_do_arquivo": f"{ARQUIVO}.{'png' if png else 'svg'}",
                "formato": "PNG" if png else "SVG",
                # Fallback sem PNG: o SVG gerado pelo nosso template (texto escapado nele).
                "svg": None if png else mark_safe(_svg(request, pessoa, narrativa)),
                "alt": card.descricao(narrativa.compartilhavel, nome),
                "nome_disponivel": narrativa.compartilhavel.nome_disponivel,
                "com_nome": bool(nome),
            },
        },
    )


@require_GET
@never_cache
@_respondendo
def card_svg(request, pessoa, narrativa):
    resposta = HttpResponse(_svg(request, pessoa, narrativa), content_type="image/svg+xml")
    resposta["Content-Disposition"] = f'attachment; filename="{ARQUIVO}.svg"'
    return resposta


@require_GET
@never_cache
@_respondendo
def card_png(request, pessoa, narrativa):
    png = rasterizacao.png_de(_svg(request, pessoa, narrativa))
    if png is None:
        raise Http404
    resposta = HttpResponse(png, content_type="image/png")
    # inline: abre como imagem (salvável com toque longo); o download vem do atributo
    # `download` da página (research R9).
    resposta["Content-Disposition"] = f'inline; filename="{ARQUIVO}.png"'
    return resposta

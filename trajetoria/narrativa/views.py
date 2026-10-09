"""Página "Minha trajetória no Ifes" e o card (Feature 021; contracts/rotas.md).

Camada fina: a narrativa vem de `montagem.montar`, os fatos de `consultas`, o card de
`card` e o PNG de `rasterizacao`. Nenhuma view grava nada (FR-008). Sem Pessoa na sessão
(018), vai para `/acesso/`; sem Participação concluída institucional, para `/formacoes/`,
sem mencionar a narrativa (FR-002). O nome só entra no card com `nome=1` (FR-034).
"""

import logging
from functools import wraps

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from trajetoria.acesso.sessao import destino_da_entrada, pessoa_em_uso
from trajetoria.narrativa import card, catalogo, consultas, imagens, rasterizacao
from trajetoria.narrativa.composicao import ComposicaoImpossivel, composicao_visual
from trajetoria.narrativa.montagem import montar
from trajetoria.video import operacoes as video
from trajetoria.video import renderizador as renderizador_de_video

ARQUIVO = "minha-trajetoria-ifes"


class Redirecionar(Exception):
    def __init__(self, destino):
        self.destino = destino


def _pessoa_e_narrativa(request):
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        raise Redirecionar(destino_da_entrada(request))  # 023 FR-001
    if not consultas.elegivel(pessoa):
        raise Redirecionar("/formacoes/")
    entrada = consultas.entrada_da_pessoa(
        pessoa, timezone.localdate(), settings.TRAJETORIA_DEMONSTRACAO
    )
    return pessoa, montar(entrada)


def _nome_escolhido(request, pessoa) -> str | None:
    return pessoa.nome if request.GET.get("nome") == "1" and pessoa.nome else None


def composicao_da_sessao(request, quer_nome: bool) -> tuple[dict, str]:
    """Para o vídeo (022): a composição visual do card da Pessoa da sessão, com a mesma regra
    de acesso e de nome da 021, e o sufixo `?nome=1` da escolha. Recalculada a cada
    requisição: o cliente nunca informa qual vídeo quer (022 FR-025). Levanta `Redirecionar`
    ou `ComposicaoImpossivel`."""
    pessoa, narrativa = _pessoa_e_narrativa(request)
    nome = pessoa.nome if quer_nome and pessoa.nome else None
    composicao = composicao_visual(
        narrativa.compartilhavel, nome, settings.TRAJETORIA_DEMONSTRACAO
    )
    return composicao, "?nome=1" if nome else ""


def _bloco_do_video(narrativa, nome, sufixo) -> dict:
    """O bloco #video (022) nunca derruba a página: qualquer falha o esconde (FR-033). Sem
    o renderizador, nem a composição é montada."""
    try:
        if not renderizador_de_video.disponivel():
            return {"disponivel": False}
        composicao = composicao_visual(
            narrativa.compartilhavel, nome, settings.TRAJETORIA_DEMONSTRACAO
        )
        return video.bloco(composicao, sufixo)
    except ComposicaoImpossivel:
        return {"disponivel": False}
    except Exception:
        # Só o fato técnico (022 FR-027).
        logging.getLogger("trajetoria.video").exception("video: falha ao montar o bloco")
        return {"disponivel": False}


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
        except Redirecionar as r:
            return redirect(r.destino)

    return envolvida


def _abertura(narrativa):
    """Imagem do catálogo com legenda, e o que o Ifes registra (FR-026, FR-076, FR-083)."""
    unidade = narrativa.compartilhavel.unidade_da_imagem
    imagem = imagens.imagem_para(unidade)
    registro = narrativa.secao("o_que_o_ifes_registra")
    return {
        # Ativo versionado do catálogo, decorativo: a legenda é o texto.
        "imagem": imagens.svg_decorativo(imagem),
        "legenda": imagens.legenda(imagem),
        "frases": list(registro.frases) if registro else [],
    }


def _capitulos(narrativa):
    """Distribui as seções da montagem nos capítulos (FR-026, R21), sem regra de dado nova:
    a primeira formação e o início em "Sua formação"; as demais, com o "depois de", em "Sua
    continuidade no Ifes"; os agregados em destaque em "Naquele ano no Ifes"; o card."""
    trajetoria = narrativa.secao("trajetoria_academica")
    frases = trajetoria.frases if trajetoria else ()
    outras = narrativa.secao("outras_formacoes")
    depois = {f.formacao: f for f in (outras.frases if outras else ())}
    indices = sorted({f.formacao for f in frases if f.formacao is not None})

    def item(i):
        return {
            "ano": narrativa.formacoes[i].ano_conclusao,
            "relacao": depois.get(i),
            "frases": [f for f in frases if f.formacao == i],
        }

    capitulos = []
    inicio = [f for f in frases if f.formacao is None]
    if indices or inicio:
        capitulos.append(
            {"chave": "sua_formacao", "abertura": inicio, "itens": [item(i) for i in indices[:1]]}
        )
    if len(indices) > 1:
        capitulos.append({"chave": "continuidade", "itens": [item(i) for i in indices[1:]]})
    if agregados := narrativa.secao("naquele_ano"):
        frases_agregadas = [f for f in agregados.frases if f.formacao is not None]
        capitulos.append({
            "chave": "naquele_ano",
            "destaques": [
                {"numero": card.numero_formatado(c.valor), "frase": f}
                for c, f in zip(narrativa.contextos_agregados, frases_agregadas, strict=True)
            ],
            "apuracoes": [f for f in agregados.frases if f.formacao is None],
        })
    capitulos.append({"chave": "seu_card"})
    for k, capitulo in enumerate(capitulos, 1):
        capitulo["titulo"] = catalogo.TITULOS_DOS_CAPITULOS[capitulo["chave"]]
        capitulo["indicador"] = (
            catalogo.CAPITULO.format(k=k, total=len(capitulos)) if len(capitulos) > 1 else None
        )
    return capitulos


@require_GET
@never_cache
@_respondendo
def minha_trajetoria(request, pessoa, narrativa):
    nome = _nome_escolhido(request, pessoa)
    sufixo = "?nome=1" if nome else ""
    png = rasterizacao.rasterizacao_disponivel()
    return render(
        request,
        "narrativa/minha_trajetoria.html",
        {
            "titulo": catalogo.TITULO,
            "abertura": _abertura(narrativa),
            "capitulos": _capitulos(narrativa),
            "video": _bloco_do_video(narrativa, nome, sufixo),
            "card": {
                "png": png,
                "arquivo": f"/minha-trajetoria/card.{'png' if png else 'svg'}{sufixo}",
                "nome_do_arquivo": f"{ARQUIVO}.{'png' if png else 'svg'}",
                "formato": "PNG" if png else "SVG",
                # Fallback sem PNG: o SVG gerado pelo nosso template (texto escapado nele).
                "svg": None if png else mark_safe(_svg(request, pessoa, narrativa)),
                "alt": card.descricao(
                    narrativa.compartilhavel, nome, settings.TRAJETORIA_DEMONSTRACAO
                ),
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

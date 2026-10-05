"""Telas dos Lotes de mobilização (Feature 020; contracts/rotas.md; research R13).

Somente contagens agregadas: nenhuma tela lista membros, nomes ou endereços (FR-038).
Respostas nunca guardadas em cache. Recusas por categoria fixa, sem dado pessoal.
"""

from urllib.parse import urlencode

from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import recusa
from trajetoria.campanha.consultas import EstadoCampanha, estado, populacao_no_momento
from trajetoria.demonstracao.operador import operador_ficticio
from trajetoria.mobilizacao import operacoes as op
from trajetoria.mobilizacao.acesso import (
    RecusaDeLote,
    campanha_autorizada,
    lote_autorizado,
    lotes,
    lotes_visiveis,
)
from trajetoria.mobilizacao.models import SituacaoDoMembro

S = SituacaoDoMembro
AVISO_ACEITE = "Aceite do transporte não comprova entrega da mensagem."
AVISO_CAUSA = (
    "Pertencer a um Lote não prova que a comunicação causou uma resposta: o link é neutro e "
    "qualquer egresso na abrangência da Campanha pode responder, abordado ou não."
)
RECUSAS = {
    "unidade_fora_do_escopo": "Escolha ao menos uma unidade, somente entre as da sua atuação.",
    "filtros_invalidos": "Filtros inválidos. Confira os anos e os textos informados.",
    "nome_invalido": "Informe um nome curto para o Lote (até 120 caracteres).",
    "confirmacao_de_abrangencia": (
        "Sem filtros, o Lote abrange todas as Pessoas da Campanha. Confirme explicitamente."
    ),
    "lote_vazio": (
        "Nenhuma Pessoa a mobilizar com esses filtros: o recorte está vazio ou todas já "
        "foram abordadas nesta Campanha. Nenhum Lote foi gravado."
    ),
    "campanha_encerrada": "A Campanha está encerrada. Nada foi gravado nem enviado.",
    "campanha_fora_da_coleta": (
        "O envio só ocorre com a Campanha em coleta. Os membros continuam não tentados."
    ),
    "mobilizacao_concorrente": (
        "Outro Lote desta Campanha foi confirmado ao mesmo tempo. Nada foi gravado; "
        "confira a prévia de novo."
    ),
    "transporte_inseguro": (
        "Envio recusado: a configuração do transporte não é permitida. Nenhuma mensagem saiu."
    ),
    "envio_real_desativado": (
        "O envio real está desativado até as decisões institucionais (Gates A e B). "
        "Nenhuma mensagem saiu."
    ),
    "origem_indevida": "A base contém dados fora da demonstração. Nada foi enviado.",
}
PADRAO = "Ação recusada. Nada foi gravado nem enviado."


def _pagina(request, template, dados, status=200):
    resposta = render(
        request, template, {"banner": ap.BANNER, "atuacao": request.atuacao, **dados}, status=status
    )
    resposta["Cache-Control"] = "no-store"
    return resposta


def _trilha(campanha, *final):
    return [
        ("Acompanhamento da coleta", "/acompanhamento/"),
        (campanha.nome, f"/acompanhamento/campanhas/{campanha.pk}/"),
        *final,
    ]


def _recusada(request, exc, campanha=None, status=None):
    if exc.status == 404:
        raise Http404
    if exc.status == 403 and exc.categoria in ("sem_autorizacao", "fora_do_escopo"):
        return recusa(request, "Ação não autorizada para esta atuação ou escopo.")
    return _pagina(
        request,
        "mobilizacao/aviso.html",
        {
            "campanha": campanha,
            "texto": RECUSAS.get(exc.categoria, PADRAO),
            "trilha": _trilha(campanha, ("Lotes de mobilização", None)) if campanha else [],
        },
        status or exc.status,
    )


def _filtros_do_pedido(dados):
    return dict(
        unidades=dados.getlist("unidade"),
        nivel=dados.get("nivel") or None,
        ano_minimo=dados.get("ano_minimo") or None,
        ano_maximo=dados.get("ano_maximo") or None,
        curso=dados.get("curso") or None,
    )


def _opcoes(campanha, escopo):
    conclusoes = populacao_no_momento(campanha)
    if not escopo.institucional:
        conclusoes = conclusoes.filter(unidade__in=sorted(escopo.unidades))
    unidades = sorted({u for u in conclusoes.values_list("unidade", flat=True) if u})
    niveis = sorted({n for n in conclusoes.values_list("nivel", flat=True) if n})
    return unidades, niveis


def _rotulo(operador):
    ficticio = operador_ficticio(operador)
    return ficticio.rotulo if ficticio else "Operador"


def situacao_do_lote(contagens) -> str:
    """Derivada dos membros (FR-031); o Lote não tem estado próprio."""
    nao_tentados = contagens.get(S.NAO_TENTADO, 0)
    tentados = sum(contagens.get(s, 0) for s in (
        S.EM_TENTATIVA, S.SUBMETIDO_AO_TRANSPORTE, S.FALHA_DE_TRANSPORTE))
    if nao_tentados and not tentados:
        return "Não enviado"
    if nao_tentados:
        return "Envio parcial"
    return "Envio concluído"


def _contagens(lote):
    return {
        linha["situacao"]: linha["n"]
        for linha in lote.membros.values("situacao").annotate(n=Count("id"))
    }


@lotes
@require_GET
def lista(request, campanha):
    contexto = request.lotes
    try:
        visivel = campanha_autorizada(campanha, contexto)
    except RecusaDeLote as exc:
        return _recusada(request, exc)
    agora = timezone.now()
    situacao = estado(visivel, agora=agora)
    linhas = []
    for lote in lotes_visiveis(visivel, contexto.escopo):
        contagens = _contagens(lote)
        linhas.append(
            {"lote": lote, "situacao": situacao_do_lote(contagens),
             "membros": sum(contagens.values()), "rotulo": _rotulo(lote.operador)}
        )
    dados = {
        "campanha": visivel,
        "situacao_campanha": ap.situacao(situacao),
        "linhas": linhas,
        "trilha": _trilha(visivel, ("Lotes de mobilização", None)),
        "pode_preparar": contexto.preparar and situacao is not EstadoCampanha.ENCERRADA,
        "aviso_causa": AVISO_CAUSA,
        "institucional": contexto.escopo.institucional,
    }
    if dados["pode_preparar"]:
        unidades, niveis = _opcoes(visivel, contexto.escopo)
        filtros = _filtros_do_pedido(request.GET)
        dados.update(unidades=unidades, niveis=niveis, pedido=filtros)
        if "previa" in request.GET:
            try:
                dados["previa"] = op.previa(visivel.pk, contexto.operador, filtros, agora=agora)
            except RecusaDeLote as exc:
                if exc.status in (404,) or exc.categoria in ("sem_autorizacao", "fora_do_escopo"):
                    return _recusada(request, exc, visivel)
                dados["erro"] = RECUSAS.get(exc.categoria, PADRAO)
                return _pagina(request, "mobilizacao/lotes.html", dados, exc.status)
            dados["consulta"] = urlencode(
                [("unidade", u) for u in filtros["unidades"]]
                + [(k, v) for k, v in filtros.items() if k != "unidades" and v]
            )
    return _pagina(request, "mobilizacao/lotes.html", dados)


@lotes
@require_POST
def confirmar(request, campanha):
    contexto = request.lotes
    try:
        visivel = campanha_autorizada(campanha, contexto)
    except RecusaDeLote as exc:
        return _recusada(request, exc)
    try:
        lote = op.confirmar_lote(
            visivel.pk,
            contexto.operador,
            request.POST.get("nome", ""),
            _filtros_do_pedido(request.POST),
            request.POST.get("confirmo_abrangencia") == "1",
        )
    except RecusaDeLote as exc:
        return _recusada(request, exc, visivel)
    return HttpResponse(
        status=303,
        headers={"Location": f"/acompanhamento/campanhas/{visivel.pk}/lotes/{lote.pk}/"},
    )


def _detalhe(request, campanha, lote, *, resultado=None, erro=None, status=200):
    contagens = _contagens(lote)
    situacao = estado(campanha)
    nao_tentados = contagens.get(S.NAO_TENTADO, 0)
    return _pagina(
        request,
        "mobilizacao/lote.html",
        {
            "campanha": campanha,
            "lote": lote,
            "rotulo": _rotulo(lote.operador),
            "contagens": {
                "membros": sum(contagens.values()),
                "sem_contato": contagens.get(S.SEM_CONTATO, 0),
                "nao_tentados": nao_tentados,
                "submetidos": contagens.get(S.SUBMETIDO_AO_TRANSPORTE, 0),
                "falhas": contagens.get(S.FALHA_DE_TRANSPORTE, 0),
                "incertos": contagens.get(S.EM_TENTATIVA, 0),
            },
            "situacao": situacao_do_lote(contagens),
            "situacao_campanha": ap.situacao(situacao),
            "pode_enviar": request.lotes.enviar
            and nao_tentados > 0
            and situacao is EstadoCampanha.EM_COLETA,
            "ja_tentado": any(contagens.get(s) for s in (
                S.EM_TENTATIVA, S.SUBMETIDO_AO_TRANSPORTE, S.FALHA_DE_TRANSPORTE)),
            "em_coleta": situacao is EstadoCampanha.EM_COLETA,
            "resultado": resultado,
            "erro": erro,
            "aviso_aceite": AVISO_ACEITE,
            "aviso_causa": AVISO_CAUSA,
            "trilha": _trilha(
                campanha,
                ("Lotes de mobilização", f"/acompanhamento/campanhas/{campanha.pk}/lotes/"),
                (lote.nome, None),
            ),
        },
        status,
    )


@lotes
@require_GET
def detalhe(request, campanha, lote):
    try:
        visivel = campanha_autorizada(campanha, request.lotes)
        autorizado = lote_autorizado(visivel, lote, request.lotes)
    except RecusaDeLote as exc:
        return _recusada(request, exc)
    return _detalhe(request, visivel, autorizado)


@lotes
@require_POST
def enviar(request, campanha, lote):
    contexto = request.lotes
    try:
        visivel = campanha_autorizada(campanha, contexto)
        autorizado = lote_autorizado(visivel, lote, contexto)
    except RecusaDeLote as exc:
        return _recusada(request, exc)
    try:
        resultado = op.enviar_lote(autorizado.pk, contexto.operador)
    except RecusaDeLote as exc:
        if exc.status == 404 or exc.categoria in ("sem_autorizacao", "fora_do_escopo"):
            return _recusada(request, exc)
        return _detalhe(
            request, visivel, autorizado, erro=RECUSAS.get(exc.categoria, PADRAO),
            status=exc.status,
        )
    return _detalhe(
        request, visivel, autorizado, resultado=resultado,
        status=500 if resultado.interrompido else 200,
    )

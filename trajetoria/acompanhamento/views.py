"""Telas da 011, somente leitura e GET; escrita da 017 no subpacote gestao.

`@acompanhamento` é o mais externo: identifica, verifica vínculo e define o escopo antes de
qualquer consulta. No detalhe, a existência e a visibilidade da Campanha são verificadas
**antes** de calcular qualquer indicador; fora do escopo, a recusa não carrega dado nenhum.
"""

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import acompanhamento, recusa
from trajetoria.acompanhamento.consultas import (
    Recorte,
    campanha_acompanhada,
    campanhas_acompanhadas,
    campanhas_visiveis,
)
from trajetoria.acompanhamento.gestao.mensagens import AVISOS
from trajetoria.acompanhamento.gestao.painel import painel
from trajetoria.campanha.models import Campanha
from trajetoria.declaracao.consultas import fila

_RAIZ = ("Acompanhamento da coleta", "/acompanhamento/")


def _contexto(request, agora, **extra) -> dict:
    return {
        "banner": ap.BANNER,
        "atuacao": request.atuacao,
        "momento": timezone.localtime(agora),
        "nao_se_aplica": ap.NAO_SE_APLICA,
        **extra,
    }


@acompanhamento
@require_GET
def campanhas(request):
    # Um só "agora" para o estado das Campanhas e para o momento exibido.
    agora = timezone.now()
    itens = campanhas_acompanhadas(
        request.escopo, pode_consultar_rascunho=request.atuacao.consultar_rascunho, agora=agora
    )
    linhas = [{"item": item, **ap.numeros(item.indicadores)} for item in itens]
    return render(
        request,
        "acompanhamento/campanhas.html",
        _contexto(
            request,
            agora,
            linhas=linhas,
            texto_lista=ap.TEXTO_LISTA,
            lista_vazia=ap.LISTA_VAZIA,
            trilha=[(_RAIZ[0], None)],
        ),
    )


def _recorte_pedido(request) -> Recorte | None:
    """Ausente → `None` (padrão); um valor da lista fechada → o recorte; qualquer outra coisa,
    inclusive vazio ou repetido → inexistente (FR-059)."""
    valores = request.GET.getlist("recorte")
    if not valores:
        return None
    recorte = Recorte.de_valor(valores[0]) if len(valores) == 1 else None
    if recorte is None:
        raise Http404
    return recorte


@acompanhamento
@require_GET
def campanha(request, campanha):
    visivel = campanhas_visiveis(request.escopo).filter(pk=campanha).first()
    if visivel is None:
        # Só na falta: distinguir "inexistente" (404) de "fora do escopo" (403).
        if not Campanha.objects.filter(pk=campanha).exists():
            raise Http404
        return recusa(request, ap.RECUSA_FORA_DO_ESCOPO)
    agora = timezone.now()
    item = campanha_acompanhada(
        visivel,
        request.escopo,
        pode_consultar_rascunho=request.atuacao.consultar_rascunho,
        recorte=_recorte_pedido(request),
        agora=agora,
    )
    linhas = [
        {"rotulos": linha.rotulos(item.recorte), **ap.numeros(linha.indicadores)}
        for linha in item.linhas
    ]
    return render(
        request,
        "acompanhamento/campanha.html",
        _contexto(
            request,
            agora,
            item=item,
            # Só os itens da fila desta Campanha, no escopo do operador (019 FR-101).
            validacoes_na_fila=(
                fila(request.vinculos).filter(participacao__campanha=visivel).count()
                if request.atuacao.validar_formacao
                else None
            ),
            painel=painel(visivel, agora) if request.atuacao.gerir_campanha else None,
            aviso_gestao=AVISOS.get(request.GET.get("aviso"))
            if request.atuacao.gerir_campanha
            else None,
            resumo=ap.numeros(item.indicadores),
            definicoes=ap.DEFINICOES,
            contagem_por_formacao=ap.CONTAGEM_POR_FORMACAO,
            sem_elegiveis=ap.SEM_ELEGIVEIS,
            linhas=linhas,
            forma_encerramento=(
                ap.forma_de_encerramento(item.encerramento[0]) if item.encerramento else None
            ),
            trilha=[_RAIZ, (visivel.nome, None)],
        ),
    )

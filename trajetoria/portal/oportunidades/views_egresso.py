"""Página de Oportunidades do egresso (025 FR-017 a FR-024; contracts/oportunidades-egresso.md).

Só leitura: nada é gravado ao calcular ou exibir (FR-015). Destinos fixos, nenhum parâmetro
do cliente decide nada (024 FR-006).
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.declaracao.sessao import declaracoes_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal.oportunidades import mensagens
from trajetoria.portal.oportunidades.consultas import itens_da_pessoa
from trajetoria.portal.oportunidades.pertinencia import FORMACAO, TODOS


def _ir(destino: str) -> HttpResponse:
    return HttpResponse(status=303, headers={"Location": destino})


@never_cache
@require_GET
def oportunidades(request):
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        if declaracoes_em_uso(request) is not None:
            return _ir("/declaracao/")
        return _ir("/entrar/?aviso=sessao" if getattr(request, "_sessao_expirada", False)
                   else "/entrar/")
    if not elegivel(pessoa):
        return _ir("/inicio/")  # FR-024: sem Conclusão, sem oportunidades
    itens = itens_da_pessoa(pessoa, timezone.localdate())
    grupos = [
        (titulo, [i for i in itens if i.grupo == grupo])
        for titulo, grupo in ((mensagens.GRUPO_FORMACAO, FORMACAO), (mensagens.GRUPO_TODOS, TODOS))
    ]
    return render(request, "portal/oportunidades.html", {
        "titulo": mensagens.TITULO,
        "introducao": mensagens.INTRODUCAO,
        "grupos": [(titulo, lista) for titulo, lista in grupos if lista],
        "vazio": mensagens.VAZIO,
        "voltar": mensagens.VOLTAR_AO_INICIO,
    })

"""Página "Meu e-mail" (Feature 020, FR-009 a FR-014; contracts/rotas.md).

Fora do percurso do instrumento e da narrativa. Identifica a Pessoa só pela sessão da 018;
sem Pessoa (inclusive declarante da 019) vai para a entrada. Nunca exibe contato guardado
(E5): nem o informado nem o importado. Respostas sem cache.
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.contato.endereco import EnderecoInvalido
from trajetoria.contato.operacoes import informar_email
from trajetoria.narrativa.consultas import elegivel as narrativa_disponivel

ERRO = "Informe um e-mail válido, por exemplo nome@provedor.com.br."


def _pagina(request, pessoa, *, situacao=None, erro=None, status=200):
    return render(
        request,
        "contato/meu_email.html",
        {
            "situacao": situacao,
            "erro": erro,
            "narrativa_disponivel": narrativa_disponivel(pessoa),
        },
        status=status,
    )


@never_cache
@require_http_methods(["GET", "POST"])
def meu_email(request):
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        return HttpResponse(status=303, headers={"Location": "/acesso/"})
    if request.method == "GET":
        return _pagina(request, pessoa)
    if request.POST.get("acao") != "salvar":
        return _pagina(request, pessoa, situacao="recusado")
    try:
        informar_email(pessoa, request.POST.get("email", ""))
    except EnderecoInvalido:
        return _pagina(request, pessoa, erro=ERRO, status=422)
    return _pagina(request, pessoa, situacao="salvo")

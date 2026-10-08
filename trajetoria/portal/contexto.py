"""Itens da navegação do Portal (024; contracts/navegacao.md; research R7).

O shell do núcleo só tem um ponto de extensão neutro (`navegacao`); quem o preenche é este
provedor. Devolve `{}` fora do modo de demonstração, com o Portal desligado, sem Pessoa na
sessão e para o declarante (019): nesses casos, nenhuma tela mostra navegação (FR-027).
"""

import re

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal import mensagens

_CONFIRMACAO = re.compile(r"^/participacoes/[^/]+/concluida/$")


def _atual(caminho: str, endereco: str) -> bool:
    if endereco == "/formacoes/":
        return caminho == endereco or bool(_CONFIRMACAO.match(caminho))
    return caminho == endereco


def _itens(request, pessoa) -> list[dict]:
    itens = [(mensagens.NAVEGACAO_INICIO, "/inicio/")]
    if elegivel(pessoa):
        itens.append((mensagens.NAVEGACAO_TRAJETORIA, "/minha-trajetoria/"))
    itens += [
        (mensagens.NAVEGACAO_PESQUISA, "/formacoes/"),
        (mensagens.NAVEGACAO_EMAIL, "/meu-email/"),
    ]
    return [
        {"rotulo": rotulo, "endereco": endereco, "atual": _atual(request.path, endereco)}
        for rotulo, endereco in itens
    ]


def navegacao(request) -> dict:
    if not (settings.TRAJETORIA_DEMONSTRACAO and settings.TRAJETORIA_PORTAL):
        return {}
    pessoa = pessoa_em_uso(request)  # já resolvida pelo contexto da demonstração
    if pessoa is None:
        return {}
    # Preguiçoso: só consulta o banco se a tela mostrar a navegação (FR-022). As Seções não
    # a mostram, e suas consultas não podem crescer (014; 023).
    return {
        "navegacao": SimpleLazyObject(lambda: _itens(request, pessoa)),
        "navegacao_rotulo": mensagens.ROTULO_NAVEGACAO,
    }

"""Itens da navegação do Portal (024; contracts/navegacao.md; research R7).

O shell do núcleo só tem pontos de extensão neutros (`navegacao`, `produto`, `acao_sair`,
`retorno`); quem os preenche é este provedor. Devolve `{}` fora do modo de demonstração, com o
Portal desligado, sem Pessoa na sessão e para o declarante (019): nesses casos, nenhuma tela
mostra navegação e o shell é o da 015 (FR-027).

Revisão de 2026-10-08 (avaliação por IA, A1 a A4): nas telas que exibem a navegação do Portal
(FR-022), o cabeçalho diz "Portal do Egresso", "Sair" volta à entrada do Portal e o fim da
trajetória e do e-mail leva ao Início. As Seções, `/acesso/` e a declaração não mudam.
"""

import re

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal import mensagens

_CONFIRMACAO = re.compile(r"^/participacoes/[^/]+/concluida/$")
# As telas com a navegação do Portal (FR-022; contracts/navegacao.md). Lista fechada: o
# caminho só decide o cabeçalho e os destinos fixos abaixo, nunca um endereço do cliente.
_TELAS_COM_NAVEGACAO = frozenset(
    {"/inicio/", "/formacoes/", "/minha-trajetoria/", "/oportunidades/", "/meu-email/"}
)
_TELAS_COM_LAYOUT = frozenset(
    {"/inicio/", "/minha-trajetoria/", "/oportunidades/", "/meu-email/"}
)


def _atual(caminho: str, endereco: str) -> bool:
    if endereco == "/formacoes/":
        return caminho == endereco or bool(_CONFIRMACAO.match(caminho))
    return caminho == endereco


def _itens(request, pessoa) -> list[dict]:
    itens = [(mensagens.NAVEGACAO_INICIO, "/inicio/")]
    if elegivel(pessoa):  # uma consulta para os dois itens (025 FR-020)
        itens += [
            (mensagens.NAVEGACAO_TRAJETORIA, "/minha-trajetoria/"),
            (mensagens.NAVEGACAO_OPORTUNIDADES, "/oportunidades/"),
        ]
    itens += [
        (mensagens.NAVEGACAO_PESQUISA, "/formacoes/"),
        (mensagens.NAVEGACAO_EMAIL, "/meu-email/"),
    ]
    return [
        {"rotulo": rotulo, "endereco": endereco, "atual": _atual(request.path, endereco)}
        for rotulo, endereco in itens
    ]


def _tela_com_navegacao(caminho: str) -> bool:
    return caminho in _TELAS_COM_NAVEGACAO or bool(_CONFIRMACAO.match(caminho))


def _shell_do_portal() -> dict:
    return {
        "produto": mensagens.PRODUTO,
        "produto_subtitulo": mensagens.PRODUTO_SUBTITULO,
        "acao_sair": "/sair/",
        "retorno": {"rotulo": mensagens.VOLTAR_AO_INICIO, "endereco": "/inicio/"},
    }


def navegacao(request) -> dict:
    if not (settings.TRAJETORIA_DEMONSTRACAO and settings.TRAJETORIA_PORTAL):
        return {}
    pessoa = pessoa_em_uso(request)  # já resolvida pelo contexto da demonstração
    if pessoa is None:
        return {}
    # Preguiçoso: só consulta o banco se a tela mostrar a navegação (FR-022). As Seções não
    # a mostram, e suas consultas não podem crescer (014; 023).
    contexto = {
        "navegacao": SimpleLazyObject(lambda: _itens(request, pessoa)),
        "navegacao_rotulo": mensagens.ROTULO_NAVEGACAO,
    }
    if _tela_com_navegacao(request.path):
        contexto.update(_shell_do_portal())
    if request.path in _TELAS_COM_LAYOUT:
        contexto["layout_base"] = "portal/base.html"
    return contexto

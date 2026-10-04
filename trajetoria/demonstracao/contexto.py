"""Processador de contexto da demonstração (contracts/demonstracao.md).

Desligado o modo, devolve `{}` sem ler cookie nem consultar o banco: as páginas de erro
nunca mostram faixa de demonstração nem nome de Pessoa (FR-001).
"""

from django.conf import settings

from trajetoria.acesso.sessao import pessoa_em_uso


def demonstracao(request) -> dict:
    if not settings.TRAJETORIA_DEMONSTRACAO:
        return {}
    return {"modo_demonstracao": True, "pessoa_demonstracao": pessoa_em_uso(request)}

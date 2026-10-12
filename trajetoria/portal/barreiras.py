"""Barreiras de acesso das telas do Portal (024 FR-006; 025 contracts/curadoria.md; 026 R12;
031 contracts/rotas.md). Uma regra só, usada por todas as telas da camada.

- `egresso`: Pessoa identificada pela 018 e com ao menos uma Conclusão. Sem Pessoa, o destino
  fixo de `destinos.sem_pessoa`; sem Conclusão, 404.
- `operador(...)`: demonstração, operador fictício e competência, relidos a cada pedido. O
  identificador do operador nunca vai ao template. Cada tela de operação (curadoria, lista
  da unidade, moderação) informa a sua competência, o seu escopo, a recusa e o destino da
  escolha de operador.
"""

from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect

from trajetoria.acesso.sessao import pessoa_em_uso
from trajetoria.acompanhamento.acesso import Atuacao, recusa
from trajetoria.demonstracao.operador import vinculos_do_operador_em_uso
from trajetoria.narrativa.consultas import elegivel
from trajetoria.portal.destinos import sem_pessoa


def egresso(view):
    """Passa a Pessoa à view como segundo argumento."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        pessoa = pessoa_em_uso(request)
        if pessoa is None:
            return sem_pessoa(request)
        if not elegivel(pessoa):
            raise Http404
        return view(request, pessoa, *args, **kwargs)

    return envolvida


def operador(*, pode, escopo_de, mensagem_de_recusa: str, destino: str):
    """Fábrica da barreira das telas de operação. Deixa em `request.escopo` o escopo da
    competência e em `request.atuacao` os rótulos dos vínculos."""
    escolha_de_operador = f"/demonstracao/operador/?destino={destino}"

    def decorador(view):
        @wraps(view)
        def envolvida(request, *args, **kwargs):
            if not settings.TRAJETORIA_DEMONSTRACAO:
                raise Http404
            vinculos = vinculos_do_operador_em_uso(request)
            if vinculos is None:
                return redirect(escolha_de_operador)
            if not pode(vinculos):
                return recusa(request, mensagem_de_recusa, destino_operador=destino)
            request.escopo = escopo_de(vinculos)
            request.atuacao = Atuacao(tuple(v.rotulo_de_atuacao for v in vinculos), False)
            return view(request, *args, **kwargs)

        return envolvida

    return decorador

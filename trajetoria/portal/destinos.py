"""Destino de quem abre uma tela do egresso sem Pessoa na sessão (024 FR-006; 023 FR-001).

Uma regra só para o Início, a Participação, Oportunidades e a contribuição: o declarante (019)
volta à declaração; os demais vão à entrada do Portal, com aviso quando a sessão acabou de
expirar. Destinos fixos: nenhum valor do cliente decide para onde a pessoa vai.
"""

from django.http import HttpResponse

from trajetoria.declaracao.sessao import declaracoes_em_uso


def ir(destino: str) -> HttpResponse:
    return HttpResponse(status=303, headers={"Location": destino})


def sem_pessoa(request) -> HttpResponse:
    if declaracoes_em_uso(request) is not None:
        return ir("/declaracao/")
    return ir("/entrar/?aviso=sessao" if getattr(request, "_sessao_expirada", False)
              else "/entrar/")

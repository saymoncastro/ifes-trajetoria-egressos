"""Modo de demonstração (008 FR-001; contracts/demonstracao.md).

Desligado — o padrão —, nenhuma página responde: toda requisição é 404, antes de qualquer
view. A setting é lida a cada requisição. As únicas rotas do projeto são a interface do
egresso (008), o editor institucional do instrumento (009, `/editor/`) e o acompanhamento
da coleta (011, `/acompanhamento/`): todos existem só neste modo não produtivo, e "toda
requisição" coincide com "toda página" de todos.
"""

from django.conf import settings
from django.http import Http404


class ModoDemonstracaoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise Http404
        return self.get_response(request)

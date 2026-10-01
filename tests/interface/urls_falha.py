"""URLs só de teste: as do projeto mais uma view que falha, para verificar a página genérica
de erro inesperado (008 FR-069). Nunca usadas fora dos testes."""

from django.urls import path

from config.urls import urlpatterns as do_projeto


def falha(request):
    raise RuntimeError("falha simulada de teste")


urlpatterns = [path("falha-de-teste/", falha), *do_projeto]

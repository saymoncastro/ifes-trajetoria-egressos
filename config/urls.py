"""Rotas: só a interface de demonstração da Feature 008 (adaptador e jornada). Com o modo
de demonstração desligado, toda requisição é 404 (`ModoDemonstracaoMiddleware`)."""

from django.urls import include, path

urlpatterns = [
    path("", include("trajetoria.demonstracao.urls")),
    path("", include("trajetoria.interface.urls")),
]

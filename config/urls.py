"""Rotas: a interface de demonstração da Feature 008 (adaptador e jornada) e o editor
institucional do instrumento da Feature 009 (`/editor/`). Com o modo de demonstração
desligado, toda requisição é 404 (`ModoDemonstracaoMiddleware`)."""

from django.urls import include, path

urlpatterns = [
    path("editor/", include("trajetoria.editor.urls")),
    path("", include("trajetoria.demonstracao.urls")),
    path("", include("trajetoria.interface.urls")),
]

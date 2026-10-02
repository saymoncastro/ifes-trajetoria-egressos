"""Rotas: a interface de demonstração da Feature 008 (adaptador e jornada), o editor
institucional do instrumento da Feature 009 (`/editor/`) e o acompanhamento operacional da
coleta da Feature 011 (`/acompanhamento/`). Com o modo de demonstração desligado, toda
requisição é 404 (`ModoDemonstracaoMiddleware`)."""

from django.urls import include, path

urlpatterns = [
    path("editor/", include("trajetoria.editor.urls")),
    path("acompanhamento/", include("trajetoria.acompanhamento.urls")),
    path("", include("trajetoria.demonstracao.urls")),
    path("", include("trajetoria.interface.urls")),
]

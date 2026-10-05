"""Rotas: a interface de demonstração da Feature 008 (adaptador e jornada), o editor
institucional do instrumento da Feature 009 (`/editor/`), o acompanhamento operacional da
coleta da Feature 011 (`/acompanhamento/`), a devolutiva da Feature 021
(`/minha-trajetoria/`) e o vídeo da Feature 022 (`/minha-trajetoria/video…`). Com o modo de
demonstração desligado, toda requisição é 404 (`ModoDemonstracaoMiddleware`)."""

from django.urls import include, path

urlpatterns = [
    path("", include("trajetoria.declaracao.urls")),
    path("editor/", include("trajetoria.editor.urls")),
    path("acompanhamento/", include("trajetoria.acompanhamento.urls")),
    path("", include("trajetoria.demonstracao.urls")),
    path("acesso/", include("trajetoria.acesso.urls")),
    path("", include("trajetoria.video.urls")),
    path("", include("trajetoria.narrativa.urls")),
    path("", include("trajetoria.interface.urls")),
]

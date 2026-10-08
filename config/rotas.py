"""Rotas do projeto, como função de `com_portal` (024 FR-027; research R8). Separada de
`config/urls.py` para que montar as rotas sem o Portal (nos testes) não dependa da ordem de
importação do `urlconf` principal."""

from django.urls import include, path


def rotas(com_portal: bool) -> list:
    portal = [path("", include("trajetoria.portal.urls"))] if com_portal else []
    return [
        path("", include("trajetoria.declaracao.urls")),
        path("editor/", include("trajetoria.editor.urls")),
        path("acompanhamento/", include("trajetoria.acompanhamento.urls")),
        path("", include("trajetoria.demonstracao.urls")),
        path("acesso/", include("trajetoria.acesso.urls")),
        path("", include("trajetoria.video.urls")),
        path("", include("trajetoria.narrativa.urls")),
        path("", include("trajetoria.contato.urls")),
        *portal,
        path("", include("trajetoria.interface.urls")),
    ]

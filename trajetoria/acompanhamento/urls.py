"""Rotas do acompanhamento da coleta (Feature 011; contracts/rotas.md). Só existem no modo
de demonstração local: desligado, `ModoDemonstracaoMiddleware` responde 404 antes de
resolver qualquer rota."""

from django.urls import path

from trajetoria.acompanhamento import views

urlpatterns = [
    path("", views.campanhas),
    path("campanhas/<uuid:campanha>/", views.campanha),
]

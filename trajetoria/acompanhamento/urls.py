"""Rotas do acompanhamento da coleta (Feature 011; contracts/rotas.md). Só existem no modo
de demonstração local: desligado, `ModoDemonstracaoMiddleware` responde 404 antes de
resolver qualquer rota."""

from django.urls import path

from trajetoria.acompanhamento import views
from trajetoria.acompanhamento.gestao import views as gestao
from trajetoria.comunicacao import views as comunicacao

urlpatterns = [
    path("", views.campanhas),
    path("campanhas/nova/", gestao.nova),
    path("campanhas/<uuid:campanha>/encerrar/", gestao.encerrar),
    path("campanhas/<uuid:campanha>/abrir/", gestao.abrir),
    path("campanhas/<uuid:campanha>/editar/", gestao.editar),
    path("campanhas/<uuid:campanha>/comunicacao/", comunicacao.preparar),
    path("campanhas/<uuid:campanha>/comunicacao/simular/", comunicacao.simular),
    path("campanhas/<uuid:campanha>/", views.campanha),
]

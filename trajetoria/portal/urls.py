"""Rotas do Portal (024; contracts/rotas.md; 025; 026 plan, "Rotas"). Só incluídas com
`TRAJETORIA_PORTAL` ligado."""

from django.urls import path

from trajetoria.portal import views
from trajetoria.portal.contribuicao import views_egresso as contribuicao
from trajetoria.portal.contribuicao import views_unidade as contribuicao_unidade
from trajetoria.portal.oportunidades import views_curadoria, views_egresso

urlpatterns = [
    path("", views.entrada),
    path("entrar/", views.entrar),
    path("inicio/", views.inicio),
    path("sair/", views.sair),
    path("oportunidades/", views_egresso.oportunidades),
    path("curadoria/oportunidades/", views_curadoria.lista),
    path("curadoria/oportunidades/nova/", views_curadoria.nova),
    path("curadoria/oportunidades/<uuid:pk>/editar/", views_curadoria.editar),
    path("curadoria/oportunidades/<uuid:pk>/publicar/", views_curadoria.publicar),
    path("curadoria/oportunidades/<uuid:pk>/retirar/", views_curadoria.retirar),
    path("contribuir/", contribuicao.contribuir),
    path("contribuir/confirmar/", contribuicao.confirmar),
    path("contribuicoes/", contribuicao.contribuicoes),
    path("contribuicoes/<uuid:pk>/", contribuicao.detalhe),
    path("contribuicoes/<uuid:pk>/retirar/", contribuicao.retirar),
    path("curadoria/contribuicoes/", contribuicao_unidade.lista),
    path("curadoria/contribuicoes/exportar.csv", contribuicao_unidade.exportar),
    path("curadoria/contribuicoes/<uuid:pk>/contato/", contribuicao_unidade.contato),
]

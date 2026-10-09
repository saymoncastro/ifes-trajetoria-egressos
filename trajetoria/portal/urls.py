"""Rotas do Portal (024; contracts/rotas.md). Só incluídas com `TRAJETORIA_PORTAL` ligado."""

from django.urls import path

from trajetoria.portal import views
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
]

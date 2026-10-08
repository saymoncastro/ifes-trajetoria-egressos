"""Rotas do Portal (024; contracts/rotas.md). Só incluídas com `TRAJETORIA_PORTAL` ligado."""

from django.urls import path

from trajetoria.portal import views

urlpatterns = [
    path("", views.entrada),
    path("entrar/", views.entrar),
    path("inicio/", views.inicio),
    path("sair/", views.sair),
]

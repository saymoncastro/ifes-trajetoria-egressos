"""Rotas da Feature 021 (contracts/rotas.md)."""

from django.urls import path

from trajetoria.narrativa import views

urlpatterns = [
    path("minha-trajetoria/", views.minha_trajetoria),
    path("minha-trajetoria/card.png", views.card_png),
    path("minha-trajetoria/card.svg", views.card_svg),
]

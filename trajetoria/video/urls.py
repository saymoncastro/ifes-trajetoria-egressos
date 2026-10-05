"""Rotas da Feature 022 (contracts/rotas.md)."""

from django.urls import path

from trajetoria.video import views

urlpatterns = [
    path("minha-trajetoria/video/", views.solicitar_video),
    path("minha-trajetoria/video.mp4", views.video_mp4),
    path("minha-trajetoria/video/estado", views.estado_video),
]

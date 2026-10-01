from django.urls import path

from trajetoria.demonstracao import views

urlpatterns = [
    path("demonstracao/", views.entrada),
    path("demonstracao/escolher/", views.escolher),
    path("demonstracao/encerrar/", views.encerrar),
]

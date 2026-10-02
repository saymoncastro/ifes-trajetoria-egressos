from django.urls import path

from trajetoria.demonstracao import views

urlpatterns = [
    path("demonstracao/", views.entrada),
    path("demonstracao/escolher/", views.escolher),
    path("demonstracao/encerrar/", views.encerrar),
    path("demonstracao/operador/", views.operadores),
    path("demonstracao/operador/escolher/", views.escolher_operador),
    path("demonstracao/operador/encerrar/", views.encerrar_operador),
]

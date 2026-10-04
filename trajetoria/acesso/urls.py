from django.urls import path

from trajetoria.acesso import views

urlpatterns = [path("", views.entrada), path("sair/", views.sair)]

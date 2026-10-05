from django.urls import path

from trajetoria.contato import views

urlpatterns = [path("meu-email/", views.meu_email)]

from django.urls import path

from trajetoria.declaracao import views_egresso as egresso
from trajetoria.declaracao import views_validacao as validacao

urlpatterns = [
    path("validacoes-formacao/", validacao.fila, name="validacoes-formacao"),
    path("validacoes-formacao/<uuid:id>/", validacao.detalhe, name="validacao-formacao"),
    path("validacoes-formacao/<uuid:id>/revelar/", validacao.revelar, name="validacao-revelar"),
    path(
        "validacoes-formacao/<uuid:id>/registrar/", validacao.registrar, name="validacao-registrar"
    ),
    path("declaracao/", egresso.entrada, name="declaracao"),
    path("declaracao/nova/", egresso.nova, name="declaracao-nova"),
    path("declaracao/comecar/", egresso.comecar, name="declaracao-comecar"),
]

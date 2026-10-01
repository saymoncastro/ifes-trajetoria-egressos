from django.urls import path

from trajetoria.interface import views

urlpatterns = [
    path("", views.inicio),
    path("formacoes/", views.formacoes),
    path("formacoes/entrar/", views.entrar_view),
    path("participacoes/<uuid:participacao>/", views.participacao),
    path("participacoes/<uuid:participacao>/secoes/<int:posicao>/", views.secao),
    path("participacoes/<uuid:participacao>/concluir/", views.concluir_view),
    path("participacoes/<uuid:participacao>/concluida/", views.concluida),
]

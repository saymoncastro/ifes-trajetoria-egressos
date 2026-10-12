"""Rotas do Portal (024; contracts/rotas.md; 025; 026 plan, "Rotas"; 031 contracts/rotas.md,
incremento 1). Só incluídas com `TRAJETORIA_PORTAL` ligado."""

from django.urls import path

from trajetoria.portal import views
from trajetoria.portal.contribuicao import views_egresso as contribuicao
from trajetoria.portal.contribuicao import views_unidade as contribuicao_unidade
from trajetoria.portal.encontros import views_egresso as encontros
from trajetoria.portal.encontros import views_moderacao as moderacao
from trajetoria.portal.encontros import views_organizador as organizador
from trajetoria.portal.oportunidades import views_curadoria, views_egresso

urlpatterns = [
    path("", views.entrada),
    path("entrar/", views.entrar),
    path("inicio/", views.inicio),
    path("participacao/", views.participacao),
    path("sair/", views.sair),
    path("fontes/<str:nome>", views.fonte),
    path("oportunidades/", views_egresso.oportunidades),
    path("curadoria/oportunidades/", views_curadoria.lista),
    path("curadoria/oportunidades/nova/", views_curadoria.nova),
    path("curadoria/oportunidades/<uuid:pk>/editar/", views_curadoria.editar),
    path("curadoria/oportunidades/<uuid:pk>/publicar/", views_curadoria.publicar),
    path("curadoria/oportunidades/<uuid:pk>/retirar/", views_curadoria.retirar),
    path("contribuir/", contribuicao.contribuir),
    path("contribuir/confirmar/", contribuicao.confirmar),
    path("contribuicoes/", contribuicao.contribuicoes),
    path("contribuicoes/<uuid:pk>/", contribuicao.detalhe),
    path("contribuicoes/<uuid:pk>/retirar/", contribuicao.retirar),
    path("curadoria/contribuicoes/", contribuicao_unidade.lista),
    path("curadoria/contribuicoes/exportar.csv", contribuicao_unidade.exportar),
    path("curadoria/contribuicoes/<uuid:pk>/contato/", contribuicao_unidade.contato),
    path("encontros/", encontros.encontros),
    path("encontros/propor/", organizador.propor),
    path("encontros/propor/enviar/", organizador.enviar),
    path("encontros/seus/", organizador.seus),
    path("encontros/<uuid:pk>/", encontros.pagina),
    path("encontros/<uuid:pk>/participar/", encontros.participar),
    path("encontros/<uuid:pk>/cancelar-participacao/", encontros.cancelar_participacao),
    path("encontros/<uuid:pk>/cancelar/", organizador.cancelar),
    path("curadoria/encontros/", moderacao.lista),
    path("curadoria/encontros/<uuid:pk>/", moderacao.analisar),
    path("curadoria/encontros/<uuid:pk>/recusar/", moderacao.recusar),
    path("curadoria/encontros/<uuid:pk>/retirar/", moderacao.retirar),
]

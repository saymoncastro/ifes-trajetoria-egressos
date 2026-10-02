"""Rotas do editor institucional (Feature 009; contracts/rotas.md). Só existem no modo de
demonstração local: desligado, `ModoDemonstracaoMiddleware` responde 404 antes de resolver
qualquer rota."""

from django.urls import path

from trajetoria.editor import views

urlpatterns = [
    path("", views.pesquisas),
    path("pesquisas/nova/", views.pesquisa_nova),
    path("pesquisas/<uuid:pesquisa>/", views.pesquisa),
    path("pesquisas/<uuid:pesquisa>/versoes/nova/", views.versao_nova),
    path("versoes/<uuid:versao>/", views.versao),
    path("versoes/<uuid:versao>/nova-a-partir/", views.versao_a_partir),
    path("versoes/<uuid:versao>/dados/", views.versao_dados),
    path("versoes/<uuid:versao>/diagnostico/", views.diagnostico),
    path("versoes/<uuid:versao>/previa/", views.previa),
    path("versoes/<uuid:versao>/previa/secoes/<int:ordinal>/", views.previa_secao),
    path("versoes/<uuid:versao>/secoes/nova/", views.secao_nova),
    path("secoes/<uuid:secao>/", views.secao),
    path("secoes/<uuid:secao>/editar/", views.secao_editar),
    path("secoes/<uuid:secao>/mover/", views.secao_mover),
    path("secoes/<uuid:secao>/remover/", views.secao_remover),
    path("secoes/<uuid:secao>/perguntas/nova/", views.pergunta_nova),
    path("perguntas/<uuid:pergunta>/", views.pergunta),
    path("perguntas/<uuid:pergunta>/editar/", views.pergunta_editar),
    path("perguntas/<uuid:pergunta>/mover/", views.pergunta_mover),
    path("perguntas/<uuid:pergunta>/trocar-secao/", views.pergunta_trocar_secao),
    path("perguntas/<uuid:pergunta>/remover/", views.pergunta_remover),
    path("perguntas/<uuid:pergunta>/opcoes/nova/", views.opcao_nova),
    path("opcoes/<uuid:opcao>/", views.opcao_editar),
    path("opcoes/<uuid:opcao>/mover/", views.opcao_mover),
    path("opcoes/<uuid:opcao>/remover/", views.opcao_remover),
]

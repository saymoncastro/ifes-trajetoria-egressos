"""A devolutiva não interfere na pesquisa (021 US4; FR-008; SC-006)."""

import pytest
from django.apps import apps

from tests.narrativa import construcao as cn

pytestmark = pytest.mark.django_db

ROTAS = (
    "/minha-trajetoria/",
    "/minha-trajetoria/?nome=1",
    "/minha-trajetoria/card.svg?nome=1",
    "/minha-trajetoria/card.png?nome=1",
)


def _contagens():
    return {
        modelo._meta.label: modelo.objects.count()
        for modelo in apps.get_models()
        if modelo._meta.app_label != "sessions"
    }


@pytest.mark.parametrize("rota", ROTAS)
def test_abrir_e_baixar_nao_grava_nada(client, cenario, rota):
    maria = cenario.pessoa("SIM-P-0003")
    cenario.concluir(maria.conclusoes.first())
    cn.entrar(client, maria)
    antes = _contagens()
    resposta = client.get(rota)
    assert resposta.status_code == 200
    assert _contagens() == antes

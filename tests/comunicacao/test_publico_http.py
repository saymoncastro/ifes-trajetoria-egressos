from uuid import uuid4

import pytest
from django.test import Client

from tests.editor.construcao_editor import A, B, C

pytestmark = pytest.mark.django_db


def url(c):
    return f"/acompanhamento/campanhas/{c.pk}/comunicacao/"


def test_get_administrativo(campanha, clientes, snapshot):
    antes = snapshot()
    for i in (A, B):
        resposta = clientes[i].get(url(campanha))
        assert resposta.status_code == 200
        assert resposta.context["totais"]["pessoas"] == (9 if i == A else 2)
    assert snapshot() == antes
    assert clientes[C].get(url(campanha)).status_code == 403
    assert Client().get(url(campanha)).status_code == 302
    assert clientes[A].post(url(campanha)).status_code == 405


def test_fora_escopo_inexistente_e_modo(campanha, clientes, settings):
    outra = campanha.__class__.objects.get(nome="Demonstração — coleta sobreposta")
    resposta = clientes[B].get(url(outra))
    assert resposta.status_code == 403
    assert outra.nome not in resposta.content.decode()
    assert clientes[A].get(f"/acompanhamento/campanhas/{uuid4()}/comunicacao/").status_code == 404
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert clientes[A].get(url(campanha)).status_code == 404


def test_erro_origem_sem_dados(campanha, clientes, caplog):
    from trajetoria.academico.models import Pessoa

    Pessoa.objects.all().update(fonte="sentinela-segredo")
    resposta = clientes[A].get(url(campanha))
    assert resposta.status_code == 422
    assert "sentinela-segredo" not in resposta.content.decode() + caplog.text
    assert campanha.nome not in resposta.content.decode()

"""Participação ancorada em Formação Declarada (019) não ganha narrativa (021 FR-007)."""

import pytest
from django.conf import settings

from tests.declaracao import construcao as cd
from tests.participacao import construcao as c

pytestmark = pytest.mark.django_db


def _como_declarante(client, formacao):
    sessao = client.session
    sessao.update({
        "declaracao.formacoes": [str(formacao.pk)],
        "declaracao.confirmada_em": c.NO_PERIODO.isoformat(),
        "declaracao.ultimo_uso": c.NO_PERIODO.isoformat(),
    })
    sessao.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key


def test_confirmacao_declarada_sem_ligacao_para_a_narrativa(client, cenario):
    formacao = cd.declaracao_concluida(cenario.campanha)
    _como_declarante(client, formacao)
    from trajetoria.participacao.models import Participacao

    participacao = Participacao.objects.get(formacao_declarada=formacao)
    resposta = client.get(f"/participacoes/{participacao.pk}/concluida/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "/minha-trajetoria/" not in html
    assert '<a href="/declaracao/">Ver suas formações informadas</a>' in html


def test_declarante_nao_abre_a_narrativa(client, cenario):
    _como_declarante(client, cd.declaracao_concluida(cenario.campanha))
    resposta = client.get("/minha-trajetoria/")
    assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"

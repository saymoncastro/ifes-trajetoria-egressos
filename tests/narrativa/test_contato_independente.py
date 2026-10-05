"""Impacto compartilhado da 020 na tela de conclusão, sem acoplar contato à narrativa
(020 FR-009, FR-010, E7; 021 FR-003 revista, FR-009; T045)."""

import re

import pytest

from tests.contato.conftest import contato
from tests.declaracao import construcao as cd
from tests.narrativa import construcao as cn
from tests.narrativa.test_declarada import _como_declarante
from trajetoria.contato.models import Origem
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db
CONVITE = "Quer manter seu e-mail atualizado com o Ifes?"


@pytest.fixture
def maria(cenario):
    pessoa = cenario.pessoa("SIM-P-0003")
    cenario.concluir(pessoa.conclusoes.first())
    return pessoa


def _principal(resposta):
    return resposta.content.decode().split('<main id="conteudo"')[1].split("</main>")[0]


def test_conclusao_acao_principal_primeiro_e_convite_depois(client, maria):
    cn.entrar(client, maria)
    participacao = Participacao.objects.get(conclusao__pessoa=maria, concluida_em__isnull=False)
    principal = _principal(client.get(f"/participacoes/{participacao.pk}/concluida/"))
    links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', principal)
    assert links[-2:] == [
        ("/minha-trajetoria/", "Ver minha trajetória no Ifes"), ("/meu-email/", CONVITE),
    ]
    assert 'class="nota convite-contato"' in principal


def test_conclusao_declarada_sem_convite(client, cenario):
    formacao = cd.declaracao_concluida(cenario.campanha)
    _como_declarante(client, formacao)
    participacao = Participacao.objects.get(formacao_declarada=formacao)
    html = client.get(f"/participacoes/{participacao.pk}/concluida/").content.decode()
    assert CONVITE not in html and "/meu-email/" not in html
    assert client.get("/meu-email/")["Location"] == "/acesso/"  # declarante não tem Pessoa


def _sem_csrf(conteudo: bytes) -> str:
    return re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", conteudo.decode())


def test_narrativa_e_card_identicos_com_e_sem_contato(client, maria):
    cn.entrar(client, maria)

    def retrato():
        return tuple(
            _sem_csrf(client.get(u).content)
            for u in ("/minha-trajetoria/", "/minha-trajetoria/card.svg")
        )

    antes = retrato()
    contato(maria, "marcador-maria@example.invalid", Origem.EGRESSO)
    depois = retrato()
    assert antes == depois
    for texto in depois:
        assert CONVITE not in texto and "/meu-email/" not in texto
        assert "example.invalid" not in texto

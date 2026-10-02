"""Pesquisas no editor (US1, US2; FR-007 a FR-012)."""

import re

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Pesquisa

pytestmark = pytest.mark.django_db


# --- US1: listar ---------------------------------------------------------------------------


def test_lista_pesquisas_com_quantidade_de_versoes(client, pesquisa):
    op.criar_versao(pesquisa, "A")
    op.criar_versao(pesquisa, "B")
    op.criar_pesquisa("Outra pesquisa fictícia")
    resposta = client.get("/editor/")
    assert resposta.status_code == 200
    texto = ce.texto_visivel(resposta)
    assert "Pesquisa fictícia de teste" in texto and "2 Versões" in texto
    assert "Outra pesquisa fictícia" in texto and "nenhuma Versão" in texto
    assert f'href="/editor/pesquisas/{pesquisa.pk}/"' in resposta.content.decode()
    assert ce.padroes_tecnicos(resposta) == []


def test_lista_vazia(client, db):
    resposta = client.get("/editor/")
    assert "Ainda não há Pesquisas" in ce.texto_visivel(resposta)
    assert 'href="/editor/pesquisas/nova/"' in resposta.content.decode()


# --- US2: criar --------------------------------------------------------------------------


def test_formulario_pede_somente_o_nome(client, db):
    html = client.get("/editor/pesquisas/nova/").content.decode()
    assert set(re.findall(r'name="([^"]+)"', html)) == {"csrfmiddlewaretoken", "nome", "viewport"}


def test_cria_pesquisa(client, db):
    resposta = client.post("/editor/pesquisas/nova/", {"nome": "Pesquisa de teste"})
    pesquisa = Pesquisa.objects.get(nome="Pesquisa de teste")
    assert resposta.status_code == 302
    assert resposta["Location"] == f"/editor/pesquisas/{pesquisa.pk}/?aviso=pesquisa-criada"
    assert pesquisa.versoes.count() == 0
    seguinte = client.get(resposta["Location"])
    assert "Pesquisa criada." in ce.texto_visivel(seguinte)


@pytest.mark.parametrize("nome", ["", "   "])
def test_nome_vazio_recusado_no_campo(client, db, nome):
    antes = ce.contagens()
    resposta = client.post("/editor/pesquisas/nova/", {"nome": nome})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Informe o texto." in html and 'id="id_nome-erro"' in html
    assert ce.contagens() == antes


def test_nome_repetido_pede_confirmacao_e_nao_proibe(client, db):
    op.criar_pesquisa("Pesquisa de teste")
    antes = ce.contagens()
    resposta = client.post("/editor/pesquisas/nova/", {"nome": "Pesquisa de teste"})
    assert resposta.status_code == 200
    assert "Já existe uma Pesquisa com este nome" in ce.texto_visivel(resposta)
    assert 'name="confirmar_nome_repetido"' in resposta.content.decode()
    assert ce.contagens() == antes
    confirmado = client.post(
        "/editor/pesquisas/nova/", {"nome": "Pesquisa de teste", "confirmar_nome_repetido": "on"}
    )
    assert confirmado.status_code == 302
    assert Pesquisa.objects.filter(nome="Pesquisa de teste").count() == 2


def test_sem_renomear_nem_excluir(client, pesquisa):
    for sufixo in ("editar/", "renomear/", "remover/", "excluir/"):
        assert client.get(f"/editor/pesquisas/{pesquisa.pk}/{sufixo}").status_code == 404

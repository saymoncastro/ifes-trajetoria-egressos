import re

import pytest
from django.test import Client

from tests.declaracao.construcao import CPF, DADOS, DATA
from tests.participacao import construcao as c
from trajetoria.declaracao.models import FormacaoDeclarada
from trajetoria.declaracao.selo import selar_transito

pytestmark = pytest.mark.django_db


def token(resposta):
    return re.search(r'name="selo" value="([^"]+)"', resposta.content.decode())[1]


def preparar():
    c.campanha_aberta(c.instrumento().versao)
    # Vocabulário da demonstração sem criar a identidade do declarante.
    x = c.conclusao()
    x.nivel = "Técnico"
    x.save()


def test_fluxo_idempotente(client):
    preparar()
    transito = selar_transito(CPF, DATA)
    r = client.post("/declaracao/", {"selo": transito})
    assert r.status_code == 200 and "no-store" in r["Cache-Control"]
    assert client.get("/declaracao/nova/").status_code == 405
    r = client.post("/declaracao/nova/", {"selo": transito, **DADOS})
    assert r.status_code == 200 and "Formação informada por você" in r.content.decode()
    inicio = token(r)
    a = client.post("/declaracao/comecar/", {"selo": inicio})
    b = client.post("/declaracao/comecar/", {"selo": inicio})
    assert a.status_code == 303 and a["Location"] == b["Location"]
    assert FormacaoDeclarada.objects.count() == 1
    assert CPF not in a["Location"]
    assert client.get(a["Location"]).status_code == 302
    assert client.get("/declaracao/").status_code == 200
    assert Client().get(a["Location"])["Location"] == "/acesso/"


def test_selo_invalido_chave_indisponivel(client, settings):
    assert client.post("/declaracao/", {"selo": "adulterado"})["Location"] == "/acesso/"
    settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO = ""
    r = client.post("/declaracao/", {"selo": ""})
    assert r.status_code == 503
    assert not FormacaoDeclarada.objects.exists()


def test_desistir_sem_gravar(client):
    preparar()
    r = client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    assert r.status_code == 200
    assert not FormacaoDeclarada.objects.exists()


def test_botao_somente_em_nao_confirmada(client, settings):
    from tests.acesso.construcao import ANA, preparar_material

    preparar_material("SIM-P-0001")
    inexistente = client.post("/acesso/", {"cpf": CPF, "data_nascimento": "12/04/1998"})
    errado = client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": "12/04/1999"})
    for r in (inexistente, errado):
        html = r.content.decode()
        assert r.status_code == 200 and "Informar minha formação" in html
        assert html.index("Conferir os dados") < html.index("Informar minha formação")
    invalido = client.post("/acesso/", {"cpf": "123", "data_nascimento": "12/04/1998"})
    assert "Informar minha formação" not in invalido.content.decode()
    confirmada = client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento})
    assert confirmada.status_code == 303 and "selo" not in str(confirmada.headers)
    settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO = ""
    indisponivel = client.post("/acesso/", {"cpf": CPF, "data_nascimento": "12/04/1998"})
    assert indisponivel.status_code == 503
    assert "Informar minha formação" not in indisponivel.content.decode()


def test_avisos_de_salvar_e_sair_do_declarante(client):
    # Regressão (code review da 019): os dois avisos da 014 chegam ao declarante; "saida"
    # não pode ser ignorado nem confundido com "salvo".
    from trajetoria.interface.mensagens import AVISOS

    preparar()
    client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    saida = client.get("/declaracao/?aviso=saida").content.decode()
    assert AVISOS["saida"] in saida and AVISOS["salvo"] not in saida
    salvo = client.get("/declaracao/?aviso=salvo").content.decode()
    assert AVISOS["salvo"] in salvo
    assert AVISOS["saida"] not in client.get("/declaracao/?aviso=outro").content.decode()

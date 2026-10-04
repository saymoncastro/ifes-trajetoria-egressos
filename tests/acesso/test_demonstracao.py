import pytest

from tests.acesso.construcao import ANA, DADOS

pytestmark = pytest.mark.django_db


def test_painel_sem_banco(django_assert_num_queries):
    from trajetoria.acesso.demonstracao import painel

    with django_assert_num_queries(0):
        linhas = painel()
    assert len(linhas) == 13
    assert [linha["cpf"] for linha in linhas[:12]] == [d.cpf for d in DADOS]
    assert [linha["nascimento"] for linha in linhas[:12]] == [d.nascimento for d in DADOS]
    assert "compartilhado" in linhas[9]["nota"]
    assert "Sem CPF" in linhas[4]["nota"]
    assert "Sem data" in linhas[8]["nota"]


def test_painel_post_real(preparado, client):
    r = client.get("/acesso/")
    assert r.content.decode().count(">Usar estes dados</button>") == 13
    assert (
        client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}).status_code
        == 303
    )
    assert (
        client.post(
            "/acesso/", {"cpf": "000.000.009-49", "data_nascimento": "30/06/2001"}
        ).status_code
        == 200
    )

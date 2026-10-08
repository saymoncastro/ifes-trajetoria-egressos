import pytest
from django.core.cache import caches
from django.test import Client

from tests.acesso.construcao import ANA, linhas_de_dominio
from trajetoria.academico.models import Pessoa

pytestmark = pytest.mark.django_db


def post(client, dados=ANA):
    return client.post("/acesso/", {"cpf": dados.cpf, "data_nascimento": dados.nascimento})


def test_entrada_e_confirmacao(preparado, client):
    antes = linhas_de_dominio()
    r = client.get("/acesso/?cpf=segredo&data_nascimento=segredo")
    assert r.status_code == 200 and "no-store" in r["Cache-Control"]
    assert 'value="segredo"' not in r.content.decode()
    r = post(client)
    assert r.status_code == 303 and r["Location"] == "/formacoes/"
    assert len(dict(client.session)) == 4 and linhas_de_dominio() == antes
    # Raiz revisada pela 024 (FR-005): com o Portal ligado, é a entrada do Portal.
    assert client.get("/")["Location"] == "/inicio/"
    assert client.get("/formacoes/").status_code == 200
    assert client.get("/editor/").status_code == 302
    assert client.get("/acompanhamento/").status_code == 302


def test_metodos_csrf_compatibilidade_e_raiz(preparado, client, settings):
    assert client.get("/")["Location"] == "/entrar/"  # 024 FR-005: entrada do Portal
    assert client.get("/formacoes/")["Location"] == "/acesso/"
    assert Client(enforce_csrf_checks=True).post("/acesso/").status_code == 403
    assert client.put("/acesso/").status_code == 405
    r = client.get("/demonstracao/")
    assert r.status_code == 301 and r["Location"] == "/acesso/"
    for url in ("/demonstracao/escolher/", "/demonstracao/encerrar/"):
        assert client.post(url).status_code == 404
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert client.get("/acesso/").status_code == 404


def test_base_nao_simulada_nao_avalia(client, monkeypatch):
    from trajetoria.acesso import views

    Pessoa.objects.create(fonte="outra", id_externo="X")
    monkeypatch.setattr(views, "verificar", lambda *a, **kw: pytest.fail("avaliou"))
    for r in (client.get("/acesso/"), post(client)):
        assert r.status_code == 422
        assert (
            "A entrada de demonstração não pode ser usada com este banco de dados."
            in r.content.decode()
        )
        assert "Dados fictícios para demonstração" not in r.content.decode()
        assert "<input" not in r.content.decode()
    assert not caches["acesso"]._cache


def _sem_eco(html):
    import re

    return re.sub(r'value="[^"]*"', 'value=""', html)


def test_nao_confirmadas_identicas_preservam_sessao(preparado, client, relogio):
    from django.core.cache import caches

    from tests.acesso.test_verificacao import CASOS_NAO_CONFIRMADOS

    post(client)
    antes = linhas_de_dominio()
    chave = client.session.session_key
    sessao = dict(client.session)
    respostas = []
    for cpf, data in CASOS_NAO_CONFIRMADOS:
        caches["acesso"].clear()
        r = client.post("/acesso/", {"cpf": cpf, "data_nascimento": data})
        html = r.content.decode()
        assert r.status_code == 200
        assert "Não foi possível confirmar os dados informados." in html
        assert 'href="#cpf"' in html
        assert f'value="{cpf}"' in html and f'value="{data}"' in html
        assert 'tabindex="-1"' in html and "autofocus" in html
        assert "no-store" in r["Cache-Control"]
        assert dict(client.session) == sessao and client.session.session_key == chave
        assert linhas_de_dominio() == antes
        respostas.append(_sem_eco(html))
    assert len(set(respostas)) == 1


def test_formato_invalido_orienta_campos(preparado, client):
    r = client.post("/acesso/", {"cpf": "123", "data_nascimento": "31/02/2000"})
    html = r.content.decode()
    assert r.status_code == 200
    assert "Confira o CPF informado." in html and "Confira a data de nascimento informada." in html
    assert 'aria-invalid="true"' in html
    assert "Não foi possível confirmar os dados informados." not in html

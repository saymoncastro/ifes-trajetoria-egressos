"""Entrada 018 e isolamento do modo de demonstração; substitui o seletor da 008."""

from uuid import uuid4

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db
ROTAS = (
    "/",
    "/acesso/",
    "/acesso/sair/",
    "/demonstracao/",
    "/demonstracao/escolher/",
    "/demonstracao/encerrar/",
    "/demonstracao/operador/",
    "/demonstracao/operador/escolher/",
    "/demonstracao/operador/encerrar/",
    "/formacoes/",
    "/formacoes/entrar/",
    f"/participacoes/{uuid4()}/",
    f"/participacoes/{uuid4()}/secoes/1/",
    f"/participacoes/{uuid4()}/concluir/",
    f"/participacoes/{uuid4()}/concluida/",
)


@pytest.fixture
def pessoas():
    ce.incorporar(FonteSimulada())
    return {p.id_externo: p for p in Pessoa.objects.all()}


@pytest.mark.parametrize("rota", ROTAS)
def test_modo_desligado_toda_rota_e_404(client, settings, pessoas, rota):
    ci.entrar_como(client, pessoas["SIM-P-0003"])
    settings.TRAJETORIA_DEMONSTRACAO = False
    for metodo in (client.get, client.post):
        r = metodo(rota)
        assert r.status_code == 404
        texto = ci.texto_visivel(r)
        assert "Maria" not in texto and "Ambiente de demonstração" not in texto


def test_modo_desligado_nao_consulta_o_banco(client, settings, pessoas, django_assert_num_queries):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    settings.TRAJETORIA_DEMONSTRACAO = False
    with django_assert_num_queries(0):
        assert client.get("/formacoes/").status_code == 404


def test_base_nao_simulada_recusa_sem_painel(client, pessoas):
    Pessoa.objects.create(fonte="teste-interface", id_externo="TI-1", nome="Zé Real")
    r = client.get("/acesso/")
    assert r.status_code == 422
    assert "Zé Real" not in ci.texto_visivel(r)
    assert "Dados fictícios para demonstração" not in ci.texto_visivel(r)


def test_painel_ficticio_nao_depende_do_preparo(client):
    texto = ci.texto_visivel(client.get("/acesso/"))
    for nome in ("Ana Exemplo", "Maria Exemplo", "Diego Exemplo", "Bruno Exemplo"):
        assert nome in texto
    assert "Pessoa fictícia sem nome informado" in texto
    assert texto.count("Carla Exemplo") >= 2
    assert "CPF compartilhado" in texto
    assert "Licenciatura em Pedagogia" not in texto


def test_inicio_redireciona_conforme_a_pessoa(client, pessoas):
    assert client.get("/")["Location"] == "/acesso/"
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    assert client.get("/")["Location"] == "/formacoes/"


def test_cookie_antigo_nao_autoriza_jornada(client):
    client.cookies["trajetoria_demonstracao_pessoa"] = "qualquer-coisa"
    assert client.get("/formacoes/")["Location"] == "/acesso/"


def test_cabecalho_mostra_sessao_sem_seletor(client, pessoas):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    texto = ci.texto_visivel(client.get("/formacoes/"))
    assert "Pessoa fictícia: Ana Exemplo" in texto
    assert "Trocar de pessoa" not in texto and "Encerrar demonstração" not in texto
    assert "não é autenticação forte" in texto


def test_seletor_removido(client):
    for url in ("/demonstracao/escolher/", "/demonstracao/encerrar/"):
        assert client.get(url).status_code == 404
        assert client.post(url).status_code == 404


def test_allowed_hosts_sem_espacos(monkeypatch):
    import runpy
    from pathlib import Path

    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", " localhost , 127.0.0.1,, ")
    configuracao = runpy.run_path(str(Path(__file__).resolve().parents[2] / "config/settings.py"))
    assert configuracao["ALLOWED_HOSTS"] == ["localhost", "127.0.0.1"]

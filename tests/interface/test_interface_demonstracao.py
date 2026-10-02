"""Entrada de demonstração e modo de demonstração (008 US1; FR-001 a FR-011; SC-012)."""

from uuid import uuid4

import pytest
from django.core import signing

from tests.interface import construcao_interface as ci
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import Pessoa
from trajetoria.demonstracao.entrada import COOKIE, SALT
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db

ROTAS = (
    "/",
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


def _cookie_de(pessoa) -> str:
    return signing.get_cookie_signer(salt=COOKIE + SALT).sign(str(pessoa.pk))


# --- Modo desligado -----------------------------------------------------------------------


@pytest.mark.parametrize("rota", ROTAS)
def test_modo_desligado_toda_rota_e_404(client, settings, pessoas, rota):
    ci.entrar_como(client, pessoas["SIM-P-0003"])  # cookie válido, gravado com o modo ligado
    settings.TRAJETORIA_DEMONSTRACAO = False
    for metodo in (client.get, client.post):
        resposta = metodo(rota)
        assert resposta.status_code == 404
        texto = ci.texto_visivel(resposta)
        assert "Maria" not in texto and "Ambiente de demonstração" not in texto
        assert "Trocar de pessoa" not in texto


def test_modo_desligado_nao_consulta_o_banco(client, settings, pessoas, django_assert_num_queries):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    settings.TRAJETORIA_DEMONSTRACAO = False
    with django_assert_num_queries(0):
        assert client.get("/formacoes/").status_code == 404


# --- Entrada de demonstração -----------------------------------------------------------------


def test_lista_so_pessoas_da_fonte_simulada(client, pessoas):
    Pessoa.objects.create(fonte="teste-interface", id_externo="TI-1", nome="Zé Real")
    resposta = client.get("/demonstracao/")
    assert resposta.status_code == 200
    texto = ci.texto_visivel(resposta)
    assert "Zé Real" not in texto
    for nome in ("Ana Exemplo", "Maria Exemplo", "Diego Exemplo", "Bruno Exemplo"):
        assert nome in texto
    assert "Pessoa fictícia sem nome informado" in texto
    assert "Ambiente de demonstração." in texto
    assert ci.tecnicos_em(texto) == []


def test_homonimas_distintas_pelo_resumo_das_formacoes(client, pessoas):
    texto = ci.texto_visivel(client.get("/demonstracao/"))
    assert texto.count("Carla Exemplo") >= 2
    assert "Licenciatura em Pedagogia · Vitória · 2016" in texto
    assert "Tecnologia em Redes de Computadores · Serra · 2023" in texto


def test_ordem_por_nome_e_estavel(client, pessoas):
    texto = ci.texto_visivel(client.get("/demonstracao/"))
    posicoes = [texto.index(n) for n in ("Ana Exemplo", "Bruno Exemplo", "Diego Exemplo")]
    assert posicoes == sorted(posicoes)
    assert texto.index("Pessoa fictícia sem nome informado") > texto.index("Maria Exemplo")
    assert ci.texto_visivel(client.get("/demonstracao/")) == texto


def test_sem_pessoas_orienta_o_preparo(client):
    texto = ci.texto_visivel(client.get("/demonstracao/"))
    assert "Nenhuma pessoa fictícia preparada" in texto


def test_escolher_grava_so_o_cookie(client, pessoas):
    antes = ce.linhas()
    resposta = client.post("/demonstracao/escolher/", {"pessoa": str(pessoas["SIM-P-0003"].pk)})
    assert resposta.status_code == 302 and resposta["Location"] == "/formacoes/"
    assert COOKIE in resposta.cookies
    assert resposta.cookies[COOKIE]["httponly"]
    assert resposta.cookies[COOKIE]["samesite"] == "Lax"
    assert not resposta.cookies[COOKIE]["max-age"]
    assert ce.linhas() == antes


@pytest.mark.parametrize("valor", ["outra-fonte", "inexistente", "malformado", ""])
def test_escolher_pessoa_invalida_e_404(client, pessoas, valor):
    outra = Pessoa.objects.create(fonte="teste-interface", id_externo="TI-2")
    pk = {"outra-fonte": str(outra.pk), "inexistente": str(uuid4()), "malformado": "x"}
    resposta = client.post("/demonstracao/escolher/", {"pessoa": pk.get(valor, "")})
    assert resposta.status_code == 404
    assert COOKIE not in resposta.cookies


def test_escolher_por_get_e_405(client):
    assert client.get("/demonstracao/escolher/").status_code == 405
    assert client.get("/demonstracao/encerrar/").status_code == 405


def test_inicio_redireciona_conforme_a_pessoa(client, pessoas):
    assert client.get("/")["Location"] == "/demonstracao/"
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    assert client.get("/")["Location"] == "/formacoes/"


def test_cabecalho_mostra_a_pessoa_e_as_acoes(client, pessoas):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    texto = ci.texto_visivel(client.get("/demonstracao/"))
    assert "Pessoa fictícia: Ana Exemplo" in texto
    assert "Trocar de pessoa" in texto and "Encerrar demonstração" in texto


@pytest.mark.parametrize("caso", ["adulterado", "removida", "outra-fonte"])
def test_cookie_invalido_volta_a_entrada(client, pessoas, caso):
    if caso == "adulterado":
        client.cookies[COOKIE] = "qualquer-coisa"
    elif caso == "removida":
        client.cookies[COOKIE] = _cookie_de(Pessoa(pk=uuid4()))
    else:
        outra = Pessoa.objects.create(fonte="teste-interface", id_externo="TI-3")
        client.cookies[COOKIE] = _cookie_de(outra)
    resposta = client.get("/formacoes/")
    assert resposta.status_code == 302 and resposta["Location"] == "/demonstracao/"


def test_encerrar_apaga_o_cookie(client, pessoas):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    resposta = client.post("/demonstracao/encerrar/")
    assert resposta.status_code == 302 and resposta["Location"] == "/demonstracao/"
    assert resposta.cookies[COOKIE].value == ""
    assert client.get("/formacoes/")["Location"] == "/demonstracao/"


def test_pessoa_lida_uma_vez_por_requisicao(pessoas, django_assert_num_queries):
    from django.test import RequestFactory

    from trajetoria.demonstracao.entrada import pessoa_em_uso

    requisicao = RequestFactory().get("/")
    requisicao.COOKIES[COOKIE] = _cookie_de(pessoas["SIM-P-0001"])
    with django_assert_num_queries(1):
        assert pessoa_em_uso(requisicao) == pessoa_em_uso(requisicao) == pessoas["SIM-P-0001"]


def test_trocar_de_pessoa_e_ligacao_e_encerrar_e_o_unico_post(client, pessoas):
    ci.entrar_como(client, pessoas["SIM-P-0001"])
    html = client.get("/demonstracao/").content.decode()
    assert '<a href="/demonstracao/">Trocar de pessoa</a>' in html
    assert html.count('action="/demonstracao/encerrar/"') == 1
    assert 'name="acao"' not in html


def test_allowed_hosts_sem_espacos(monkeypatch):
    import runpy
    from pathlib import Path

    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", " localhost , 127.0.0.1,, ")
    configuracao = runpy.run_path(str(Path(__file__).resolve().parents[2] / "config/settings.py"))
    assert configuracao["ALLOWED_HOSTS"] == ["localhost", "127.0.0.1"]

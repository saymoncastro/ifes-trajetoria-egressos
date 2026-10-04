"""Operador fictício no modo de demonstração (Feature 010 US2; spec FR-053 a FR-061;
contracts/demonstracao-operador.md).

A escolha só **identifica** o operador; as atuações exibidas vêm dos vínculos de governança.
"""

from io import StringIO

import pytest
from django.core import signing
from django.core.management import CommandError, call_command
from django.test import RequestFactory

from tests.interface import construcao_interface as ci
from trajetoria.demonstracao.operador import COOKIE, OPERADORES_FICTICIOS, SALT, operador_em_uso
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.operacoes import desativar_vinculo, registrar_vinculo

pytestmark = pytest.mark.django_db

A, B, C = (o.identificador for o in OPERADORES_FICTICIOS)


def _assinado(valor: str) -> str:
    return signing.get_cookie_signer(salt=COOKIE + SALT).sign(valor)


def _requisicao(cookie: str | None):
    request = RequestFactory().get("/editor/")
    if cookie is not None:
        request.COOKIES[COOKIE] = cookie
    return request


@pytest.fixture
def vinculos():
    return {
        "a": registrar_vinculo(A, Papel.CPAEG),
        "b": registrar_vinculo(B, Papel.CSAEG, "Vitória"),
    }


# --- Identificação --------------------------------------------------------------------------


def test_tres_operadores_ficticios_fixos():
    assert [o.identificador for o in OPERADORES_FICTICIOS] == [
        "demonstracao:operador-a",
        "demonstracao:operador-b",
        "demonstracao:operador-c",
    ]


def test_operador_em_uso_aceita_so_a_lista_fechada():
    assert operador_em_uso(_requisicao(None)) is None
    assert operador_em_uso(_requisicao(_assinado(A))) == A
    assert operador_em_uso(_requisicao(_assinado("pessoa-real"))) is None
    assert operador_em_uso(_requisicao(A)) is None  # sem assinatura
    assert operador_em_uso(_requisicao(_assinado(A) + "x")) is None  # adulterado


def test_operador_em_uso_none_com_modo_desligado(settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert operador_em_uso(_requisicao(_assinado(A))) is None


# --- Telas ----------------------------------------------------------------------------------


def test_lista_mostra_atuacoes_lidas_dos_vinculos(client, vinculos):
    texto = ci.texto_visivel(client.get("/demonstracao/operador/"))
    assert "Operador fictício A" in texto and "Operador fictício C" in texto
    assert "Comissão Própria de Acompanhamento do Egresso (CPAEG) — atuação institucional" in texto
    assert "Comissão Setorial de Acompanhamento de Egressos (CSAEG) — unidade Vitória" in texto
    assert "Sem atuação institucional ativa" in texto
    assert "decorre dos vínculos de governança registrados" in texto
    assert "demonstracao:operador" not in texto
    desativar_vinculo(vinculos["a"])
    texto = ci.texto_visivel(client.get("/demonstracao/operador/"))
    assert "— atuação institucional" not in texto
    assert texto.count("Sem atuação institucional ativa") == 2


def test_escolher_volta_ao_inicio_do_editor(client):
    resposta = client.post("/demonstracao/operador/escolher/", {"operador": A})
    assert resposta.status_code == 302 and resposta["Location"] == "/editor/"
    assert client.cookies[COOKIE].value
    assert operador_em_uso(_requisicao(client.cookies[COOKIE].value)) == A


def test_escolher_identificador_fora_da_lista_e_404(client):
    resposta = client.post("/demonstracao/operador/escolher/", {"operador": "pessoa-real"})
    assert resposta.status_code == 404 and COOKIE not in client.cookies


# --- Destino fechado (Feature 011; research R13) ------------------------------------------------


def test_escolha_com_destino_acompanhamento(client):
    html = client.get("/demonstracao/operador/?destino=acompanhamento").content.decode()
    assert '<input type="hidden" name="destino" value="acompanhamento">' in html
    resposta = client.post(
        "/demonstracao/operador/escolher/", {"operador": B, "destino": "acompanhamento"}
    )
    assert resposta.status_code == 302 and resposta["Location"] == "/acompanhamento/"


@pytest.mark.parametrize(
    "destino", ["qualquer-coisa", "/externo/", "https://exemplo.invalid/", "/acompanhamento/", ""]
)
def test_destino_fora_da_lista_fechada_volta_ao_editor(client, destino):
    resposta = client.post("/demonstracao/operador/escolher/", {"operador": A, "destino": destino})
    assert resposta["Location"] == "/editor/"
    html = client.get(f"/demonstracao/operador/?destino={destino}").content.decode()
    assert 'name="destino"' not in html


def test_links_para_as_duas_areas_do_operador_em_uso(client):
    assert 'href="/acompanhamento/"' not in client.get("/demonstracao/operador/").content.decode()
    client.post("/demonstracao/operador/escolher/", {"operador": B})
    html = client.get("/demonstracao/operador/").content.decode()
    assert 'href="/editor/"' in html and 'href="/acompanhamento/"' in html
    texto = ci.texto_visivel(client.get("/demonstracao/operador/"))
    assert "Editor do instrumento" in texto and "Acompanhamento da coleta" in texto


def test_trocar_e_encerrar(client):
    client.post("/demonstracao/operador/escolher/", {"operador": A})
    client.post("/demonstracao/operador/escolher/", {"operador": B})
    assert operador_em_uso(_requisicao(client.cookies[COOKIE].value)) == B
    texto = ci.texto_visivel(client.get("/demonstracao/operador/"))
    assert "Atuando agora como Operador fictício B" in texto
    resposta = client.post("/demonstracao/operador/encerrar/")
    assert resposta["Location"] == "/demonstracao/operador/"
    assert client.cookies[COOKIE].value == ""


def test_operador_e_pessoa_ficticia_sao_independentes(client, cenario):
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    client.post("/demonstracao/operador/escolher/", {"operador": B})
    client.post("/acesso/sair/")  # encerra a Pessoa, não o operador
    assert operador_em_uso(_requisicao(client.cookies[COOKIE].value)) == B


# --- Preparo --------------------------------------------------------------------------------


def _preparar():
    call_command("preparar_demonstracao", stdout=StringIO())


def _vinculos():
    return sorted(
        VinculoDeGovernanca.objects.values_list(
            "identificador_operador", "papel", "unidade", "ativo"
        )
    )


def test_preparo_cria_vinculos_de_a_e_b_e_e_idempotente():
    _preparar()
    esperado = [(A, "CPAEG", "", True), (B, "CSAEG", "Vitória", True)]
    assert _vinculos() == esperado
    _preparar()
    assert _vinculos() == esperado


def test_preparo_recusa_vinculo_nao_ficticio():
    registrar_vinculo("servidor-real", Papel.CPAEG)
    with pytest.raises(CommandError, match="vínculos de governança que não são fictícios"):
        _preparar()
    assert _vinculos() == [("servidor-real", "CPAEG", "", True)]

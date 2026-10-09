"""Entradas do Portal e do convite (024 US1, US3; FR-001 a FR-008, FR-030, FR-033 itens 1–5 e
9; contracts/rotas.md)."""

from datetime import timedelta

import pytest

from tests.acesso.construcao import MARIA
from tests.declaracao import construcao as cd
from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from trajetoria.acesso import mensagens as mensagens_acesso
from trajetoria.portal import contexto, mensagens

pytestmark = pytest.mark.django_db


def _local(resposta) -> str:
    assert resposta.status_code in (302, 303), resposta.status_code
    return resposta["Location"]


# --- Caminho B: entrada do Portal (US1) ----------------------------------------------------


def test_raiz_sem_sessao_mostra_a_pagina_publica(client, cenario):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert 'href="/entrar/"' in resposta.content.decode()


def test_raiz_com_pessoa_vai_ao_inicio(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    assert _local(client.get("/")) == "/inicio/"


def test_raiz_e_entrar_com_declarante_vao_para_a_declaracao(client, cenario):
    cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
    assert _local(client.get("/")) == "/declaracao/"
    assert _local(client.get("/entrar/")) == "/declaracao/"
    assert _local(client.get("/inicio/")) == "/declaracao/"


def test_entrar_mostra_a_identificacao_da_018_rotulada(client, cenario):
    resposta = client.get("/entrar/")
    html = resposta.content.decode()
    assert resposta.status_code == 200 and "no-store" in resposta["Cache-Control"]
    assert mensagens.ROTULO_ENTRADA in html
    assert html.count('action="/entrar/"') >= 2  # formulário e painel da demonstração
    assert 'action="/acesso/"' not in html
    assert 'name="cpf"' in html and 'name="data_nascimento"' in html


def test_entrar_com_pessoa_vai_ao_inicio_sem_formulario(client, cenario):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    assert _local(client.get("/entrar/")) == "/inicio/"


def test_identificacao_confirmada_pelo_portal_leva_ao_inicio(client, cenario):
    cp.com_material("SIM-P-0003")
    assert _local(cp.entrar_pelo_portal(client, "SIM-P-0003")) == "/inicio/"
    assert client.get("/inicio/").status_code == 200


def test_nao_confirmada_pelo_portal_tem_a_mesma_saida_da_019(client, cenario):
    cp.com_material("SIM-P-0003")
    dados = {"cpf": MARIA.cpf, "data_nascimento": "01/01/1990"}
    portal = client.post("/entrar/", dados).content.decode()
    assert mensagens_acesso.NAO_CONFIRMADA in portal
    assert 'action="/declaracao/"' in portal and 'name="selo"' in portal


def test_formato_invalido_e_limite_pelo_portal(client, cenario):
    cp.com_material("SIM-P-0003")
    invalido = {"cpf": "abc", "data_nascimento": "x"}
    portal, convite = client.post("/entrar/", invalido), client.post("/acesso/", invalido)
    assert portal.status_code == convite.status_code
    assert "Confira os dados informados" in portal.content.decode()
    errado = {"cpf": MARIA.cpf, "data_nascimento": "01/01/1990"}
    respostas = [client.post("/entrar/", errado) for _ in range(5)]
    limitada = respostas[-1]
    assert limitada.status_code == 429 and "Retry-After" in limitada


def test_parametros_do_cliente_nao_decidem_destino(client, cenario):
    """FR-006: nenhum valor vindo do cliente decide o destino."""
    cp.com_material("SIM-P-0003")
    for consulta in ("?destino=/editor/", "?next=https://exemplo.invalid/", "?proximo=/acesso/"):
        assert client.get("/" + consulta).status_code == 200
        dados = {"cpf": MARIA.cpf, "data_nascimento": MARIA.nascimento, "next": "/editor/"}
        assert _local(client.post("/entrar/" + consulta, dados)) == "/inicio/"
        client.post("/acesso/sair/")


def test_fora_da_demonstracao_o_portal_nao_existe(client, cenario, settings):
    """FR-030."""
    settings.TRAJETORIA_DEMONSTRACAO = False
    for url in ("/", "/entrar/", "/inicio/"):
        assert client.get(url).status_code == 404
    assert contexto.navegacao(type("R", (), {"path": "/inicio/"})()) == {}


# --- Sessão expirada (FR-007) --------------------------------------------------------------


def test_inicio_sem_sujeito_vai_para_entrar(client, cenario):
    assert _local(client.get("/inicio/")) == "/entrar/"


def test_inicio_com_sessao_expirada_avisa_sem_frase_do_envio(client, cenario, relogio,
                                                             monkeypatch):
    cp.entrar(client, cenario.pessoa("SIM-P-0003"))
    relogio.agora += timedelta(minutes=31)
    assert _local(client.get("/inicio/")) == "/entrar/?aviso=sessao"
    monkeypatch.setattr("trajetoria.acesso.pendente.ler", lambda request: object())
    portal = client.get("/entrar/?aviso=sessao").content.decode()
    convite = client.get("/acesso/?aviso=sessao").content.decode()
    assert mensagens_acesso.SESSAO_ENCERRADA in portal
    assert mensagens_acesso.ENVIO_GUARDADO not in portal
    assert mensagens_acesso.ENVIO_GUARDADO in convite  # o caminho do convite não muda


# --- Caminho A: convite (US3; FR-008) ------------------------------------------------------


class TestCaminhoDoConvite:
    def test_identificacao_pelo_convite_leva_a_formacoes(self, client, cenario):
        cp.com_material("SIM-P-0003")
        assert _local(cp.entrar_pelo_convite(client, "SIM-P-0003")) == "/formacoes/"
        html = client.get("/acesso/").content.decode()
        assert "Continuar para suas formações" in html and 'action="/acesso/"' in html
        assert mensagens.ROTULO_ENTRADA not in html

    def test_rascunho_mostra_continuar(self, client, cenario):
        ana = cenario.pessoa("SIM-P-0001")
        ci.iniciar(client, ana)
        texto = ci.texto_visivel(client.get("/formacoes/"))
        assert "Continuar a pesquisa" in texto

    def test_concluida_sem_entrada_pendente_e_com_trajetoria(self, client, cenario):
        ana = cenario.pessoa("SIM-P-0001")
        cenario.concluir(ana.conclusoes.first())
        cp.entrar(client, ana)
        texto = ci.texto_visivel(client.get("/formacoes/"))
        assert "Não há pesquisa pendente para você neste momento." in texto
        assert "Ver minha trajetória no Ifes" in texto

    def test_fora_do_periodo_sem_pesquisa(self, client, cenario, relogio):
        relogio.agora = c.DEPOIS_DO_FIM
        cp.entrar(client, cenario.pessoa("SIM-P-0001"))
        texto = ci.texto_visivel(client.get("/formacoes/"))
        assert "No momento, não há pesquisa disponível para as suas formações." in texto

    def test_declarante_continua_na_declaracao(self, client, cenario):
        cp.sessao_de_declarante(client, cd.declaracao_concluida(cenario.campanha))
        assert client.get("/declaracao/").status_code == 200


class TestCaminhosEquivalentes:
    """Os mesmos estados, entrando pelo Portal: o Início convida e a ação leva à mesma
    escolha de formações do caminho A."""

    def test_rascunho(self, client, cenario):
        ana = cenario.pessoa("SIM-P-0001")
        ci.iniciar(client, ana)
        inicio = ci.texto_visivel(client.get("/inicio/"))
        assert mensagens.ACAO_CONTINUAR in inicio
        assert "Continuar a pesquisa" in ci.texto_visivel(client.get("/formacoes/"))

    def test_concluida(self, client, cenario):
        ana = cenario.pessoa("SIM-P-0001")
        cenario.concluir(ana.conclusoes.first())
        cp.entrar(client, ana)
        inicio = ci.texto_visivel(client.get("/inicio/"))
        assert "Não há pesquisa pendente para você neste momento." in inicio
        assert 'href="/formacoes/" class' not in client.get("/inicio/").content.decode()

    def test_fora_do_periodo(self, client, cenario, relogio):
        relogio.agora = c.DEPOIS_DO_FIM
        cp.entrar(client, cenario.pessoa("SIM-P-0001"))
        inicio = ci.texto_visivel(client.get("/inicio/"))
        assert "No momento, não há pesquisa disponível para as suas formações." in inicio
        assert mensagens.ACAO_RESPONDER not in inicio

    def test_envio_guardado_volta_pela_escolha_de_formacoes(self, client, cenario, settings,
                                                            relogio):
        """023 FR-006 pelo caminho B: o Início não retoma; o convite leva a /formacoes/, que
        retoma uma vez."""
        ana = cenario.pessoa("SIM-P-0001")
        participacao = cp.envio_guardado(client, settings, relogio, ana)
        cp.entrar(client, ana)
        assert client.get("/inicio/").status_code == 200
        assert _local(client.get("/formacoes/")) == f"/participacoes/{participacao}/"


# --- Revisão de código: a sessão anterior, o cache da raiz e o título da aba ----------------


@pytest.mark.parametrize("endereco", ["/acesso/", "/entrar/"])
def test_tentativa_falha_nao_mexe_na_sessao_anterior(client, cenario, relogio, settings,
                                                      endereco):
    """018: um resultado sem confirmação nunca modifica a sessão anterior, em qualquer
    entrada que identifica (024 FR-002)."""
    cp.com_material("SIM-P-0003")
    cp.entrar(client, cenario.pessoa("SIM-P-0001"))
    antes = dict(client.session)
    relogio.agora += timedelta(minutes=2)  # passaria a renovar o último uso
    errado = {"cpf": MARIA.cpf, "data_nascimento": "01/01/1990"}
    assert client.post(endereco, errado).status_code == 200
    assert dict(client.session) == antes
    # Com a sessão já vencida, a tentativa falha também não a descarta.
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=1)
    client.post(endereco, errado)
    assert dict(client.session) == antes


def test_raiz_nao_e_guardada_em_cache(client, cenario):
    assert "no-store" in client.get("/")["Cache-Control"]


def test_titulo_da_aba_segue_o_produto(client, cenario):
    entrar = client.get("/entrar/").content.decode()
    acesso = client.get("/acesso/").content.decode()
    assert "— Portal do Egresso (demonstração)</title>" in entrar
    assert "— Trajetória Ifes (demonstração)</title>" in acesso

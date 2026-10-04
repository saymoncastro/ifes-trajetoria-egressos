"""Iniciar ou retomar a Participação pela interface (008 US3; FR-029 a FR-031, FR-089,
FR-090). A interface só chama a entrada da 007."""

from uuid import uuid4

import pytest
from django.test import Client

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.regras import ParticipacaoRejeitada, coleta_nao_admitida

pytestmark = pytest.mark.django_db


@pytest.fixture
def inst():
    ce.incorporar(FonteSimulada())
    return c.instrumento()


@pytest.fixture
def campanha(inst):
    return c.campanha_aberta(inst.versao)


def _pessoa(id_externo):
    return ce.pessoa_da_fonte(id_externo)


def test_entrada_resolvida_inicia_uma_vez_e_leva_a_secao_atual(client, campanha):
    ana = _pessoa("SIM-P-0001")
    resposta = ci.iniciar(client, ana)
    assert resposta.status_code == 302
    participacao = Participacao.objects.get()
    assert resposta["Location"] == f"/participacoes/{participacao.pk}/"
    assert participacao.conclusao == ana.conclusoes.get() and participacao.campanha == campanha
    destino = client.get(resposta["Location"])
    assert destino["Location"] == f"/participacoes/{participacao.pk}/secoes/1/"
    de_novo = client.post("/formacoes/entrar/")
    assert de_novo["Location"] == resposta["Location"]
    assert Participacao.objects.count() == 1


def test_selecao_cada_formacao_tem_sua_participacao(client, campanha):
    maria = _pessoa("SIM-P-0003")
    ci.entrar_como(client, maria)
    ids = set()
    for conclusao in maria.conclusoes.all():
        resposta = client.post("/formacoes/entrar/", {"formacao": str(conclusao.pk)})
        ids.add(ci.participacao_de(resposta))
    assert len(ids) == 2
    assert {p.conclusao_id for p in Participacao.objects.all()} == {
        c.pk for c in maria.conclusoes.all()
    }


@pytest.mark.parametrize("caso", ["alheia", "inexistente", "malformada"])
def test_formacao_que_nao_e_da_pessoa_e_404(client, campanha, caso):
    alheia = _pessoa("SIM-P-0010").conclusoes.get()
    valor = {"alheia": str(alheia.pk), "inexistente": str(uuid4()), "malformada": "x"}[caso]
    ci.entrar_como(client, _pessoa("SIM-P-0011"))
    antes = ce.linhas()
    resposta = client.post("/formacoes/entrar/", {"formacao": valor})
    assert resposta.status_code == 404
    texto = ci.texto_visivel(resposta)
    assert "Formação não disponível." in texto and alheia.curso not in texto
    assert ce.linhas() == antes


def test_sem_formacao_informada_na_selecao_nada_e_criado(client, campanha):
    resposta = ci.iniciar(client, _pessoa("SIM-P-0003"))
    assert resposta["Location"] == "/formacoes/?aviso=situacao"
    assert not Participacao.objects.exists()


def test_formacao_sem_pesquisa_nada_e_criado(client, inst):
    c.campanha_aberta(inst.versao, niveis=["Pós-graduação"])
    diego = _pessoa("SIM-P-0004")
    resposta = ci.iniciar(client, diego, diego.conclusoes.get(curso="Técnico em Química"))
    assert resposta["Location"] == "/formacoes/?aviso=situacao"
    assert not Participacao.objects.exists()


def test_formacao_ja_concluida_informa_e_nao_cria(client, campanha, inst):
    ana = _pessoa("SIM-P-0001")
    ce.participacao_concluida(campanha, ana.conclusoes.get(), inst)
    resposta = ci.iniciar(client, ana, ana.conclusoes.get())
    assert resposta.status_code == 200
    assert "Esta pesquisa já foi respondida." in ci.texto_visivel(resposta)
    assert Participacao.objects.count() == 1


def test_campanha_encerrada_entre_a_tela_e_a_acao(client, campanha, relogio):
    ci.entrar_como(client, _pessoa("SIM-P-0001"))
    client.get("/formacoes/")
    relogio.agora = c.DEPOIS_DO_FIM
    ci.entrar_como(client, _pessoa("SIM-P-0001"))
    resposta = client.post("/formacoes/entrar/")
    assert resposta["Location"] == "/formacoes/?aviso=situacao"
    assert not Participacao.objects.exists()


def test_rejeicao_da_005_vira_periodo_encerrado(client, campanha, monkeypatch):
    # Só a tradução da rejeição propagada pela 007 (FR-046 da 007); não é cenário de domínio.
    def rejeita(*args, **kwargs):
        raise ParticipacaoRejeitada((coleta_nao_admitida(),))

    monkeypatch.setattr("trajetoria.interface.views.entrar", rejeita)
    resposta = ci.iniciar(client, _pessoa("SIM-P-0001"))
    assert resposta.status_code == 200
    assert "O período de resposta desta pesquisa foi encerrado." in ci.texto_visivel(resposta)


def test_metodos_e_csrf(campanha):
    client = Client(enforce_csrf_checks=True)
    assert client.get("/formacoes/entrar/").status_code == 405
    resposta = client.post("/formacoes/entrar/")
    assert resposta.status_code == 403
    assert "Não foi possível confirmar o envio." in ci.texto_visivel(resposta)


def test_sem_pessoa_vai_para_a_entrada(client, campanha):
    assert client.post("/formacoes/entrar/")["Location"] == "/acesso/"


# --- /participacoes/<id>/ ------------------------------------------------------------------


def _iniciada(client, id_externo="SIM-P-0001"):
    return ci.participacao_de(ci.iniciar(client, _pessoa(id_externo)))


def test_participacao_alheia_ou_inexistente_e_404(client, campanha):
    de_ana = _iniciada(client)
    ci.entrar_como(client, _pessoa("SIM-P-0011"))
    assert client.get(f"/participacoes/{de_ana}/").status_code == 404
    assert client.get(f"/participacoes/{uuid4()}/").status_code == 404


def test_participacao_em_rascunho_vai_para_a_secao_atual(client, campanha):
    pk = _iniciada(client)
    assert client.get(f"/participacoes/{pk}/")["Location"] == f"/participacoes/{pk}/secoes/1/"


def test_participacao_finalizada_vai_para_a_conclusao(client, campanha, inst):
    pk = _iniciada(client)
    c.preencher_instrumento(Participacao.objects.get(pk=pk), inst)
    assert client.get(f"/participacoes/{pk}/")["Location"] == f"/participacoes/{pk}/concluir/"


def test_participacao_concluida_vai_para_a_confirmacao(client, campanha, inst):
    ana = _pessoa("SIM-P-0001")
    participacao = ce.participacao_concluida(campanha, ana.conclusoes.get(), inst)
    ci.entrar_como(client, ana)
    resposta = client.get(f"/participacoes/{participacao.pk}/")
    assert resposta["Location"] == f"/participacoes/{participacao.pk}/concluida/"


def test_participacao_com_campanha_encerrada(client, campanha, relogio):
    pk = _iniciada(client)
    relogio.agora = c.DEPOIS_DO_FIM
    ci.entrar_como(client, _pessoa("SIM-P-0001"))
    resposta = client.get(f"/participacoes/{pk}/")
    assert resposta.status_code == 200
    assert "O período de resposta desta pesquisa foi encerrado." in ci.texto_visivel(resposta)

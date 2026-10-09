"""Fronteiras da contribuição (026 FR-004, FR-008, FR-015 a FR-017; SC-004a, SC-005, SC-006;
T019)."""

import ast
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command

from tests.participacao import construcao as c
from tests.portal import construcao as cp
from tests.portal import construcao_contribuicao as cc
from trajetoria.academico.models import Pessoa
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.contato.models import ContatoDaPessoa
from trajetoria.contato.politica import contato_utilizavel
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import csv_do_dataset
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.models import Manifestacao

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"
CONTRIBUICAO = RAIZ / "portal/contribuicao"


# --- E-mail da contribuição × contato da 020 (D-2602; FR-004, FR-008) ------------------------

@pytest.mark.django_db
def test_contribuir_nao_grava_contato_nem_entra_nos_convites(cenario):
    diego = cenario.pessoa("SIM-P-0004")
    antes = list(ContatoDaPessoa.objects.values())
    escolhido_antes = contato_utilizavel(diego.pk, c.NO_PERIODO)
    manifestacao = cc.registrar(diego, email="so.para.contribuir@example.invalid")
    operacoes.registrar_contato(manifestacao.pk, operador=cc.OPERADOR_A, escopo=cc.ESCOPO_A,
                                agora=c.NO_PERIODO)
    operacoes.retirar(diego, manifestacao.pk, agora=c.NO_PERIODO)
    assert list(ContatoDaPessoa.objects.values()) == antes
    escolhido = contato_utilizavel(diego.pk, c.NO_PERIODO)
    assert escolhido == escolhido_antes
    assert escolhido is None or escolhido.valor != "so.para.contribuir@example.invalid"


@pytest.mark.django_db
def test_operacoes_so_gravam_a_manifestacao(cenario):
    nucleo = {k: v for k, v in cp.contagens().items() if k != "portal.Manifestacao"}
    diego = cenario.pessoa("SIM-P-0004")
    manifestacao = cc.registrar(diego)
    operacoes.registrar_contato(manifestacao.pk, operador=cc.OPERADOR_A, escopo=cc.ESCOPO_A,
                                agora=c.NO_PERIODO)
    operacoes.retirar(diego, manifestacao.pk, agora=c.NO_PERIODO)
    assert {k: v for k, v in cp.contagens().items() if k != "portal.Manifestacao"} == nucleo


@pytest.mark.django_db
def test_fluxo_do_egresso_so_grava_ao_enviar_e_retirar(client, cenario):
    """Critério de entrega 5: abrir, escolher, confirmar com erro e ver não gravam."""
    diego = cenario.pessoa("SIM-P-0004")
    cp.entrar(client, diego)
    conclusao = diego.conclusoes.first()
    antes = cp.contagens()
    client.get("/contribuir/")
    client.post("/contribuir/", cc.escolha(conclusao))
    client.post("/contribuir/confirmar/", cc.confirmacao(conclusao, email="invalido"))
    client.get("/contribuicoes/")
    assert cp.contagens() == antes
    client.post("/contribuir/confirmar/", cc.confirmacao(conclusao))
    assert cp.contagens() == {**antes, "portal.Manifestacao": 1}


# --- Analítico e exportações (FR-016; SC-005) -------------------------------------------------

@pytest.mark.django_db
def test_snapshot_e_exportacao_identicos_com_manifestacoes(cenario, settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "chave-ficticia-de-teste-026-000000000000001"
    cenario.concluir(cenario.pessoa("SIM-P-0001").conclusoes.first())
    op_campanha.encerrar(cenario.campanha)
    snapshot = capturar_snapshot(cenario.campanha)

    def retrato():
        registros = sorted(map(repr, RegistroDoSnapshot.objects.filter(snapshot=snapshot).values()))
        dataset = dataset_exportado(snapshot)
        return (list(SnapshotAnalitico.objects.values()), registros, repr(dataset.dados),
                csv_do_dataset(dataset))

    antes = retrato()
    cc.registrar(cenario.pessoa("SIM-P-0001"), email="contribuicao@example.invalid")
    assert Manifestacao.objects.count() == 1
    assert retrato() == antes
    assert b"contribuicao@example.invalid" not in antes[3]


def _importa(pasta: Path, prefixo: str) -> list[str]:
    infratores = []
    for arquivo in pasta.rglob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text("utf-8"))):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom) and no.module:
                nomes = [no.module]
            infratores += [f"{arquivo.name}: {n}" for n in nomes if n.startswith(prefixo)]
    return infratores


@pytest.mark.parametrize("modulo", ["analitico", "exportacao", "mobilizacao", "contato"])
def test_nucleo_nao_importa_a_contribuicao(modulo):
    assert _importa(RAIZ / modulo, "trajetoria.portal") == []


def test_contribuicao_nao_importa_a_politica_de_convites():
    """O e-mail da contribuição não passa pela 020: só a validação de `contato/endereco.py`
    é reaproveitada (R3)."""
    importados = _importa(CONTRIBUICAO, "trajetoria.contato")
    assert importados and {i.split(": ")[1] for i in importados} == {"trajetoria.contato.endereco"}


# --- Escritas só nas operações (plan, "Testes": fronteira) -------------------------------------

_ESCRITAS = {"create", "save", "update", "delete", "bulk_create", "bulk_update",
             "get_or_create", "update_or_create"}


def test_escritas_so_em_operacoes():
    infratores = []
    for arquivo in CONTRIBUICAO.glob("*.py"):
        if arquivo.name == "operacoes.py":
            continue
        for no in ast.walk(ast.parse(arquivo.read_text("utf-8"))):
            if isinstance(no, ast.Attribute) and no.attr in _ESCRITAS:
                infratores.append(f"{arquivo.name}: {no.attr}")
    assert infratores == []


def test_campos_da_manifestacao():
    """FR-001: só os campos do plan; nenhum CPF, nascimento ou nome copiado."""
    campos = {f.name for f in Manifestacao._meta.get_fields()}
    assert campos == {
        "id", "pessoa_id", "conclusao_id", "unidade", "forma", "mensagem", "email",
        "versao_da_ciencia", "registrada_em", "contato_registrado_em", "contato_registrado_por",
        "retirada_em",
    }


# --- Demonstração (R13) ------------------------------------------------------------------------

@pytest.mark.django_db
def test_preparo_carrega_duas_manifestacoes_idempotente():
    call_command("preparar_demonstracao", stdout=StringIO())
    assert Manifestacao.objects.count() == 2
    unidades = sorted(Manifestacao.objects.values_list("unidade", flat=True))
    assert unidades == ["Vila Velha", "Vitória"]
    assert not ContatoDaPessoa.objects.filter(valor__contains="contribuicao").exists()
    call_command("preparar_demonstracao", stdout=StringIO())
    assert Manifestacao.objects.count() == 2


@pytest.mark.django_db
def test_manifestacao_recusada_desfaz_o_preparo_e_orienta(monkeypatch):
    from django.core.management.base import CommandError

    from trajetoria.portal.contribuicao import demonstracao

    monkeypatch.setattr(demonstracao, "VERSAO_DA_CIENCIA", "antiga")
    with pytest.raises(CommandError, match="manifestações fictícias.*Recrie o banco local"):
        call_command("preparar_demonstracao", stdout=StringIO())
    assert not Manifestacao.objects.exists()
    assert not Pessoa.objects.filter(fonte=FonteSimulada.codigo).exists()


# --- Portal desligado (SC-006) -------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.urls("tests.portal.urls_sem_portal")
def test_rotas_da_contribuicao_nao_existem_sem_o_portal(client, cenario, settings):
    settings.TRAJETORIA_PORTAL = False
    diego = cenario.pessoa("SIM-P-0004")
    manifestacao = cc.registrar(diego)
    cp.entrar(client, diego)
    for url in ("/contribuir/", "/contribuicoes/", f"/contribuicoes/{manifestacao.pk}/",
                "/curadoria/contribuicoes/", "/curadoria/contribuicoes/exportar.csv"):
        assert client.get(url).status_code == 404, url
    assert client.post("/contribuir/confirmar/", cc.confirmacao(diego.conclusoes.first())
                       ).status_code == 404
    assert "/contribuir" not in client.get("/formacoes/").content.decode()

"""Fronteiras dos encontros (031 FR-031 a FR-034; SC-006, SC-008; T032; ADR 0008)."""

import ast
import logging
from pathlib import Path

import pytest

from tests.participacao import construcao as c
from tests.portal import construcao as cp
from tests.portal import construcao_encontros as ce
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.contato.models import ContatoDaPessoa
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import csv_do_dataset
from trajetoria.portal.encontros import operacoes
from trajetoria.portal.models import Confirmacao, Encontro

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"
ENCONTROS = RAIZ / "portal/encontros"
CAMADA = {"portal.Encontro", "portal.Confirmacao"}


def _fora_da_camada(contagens: dict) -> dict:
    return {k: v for k, v in contagens.items() if k not in CAMADA}


@pytest.mark.django_db
def test_operacoes_so_gravam_encontro_e_confirmacao(cenario):
    """FR-031, FR-034: nada do núcleo é gravado, nem contato."""
    maria, diego = cenario.pessoa("SIM-P-0003"), cenario.pessoa("SIM-P-0004")
    antes = _fora_da_camada(cp.contagens())
    contatos = list(ContatoDaPessoa.objects.values())
    encontro = ce.publicado(maria)
    ce.confirmar(diego, encontro)
    operacoes.cancelar_participacao(diego, encontro.pk, agora=c.NO_PERIODO)
    operacoes.cancelar(maria, encontro.pk, agora=c.NO_PERIODO)
    assert _fora_da_camada(cp.contagens()) == antes
    assert list(ContatoDaPessoa.objects.values()) == contatos


@pytest.mark.django_db
def test_abrir_as_telas_nao_grava(client, cenario):
    maria = cenario.pessoa("SIM-P-0003")
    encontro = ce.publicado(maria)
    cp.entrar(client, cenario.pessoa("SIM-P-0004"))
    antes = cp.contagens()
    for url in ("/encontros/", f"/encontros/{encontro.pk}/", "/encontros/propor/",
                "/encontros/seus/", f"/encontros/{encontro.pk}/cancelar-participacao/"):
        client.get(url)
    client.post("/encontros/propor/", ce.formulario(maria.conclusoes.first(), titulo=""))
    assert cp.contagens() == antes


@pytest.mark.django_db
def test_snapshot_e_exportacao_identicos_com_encontros(cenario, settings):
    """FR-032: confirmações e encontros fora do dado analítico."""
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "chave-ficticia-de-teste-031-000000000000001"
    cenario.concluir(cenario.pessoa("SIM-P-0001").conclusoes.first())
    op_campanha.encerrar(cenario.campanha)
    snapshot = capturar_snapshot(cenario.campanha)

    def retrato():
        registros = sorted(map(repr, RegistroDoSnapshot.objects.filter(snapshot=snapshot).values()))
        dataset = dataset_exportado(snapshot)
        return (list(SnapshotAnalitico.objects.values()), registros, repr(dataset.dados),
                csv_do_dataset(dataset))

    antes = retrato()
    encontro = ce.publicado(cenario.pessoa("SIM-P-0003"))
    ce.confirmar(cenario.pessoa("SIM-P-0001"), encontro)
    assert Encontro.objects.count() == 1 and Confirmacao.objects.count() == 1
    assert retrato() == antes


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
def test_nucleo_nao_importa_a_camada(modulo):
    assert _importa(RAIZ / modulo, "trajetoria.portal") == []


def test_encontros_nao_leem_contato_participacao_nem_resposta():
    """FR-033, FR-034: a 031 não usa e-mail nem dado da pesquisa."""
    for prefixo in ("trajetoria.contato", "trajetoria.participacao", "trajetoria.declaracao"):
        assert _importa(ENCONTROS, prefixo) == [], prefixo


_ESCRITAS = {"create", "save", "update", "delete", "bulk_create", "bulk_update",
             "get_or_create", "update_or_create"}


def test_escritas_so_em_operacoes():
    infratores = []
    for arquivo in ENCONTROS.glob("*.py"):
        if arquivo.name == "operacoes.py":
            continue
        for no in ast.walk(ast.parse(arquivo.read_text("utf-8"))):
            if isinstance(no, ast.Attribute) and no.attr in _ESCRITAS:
                infratores.append(f"{arquivo.name}: {no.attr}")
    assert infratores == []


def test_campos_sem_dado_pessoal_copiado():
    """Nenhum CPF, nascimento, nome do registro ou contato no Encontro e na Confirmação. O nome
    de apresentação é declarado pelo organizador (ADR 0010)."""
    for modelo in (Encontro, Confirmacao):
        campos = {f.name for f in modelo._meta.get_fields()} - {"nome_apresentacao"}
        for proibido in ("cpf", "nascimento", "nome", "email", "telefone"):
            assert not any(proibido == c or c.startswith(proibido + "_") for c in campos), (
                modelo.__name__, proibido)


@pytest.mark.django_db
def test_logs_sem_dados_pessoais(cenario, caplog):
    """Constituição XVI (analyze C1): as operações não registram a Pessoa, o link nem o
    complemento."""
    caplog.set_level(logging.DEBUG)
    maria, diego = cenario.pessoa("SIM-P-0003"), cenario.pessoa("SIM-P-0004")
    encontro = ce.publicado(maria)
    ce.confirmar(diego, encontro)
    operacoes.retirar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="outro",
                      complemento="Complemento sigiloso.", agora=c.NO_PERIODO)
    texto = caplog.text
    for sensivel in (str(maria.pk), str(diego.pk), ce.LINK, "Complemento sigiloso."):
        assert sensivel not in texto

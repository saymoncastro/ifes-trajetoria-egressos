"""Metadados fixos para o snapshot (US8; spec FR-060 a FR-067; data-model §3; research R8)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from tests.exportacao import apoio
from trajetoria.analitico.consultas import indicadores_do_snapshot
from trajetoria.campanha.models import Campanha
from trajetoria.exportacao.contrato import NOTAS
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.instrumento.operacoes import renomear_pesquisa

pytestmark = pytest.mark.django_db

CHAVES = [
    ("contrato_versao", "inteiro"),
    ("pseudonimizacao_esquema", "texto"),
    ("finalidade", "texto"),
    ("snapshot", "texto"),
    ("capturado_em", "momento"),
    ("campanha", "texto"),
    ("campanha_nome", "texto"),
    ("campanha_inicio", "data"),
    ("campanha_fim", "data"),
    ("campanha_aberta_em", "momento"),
    ("versao", "texto"),
    ("versao_designacao", "texto"),
    ("versao_titulo", "texto"),
    ("versao_publicada_em", "momento"),
    ("registros", "inteiro"),
    ("elegiveis_no_snapshot", "inteiro"),
    ("nao_elegiveis_com_participacao", "inteiro"),
    ("com_participacao", "inteiro"),
    ("participacoes_concluidas", "inteiro"),
    ("participacoes_com_percurso_nao_determinavel", "inteiro"),
    ("colunas_de_dados", "inteiro"),
    ("nota_snapshot", "texto"),
    ("nota_privacidade", "texto"),
    ("nota_representacao", "texto"),
    ("nota_proveniencia", "texto"),
    ("nota_aplicabilidade", "texto"),
    ("nota_escape_csv", "texto"),
]


def test_chaves_ordem_e_tipos(snapshot):
    linhas = dataset_exportado(snapshot).metadados.linhas
    assert [(chave, tipo) for chave, _, tipo in linhas] == CHAVES


def test_valores_do_snapshot_da_campanha_e_da_versao(snapshot, inst):
    m = apoio.metadados(snapshot)
    campanha, versao = snapshot.campanha, inst.versao
    versao.refresh_from_db()
    assert m["contrato_versao"] == 2
    assert m["pseudonimizacao_esquema"] == "hmac-sha256-v1"
    assert m["snapshot"] == str(snapshot.pk)
    assert m["capturado_em"] == timezone.localtime(snapshot.capturado_em)
    assert m["campanha"] == str(campanha.pk)
    assert m["campanha_nome"] == campanha.nome
    assert (m["campanha_inicio"], m["campanha_fim"]) == (campanha.inicio, campanha.fim)
    assert m["campanha_aberta_em"] == timezone.localtime(campanha.aberta_em)
    assert m["versao"] == str(versao.pk)
    assert m["versao_designacao"] == versao.designacao
    assert m["versao_titulo"] == versao.titulo  # pode ser None
    assert m["versao_publicada_em"] == timezone.localtime(versao.publicada_em)
    for chave in ("capturado_em", "campanha_aberta_em", "versao_publicada_em"):
        assert m[chave].utcoffset() is not None, chave


def test_contagens_iguais_as_de_dados_e_aos_indicadores(snapshot):
    m = apoio.metadados(snapshot)
    indicadores = indicadores_do_snapshot(snapshot)
    linhas = apoio.linhas(snapshot)
    assert m["registros"] == len(linhas) == indicadores.registros
    assert m["elegiveis_no_snapshot"] == indicadores.elegiveis
    assert m["nao_elegiveis_com_participacao"] == indicadores.iniciadas_nao_elegiveis
    assert m["com_participacao"] == sum(1 for x in linhas if x["possui_participacao"])
    assert m["participacoes_concluidas"] == sum(1 for x in linhas if x["participacao_concluida"])
    assert m["participacoes_com_percurso_nao_determinavel"] == 0
    assert m["colunas_de_dados"] == len(dataset_exportado(snapshot).dados.cabecalho)


def test_notas_do_contrato(snapshot):
    m = apoio.metadados(snapshot)
    for chave, texto in NOTAS.items():
        assert m[chave] == texto


def test_ausencias_deliberadas(snapshot, inst, chave_ficticia):
    dataset = dataset_exportado(snapshot)
    chaves = [chave for chave, _, _ in dataset.metadados.linhas]
    assert not [c for c in chaves if any(p in c for p in ("gerado", "export", "chave", "encerr"))]
    celulas = {
        v
        for tabela in (dataset.dados, dataset.dicionario, dataset.metadados)
        for linha in tabela.linhas
        for v in linha
        if isinstance(v, str)
    }
    assert inst.versao.pesquisa.nome not in celulas
    assert not [v for v in celulas if chave_ficticia in v]


def test_reproducao_depois_de_renomear_e_de_encerramento_retroativo(snapshot, inst):
    antes = dataset_exportado(snapshot)
    renomear_pesquisa(inst.versao.pesquisa, "Outro nome da Pesquisa")
    # simula encerramento retroativo (spec C13): `encerrada_em` gravado depois da captura
    Campanha.objects.filter(pk=snapshot.campanha_id).update(
        encerrada_em=snapshot.capturado_em - timedelta(days=1)
    )
    assert dataset_exportado(snapshot) == antes

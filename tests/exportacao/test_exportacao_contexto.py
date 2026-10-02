"""Contexto congelado e estado da Participação (US4; spec FR-003, FR-022 a FR-025; casos P, Q)."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from tests.analitico import construcao as c
from tests.exportacao import apoio
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.pseudonimos import pseudonimo

pytestmark = pytest.mark.django_db

CONTEXTO = ("unidade", "curso", "nivel", "modalidade", "forma_oferta", "ano_conclusao")


def test_alteracao_academica_depois_da_captura_nao_muda_a_exportacao(snapshot, cenario):  # Q
    antes = dataset_exportado(snapshot)
    for conclusao in (cenario.serra_info, cenario.vitoria_info, cenario.serra_eng):
        c.simular_correcao(  # simula 001/DP-005
            conclusao,
            unidade="Cefor",
            curso="Outro",
            nivel="Outro",
            modalidade="Outra",
            forma_oferta="Outra",
            ano_conclusao=1999,
        )
    assert dataset_exportado(snapshot) == antes


def test_valores_sao_os_congelados(snapshot, chave_ficticia):
    retrato = c.retrato(snapshot)  # {conclusao_id: (elegivel, *contexto congelado)}
    linhas = apoio.por_conclusao(snapshot, chave_ficticia)
    for conclusao_id, (elegivel, *contexto) in retrato.items():
        linha = linhas[pseudonimo("conclusao", conclusao_id, chave_ficticia)]
        assert linha["elegivel_no_snapshot"] is elegivel
        # CAMPOS_DE_CONTEXTO: curso, unidade, nivel, modalidade, forma_oferta, ano, data
        assert [linha[n] for n in ("curso", "unidade", "nivel", "modalidade", "forma_oferta")] == (
            contexto[:5]
        )
        assert linha["ano_conclusao"] == contexto[5]
        assert linha["data_conclusao"] == contexto[6]


def test_conclusao_nova_depois_da_captura_nao_aparece(snapshot):
    antes = len(apoio.linhas(snapshot))
    c.conclusao(unidade="Serra", ano=2023)
    assert len(apoio.linhas(snapshot)) == antes


def test_nao_informado_e_ausencia(snapshot, cenario, chave_ficticia):
    linha = apoio.linha_de(snapshot, cenario.vitoria_sem_atributos, chave_ficticia)
    assert all(linha[n] is None for n in CONTEXTO if n != "unidade")
    assert "Não informado" not in {v for v in linha.values() if isinstance(v, str)}


def test_cursos_homonimos_distinguidos_pela_unidade(snapshot, cenario, chave_ficticia):  # P
    serra = apoio.linha_de(snapshot, cenario.serra_info, chave_ficticia)
    vitoria = apoio.linha_de(snapshot, cenario.vitoria_info, chave_ficticia)
    assert serra["curso"] == vitoria["curso"] == "Técnico em Informática"
    assert (serra["unidade"], vitoria["unidade"]) == ("Serra", "Vitória")
    assert not [n for n in serra if "codigo" in n]


def test_concluida(snapshot, cenario, chave_ficticia):
    linha = apoio.linha_de(snapshot, cenario.serra_info, chave_ficticia)
    p = cenario.concluida
    p.refresh_from_db()
    assert (linha["possui_participacao"], linha["participacao_concluida"]) == (True, True)
    assert linha["participacao_iniciada_em"] == timezone.localtime(p.iniciada_em).date()
    assert linha["participacao_concluida_em"] == timezone.localtime(p.concluida_em).date()


def test_rascunho(snapshot, cenario, chave_ficticia):
    linha = apoio.linha_de(snapshot, cenario.serra_eng, chave_ficticia)
    p = cenario.rascunho
    assert (linha["possui_participacao"], linha["participacao_concluida"]) == (True, False)
    assert linha["participacao_iniciada_em"] == timezone.localtime(p.iniciada_em).date()
    assert linha["participacao_concluida_em"] is None


def test_sem_participacao(snapshot, cenario, chave_ficticia):
    linha = apoio.linha_de(snapshot, cenario.vitoria_sem_atributos, chave_ficticia)
    assert linha["possui_participacao"] is False
    assert linha["participacao_concluida"] is None
    assert linha["participacao_iniciada_em"] is None
    assert linha["participacao_concluida_em"] is None


def test_unica_leitura_da_001_e_a_referencia_a_pessoa(snapshot):
    with CaptureQueriesContext(connection) as consultas:
        dataset_exportado(snapshot)
    sqls = [q["sql"] for q in consultas.captured_queries]
    da_001 = [s for s in sqls if "academico_conclusaoacademica" in s]
    assert len(da_001) == 1
    assert '"academico_conclusaoacademica"."pessoa_id"' in da_001[0]
    for coluna in ("curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao"):
        assert f'"academico_conclusaoacademica"."{coluna}"' not in da_001[0]
    assert not [s for s in sqls if "academico_pessoa" in s]

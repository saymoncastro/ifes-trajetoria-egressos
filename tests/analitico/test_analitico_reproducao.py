"""Reprodução sem o estado acadêmico atual (US6, US8, US9, US10; spec FR-080 a FR-091)."""

import ast
from decimal import Decimal
from pathlib import Path

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

import trajetoria
from tests.analitico import construcao as c
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.acompanhamento.apresentacao import AVISO_POPULACAO_ATUAL
from trajetoria.acompanhamento.consultas import (
    Recorte,
    campanha_acompanhada,
    indicadores_da_campanha,
)
from trajetoria.analitico.consultas import (
    IndicadoresDoSnapshot,
    LinhaDoRecorte,
    RecorteDoSnapshot,
    indicadores_do_snapshot,
    recorte_do_snapshot,
)
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao

pytestmark = pytest.mark.django_db

_TABELAS_PROIBIDAS = tuple(
    m._meta.db_table for m in (ConclusaoAcademica, Pessoa, Resposta, RespostaOpcao)
)


def _corrigir_todas(cenario):
    """Simula 001/DP-005 nos seis atributos de todas as Conclusões do universo."""
    for conclusao in (
        cenario.serra_info,
        cenario.vitoria_info,
        cenario.serra_eng,
        cenario.vitoria_sem_atributos,
        cenario.serra_sem_participacao,
    ):
        c.simular_correcao(
            conclusao,
            unidade="Cefor",
            curso="Curso corrigido",
            nivel="Nível corrigido",
            modalidade="A distância",
            forma_oferta="Concomitante",
            ano_conclusao=1999,
        )


# --- US6: o que foi gravado não muda ----------------------------------------------------------


def test_snapshot_identico_depois_de_correcao_e_incorporacao(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = c.retrato(snapshot)
    _corrigir_todas(cenario)
    nova = c.conclusao(unidade="Serra")
    assert c.retrato(snapshot) == antes
    assert nova.pk not in antes


# --- US8: indicadores -------------------------------------------------------------------------

_INSTITUCIONAL = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())


def _sql(consultas) -> str:
    return " ".join(q["sql"] for q in consultas.captured_queries)


def test_indicadores_do_cenario_de_referencia(cenario):
    ind = indicadores_do_snapshot(capturar_snapshot(cenario.campanha))
    assert isinstance(ind, IndicadoresDoSnapshot)
    assert (ind.elegiveis, ind.iniciadas_elegiveis, ind.iniciadas_nao_elegiveis) == (5, 3, 0)
    assert (ind.concluidas_elegiveis, ind.concluidas_nao_elegiveis) == (2, 0)
    assert (ind.iniciadas, ind.concluidas, ind.nao_concluidas) == (3, 2, 1)
    assert ind.registros == 5
    assert ind.taxa_inicio == Decimal(3) / Decimal(5)
    assert ind.taxa_conclusao == Decimal(2) / Decimal(5)


def test_participacao_nao_elegivel_conta_no_numerador_e_taxa_passa_de_100(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    a, b = c.conclusao(unidade="Serra"), c.conclusao(unidade="Serra")
    c.concluida(campanha, a, inst)
    c.iniciada(campanha, b)
    c.conclusao(unidade="Serra")  # a única elegível sem Participação depois da correção
    c.simular_correcao(a, unidade="Vitória")  # simula 001/DP-005
    c.simular_correcao(b, unidade="Vitória")
    ind = indicadores_do_snapshot(capturar_snapshot(campanha))
    assert (ind.elegiveis, ind.iniciadas_elegiveis, ind.iniciadas_nao_elegiveis) == (1, 0, 2)
    assert (ind.concluidas_nao_elegiveis, ind.registros) == (1, 3)
    assert ind.taxa_inicio == Decimal(2)  # 200%, sem truncamento
    assert ind.taxa_conclusao == Decimal(1)


def test_zero_elegiveis_taxas_nao_se_aplicam(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Ninguém"])
    ind = indicadores_do_snapshot(capturar_snapshot(campanha))
    assert ind.elegiveis == 0
    assert ind.taxa_inicio is None and ind.taxa_conclusao is None


def test_indicadores_identicos_depois_de_correcao_e_incorporacao(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = indicadores_do_snapshot(snapshot)
    _corrigir_todas(cenario)
    c.conclusao(unidade="Serra")
    assert indicadores_do_snapshot(snapshot) == antes


def test_logo_apos_a_captura_coincide_com_a_011(cenario):
    ind = indicadores_do_snapshot(capturar_snapshot(cenario.campanha))
    atual = indicadores_da_campanha(cenario.campanha, _INSTITUCIONAL)
    assert (ind.elegiveis, ind.iniciadas, ind.concluidas) == (
        atual.elegiveis,
        atual.iniciadas,
        atual.concluidas,
    )


def test_indicadores_numa_consulta_sem_001_nem_resposta(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    with CaptureQueriesContext(connection) as consultas:
        indicadores_do_snapshot(snapshot)
    assert len(consultas) == 1
    for tabela in _TABELAS_PROIBIDAS:
        assert tabela not in _sql(consultas)


# --- US9: seis recortes -----------------------------------------------------------------------


def _por_chave(linhas) -> dict:
    return {linha.chave: linha.indicadores for linha in linhas}


def test_seis_recortes_com_os_campos_da_011():
    assert [r.name for r in RecorteDoSnapshot] == [r.name for r in Recorte]
    for recorte in RecorteDoSnapshot:
        assert recorte.campos == Recorte[recorte.name].campos


@pytest.mark.parametrize("recorte", list(RecorteDoSnapshot))
def test_soma_das_linhas_e_o_total(cenario, recorte):
    snapshot = capturar_snapshot(cenario.campanha)
    linhas = recorte_do_snapshot(snapshot, recorte)
    assert all(isinstance(linha, LinhaDoRecorte) for linha in linhas)
    soma = IndicadoresDoSnapshot()
    for linha in linhas:
        soma = soma + linha.indicadores
    assert soma == indicadores_do_snapshot(snapshot)


def test_recorte_por_unidade_contagem_manual(cenario):
    linhas = _por_chave(
        recorte_do_snapshot(capturar_snapshot(cenario.campanha), RecorteDoSnapshot.UNIDADE)
    )
    serra, vitoria = linhas[("Serra",)], linhas[("Vitória",)]
    assert (serra.elegiveis, serra.iniciadas, serra.concluidas) == (3, 2, 1)
    assert (vitoria.elegiveis, vitoria.iniciadas, vitoria.concluidas) == (2, 1, 1)
    assert set(linhas) == {("Serra",), ("Vitória",)}


def test_recorte_por_curso_separa_homonimos_e_tem_nao_informado(cenario):
    linhas = _por_chave(
        recorte_do_snapshot(capturar_snapshot(cenario.campanha), RecorteDoSnapshot.CURSO)
    )
    assert linhas[("Serra", "Técnico em Informática")].concluidas == 1
    assert linhas[("Vitória", "Técnico em Informática")].concluidas == 1
    assert linhas[("Vitória", None)].elegiveis == 1  # curso não informado


def test_ano_nao_informado_forma_linha_propria(cenario):
    linhas = _por_chave(
        recorte_do_snapshot(capturar_snapshot(cenario.campanha), RecorteDoSnapshot.ANO_CONCLUSAO)
    )
    assert linhas[(None,)].elegiveis == 1
    assert linhas[(2022,)].elegiveis == 2


def test_nao_elegivel_conta_na_linha_sem_entrar_no_denominador(cenario):
    c.simular_correcao(cenario.serra_info, unidade="Cefor")  # simula 001/DP-005
    linhas = _por_chave(
        recorte_do_snapshot(capturar_snapshot(cenario.campanha), RecorteDoSnapshot.UNIDADE)
    )
    cefor = linhas[("Cefor",)]
    assert (cefor.elegiveis, cefor.iniciadas_nao_elegiveis, cefor.concluidas) == (0, 1, 1)
    assert cefor.taxa_inicio is None


@pytest.mark.parametrize("recorte", list(RecorteDoSnapshot))
def test_recortes_identicos_depois_de_correcao(cenario, recorte):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = recorte_do_snapshot(snapshot, recorte)
    _corrigir_todas(cenario)
    assert recorte_do_snapshot(snapshot, recorte) == antes


@pytest.mark.parametrize("recorte", list(RecorteDoSnapshot))
def test_logo_apos_a_captura_recortes_coincidem_com_a_011(cenario, recorte):
    snapshot = capturar_snapshot(cenario.campanha)
    nossas = {
        linha.chave: (
            linha.indicadores.elegiveis,
            linha.indicadores.iniciadas,
            linha.indicadores.concluidas,
        )
        for linha in recorte_do_snapshot(snapshot, recorte)
    }
    da_011 = campanha_acompanhada(
        cenario.campanha,
        _INSTITUCIONAL,
        pode_consultar_rascunho=True,
        recorte=Recorte[recorte.name],
    ).linhas
    atuais = {
        linha.chave: (
            linha.indicadores.elegiveis,
            linha.indicadores.iniciadas,
            linha.indicadores.concluidas,
        )
        for linha in da_011
        if any((linha.indicadores.elegiveis, linha.indicadores.iniciadas))
    }
    assert nossas == atuais


@pytest.mark.parametrize("recorte", list(RecorteDoSnapshot))
def test_recorte_numa_consulta_sem_001_nem_resposta(cenario, recorte):
    snapshot = capturar_snapshot(cenario.campanha)
    with CaptureQueriesContext(connection) as consultas:
        recorte_do_snapshot(snapshot, recorte)
    assert len(consultas) == 1
    for tabela in _TABELAS_PROIBIDAS:
        assert tabela not in _sql(consultas)


# --- US10: elegibilidade congelada × atual; a 011 não muda ------------------------------------


def test_a_011_continua_mostrando_elegiveis_atuais(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    c.conclusao(unidade="Serra")
    c.conclusao(unidade="Vitória")
    assert indicadores_da_campanha(cenario.campanha, _INSTITUCIONAL).elegiveis == 7
    assert indicadores_do_snapshot(snapshot).elegiveis == 5


def test_a_011_mantem_o_aviso_de_populacao_atual(cenario):
    capturar_snapshot(cenario.campanha)
    acompanhada = campanha_acompanhada(
        cenario.campanha, _INSTITUCIONAL, pode_consultar_rascunho=True
    )
    assert AVISO_POPULACAO_ATUAL in acompanhada.avisos


def _importa_analitico(arquivo: Path) -> bool:
    arvore = ast.parse(arquivo.read_text())
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and (no.module or "").startswith("trajetoria.analitico"):
            return True
        if isinstance(no, ast.Import) and any(
            a.name.startswith("trajetoria.analitico") for a in no.names
        ):
            return True
    return False


def test_nenhum_outro_app_importa_o_analitico():
    raiz = Path(trajetoria.__file__).parent
    # `exportacao` (Feature 013) é a consumidora prevista da fronteira de leitura (spec 012
    # FR-070); a proibição continua para todos os outros apps.
    ignorados = ("analitico", "exportacao", "__pycache__")
    outros = [p for p in raiz.iterdir() if p.is_dir() and p.name not in ignorados]
    assert outros
    for app in outros:
        for arquivo in app.rglob("*.py"):
            assert not _importa_analitico(arquivo), arquivo


# --- Regressões da revisão de código ----------------------------------------------------------


def test_soma_de_indicadores_campo_a_campo():
    a = IndicadoresDoSnapshot(1, 2, 3, 4, 5)
    b = IndicadoresDoSnapshot(10, 20, 30, 40, 50)
    assert a + b == IndicadoresDoSnapshot(
        elegiveis=11,
        iniciadas_elegiveis=22,
        iniciadas_nao_elegiveis=33,
        concluidas_elegiveis=44,
        concluidas_nao_elegiveis=55,
    )


def test_recortes_sem_alias_no_enum():
    identificadores = [r.identificador for r in RecorteDoSnapshot]
    assert len(identificadores) == len(set(identificadores)) == 6
    assert len({r.campos for r in RecorteDoSnapshot}) == 6


def test_cada_exists_de_participacao_aparece_uma_vez_no_sql(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    tabela = Participacao._meta.db_table
    for leitura in (
        lambda: indicadores_do_snapshot(snapshot),
        lambda: recorte_do_snapshot(snapshot, RecorteDoSnapshot.CURSO),
    ):
        with CaptureQueriesContext(connection) as consultas:
            leitura()
        assert _sql(consultas).count(f'FROM "{tabela}"') == 2  # iniciada e concluída

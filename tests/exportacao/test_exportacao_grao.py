"""Grão e universo (US3, US7; spec FR-001, FR-002, FR-010 a FR-014; casos A, D, R, S)."""

import inspect
from decimal import Decimal

import pytest

from tests.analitico import construcao as c
from tests.exportacao import apoio
from trajetoria.analitico.consultas import indicadores_do_snapshot
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao import dataset, formatos
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.pseudonimos import pseudonimo

pytestmark = pytest.mark.django_db


# --- US3: uma linha por registro ------------------------------------------------------------------


def test_uma_linha_por_registro_identificada_pelo_pseudonimo(snapshot, chave_ficticia):
    esperados = {
        pseudonimo("conclusao", pk, chave_ficticia)
        for pk in snapshot.registros.values_list("conclusao_id", flat=True)
    }
    linhas = apoio.linhas(snapshot)
    assert len(linhas) == snapshot.registros.count()
    assert {linha["conclusao_analitica_id"] for linha in linhas} == esperados


def test_elegivel_sem_participacao(snapshot, cenario, chave_ficticia):  # caso A
    linha = apoio.linha_de(snapshot, cenario.serra_sem_participacao, chave_ficticia)
    assert linha["elegivel_no_snapshot"] is True
    assert linha["possui_participacao"] is False
    assert linha["unidade"] == "Serra" and linha["curso"] == "Engenharia"
    assert linha["pessoa_analitica_id"]
    vazias = [nome for nome, valor in linha.items() if nome.startswith("participacao_")]
    assert all(linha[nome] is None for nome in vazias)
    assert all(v is None for nome, v in linha.items() if nome.startswith("pergunta_"))


def _taxa(linhas, coluna):
    elegiveis = sum(1 for linha in linhas if linha["elegivel_no_snapshot"])
    return Decimal(sum(1 for linha in linhas if linha[coluna])) / Decimal(elegiveis)


def test_nao_elegivel_com_participacao_e_taxa_acima_de_100(inst, chave_ficticia):  # caso D
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    a, b, sem = (c.conclusao(unidade="Serra") for _ in range(3))
    c.iniciada(campanha, a)
    c.iniciada(campanha, b)
    c.simular_correcao(a, unidade="Cefor")  # simula 001/DP-005
    c.simular_correcao(b, unidade="Cefor")  # simula 001/DP-005
    snapshot = capturar_snapshot(campanha)
    linhas = apoio.linhas(snapshot)
    assert len(linhas) == 3
    fora = apoio.linha_de(snapshot, a, chave_ficticia)
    assert fora["elegivel_no_snapshot"] is False and fora["possui_participacao"] is True
    assert apoio.linha_de(snapshot, sem, chave_ficticia)["elegivel_no_snapshot"] is True
    assert _taxa(linhas, "possui_participacao") == Decimal(2)
    assert _taxa(linhas, "possui_participacao") == indicadores_do_snapshot(snapshot).taxa_inicio


def test_pessoa_com_tres_conclusoes_tem_tres_linhas(inst, chave_ficticia):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    primeira = c.conclusao(unidade="Serra", curso="A")
    outras = [c.conclusao(unidade="Serra", curso=curso, pessoa=primeira.pessoa) for curso in "BC"]
    snapshot = capturar_snapshot(campanha)
    linhas = [apoio.linha_de(snapshot, x, chave_ficticia) for x in (primeira, *outras)]
    assert len({linha["conclusao_analitica_id"] for linha in linhas}) == 3
    assert len({linha["pessoa_analitica_id"] for linha in linhas}) == 1


def test_totais_de_dados_iguais_aos_indicadores_da_012(snapshot):
    linhas = apoio.linhas(snapshot)
    indicadores = indicadores_do_snapshot(snapshot)

    def conta(elegivel, coluna):
        return sum(
            1 for linha in linhas if linha["elegivel_no_snapshot"] is elegivel and linha[coluna]
        )

    assert sum(1 for linha in linhas if linha["elegivel_no_snapshot"]) == indicadores.elegiveis
    assert conta(True, "possui_participacao") == indicadores.iniciadas_elegiveis
    assert conta(False, "possui_participacao") == indicadores.iniciadas_nao_elegiveis
    assert conta(True, "participacao_concluida") == indicadores.concluidas_elegiveis
    assert conta(False, "participacao_concluida") == indicadores.concluidas_nao_elegiveis


# --- US7: snapshot sempre explícito, nunca estado atual ------------------------------------------


def test_funcoes_publicas_recebem_o_snapshot_ou_o_dataset_dele(cenario):
    assert dataset.__all__ == ["DatasetExportado", "Tabela", "dataset_exportado"]
    assert formatos.__all__ == [
        "csv_do_dataset",
        "exportar_csv",
        "exportar_xlsx",
        "xlsx_do_dataset",
    ]
    for funcao, parametro in (
        (dataset.dataset_exportado, "snapshot"),
        (formatos.exportar_csv, "snapshot"),
        (formatos.exportar_xlsx, "snapshot"),
        (formatos.csv_do_dataset, "dataset"),
        (formatos.xlsx_do_dataset, "dataset"),
    ):
        parametros = list(inspect.signature(funcao).parameters.values())
        assert [p.name for p in parametros] == [parametro]
        assert parametros[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    # o dataset só nasce de um snapshot explícito: nada além de DatasetExportado é aceito
    for serializar in (formatos.csv_do_dataset, formatos.xlsx_do_dataset):
        with pytest.raises(TypeError):
            serializar(cenario.campanha)


def test_nenhuma_funcao_escolhe_snapshot_ou_recebe_campanha():
    proibidos = ("atual", "vigente", "ultimo", "recente", "campanha")
    publicos = [*dataset.__all__, *formatos.__all__]
    assert not [n for n in publicos if any(p in n.lower() for p in proibidos)]


def test_dois_snapshots_exportados_um_a_um(cenario, chave_ficticia):  # casos R e S
    primeiro = capturar_snapshot(cenario.campanha)
    nova = c.conclusao(unidade="Serra", ano=2023)  # incorporada entre as capturas
    segundo = capturar_snapshot(cenario.campanha)
    a, b = apoio.linhas(primeiro), apoio.linhas(segundo)
    assert len(b) == len(a) + 1
    novo_id = apoio.id_de(nova, chave_ficticia)
    assert novo_id not in {linha["conclusao_analitica_id"] for linha in a}
    assert novo_id in {linha["conclusao_analitica_id"] for linha in b}
    assert apoio.metadados(primeiro)["snapshot"] == str(primeiro.pk)
    assert apoio.metadados(segundo)["snapshot"] == str(segundo.pk)
    assert dataset_exportado(primeiro).dados.cabecalho == dataset_exportado(segundo).dados.cabecalho


def test_incorporacao_depois_da_captura_nao_muda_o_dataset(snapshot):
    antes = dataset_exportado(snapshot)
    c.conclusao(unidade="Serra", ano=2024)
    c.conclusao(unidade="Vitória", ano=2024)
    assert dataset_exportado(snapshot) == antes

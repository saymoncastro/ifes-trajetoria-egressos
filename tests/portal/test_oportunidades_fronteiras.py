"""Fronteiras da Oportunidade (025 FR-036 a FR-038, FR-041; SC-009; T041)."""

import ast
from pathlib import Path

import pytest

from tests.portal import construcao as cp
from tests.portal import construcao_oportunidades as co
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import csv_do_dataset
from trajetoria.portal.models import Oportunidade
from trajetoria.portal.oportunidades import operacoes

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"


def _importa_o_portal(pasta: Path) -> list[str]:
    infratores = []
    for arquivo in pasta.rglob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text("utf-8"))):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom) and no.module:
                nomes = [no.module]
            infratores += [
                f"{arquivo.name}: {n}" for n in nomes if n.startswith("trajetoria.portal")
            ]
    return infratores


@pytest.mark.parametrize("modulo", ["analitico", "exportacao"])
def test_analitico_e_exportacao_nao_importam_o_portal(modulo):
    assert _importa_o_portal(RAIZ / modulo) == []


@pytest.mark.django_db
def test_snapshot_e_exportacao_identicos_com_oportunidades(cenario, settings):
    """SC-009: publicar, editar e retirar oportunidades não muda snapshot nem exportação."""
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "chave-ficticia-de-teste-025-000000000000001"
    cenario.concluir(cenario.pessoa("SIM-P-0001").conclusoes.first())
    op_campanha.encerrar(cenario.campanha)
    snapshot = capturar_snapshot(cenario.campanha)

    def retrato():
        registros = sorted(map(repr, RegistroDoSnapshot.objects.filter(snapshot=snapshot).values()))
        dataset = dataset_exportado(snapshot)
        return (list(SnapshotAnalitico.objects.values()), registros, repr(dataset.dados),
                csv_do_dataset(dataset))

    antes = retrato()
    co.publicada("Para todos")
    publicada = co.publicada("Para Vitória", publico_unidades=["Vitória"])
    operacoes.retirar(publicada.pk, operador=co.OPERADOR_A, escopo=co.ESCOPO_A,
                      agora=publicada.publicada_em)
    assert Oportunidade.objects.count() == 2
    assert retrato() == antes
    assert b"Para todos" not in antes[3] and b"oportunidade" not in antes[3].lower()


@pytest.mark.django_db
def test_curadoria_nao_toca_o_nucleo(cenario):
    """FR-037: cadastrar, editar, publicar e retirar só gravam a Oportunidade."""
    nucleo = {k: v for k, v in cp.contagens().items() if k != "portal.Oportunidade"}
    o = co.rascunho()
    operacoes.editar(o.pk, co.dados("Outro título"), operador=co.OPERADOR_A,
                     escopo=co.ESCOPO_A, hoje=co.HOJE)
    o = operacoes.publicar(o.pk, operador=co.OPERADOR_A, escopo=co.ESCOPO_A,
                           agora=co.c.NO_PERIODO)
    operacoes.retirar(o.pk, operador=co.OPERADOR_A, escopo=co.ESCOPO_A, agora=co.c.NO_PERIODO)
    assert {k: v for k, v in cp.contagens().items() if k != "portal.Oportunidade"} == nucleo


def test_nenhum_dado_pessoal_novo():
    """FR-041: só os campos do data-model; nenhum identifica egresso. A página do egresso não
    tem formulário (só GET; ver test_oportunidades_egresso.py)."""
    campos = {f.name for f in Oportunidade._meta.get_fields()}
    assert campos == {
        "id", "titulo", "resumo", "categoria", "unidade_responsavel", "endereco", "inicio",
        "fim", "publico_unidades", "publico_niveis", "publico_cursos", "publicada_em",
        "publicada_por", "retirada_em", "retirada_por",
    }

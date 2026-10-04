import pytest

from tests.declaracao.construcao import declaracao_concluida, validar
from tests.participacao import construcao as c
from trajetoria.analitico.consultas import indicadores_do_snapshot, linhas_do_dataset
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.campanha.operacoes import encerrar

pytestmark = pytest.mark.django_db


def test_quarentena_congelada(monkeypatch):
    campanha = c.campanha_aberta(c.instrumento().versao)
    x = c.conclusao()
    f = declaracao_concluida(campanha)
    encerrar(campanha, agora=c.NO_PERIODO)
    monkeypatch.setattr(
        "trajetoria.analitico.operacoes.momento_de_referencia", lambda _: c.NO_PERIODO
    )
    s1 = capturar_snapshot(campanha)
    antes = list(linhas_do_dataset(s1))
    indicadores = indicadores_do_snapshot(s1)
    assert all(linha.participacao is None for linha in antes)
    validar(f, x)
    assert list(linhas_do_dataset(s1)) == antes
    assert indicadores_do_snapshot(s1) == indicadores
    s2 = capturar_snapshot(campanha)
    linha = list(linhas_do_dataset(s2))[0]
    assert linha.participacao.id == f.participacao.pk
    assert linha.origem_formacao == "declarada_validada_fonte_digital"


def test_origem_nao_desloca_argumento_posicional_da_013():
    from inspect import signature

    from trajetoria.analitico.consultas import LinhaDoDataset

    parametros = signature(LinhaDoDataset).parameters
    assert parametros["origem_formacao"].kind.name == "KEYWORD_ONLY"
    assert parametros["perguntas_do_percurso"].kind.name == "POSITIONAL_OR_KEYWORD"


def test_duas_oficiais_com_a_mesma_conclusao_recusam_a_captura(monkeypatch):
    # Regressão (code review da 019): nunca congelar só uma delas em silêncio (FR-093).
    from trajetoria.analitico.models import SnapshotAnalitico
    from trajetoria.analitico.regras import CapturaInconsistente
    from trajetoria.participacao.models import Participacao

    campanha = c.campanha_aberta(c.instrumento().versao)
    x = c.conclusao()
    Participacao.objects.create(campanha=campanha, conclusao=x, iniciada_em=c.NO_PERIODO)
    validar(declaracao_concluida(campanha), x)
    encerrar(campanha, agora=c.NO_PERIODO)
    monkeypatch.setattr(
        "trajetoria.analitico.operacoes.momento_de_referencia", lambda _: c.NO_PERIODO
    )
    with pytest.raises(CapturaInconsistente):
        capturar_snapshot(campanha)
    assert not SnapshotAnalitico.objects.exists()

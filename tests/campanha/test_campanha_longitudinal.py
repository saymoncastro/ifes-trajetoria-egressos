"""Várias Campanhas, sobreposição sem prioridade, admissão sem convite e população dinâmica
(US10; FR-031–FR-033, FR-048–FR-054)."""

from datetime import date

import pytest
from django.apps import apps

from tests.campanha import construcao as c
from tests.campanha.construcao import linha, momento
from trajetoria.academico.incorporacao import incorporar_pessoa
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import (
    admite_participacao,
    avaliar,
    campanhas_em_coleta_para,
    populacao_no_momento,
)
from trajetoria.campanha.models import Campanha
from trajetoria.fonte_academica import cenarios

pytestmark = pytest.mark.django_db


def _campanha(versao, inicio, fim, *, abrir_em=None, nome="Campanha", **criterios):
    campanha = op.definir_periodo(op.criar_campanha(nome, versao), inicio, fim)
    if criterios:
        op.definir_criterios(campanha, **criterios)
    if abrir_em is not None:
        op.abrir(campanha, agora=abrir_em)
    return Campanha.objects.get(pk=campanha.pk)


def test_mesma_conclusao_em_campanhas_de_momentos_distintos(versao_publicada):
    ads_2024 = c.conclusao(ano=2024, unidade="Serra", nivel="Graduação")
    campanhas = [
        _campanha(versao_publicada, date(ano, 4, 1), date(ano, 6, 30), ano_maximo=2024)
        for ano in (2025, 2027, 2030)
    ]
    antes = [linha(x) for x in campanhas]
    for campanha in campanhas:
        assert avaliar(campanha, ads_2024).elegivel
    assert [linha(x) for x in campanhas] == antes  # nenhuma avaliação grava nada


def test_campanhas_sobrepostas_devolvidas_sem_prioridade(versao_publicada):
    conclusao = c.conclusao(ano=2022, unidade="Serra")
    agora = momento(2027, 5, 1)
    institucional = _campanha(
        versao_publicada, date(2027, 4, 1), date(2027, 6, 30), abrir_em=momento(2027, 4, 1)
    )
    da_unidade = _campanha(
        versao_publicada,
        date(2027, 3, 1),
        date(2027, 5, 31),
        abrir_em=momento(2027, 3, 1),
        unidades=["Serra"],
    )
    aplicaveis = campanhas_em_coleta_para(conclusao, agora=agora)
    assert aplicaveis == (da_unidade, institucional)  # ordem (inicio, id), sem preferência


def test_nenhuma_campanha_aplicavel(versao_publicada):
    conclusao = c.conclusao(ano=2010)
    _campanha(
        versao_publicada,
        date(2027, 4, 1),
        date(2027, 6, 30),
        abrir_em=momento(2027, 4, 1),
        ano_minimo=2020,
    )
    assert campanhas_em_coleta_para(conclusao, agora=momento(2027, 5, 1)) == ()


def test_encerrada_e_em_preparacao_nao_aparecem(versao_publicada):
    conclusao = c.conclusao(ano=2022)
    _campanha(versao_publicada, date(2027, 4, 1), date(2027, 6, 30))
    encerrada = _campanha(
        versao_publicada, date(2027, 4, 1), date(2027, 6, 30), abrir_em=momento(2027, 4, 1)
    )
    op.encerrar(encerrada, agora=momento(2027, 4, 20))
    assert campanhas_em_coleta_para(conclusao, agora=momento(2027, 5, 1)) == ()


def test_admissao_sem_convite(versao_publicada):
    elegivel = c.conclusao(ano=2022)
    inelegivel = c.conclusao(ano=2010)
    em_coleta = _campanha(
        versao_publicada,
        date(2027, 4, 1),
        date(2027, 6, 30),
        abrir_em=momento(2027, 4, 1),
        ano_minimo=2020,
    )
    agora = momento(2027, 5, 1)

    assert admite_participacao(em_coleta, elegivel, agora=agora)
    assert not admite_participacao(em_coleta, inelegivel, agora=agora)
    # Nada além de Campanha existe para registrar convite, destinatário ou envio.
    assert [m.__name__ for m in apps.get_app_config("campanha").get_models()] == ["Campanha"]


def test_nao_admite_em_preparacao_nem_encerrada(versao_publicada):
    conclusao = c.conclusao(ano=2022)
    preparacao = _campanha(versao_publicada, date(2027, 4, 1), date(2027, 6, 30))
    aberta = _campanha(
        versao_publicada, date(2027, 4, 1), date(2027, 6, 30), abrir_em=momento(2027, 4, 1)
    )
    assert not admite_participacao(preparacao, conclusao, agora=momento(2027, 5, 1))
    assert not admite_participacao(aberta, conclusao, agora=momento(2027, 7, 1))


def test_nunca_aberta_e_expirada_nao_admite(versao_publicada):
    """Caso M-B de T027: período de 01/03 a 31/03/2027, consultado em 10/04/2027."""
    conclusao = c.conclusao(ano=2022)
    campanha = _campanha(versao_publicada, date(2027, 3, 1), date(2027, 3, 31))
    assert not admite_participacao(campanha, conclusao, agora=momento(2027, 4, 10))


def test_populacao_dinamica_com_incorporacao_durante_a_coleta(
    versao_publicada, fonte_simulada
):
    ids = {p.id_externo for p in cenarios.PESSOAS} - {"SIM-P-0005"}
    c.incorporar_cenarios(fonte_simulada, ids=ids)
    campanha = _campanha(
        versao_publicada,
        date(2027, 4, 1),
        date(2027, 6, 30),
        abrir_em=momento(2027, 4, 1),
        niveis=["Técnico"],
    )
    antes = linha(campanha)
    contagem_antes = populacao_no_momento(campanha).count()

    incorporar_pessoa(fonte_simulada, "SIM-P-0005")  # Técnico em Agropecuária, Alegre, 2019
    nova = c.conclusao_da_fonte("SIM-C-0009")

    assert nova in populacao_no_momento(campanha)
    assert populacao_no_momento(campanha).count() == contagem_antes + 1
    assert admite_participacao(campanha, nova, agora=momento(2027, 4, 15))
    assert linha(campanha) == antes  # nenhuma associação Campanha ↔ Conclusão gravada


def test_campanhas_em_coleta_para_coerente_com_admite_participacao(
    versao_publicada, fonte_simulada
):
    """O filtro no banco de `campanhas_em_coleta_para` coincide com `admite_participacao`
    para todas as Conclusões e Campanhas de referência."""
    c.incorporar_cenarios(fonte_simulada)
    c.conclusao()
    c.conclusao(ano=2021, unidade="Serra")
    referencia = [
        {},
        {"ano_minimo": 2020, "ano_maximo": 2024},
        {"ano_maximo": 2018},
        {"unidades": ["Serra", "Vitória"]},
        {"niveis": ["Técnico"], "formas_oferta": ["Integrado"]},
        {"modalidades": ["A distância"], "ano_minimo": 2020},
    ]
    for criterios in referencia:
        _campanha(
            versao_publicada, date(2027, 4, 1), date(2027, 6, 30),
            abrir_em=momento(2027, 4, 1), **criterios,
        )
    agora = momento(2027, 5, 1)
    campanhas = list(Campanha.objects.order_by("inicio", "id"))
    for conclusao in ConclusaoAcademica.objects.all():
        esperado = tuple(x for x in campanhas if admite_participacao(x, conclusao, agora=agora))
        assert campanhas_em_coleta_para(conclusao, agora=agora) == esperado, conclusao


def test_campanha_aberta_depois_da_data_de_referencia_nao_aparece(versao_publicada):
    conclusao = c.conclusao(ano=2022)
    _campanha(
        versao_publicada, date(2027, 4, 1), date(2027, 6, 30), abrir_em=momento(2027, 4, 20)
    )
    assert campanhas_em_coleta_para(conclusao, agora=momento(2027, 4, 10)) == ()

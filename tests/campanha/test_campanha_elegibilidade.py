"""Elegibilidade e população no momento da consulta (US3, US4, US5, US7, US11;
FR-015–FR-033)."""

from datetime import date

import pytest

from tests.campanha import construcao as c
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import (
    Criterio,
    MotivoPendencia,
    Pendencia,
    Resultado,
    avaliar,
    populacao_no_momento,
)
from trajetoria.campanha.models import Campanha

pytestmark = pytest.mark.django_db

NAO_INFORMADO, NAO_ATENDE = MotivoPendencia.NAO_INFORMADO, MotivoPendencia.NAO_ATENDE


def _campanha(versao, **criterios):
    campanha = op.criar_campanha("Campanha", versao)
    return op.definir_criterios(campanha, **criterios) if criterios else campanha


def _populacao(campanha):
    return set(populacao_no_momento(campanha))


def _pendencias(campanha, conclusao):
    return avaliar(campanha, conclusao).pendencias


# --- US3: população ampla -------------------------------------------------------------


def test_populacao_ampla_inclui_todas_as_conclusoes(versao_publicada, fonte_simulada):
    c.incorporar_cenarios(fonte_simulada)
    sem_atributos = c.conclusao()
    campanha = _campanha(versao_publicada)

    assert campanha.populacao_ampla
    for conclusao in ConclusaoAcademica.objects.all():
        resultado = avaliar(campanha, conclusao)
        assert resultado.resultado is Resultado.ELEGIVEL and resultado.pendencias == ()
        assert resultado.elegivel
    assert sem_atributos in _populacao(campanha)
    assert populacao_no_momento(campanha).count() == ConclusaoAcademica.objects.count()


# --- US4: ano de conclusão (absoluto, inclusivo) -----------------------------------------

ANO = Criterio.ANO_CONCLUSAO


@pytest.mark.parametrize(
    ("criterios", "elegiveis", "inelegiveis"),
    [
        ({"ano_minimo": 2020, "ano_maximo": 2024}, {2020, 2024}, {2019, 2025}),
        ({"ano_minimo": 2020}, {2020, 2031}, {2019}),
        ({"ano_maximo": 2024}, {1998, 2024}, {2025}),
        ({"ano_minimo": 2022, "ano_maximo": 2022}, {2022}, {2021, 2023}),
    ],
    ids=["intervalo", "so_minimo", "so_maximo", "um_ano"],
)
def test_ano_de_conclusao(versao_publicada, criterios, elegiveis, inelegiveis):
    conclusoes = {ano: c.conclusao(ano=ano) for ano in elegiveis | inelegiveis}
    campanha = _campanha(versao_publicada, **criterios)

    for ano in elegiveis:
        assert avaliar(campanha, conclusoes[ano]).elegivel, ano
    for ano in inelegiveis:
        assert _pendencias(campanha, conclusoes[ano]) == (Pendencia(ANO, NAO_ATENDE),), ano
    assert _populacao(campanha) == {conclusoes[ano] for ano in elegiveis}


# --- US5: elegibilidade por Conclusão, explicável e determinística -----------------------


def test_pessoa_com_duas_conclusoes_apenas_uma_elegivel(versao_publicada, fonte_simulada):
    c.incorporar_cenarios(fonte_simulada, ids={"SIM-P-0003"})
    serra_2022 = c.conclusao_da_fonte("SIM-C-0004")
    cefor_2025 = c.conclusao_da_fonte("SIM-C-0005")
    assert serra_2022.pessoa_id == cefor_2025.pessoa_id
    campanha = _campanha(versao_publicada, ano_minimo=2020, ano_maximo=2024)

    assert avaliar(campanha, serra_2022).elegivel
    resultado = avaliar(campanha, cefor_2025)
    assert resultado.resultado is Resultado.NAO_ELEGIVEL
    assert resultado.pendencias == (Pendencia(ANO, NAO_ATENDE),)


def test_avaliacao_identica_em_qualquer_estado_e_data(versao_publicada):
    conclusao = c.conclusao(ano=2019, unidade="Serra")
    campanha = _campanha(versao_publicada, ano_minimo=2020, unidades=["Serra"])
    referencia = avaliar(campanha, conclusao)

    Campanha.objects.filter(pk=campanha.pk).update(
        inicio=date(2027, 4, 1), fim=date(2027, 6, 30), aberta_em=c.momento(2027, 4, 1)
    )
    em_coleta = Campanha.objects.get(pk=campanha.pk)
    Campanha.objects.filter(pk=campanha.pk).update(encerrada_em=c.momento(2027, 5, 1))
    encerrada = Campanha.objects.get(pk=campanha.pk)

    assert avaliar(em_coleta, conclusao) == referencia
    assert avaliar(encerrada, conclusao) == referencia


def test_avaliar_nao_acessa_o_banco(versao_publicada, django_assert_num_queries):
    conclusao = c.conclusao(ano=2021, nivel="Técnico")
    campanha = _campanha(versao_publicada, ano_minimo=2020, niveis=["Técnico"])
    with django_assert_num_queries(0):
        avaliar(campanha, conclusao)


# --- US7: unidade, nível, modalidade e forma de oferta -----------------------------------
# Cenários da 001: C-0001 Serra/Graduação/Presencial/2022 (sem forma de oferta);
# C-0002 Vitória/Técnico/Integrado/2014; C-0003 Vitória/Graduação/2020;
# C-0004 Serra/Graduação/2022 e C-0005 Cefor/Pós-graduação/A distância/2025 (Pessoa C);
# C-0007 Vila Velha/Graduação/2017; C-0010 Cariacica/Técnico/Subsequente/2018;
# C-0011 Colatina/Técnico/Subsequente/2021.

UNIDADE, NIVEL = Criterio.UNIDADE, Criterio.NIVEL
MODALIDADE, FORMA_OFERTA = Criterio.MODALIDADE, Criterio.FORMA_OFERTA


@pytest.fixture
def cenarios(fonte_simulada):
    c.incorporar_cenarios(fonte_simulada)
    return c.conclusao_da_fonte


def test_sem_criterio_de_unidade_todas_as_unidades_atendem(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, ano_minimo=1900)
    unidades = {x.unidade for x in ConclusaoAcademica.objects.all()}
    assert len(unidades) > 3
    for conclusao in ConclusaoAcademica.objects.all():
        assert all(p.criterio is not UNIDADE for p in _pendencias(campanha, conclusao))


def test_uma_unidade(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, unidades=["Serra"])
    assert avaliar(campanha, cenarios("SIM-C-0001")).elegivel
    assert _pendencias(campanha, cenarios("SIM-C-0005")) == (Pendencia(UNIDADE, NAO_ATENDE),)


def test_uma_unidade_pessoa_com_conclusoes_em_duas_unidades(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, unidades=["Serra"])
    assert avaliar(campanha, cenarios("SIM-C-0004")).elegivel
    assert not avaliar(campanha, cenarios("SIM-C-0005")).elegivel


def test_or_dentro_do_criterio(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, unidades=["Serra", "Vitória"])
    assert avaliar(campanha, cenarios("SIM-C-0001")).elegivel
    assert avaliar(campanha, cenarios("SIM-C-0003")).elegivel
    assert not avaliar(campanha, cenarios("SIM-C-0005")).elegivel


@pytest.mark.parametrize(
    ("criterios", "elegivel", "inelegivel", "pendencia"),
    [
        ({"niveis": ["Técnico"]}, "SIM-C-0002", "SIM-C-0003", Pendencia(NIVEL, NAO_ATENDE)),
        (
            {"modalidades": ["A distância"]},
            "SIM-C-0005",
            "SIM-C-0001",
            Pendencia(MODALIDADE, NAO_ATENDE),
        ),
        (
            {"formas_oferta": ["Integrado"]},
            "SIM-C-0002",
            "SIM-C-0010",
            Pendencia(FORMA_OFERTA, NAO_ATENDE),
        ),
        (
            {"formas_oferta": ["Integrado"]},
            "SIM-C-0002",
            "SIM-C-0001",
            Pendencia(FORMA_OFERTA, NAO_INFORMADO),
        ),
    ],
    ids=["nivel", "modalidade", "forma_oferta", "forma_oferta_ausente"],
)
def test_nivel_modalidade_forma_de_oferta(
    versao_publicada, cenarios, criterios, elegivel, inelegivel, pendencia
):
    campanha = _campanha(versao_publicada, **criterios)
    assert avaliar(campanha, cenarios(elegivel)).elegivel
    assert _pendencias(campanha, cenarios(inelegivel)) == (pendencia,)


def test_and_entre_criterios(versao_publicada, cenarios):
    campanha = _campanha(
        versao_publicada, niveis=["Graduação"], ano_minimo=2020, ano_maximo=2024
    )
    assert avaliar(campanha, cenarios("SIM-C-0003")).elegivel
    assert _pendencias(campanha, cenarios("SIM-C-0007")) == (Pendencia(ANO, NAO_ATENDE),)
    assert _pendencias(campanha, cenarios("SIM-C-0011")) == (Pendencia(NIVEL, NAO_ATENDE),)
    assert _pendencias(campanha, cenarios("SIM-C-0002")) == (
        Pendencia(ANO, NAO_ATENDE),
        Pendencia(NIVEL, NAO_ATENDE),
    )


@pytest.mark.parametrize("unidade", ["serra", "Campus Serra", "Serra "])
def test_igualdade_exata_sem_normalizacao(versao_publicada, unidade):
    campanha = _campanha(versao_publicada, unidades=["Serra"])
    conclusao = c.conclusao(unidade=unidade)
    assert _pendencias(campanha, conclusao) == (Pendencia(UNIDADE, NAO_ATENDE),)
    assert conclusao not in _populacao(campanha)


# --- Coerência: avaliar × populacao_no_momento ------------------------------------------

CAMPANHAS_DE_REFERENCIA = [
    {},
    {"ano_minimo": 2020, "ano_maximo": 2024},
    {"ano_minimo": 2020},
    {"ano_maximo": 2018},
    {"unidades": ["Serra", "Vitória"]},
    {"niveis": ["Técnico"]},
    {"modalidades": ["A distância"]},
    {"formas_oferta": ["Integrado", "Subsequente"]},
    {"niveis": ["Graduação"], "unidades": ["Vitória"], "ano_minimo": 2015},
]


@pytest.mark.parametrize("criterios", CAMPANHAS_DE_REFERENCIA)
def test_populacao_coerente_com_avaliar(versao_publicada, fonte_simulada, criterios):
    c.incorporar_cenarios(fonte_simulada)
    c.conclusao()
    c.conclusao(ano=2021)
    c.conclusao(ano=2022, unidade="Serra")
    c.conclusao(ano=2016, unidade="Vitória", nivel="Graduação")
    c.conclusao(nivel="Técnico", forma_oferta="Integrado")
    campanha = _campanha(versao_publicada, **criterios)

    todas = list(ConclusaoAcademica.objects.all())
    elegiveis = {x for x in todas if avaliar(campanha, x).elegivel}
    assert _populacao(campanha) == elegiveis
    assert populacao_no_momento(campanha).count() == len(elegiveis)


# --- US11: atributo ausente — NAO_INFORMADO, nunca inferido ------------------------------

COMPLETA = {
    "ano": 2022,
    "unidade": "Serra",
    "nivel": "Graduação",
    "modalidade": "Presencial",
    "forma_oferta": "Integrado",
}
CRITERIO_POR_ATRIBUTO = {
    "ano": (ANO, {"ano_minimo": 2020}),
    "unidade": (UNIDADE, {"unidades": ["Serra"]}),
    "nivel": (NIVEL, {"niveis": ["Graduação"]}),
    "modalidade": (MODALIDADE, {"modalidades": ["Presencial"]}),
    "forma_oferta": (FORMA_OFERTA, {"formas_oferta": ["Integrado"]}),
}


@pytest.mark.parametrize("atributo", CRITERIO_POR_ATRIBUTO)
def test_atributo_ausente_com_criterio_definido(versao_publicada, atributo):
    criterio, criterios = CRITERIO_POR_ATRIBUTO[atributo]
    pessoa_completa = c.conclusao(**COMPLETA)
    # Outra Conclusão da mesma Pessoa tem o atributo: nada é deduzido dela.
    ausente = c.conclusao(**{**COMPLETA, atributo: None}, pessoa=pessoa_completa.pessoa)
    campanha = _campanha(versao_publicada, **criterios)

    assert avaliar(campanha, pessoa_completa).elegivel
    assert _pendencias(campanha, ausente) == (Pendencia(criterio, NAO_INFORMADO),)
    assert ausente not in _populacao(campanha)


@pytest.mark.parametrize("atributo", CRITERIO_POR_ATRIBUTO)
def test_atributo_ausente_sem_criterio_nao_tem_efeito(versao_publicada, atributo):
    outros = {}
    for nome, (_, criterios) in CRITERIO_POR_ATRIBUTO.items():
        if nome != atributo:
            outros.update(criterios)
    ausente = c.conclusao(**{**COMPLETA, atributo: None})
    campanha = _campanha(versao_publicada, **outros)
    assert avaliar(campanha, ausente).elegivel
    assert ausente in _populacao(campanha)


def test_nao_informado_e_nao_atende_na_mesma_avaliacao(versao_publicada):
    conclusao = c.conclusao(ano=2015, unidade=None)
    campanha = _campanha(
        versao_publicada, ano_minimo=2020, ano_maximo=2024, unidades=["Serra"]
    )
    assert _pendencias(campanha, conclusao) == (
        Pendencia(ANO, NAO_ATENDE),
        Pendencia(UNIDADE, NAO_INFORMADO),
    )

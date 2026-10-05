"""Contexto institucional daquele ano (021 US6; FR-052 a FR-061; SC-009, SC-011)."""

import re
import xml.etree.ElementTree as ET
from datetime import date

import pytest

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn
from trajetoria.contexto_trajetoria.carga import carregar_contexto
from trajetoria.contexto_trajetoria.models import ContextoInstitucionalAgregado
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.narrativa import card, catalogo
from trajetoria.narrativa.contrato import (
    METRICA_CURSO_UNIDADE_ANO,
    METRICA_UNIDADE_ANO,
    ContextoSelecionado,
)
from trajetoria.narrativa.montagem import montar

URL = "/minha-trajetoria/"
APURACAO = date(2026, 1, 31)
FRASE_CURSO = (
    f"Em 2022, 27 conclusões de {cenarios.TADS} foram registradas na unidade Serra, "
    "incluindo a sua."
)
FRASE_UNIDADE = "Em 2022, 812 conclusões foram registradas na unidade Serra."
FRASE_APURACAO = "Dados institucionais apurados em 31/01/2026."


def _abrir(client, cenario, id_externo, carregar=True):
    pessoa = cenario.pessoa(id_externo)
    if carregar:
        carregar_contexto(ContextoSimulado(), pessoa)
    cenario.concluir(pessoa.conclusoes.first())
    cn.entrar(client, pessoa)
    return ci.texto_visivel(client.get(URL))


def _naquele_ano(texto):
    return texto.split("Naquele ano no Ifes")[1].split("Seu card")[0] if (
        "Naquele ano no Ifes" in texto
    ) else ""


@pytest.mark.django_db
def test_ana_duas_frases_com_apuracao(client, cenario):
    trecho = _naquele_ano(_abrir(client, cenario, "SIM-P-0001"))
    assert FRASE_CURSO in trecho and FRASE_UNIDADE in trecho and FRASE_APURACAO in trecho


@pytest.mark.django_db
def test_ana_destaques_na_pagina_com_numero_e_frase(client, cenario):
    pessoa = cenario.pessoa("SIM-P-0001")
    carregar_contexto(ContextoSimulado(), pessoa)
    cenario.concluir(pessoa.conclusoes.first())
    cn.entrar(client, pessoa)
    html = client.get(URL).content.decode()
    assert re.findall(r'<span class="narrativa-numero" aria-hidden="true">(.*?)</span>', html) == [
        "27", "812",
    ]
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", html)
    assert h2 == ["Sua formação", "Naquele ano no Ifes", "Seu card"]


@pytest.mark.django_db
def test_maria_mesmas_frases_nada_do_cefor(client, cenario):
    trecho = _naquele_ano(_abrir(client, cenario, "SIM-P-0003"))
    assert trecho.count(FRASE_CURSO) == 1 and trecho.count(FRASE_UNIDADE) == 1
    assert "Cefor" not in trecho


@pytest.mark.django_db
def test_diego_sem_secao(client, cenario):
    assert "Naquele ano no Ifes" not in _abrir(client, cenario, "SIM-P-0004")


@pytest.mark.django_db
def test_duas_apuracoes_omitem_o_agregado(client, cenario):
    carregar_contexto(ContextoSimulado(), cenario.pessoa("SIM-P-0001"))
    ContextoInstitucionalAgregado.objects.create(
        fonte="simulada", metrica=METRICA_CURSO_UNIDADE_ANO, curso=cenarios.TADS,
        unidade="Serra", ano=2022, valor=30, apurado_em=date(2027, 1, 31),
    )
    trecho = _naquele_ano(_abrir(client, cenario, "SIM-P-0001", carregar=False))
    assert "conclusões de" not in trecho  # métrica por curso omitida, sem escolher por data
    assert FRASE_UNIDADE in trecho  # a outra métrica segue com apuração única


@pytest.mark.django_db
def test_valor_menor_que_a_base_local_e_omitido(client, cenario, caplog):
    # Ana e Maria (TADS · Serra · 2022) já estão incorporadas: 2 > 1.
    ContextoInstitucionalAgregado.objects.create(
        fonte="simulada", metrica=METRICA_CURSO_UNIDADE_ANO, curso=cenarios.TADS,
        unidade="Serra", ano=2022, valor=1, apurado_em=APURACAO,
    )
    assert "Naquele ano no Ifes" not in _abrir(client, cenario, "SIM-P-0001", carregar=False)
    assert "Agregado incoerente em simulada" in caplog.text
    assert "Ana" not in caplog.text


@pytest.mark.django_db
def test_agregado_de_outra_fonte_nao_se_aplica(client, cenario):
    ContextoInstitucionalAgregado.objects.create(
        fonte="outra", metrica=METRICA_UNIDADE_ANO, curso=None, unidade="Serra", ano=2022,
        valor=900, apurado_em=APURACAO,
    )
    assert "Naquele ano no Ifes" not in _abrir(client, cenario, "SIM-P-0001", carregar=False)


@pytest.mark.django_db
def test_base_parcial_nunca_vira_numero(client, cenario):
    texto = _abrir(client, cenario, "SIM-P-0001", carregar=False)
    assert "Naquele ano no Ifes" not in texto and "conclusões foram registradas" not in texto


def _selecionado(valor, formacao=0, metrica=METRICA_CURSO_UNIDADE_ANO, curso="A"):
    return ContextoSelecionado(metrica, "Serra", 2022, valor, APURACAO, formacao,
                               curso if metrica == METRICA_CURSO_UNIDADE_ANO else None)


def test_singular_com_valor_um():
    entrada = cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2022)],
                         agregados=[_selecionado(1),
                                    _selecionado(1, metrica=METRICA_UNIDADE_ANO)])
    frases = [f.texto for f in montar(entrada).secao("naquele_ano").frases]
    assert "Em 2022, 1 conclusão de A foi registrada na unidade Serra: a sua." in frases
    assert "Em 2022, 1 conclusão foi registrada na unidade Serra." in frases


def test_linguagem_conclusoes_e_sem_vedadas():
    entrada = cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2022)],
                         agregados=[_selecionado(27),
                                    _selecionado(812, metrica=METRICA_UNIDADE_ANO)])
    for frase in montar(entrada).secao("naquele_ano").frases:
        if not frase.texto.startswith("Dados institucionais"):
            assert "conclus" in frase.texto
        for termo in catalogo.VEDADAS:
            assert termo.lower() not in frase.texto.lower(), (termo, frase.texto)
        assert frase.origem == "agregado"


def test_card_com_no_maximo_um_par_da_primeira_formacao():
    entrada = cn.entrada(
        [cn.fato(curso="A", unidade="Serra", ano_conclusao=2018),
         cn.fato(curso="B", unidade="Vitória", ano_conclusao=2021)],
        agregados=[
            _selecionado(10, 0, curso="A"),
            _selecionado(500, 0, metrica=METRICA_UNIDADE_ANO),
            _selecionado(20, 1, curso="B"),
        ],
    )
    narrativa = montar(entrada)
    destaques = narrativa.compartilhavel.contextos_agregados
    assert [(d.metrica, d.numero) for d in destaques] == [
        (METRICA_CURSO_UNIDADE_ANO, 10), (METRICA_UNIDADE_ANO, 500),
    ]
    assert destaques[0].rotulo == ("conclusões deste curso", "na unidade Serra em 2022")
    assert destaques[1].rotulo == ("conclusões registradas", "na unidade Serra em 2022")
    assert narrativa.compartilhavel.apuracao == FRASE_APURACAO
    assert len(narrativa.secao("naquele_ano").frases) == 4  # a página mostra todos


def test_destaque_no_singular():
    entrada = cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2022)],
                         agregados=[_selecionado(1)])
    destaque = montar(entrada).compartilhavel.contextos_agregados[0]
    assert destaque.rotulo == ("conclusão deste curso", "na unidade Serra em 2022")


def test_par_com_apuracoes_distintas_fica_so_com_o_primeiro():
    """O rodapé do card tem uma só apuração; nenhuma é escolhida por data (FR-059)."""
    outra = ContextoSelecionado(METRICA_UNIDADE_ANO, "Serra", 2022, 812, date(2026, 2, 28), 0)
    entrada = cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2022)],
                         agregados=[_selecionado(27), outra])
    c = montar(entrada).compartilhavel
    assert [d.numero for d in c.contextos_agregados] == [27]
    assert c.apuracao == FRASE_APURACAO


@pytest.mark.django_db
def test_card_da_ana_com_agregados_na_area_segura(client, cenario):
    _abrir(client, cenario, "SIM-P-0001")
    svg = client.get("/minha-trajetoria/card.svg").content.decode()
    assert ">27<" in svg and "conclusões deste curso" in svg
    for texto in ET.fromstring(svg).findall("{http://www.w3.org/2000/svg}text"):
        y, tamanho = int(texto.get("y")), int(texto.get("font-size"))
        assert y - tamanho >= card.AREA_SEGURA[1]
        assert y + card.DESCENDENTE * tamanho <= card.AREA_SEGURA[3]

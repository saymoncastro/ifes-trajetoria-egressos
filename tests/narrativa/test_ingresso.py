"""Ingresso, quando a fonte de contexto o informa (021 US5; FR-046 a FR-051; SC-007)."""

import pytest

from tests.interface import construcao_interface as ci
from tests.narrativa import construcao as cn
from tests.participacao import construcao as c
from trajetoria.contexto_trajetoria.carga import carregar_contexto
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.narrativa.montagem import montar

URL = "/minha-trajetoria/"
INICIO_ANA = (
    "Sua trajetória no Ifes começou em 2019, em Tecnologia em Análise e Desenvolvimento de "
    "Sistemas."
)


def _abrir(client, cenario, id_externo, contexto=None):
    pessoa = cenario.pessoa(id_externo)
    carregar_contexto(contexto or ContextoSimulado(), pessoa)
    cenario.concluir(pessoa.conclusoes.first())
    cn.entrar(client, pessoa)
    return client.get(URL)


@pytest.mark.django_db
def test_ana_tem_frase_de_inicio(client, cenario):
    assert INICIO_ANA in ci.texto_visivel(_abrir(client, cenario, "SIM-P-0001"))


@pytest.mark.django_db
def test_maria_sem_ingresso_sem_frase(client, cenario):
    assert "começou" not in ci.texto_visivel(_abrir(client, cenario, "SIM-P-0003"))


def test_mesmo_menor_ano_de_ingresso_nenhuma_frase():
    entrada = cn.entrada([
        cn.fato(curso="A", ano_conclusao=2015, ingresso_ano=2012),
        cn.fato(curso="B", ano_conclusao=2016, ingresso_ano=2012),
    ])
    assert not any("começou" in f.texto for s in montar(entrada).secoes for f in s.frases)


def test_frase_de_inicio_abre_a_trajetoria_e_e_serializada():
    entrada = cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2015,
                                  ingresso_ano=2012)])
    narrativa = montar(entrada)
    trajetoria = narrativa.secao("trajetoria_academica")
    assert trajetoria.frases[0].texto == "Sua trajetória no Ifes começou em 2012, em A."
    assert trajetoria.frases[0].formacao is None
    from trajetoria.narrativa.contrato import serializar

    assert serializar(narrativa)["formacoes"][0]["ingresso"] == {"ano": 2012}


@pytest.mark.django_db
def test_ingresso_incoerente_e_omitido_com_log(client, cenario, caplog):
    incoerente = ContextoSimulado(complementos={"SIM-C-0001": (2023, None)})  # conclusão 2022
    texto = ci.texto_visivel(_abrir(client, cenario, "SIM-P-0001", incoerente))
    assert "começou" not in texto
    assert "simulada:SIM-C-0001" in caplog.text
    assert "Ana" not in caplog.text and "2023" not in caplog.text


@pytest.mark.django_db
def test_card_nunca_tem_ingresso(client, cenario):
    _abrir(client, cenario, "SIM-P-0001")
    svg = client.get("/minha-trajetoria/card.svg?nome=1").content.decode()
    assert "começou" not in svg and "2019" not in svg


@pytest.mark.django_db
def test_snapshot_e_exportacao_intactos(client, cenario, relogio, settings):
    from trajetoria.analitico.models import RegistroDoSnapshot
    from trajetoria.analitico.operacoes import capturar_snapshot
    from trajetoria.exportacao.dataset import dataset_exportado

    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "chave-ficticia-de-teste-da-021-000000000001"
    _abrir(client, cenario, "SIM-P-0001")
    relogio.agora = c.DEPOIS_DO_FIM
    snapshot = capturar_snapshot(cenario.campanha)
    campos = {f.name for f in RegistroDoSnapshot._meta.get_fields()}
    assert not {"ingresso", "ano_ingresso", "complemento"} & campos
    dados = dataset_exportado(snapshot).dados
    assert not [coluna for coluna in dados.cabecalho if "ingresso" in coluna]
    assert all(2019 not in linha for linha in dados.linhas)

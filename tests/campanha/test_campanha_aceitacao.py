"""Aceitação ponta a ponta: casos A–L da spec e SC-009 (escopo contido)."""

from datetime import date

import pytest
from django.apps import apps

from tests.campanha import construcao as c
from tests.campanha.construcao import momento, rejeita
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import (
    Criterio,
    MotivoPendencia,
    Pendencia,
    admite_participacao,
    avaliar,
    campanhas_em_coleta_para,
    populacao_no_momento,
)
from trajetoria.campanha.regras import Motivo
from trajetoria.formulario_2024.materializacao import materializar
from trajetoria.instrumento.models import EstadoVersao, Versao

pytestmark = pytest.mark.django_db

INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)
NO_PERIODO = momento(2027, 5, 1)


@pytest.fixture
def cenarios(fonte_simulada):
    c.incorporar_cenarios(fonte_simulada)
    return c.conclusao_da_fonte


def _campanha(versao, **criterios):
    campanha = op.definir_periodo(op.criar_campanha("Campanha", versao), INICIO, FIM)
    return op.definir_criterios(campanha, **criterios) if criterios else campanha


def _elegiveis(campanha):
    return {x.id_externo for x in populacao_no_momento(campanha)}


def test_a_campanha_para_todos_os_egressos(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada)
    assert campanha.populacao_ampla
    assert populacao_no_momento(campanha).count() == ConclusaoAcademica.objects.count()


def test_b_conclusoes_entre_dois_anos(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, ano_minimo=2020, ano_maximo=2024)
    assert _elegiveis(campanha) == {
        "SIM-C-0001", "SIM-C-0003", "SIM-C-0004", "SIM-C-0008", "SIM-C-0011", "SIM-C-0013"
    }


def test_c_campanha_institucional_com_varias_unidades(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, unidades=["Serra", "Vitória", "Cefor"])
    unidades = {x.unidade for x in populacao_no_momento(campanha)}
    assert unidades == {"Serra", "Vitória", "Cefor"}


def test_d_campanha_restrita_a_uma_unidade(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, unidades=["Vila Velha"])
    assert _elegiveis(campanha) == {"SIM-C-0006", "SIM-C-0007", "SIM-C-0008"}


def test_e_campanha_restrita_a_um_nivel(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, niveis=["Pós-graduação"])
    assert _elegiveis(campanha) == {"SIM-C-0005", "SIM-C-0008"}


def test_f_pessoa_com_duas_conclusoes_apenas_uma_elegivel(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, ano_minimo=2020, ano_maximo=2024)
    assert avaliar(campanha, cenarios("SIM-C-0004")).elegivel
    assert not avaliar(campanha, cenarios("SIM-C-0005")).elegivel


def test_g_atributo_ausente_necessario_ao_criterio(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada, formas_oferta=["Integrado"])
    assert avaliar(campanha, cenarios("SIM-C-0001")).pendencias == (
        Pendencia(Criterio.FORMA_OFERTA, MotivoPendencia.NAO_INFORMADO),
    )


def test_h_abrir_com_versao_rascunho():
    baseline = materializar().versao
    campanha = _campanha(baseline)
    rejeita([Motivo.VERSAO_NAO_PUBLICADA], op.abrir, campanha, agora=NO_PERIODO)


def test_i_periodo_invalido(versao_publicada):
    campanha = op.criar_campanha("Campanha", versao_publicada)
    rejeita([Motivo.PERIODO_INVERTIDO], op.definir_periodo, campanha, FIM, INICIO)


def test_j_alterar_significado_de_campanha_aberta(versao_publicada):
    campanha = _campanha(versao_publicada, ano_minimo=2020)
    op.abrir(campanha, agora=NO_PERIODO)
    rejeita([Motivo.CAMPANHA_JA_ABERTA], op.definir_criterios, campanha, ano_minimo=2010)


def test_k_duas_campanhas_em_momentos_distintos(versao_publicada, cenarios):
    conclusao = cenarios("SIM-C-0003")  # Vitória, 2020
    rodada_2027 = _campanha(versao_publicada, ano_minimo=2020)
    rodada_2030 = op.definir_periodo(
        op.criar_campanha("Rodada 2030", versao_publicada), date(2030, 4, 1), date(2030, 6, 30)
    )
    op.abrir(rodada_2027, agora=NO_PERIODO)
    op.abrir(rodada_2030, agora=momento(2030, 4, 1))
    assert campanhas_em_coleta_para(conclusao, agora=NO_PERIODO) == (rodada_2027,)
    assert campanhas_em_coleta_para(conclusao, agora=momento(2030, 5, 1)) == (rodada_2030,)


def test_l_acesso_nao_depende_de_convite(versao_publicada, cenarios):
    campanha = _campanha(versao_publicada)
    op.abrir(campanha, agora=NO_PERIODO)
    assert admite_participacao(campanha, cenarios("SIM-C-0009"), agora=NO_PERIODO)


# --- SC-009: escopo contido ---------------------------------------------------------------


def test_app_campanha_tem_somente_o_modelo_campanha():
    # SC-009 é sobre o escopo da 004: o app `campanha` não cria Participação, Resposta,
    # Convite, Destinatário, Segmento, Regra, Agendamento nem fotografia. A igualdade
    # garante isso sem proibir que features posteriores criem esses conceitos em seus
    # próprios apps.
    assert [m.__name__ for m in apps.get_app_config("campanha").get_models()] == ["Campanha"]


def test_versao_e_conclusao_sem_colunas_novas():
    assert [f.name for f in Versao._meta.concrete_fields] == [
        "id", "pesquisa", "designacao", "estado", "publicada_em", "origem", "titulo",
        "texto_abertura", "texto_encerramento",
    ]
    assert [f.name for f in ConclusaoAcademica._meta.concrete_fields] == [
        "id", "pessoa", "fonte", "id_externo", "curso", "unidade", "nivel", "modalidade",
        "forma_oferta", "ano_conclusao", "data_conclusao", "incorporado_em",
    ]


def test_baseline_da_003_continua_rascunho_apos_uso_em_campanha():
    baseline = materializar().versao
    campanha = _campanha(baseline)
    rejeita([Motivo.VERSAO_NAO_PUBLICADA], op.abrir, campanha, agora=NO_PERIODO)
    gravada = Versao.objects.get(pk=baseline.pk)
    assert gravada.estado == EstadoVersao.RASCUNHO and gravada.publicada_em is None

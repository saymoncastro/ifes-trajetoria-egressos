"""Operações de escrita dos encontros (031, incremento 1; T012, T013, T016–T018, T023)."""

from datetime import timedelta

import pytest

from tests.participacao import construcao as c
from tests.portal import construcao_encontros as ce
from trajetoria.portal.encontros import operacoes
from trajetoria.portal.encontros.mensagens import VERSAO_DA_CIENCIA, VERSAO_DO_TERMO
from trajetoria.portal.encontros.regras import EncontroRejeitado, Motivo
from trajetoria.portal.models import Confirmacao, Encontro

pytestmark = pytest.mark.django_db

DEPOIS = c.NO_PERIODO + timedelta(hours=1)


@pytest.fixture
def pessoas(cenario):
    return {k: cenario.pessoa(v) for k, v in (
        ("ana", "SIM-P-0001"), ("bruno", "SIM-P-0002"), ("maria", "SIM-P-0003"),
        ("diego", "SIM-P-0004"),
    )}


def _motivos(executar) -> set:
    with pytest.raises(EncontroRejeitado) as erro:
        executar()
    return set(erro.value.motivos)


# --- Propor (FR-001 a FR-006; clarify 3) --------------------------------------------------------

def test_propor_grava_em_analise_com_origem_copiada_e_termo(pessoas):
    maria = pessoas["maria"]
    especializacao = maria.conclusoes.get(curso="Especialização em Informática na Educação")
    encontro = ce.propor(maria, especializacao, publico_cursos=["Licenciatura em Química"])
    assert encontro.pessoa_id == maria.pk and encontro.conclusao_origem_id == especializacao.pk
    assert (encontro.origem_curso, encontro.origem_unidade, encontro.origem_ano) == (
        "Especialização em Informática na Educação", "Cefor", 2025)
    assert encontro.versao_do_termo == VERSAO_DO_TERMO and encontro.enviado_em == c.NO_PERIODO
    assert encontro.publicado_em is None
    assert encontro.publico_cursos == ["Licenciatura em Química"]


def test_publico_nao_precisa_incluir_a_formacao_de_quem_propoe(pessoas):
    encontro = ce.propor(pessoas["maria"], publico_unidades=["Vila Velha"])
    assert encontro.publico_unidades == ["Vila Velha"]  # FR-005


def test_conclusao_de_outra_pessoa_e_recusada(pessoas):
    alheia = pessoas["diego"].conclusoes.first()
    assert Motivo.ORIGEM in _motivos(lambda: ce.propor(pessoas["maria"], alheia))
    assert not Encontro.objects.exists()


def test_termo_desatualizado_e_recusado(pessoas):
    maria = pessoas["maria"]
    assert Motivo.TERMO in _motivos(lambda: operacoes.propor(
        maria, ce.proposta(maria.conclusoes.first()), versao_do_termo="antiga",
        agora=c.NO_PERIODO))


def test_validacoes_da_proposta(pessoas):
    motivos = _motivos(lambda: ce.propor(
        pessoas["maria"], titulo="", link="http://x.org", publico_cursos=[],
        inicio=c.NO_PERIODO + timedelta(days=1),
    ))
    assert {Motivo.TITULO, Motivo.LINK, Motivo.PUBLICO, Motivo.DATA} <= motivos


def test_limite_de_tres_ativos(pessoas):
    maria = pessoas["maria"]
    primeiro = ce.propor(maria)
    ce.propor(maria)
    ce.propor(maria)
    assert Motivo.LIMITE in _motivos(lambda: ce.propor(maria))
    operacoes.cancelar(maria, primeiro.pk, agora=DEPOIS)
    assert ce.propor(maria)  # cancelado não conta


def test_recusado_e_encerrado_nao_contam_no_limite(pessoas):
    maria = pessoas["maria"]
    recusado = ce.propor(maria)
    operacoes.recusar(recusado.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG,
                      motivo="comercial", complemento="", agora=DEPOIS)
    ce.propor(maria)
    ce.propor(maria)
    assert ce.propor(maria)


# --- Moderar (FR-015 a FR-017; clarify 2) -------------------------------------------------------

def test_publicar_grava_operador_e_escopo(pessoas):
    encontro = ce.propor(pessoas["bruno"], publico_unidades=["Vitória"])
    operacoes.publicar(encontro.pk, operador=ce.OPERADOR_B, escopo=ce.VITORIA, agora=DEPOIS)
    encontro.refresh_from_db()
    assert (encontro.publicado_em, encontro.publicado_por, encontro.publicado_por_escopo) == (
        DEPOIS, ce.OPERADOR_B, "Vitória")


def test_cpaeg_age_tambem_em_unidade_unica(pessoas):
    encontro = ce.propor(pessoas["bruno"], publico_unidades=["Vitória"])
    operacoes.publicar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, agora=DEPOIS)
    encontro.refresh_from_db()
    assert encontro.publicado_por_escopo == "institucional"


@pytest.mark.parametrize("publico", [None, ["Vitória", "Serra"]])
def test_csaeg_nao_modera_fora_da_unidade_unica(pessoas, publico):
    encontro = ce.propor(pessoas["bruno"], publico_unidades=publico)
    assert Motivo.FORA_DO_ESCOPO in _motivos(lambda: operacoes.publicar(
        encontro.pk, operador=ce.OPERADOR_B, escopo=ce.VITORIA, agora=DEPOIS))
    encontro.refresh_from_db()
    assert encontro.publicado_em is None


def test_csaeg_de_outra_unidade_nao_modera(pessoas):
    encontro = ce.propor(pessoas["bruno"], publico_unidades=["Vitória"])
    assert Motivo.FORA_DO_ESCOPO in _motivos(lambda: operacoes.publicar(
        encontro.pk, operador="x", escopo=ce.VILA_VELHA, agora=DEPOIS))


def test_recusa_com_motivo_e_definitiva(pessoas):
    encontro = ce.propor(pessoas["maria"])
    assert Motivo.COMPLEMENTO in _motivos(lambda: operacoes.recusar(
        encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="outro",
        complemento="", agora=DEPOIS))
    operacoes.recusar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="outro",
                      complemento="Explicação.", agora=DEPOIS)
    encontro.refresh_from_db()
    assert (encontro.motivo, encontro.complemento) == ("outro", "Explicação.")
    assert Motivo.ESTADO in _motivos(lambda: operacoes.publicar(
        encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, agora=DEPOIS))


def test_retirar_so_publicado(pessoas):
    em_analise = ce.propor(pessoas["maria"])
    assert Motivo.ESTADO in _motivos(lambda: operacoes.retirar(
        em_analise.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="link",
        complemento="", agora=DEPOIS))
    publicado = ce.publicado(pessoas["maria"])
    operacoes.retirar(publicado.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="link",
                      complemento="", agora=DEPOIS)
    publicado.refresh_from_db()
    assert publicado.retirado_por == ce.OPERADOR_A and publicado.motivo == "link"


def test_nao_publica_depois_do_inicio(pessoas):
    encontro = ce.propor(pessoas["maria"])
    assert Motivo.ESTADO in _motivos(lambda: operacoes.publicar(
        encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, agora=ce.INICIO))


# --- Cancelar (FR-009) --------------------------------------------------------------------------

def test_organizador_cancela_ate_o_inicio(pessoas):
    maria = pessoas["maria"]
    encontro = ce.publicado(maria)
    assert Motivo.FORA_DO_ESCOPO in _motivos(
        lambda: operacoes.cancelar(pessoas["diego"], encontro.pk, agora=DEPOIS))
    assert Motivo.ESTADO in _motivos(lambda: operacoes.cancelar(maria, encontro.pk,
                                                                agora=ce.INICIO))
    operacoes.cancelar(maria, encontro.pk, agora=DEPOIS)
    encontro.refresh_from_db()
    assert encontro.cancelado_em == DEPOIS


# --- Confirmar e cancelar a confirmação (FR-020, FR-023) ----------------------------------------

def test_confirmar_grava_ciencia_e_uma_so_ativa(pessoas):
    encontro = ce.publicado(pessoas["maria"])
    confirmacao = ce.confirmar(pessoas["diego"], encontro)
    assert confirmacao.versao_da_ciencia == VERSAO_DA_CIENCIA
    assert Motivo.DUPLICADA in _motivos(lambda: ce.confirmar(pessoas["diego"], encontro))


def test_organizador_nao_confirma_o_proprio(pessoas):
    encontro = ce.publicado(pessoas["maria"])
    assert Motivo.PROPRIO in _motivos(lambda: ce.confirmar(pessoas["maria"], encontro))


def test_nao_confirma_fora_de_publicado_nem_depois_do_inicio(pessoas):
    em_analise = ce.propor(pessoas["maria"])
    assert Motivo.ESTADO in _motivos(lambda: ce.confirmar(pessoas["diego"], em_analise))
    publicado = ce.publicado(pessoas["maria"])
    assert Motivo.ESTADO in _motivos(lambda: ce.confirmar(pessoas["diego"], publicado,
                                                          agora=ce.INICIO))


def test_ciencia_desatualizada(pessoas):
    encontro = ce.publicado(pessoas["maria"])
    assert Motivo.CIENCIA in _motivos(lambda: operacoes.confirmar(
        pessoas["diego"], encontro.pk, versao_da_ciencia="antiga", agora=c.NO_PERIODO))


def test_cancelar_confirmacao_e_confirmar_de_novo(pessoas):
    encontro = ce.publicado(pessoas["maria"])
    primeira = ce.confirmar(pessoas["diego"], encontro)
    operacoes.cancelar_participacao(pessoas["diego"], encontro.pk, agora=DEPOIS)
    primeira.refresh_from_db()
    assert primeira.cancelada_em == DEPOIS
    segunda = ce.confirmar(pessoas["diego"], encontro, agora=DEPOIS)
    assert segunda.pk != primeira.pk
    assert Confirmacao.objects.filter(encontro=encontro).count() == 2


def test_cancelar_confirmacao_so_antes_do_inicio(pessoas):
    encontro = ce.publicado(pessoas["maria"])
    ce.confirmar(pessoas["diego"], encontro)
    assert Motivo.ESTADO in _motivos(lambda: operacoes.cancelar_participacao(
        pessoas["diego"], encontro.pk, agora=ce.INICIO))

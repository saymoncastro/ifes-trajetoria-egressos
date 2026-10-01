"""Estado temporal × imutabilidade histórica (US9; FR-039, FR-040, FR-043, FR-044).

O estado temporal controla a coleta; a primeira abertura (`aberta_em`) controla a
imutabilidade. Período de todos os casos: 01/03/2027 a 31/03/2027.
"""

from datetime import date

import pytest

from tests.campanha import construcao as c
from tests.campanha.construcao import linha, momento, rejeita
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.operacoes import SituacaoAbertura
from trajetoria.campanha.regras import Motivo

pytestmark = pytest.mark.django_db

INICIO, FIM = date(2027, 3, 1), date(2027, 3, 31)

# Cada escrita de preparação, isolada. Recebe a Campanha e outra Versão publicada.
ESCRITAS = {
    "nome": lambda cp, v: op.alterar_campanha(cp, nome="Outro nome"),
    "versao": lambda cp, v: op.alterar_campanha(cp, versao=v),
    "so_inicio": lambda cp, v: op.definir_periodo(cp, date(2027, 2, 1), FIM),
    "so_fim": lambda cp, v: op.definir_periodo(cp, INICIO, date(2027, 4, 30)),
    "periodo": lambda cp, v: op.definir_periodo(cp, date(2027, 6, 1), date(2027, 6, 30)),
    "ano_minimo": lambda cp, v: op.definir_criterios(cp, ano_minimo=2019, ano_maximo=2024),
    "ano_maximo": lambda cp, v: op.definir_criterios(cp, ano_minimo=2020, ano_maximo=2025),
    "unidades": lambda cp, v: op.definir_criterios(cp, ano_minimo=2020, ano_maximo=2024,
                                                   unidades=["Serra"]),
    "niveis": lambda cp, v: op.definir_criterios(cp, ano_minimo=2020, ano_maximo=2024,
                                                 niveis=["Técnico"]),
    "modalidades": lambda cp, v: op.definir_criterios(cp, ano_minimo=2020, ano_maximo=2024,
                                                      modalidades=["A distância"]),
    "formas_oferta": lambda cp, v: op.definir_criterios(cp, ano_minimo=2020, ano_maximo=2024,
                                                        formas_oferta=["Integrado"]),
    "populacao_ampla": lambda cp, v: op.definir_criterios(cp),
    "remover": lambda cp, v: op.remover_campanha(cp),
}


@pytest.fixture
def outra_versao():
    return c.versao_publicada("outra")


def _nunca_aberta(versao):
    campanha = op.definir_periodo(op.criar_campanha("Campanha", versao), INICIO, FIM)
    return op.definir_criterios(campanha, ano_minimo=2020, ano_maximo=2024)


def _aberta(versao):
    campanha = _nunca_aberta(versao)
    assert op.abrir(campanha, agora=momento(2027, 3, 10)) is SituacaoAbertura.ABERTA
    return Campanha.objects.get(pk=campanha.pk)


def _aceita(escrita, campanha, outra_versao):
    ESCRITAS[escrita](campanha, outra_versao)
    if escrita == "remover":
        assert not Campanha.objects.filter(pk=campanha.pk).exists()
    else:
        assert Campanha.objects.get(pk=campanha.pk).aberta_em is None


def _rejeitada(escrita, campanha, outra_versao):
    antes = linha(campanha)
    rejeita([Motivo.CAMPANHA_JA_ABERTA], ESCRITAS[escrita], campanha, outra_versao)
    assert linha(campanha) == antes


# --- Nunca aberta: editável e removível, qualquer que seja o estado temporal ------------


@pytest.mark.parametrize("escrita", ESCRITAS)
def test_m_a_nunca_aberta_dentro_da_janela(versao_publicada, outra_versao, escrita):
    campanha = _nunca_aberta(versao_publicada)
    assert estado(campanha, agora=momento(2027, 3, 15)) is EstadoCampanha.EM_PREPARACAO
    _aceita(escrita, campanha, outra_versao)


def test_m_b_nunca_aberta_depois_do_fim_e_encerrada_mas_nao_acionavel(versao_publicada):
    campanha = _nunca_aberta(versao_publicada)
    agora = momento(2027, 4, 10)
    assert estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA
    assert campanha.aberta_em is None
    antes = linha(campanha)
    rejeita([Motivo.FORA_DO_PERIODO], op.abrir, campanha, agora=agora)
    rejeita([Motivo.CAMPANHA_NUNCA_ABERTA], op.encerrar, campanha, agora=agora)
    assert linha(campanha) == antes


@pytest.mark.parametrize("escrita", ESCRITAS)
def test_m_b_nunca_aberta_depois_do_fim_continua_editavel(
    versao_publicada, outra_versao, escrita
):
    campanha = _nunca_aberta(versao_publicada)
    assert estado(campanha, agora=momento(2027, 4, 10)) is EstadoCampanha.ENCERRADA
    _aceita(escrita, campanha, outra_versao)


def test_m_c_periodo_corrigido_volta_a_preparacao_sem_reabertura(versao_publicada):
    campanha = _nunca_aberta(versao_publicada)
    assert estado(campanha, agora=momento(2027, 4, 10)) is EstadoCampanha.ENCERRADA

    campanha = op.definir_periodo(campanha, date(2027, 6, 1), date(2027, 6, 30))

    assert estado(campanha, agora=momento(2027, 4, 10)) is EstadoCampanha.EM_PREPARACAO
    assert campanha.aberta_em is None
    assert op.abrir(campanha, agora=momento(2027, 6, 1)) is SituacaoAbertura.ABERTA


# --- Aberta alguma vez: imutável e não removível -----------------------------------------


def test_m_d_aberta_registra_aberta_em(versao_publicada):
    campanha = _aberta(versao_publicada)
    assert campanha.aberta_em == momento(2027, 3, 10)
    assert estado(campanha, agora=momento(2027, 3, 15)) is EstadoCampanha.EM_COLETA


@pytest.mark.parametrize("escrita", ESCRITAS)
def test_m_d_em_coleta_imutavel(versao_publicada, outra_versao, escrita):
    _rejeitada(escrita, _aberta(versao_publicada), outra_versao)


@pytest.mark.parametrize("escrita", ESCRITAS)
def test_m_e_encerrada_pelo_tempo_imutavel(versao_publicada, outra_versao, escrita):
    campanha = _aberta(versao_publicada)
    assert estado(campanha, agora=momento(2027, 4, 10)) is EstadoCampanha.ENCERRADA
    _rejeitada(escrita, campanha, outra_versao)


@pytest.mark.parametrize("escrita", ESCRITAS)
def test_m_f_encerrada_antecipadamente_imutavel(versao_publicada, outra_versao, escrita):
    campanha = _aberta(versao_publicada)
    op.encerrar(campanha, agora=momento(2027, 3, 20))
    campanha = Campanha.objects.get(pk=campanha.pk)
    assert estado(campanha, agora=momento(2027, 3, 25)) is EstadoCampanha.ENCERRADA
    _rejeitada(escrita, campanha, outra_versao)


def test_combinacao_valida_e_invalida_em_campanha_aberta_nada_aplicado(versao_publicada):
    campanha = _aberta(versao_publicada)
    antes = linha(campanha)
    rejeita(
        [Motivo.CAMPANHA_JA_ABERTA],
        op.definir_criterios,
        campanha,
        unidades=["Serra"],
        ano_minimo=0,
    )
    assert linha(campanha) == antes


def test_em_coleta_encerramento_antecipado_continua_permitido(versao_publicada):
    campanha = _aberta(versao_publicada)
    op.encerrar(campanha, agora=momento(2027, 3, 20))
    assert Campanha.objects.get(pk=campanha.pk).encerrada_em == momento(2027, 3, 20)

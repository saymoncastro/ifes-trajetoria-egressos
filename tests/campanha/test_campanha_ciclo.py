"""Estado derivado, abertura e encerramento (US6, US8; FR-034–FR-042)."""

from datetime import date, datetime

import pytest

from tests.campanha.construcao import linha, momento, rejeita
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import EstadoCampanha, FormaEncerramento, encerramento, estado
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.operacoes import SituacaoAbertura, SituacaoEncerramento
from trajetoria.campanha.regras import Motivo
from trajetoria.formulario_2024.materializacao import materializar
from trajetoria.instrumento.models import EstadoVersao, Versao

pytestmark = pytest.mark.django_db

EM_PREPARACAO = EstadoCampanha.EM_PREPARACAO
EM_COLETA = EstadoCampanha.EM_COLETA
ENCERRADA = EstadoCampanha.ENCERRADA

INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)


def _campanha(versao, **campos):
    return Campanha.objects.create(
        nome="Campanha", versao=versao, inicio=INICIO, fim=FIM, **campos
    )


# --- Estado derivado: precedência encerramento explícito → fim → abertura → preparação ---


def _sem_escrita(campanha, agora):
    antes = linha(campanha)
    resultado = estado(campanha, agora=agora)
    assert linha(campanha) == antes  # nenhuma escrita, nenhum job
    return resultado


def test_e1_antes_do_inicio_nunca_aberta(versao_publicada):
    assert _sem_escrita(_campanha(versao_publicada), momento(2027, 3, 31)) is EM_PREPARACAO


def test_e2_no_periodo_nunca_aberta(versao_publicada):
    assert _sem_escrita(_campanha(versao_publicada), momento(2027, 5, 1)) is EM_PREPARACAO


def test_e3_no_periodo_aberta(versao_publicada):
    c = _campanha(versao_publicada, aberta_em=momento(2027, 4, 1))
    assert _sem_escrita(c, momento(2027, 5, 1)) is EM_COLETA


def test_e4_encerrada_explicitamente_mesmo_dentro_do_periodo(versao_publicada):
    c = _campanha(
        versao_publicada, aberta_em=momento(2027, 4, 1), encerrada_em=momento(2027, 4, 20)
    )
    assert _sem_escrita(c, momento(2027, 5, 1)) is ENCERRADA


def test_e5_depois_do_fim_aberta(versao_publicada):
    c = _campanha(versao_publicada, aberta_em=momento(2027, 4, 1))
    assert _sem_escrita(c, momento(2027, 7, 1)) is ENCERRADA


def test_e6_depois_do_fim_nunca_aberta(versao_publicada):
    assert _sem_escrita(_campanha(versao_publicada), momento(2027, 7, 1)) is ENCERRADA


@pytest.mark.parametrize("agora", [momento(1990, 1, 1), momento(2027, 5, 1), momento(2099, 1, 1)])
def test_sem_periodo_e_sempre_em_preparacao(versao_publicada, agora):
    c = Campanha.objects.create(nome="Sem período", versao=versao_publicada)
    assert _sem_escrita(c, agora) is EM_PREPARACAO


def test_ultimo_dia_ainda_em_coleta_e_dia_seguinte_encerrada(versao_publicada):
    c = _campanha(versao_publicada, aberta_em=momento(2027, 4, 1))
    assert estado(c, agora=momento(2027, 6, 30, hora=23)) is EM_COLETA
    assert estado(c, agora=momento(2027, 7, 1, hora=0)) is ENCERRADA


# --- US6: abertura --------------------------------------------------------------------


def _preparada(versao, periodo=(INICIO, FIM)):
    campanha = op.criar_campanha("Campanha", versao)
    return op.definir_periodo(campanha, *periodo) if periodo else campanha


def _rejeita_sem_mudanca(motivos, campanha, agora):
    antes = linha(campanha)
    versao_antes = Versao.objects.filter(pk=campanha.versao_id).values().get()
    rejeita(motivos, op.abrir, campanha, agora=agora)
    assert linha(campanha) == antes
    assert Versao.objects.filter(pk=campanha.versao_id).values().get() == versao_antes


def test_versao_rascunho_impede_abertura_e_baseline_continua_rascunho():
    baseline = materializar().versao
    campanha = _preparada(baseline)
    _rejeita_sem_mudanca([Motivo.VERSAO_NAO_PUBLICADA], campanha, momento(2027, 4, 15))
    assert estado(campanha, agora=momento(2027, 4, 15)) is EM_PREPARACAO
    gravada = Versao.objects.get(pk=baseline.pk)
    assert gravada.estado == EstadoVersao.RASCUNHO and gravada.publicada_em is None


def test_versao_publicada_abre_dentro_do_periodo(versao_publicada):
    campanha = _preparada(versao_publicada)
    agora = momento(2027, 4, 1)
    assert op.abrir(campanha, agora=agora) is SituacaoAbertura.ABERTA
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert gravada.aberta_em == agora
    assert estado(gravada, agora=agora) is EM_COLETA


def test_periodo_nao_definido(versao_publicada):
    campanha = _preparada(versao_publicada, periodo=None)
    _rejeita_sem_mudanca([Motivo.PERIODO_NAO_DEFINIDO], campanha, momento(2027, 4, 15))


def test_todas_as_pendencias_numa_rejeicao(versao_rascunho):
    campanha = _preparada(versao_rascunho, periodo=None)
    _rejeita_sem_mudanca(
        [Motivo.VERSAO_NAO_PUBLICADA, Motivo.PERIODO_NAO_DEFINIDO],
        campanha,
        momento(2027, 4, 15),
    )


def test_antes_do_inicio(versao_publicada):
    campanha = _preparada(versao_publicada)
    _rejeita_sem_mudanca([Motivo.FORA_DO_PERIODO], campanha, momento(2027, 3, 31, hora=23))


@pytest.mark.parametrize("dia", [date(2027, 4, 1), date(2027, 5, 15), date(2027, 6, 30)])
def test_dentro_da_janela_inclusive_extremos(versao_publicada, dia):
    campanha = _preparada(versao_publicada)
    agora = momento(dia.year, dia.month, dia.day)
    assert op.abrir(campanha, agora=agora) is SituacaoAbertura.ABERTA


def test_depois_do_fim_nunca_aberta(versao_publicada):
    campanha = _preparada(versao_publicada)
    agora = momento(2027, 7, 1)
    assert estado(campanha, agora=agora) is ENCERRADA
    _rejeita_sem_mudanca([Motivo.FORA_DO_PERIODO], campanha, agora)


def test_segunda_abertura_nao_muda_nada(versao_publicada):
    campanha = _preparada(versao_publicada)
    op.abrir(campanha, agora=momento(2027, 4, 1))
    antes = linha(campanha)
    assert op.abrir(campanha, agora=momento(2027, 4, 2)) is SituacaoAbertura.JA_EM_COLETA
    assert linha(campanha) == antes


def test_abertura_de_campanha_aberta_e_encerrada(versao_publicada):
    campanha = _preparada(versao_publicada)
    op.abrir(campanha, agora=momento(2027, 4, 1))
    antes = linha(campanha)
    assert op.abrir(campanha, agora=momento(2027, 7, 1)) is SituacaoAbertura.JA_ENCERRADA
    assert linha(campanha) == antes


# --- US8: encerramento ----------------------------------------------------------------


def _em_coleta(versao):
    campanha = _preparada(versao)
    op.abrir(campanha, agora=momento(2027, 4, 1))
    return Campanha.objects.get(pk=campanha.pk)


def test_encerramento_antecipado(versao_publicada):
    campanha = _em_coleta(versao_publicada)
    agora = momento(2027, 5, 15)
    assert op.encerrar(campanha, agora=agora) is SituacaoEncerramento.ENCERRADA
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert gravada.encerrada_em == agora
    assert (gravada.inicio, gravada.fim) == (INICIO, FIM)
    assert estado(gravada, agora=agora) is ENCERRADA
    assert encerramento(gravada, agora=agora) == (FormaEncerramento.EXPLICITA, agora)


@pytest.mark.parametrize("aberta", [True, False], ids=["aberta", "nunca_aberta"])
def test_encerramento_pelo_fim_do_periodo(versao_publicada, aberta):
    campanha = _em_coleta(versao_publicada) if aberta else _preparada(versao_publicada)
    antes = linha(campanha)
    fim_do_ultimo_dia = momento(2027, 7, 1, hora=0)
    assert encerramento(campanha, agora=momento(2027, 7, 2)) == (
        FormaEncerramento.FIM_DO_PERIODO,
        fim_do_ultimo_dia,
    )
    assert linha(campanha) == antes


def test_encerrar_aberta_e_ja_encerrada_nao_muda_nada(versao_publicada):
    explicita = _em_coleta(versao_publicada)
    op.encerrar(explicita, agora=momento(2027, 5, 15))
    por_data = _em_coleta(versao_publicada)
    for campanha in (explicita, por_data):
        antes = linha(campanha)
        situacao = op.encerrar(campanha, agora=momento(2027, 7, 10))
        assert situacao is SituacaoEncerramento.JA_ENCERRADA
        assert linha(campanha) == antes


@pytest.mark.parametrize(
    "agora",
    [momento(2027, 3, 1), momento(2027, 5, 1), momento(2027, 7, 10)],
    ids=["periodo_futuro", "periodo_em_curso", "periodo_expirado"],
)
def test_encerrar_nunca_aberta_rejeitado_sem_gravar(versao_publicada, agora):
    campanha = _preparada(versao_publicada)
    antes = linha(campanha)
    rejeita([Motivo.CAMPANHA_NUNCA_ABERTA], op.encerrar, campanha, agora=agora)
    assert linha(campanha) == antes
    assert Campanha.objects.get(pk=campanha.pk).encerrada_em is None


def test_contexto_permanece_consultavel_apos_encerrar(versao_publicada):
    campanha = _preparada(versao_publicada)
    op.definir_criterios(campanha, ano_minimo=2020, unidades=["Serra"])
    op.abrir(campanha, agora=momento(2027, 4, 1))
    antes = linha(campanha)
    op.encerrar(campanha, agora=momento(2027, 5, 15))
    depois = linha(campanha)
    assert {k: v for k, v in depois.items() if k != "encerrada_em"} == {
        k: v for k, v in antes.items() if k != "encerrada_em"
    }
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert gravada.versao_id == versao_publicada.pk
    assert gravada.pesquisa == versao_publicada.pesquisa


def test_encerramento_e_none_fora_de_encerrada(versao_publicada):
    assert encerramento(_preparada(versao_publicada), agora=momento(2027, 5, 1)) is None
    assert encerramento(_em_coleta(versao_publicada), agora=momento(2027, 5, 1)) is None


# --- Revisão: fatos valem a partir do momento; tipos de `agora`; instância sincronizada ----


def test_encerrar_antes_da_abertura_rejeitado_sem_gravar(versao_publicada):
    campanha = _preparada(versao_publicada)
    op.abrir(campanha, agora=momento(2027, 4, 10, hora=12))
    antes = linha(campanha)
    rejeita(
        [Motivo.ANTES_DA_ABERTURA], op.encerrar, campanha, agora=momento(2027, 4, 10, hora=9)
    )
    assert linha(campanha) == antes


def test_encerramento_gravado_nao_e_sobrescrito_por_agora_anterior(versao_publicada):
    campanha = _em_coleta(versao_publicada)
    op.encerrar(campanha, agora=momento(2027, 5, 15))
    antes = linha(campanha)
    assert op.encerrar(campanha, agora=momento(2027, 5, 1)) is SituacaoEncerramento.JA_ENCERRADA
    assert linha(campanha) == antes


def test_fatos_so_valem_a_partir_do_momento_em_que_ocorreram(versao_publicada):
    campanha = _preparada(versao_publicada)
    op.abrir(campanha, agora=momento(2027, 4, 10))
    op.encerrar(campanha, agora=momento(2027, 5, 15))
    assert estado(campanha, agora=momento(2027, 4, 5)) is EM_PREPARACAO
    assert estado(campanha, agora=momento(2027, 5, 1)) is EM_COLETA
    assert estado(campanha, agora=momento(2027, 5, 20)) is ENCERRADA
    assert encerramento(campanha, agora=momento(2027, 5, 1)) is None


@pytest.mark.parametrize(
    "agora", [datetime(2027, 5, 1, 12), date(2027, 5, 1), "2027-05-01"],
    ids=["datetime_ingenuo", "date", "texto"],
)
def test_agora_de_tipo_errado(versao_publicada, agora):
    campanha = _preparada(versao_publicada)
    with pytest.raises(TypeError):
        estado(campanha, agora=agora)
    with pytest.raises(TypeError):
        op.abrir(campanha, agora=agora)


def test_operacoes_atualizam_a_instancia_recebida(versao_publicada):
    campanha = op.criar_campanha("Campanha", versao_publicada)
    op.definir_periodo(campanha, INICIO, FIM)
    op.definir_criterios(campanha, ano_minimo=2020)
    assert (campanha.inicio, campanha.fim, campanha.ano_minimo) == (INICIO, FIM, 2020)

    op.abrir(campanha, agora=momento(2027, 4, 1))
    assert campanha.aberta_em == momento(2027, 4, 1)
    assert estado(campanha, agora=momento(2027, 4, 1)) is EM_COLETA

    op.encerrar(campanha, agora=momento(2027, 4, 20))
    assert campanha.encerrada_em == momento(2027, 4, 20)
    assert estado(campanha, agora=momento(2027, 4, 20)) is ENCERRADA

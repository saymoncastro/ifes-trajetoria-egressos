"""Preparação da Campanha: criação, Versão, período e definição de critérios (US1, US2, US4,
US11; FR-001–FR-024)."""

from datetime import date

import pytest

from tests.campanha import construcao as c
from tests.campanha.construcao import linha, rejeita
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.regras import Motivo
from trajetoria.formulario_2024.materializacao import materializar
from trajetoria.instrumento.models import EstadoVersao, Versao

pytestmark = pytest.mark.django_db


def _versao_intacta(versao):
    gravada = Versao.objects.get(pk=versao.pk)
    return gravada.estado, gravada.publicada_em


# --- US1: criar Campanha vinculada a uma Versão -----------------------------------------


@pytest.mark.parametrize(
    "fabrica",
    [c.versao_publicada, c.versao_rascunho, lambda: materializar().versao],
    ids=["publicada", "rascunho", "baseline_003"],
)
def test_cria_com_versao_em_qualquer_estado(fabrica):
    versao = fabrica()
    antes = _versao_intacta(versao)

    campanha = op.criar_campanha("Pesquisa Institucional de Egressos 2027", versao)

    assert estado(campanha, agora=c.momento(2027, 1, 1)) is EstadoCampanha.EM_PREPARACAO
    assert campanha.populacao_ampla
    assert campanha.inicio is None and campanha.fim is None
    assert campanha.versao_id == versao.pk
    assert campanha.pesquisa == versao.pesquisa
    assert _versao_intacta(versao) == antes


def test_baseline_da_003_continua_rascunho():
    versao = materializar().versao
    op.criar_campanha("Com a baseline", versao)
    assert Versao.objects.get(pk=versao.pk).estado == EstadoVersao.RASCUNHO


def test_mesma_versao_em_duas_campanhas(versao_publicada):
    a = op.criar_campanha("A", versao_publicada)
    b = op.criar_campanha("B", versao_publicada)
    assert a.pk != b.pk
    assert set(Campanha.objects.filter(versao=versao_publicada)) == {a, b}


@pytest.mark.parametrize("nome", ["", "   "])
def test_nome_vazio_rejeitado_e_nada_criado(versao_publicada, nome):
    rejeita([Motivo.NOME_VAZIO], op.criar_campanha, nome, versao_publicada)
    assert not Campanha.objects.exists()


def test_nome_gravado_como_recebido(versao_publicada):
    assert op.criar_campanha("  Rodada 2027 ", versao_publicada).nome == "  Rodada 2027 "


def test_tipos_errados(versao_publicada):
    with pytest.raises(TypeError):
        op.criar_campanha("Campanha", versao_publicada.pesquisa)
    with pytest.raises(TypeError):
        op.criar_campanha(None, versao_publicada)


def test_alterar_versao_para_outra_pesquisa_e_nome(versao_publicada):
    campanha = op.criar_campanha("Original", versao_publicada)
    nova = c.versao_rascunho("outra")
    assert nova.pesquisa_id != versao_publicada.pesquisa_id

    campanha = op.alterar_campanha(campanha, versao=nova)
    assert campanha.versao_id == nova.pk and campanha.nome == "Original"
    assert campanha.pesquisa == nova.pesquisa

    campanha = op.alterar_campanha(campanha, nome="Renomeada")
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert gravada.nome == "Renomeada" and gravada.versao_id == nova.pk


def test_alterar_nome_vazio_rejeitado(versao_publicada):
    campanha = op.criar_campanha("Original", versao_publicada)
    antes = linha(campanha)
    rejeita([Motivo.NOME_VAZIO], op.alterar_campanha, campanha, nome=" ")
    assert linha(campanha) == antes


def test_remover_em_preparacao(versao_publicada):
    campanha = op.criar_campanha("Descartável", versao_publicada)
    op.remover_campanha(campanha)
    assert not Campanha.objects.filter(pk=campanha.pk).exists()
    assert Versao.objects.filter(pk=versao_publicada.pk).exists()


# --- US2: período de coleta ---------------------------------------------------------------

INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)


def test_periodo_gravado_exatamente(versao_publicada):
    campanha = op.definir_periodo(op.criar_campanha("C", versao_publicada), INICIO, FIM)
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert (gravada.inicio, gravada.fim) == (INICIO, FIM)


def test_periodo_de_um_dia(versao_publicada):
    campanha = op.definir_periodo(op.criar_campanha("C", versao_publicada), INICIO, INICIO)
    assert campanha.inicio == campanha.fim == INICIO


@pytest.mark.parametrize(
    ("inicio", "fim", "motivo"),
    [
        (None, FIM, Motivo.PERIODO_INCOMPLETO),
        (INICIO, None, Motivo.PERIODO_INCOMPLETO),
        (FIM, INICIO, Motivo.PERIODO_INVERTIDO),
    ],
)
def test_periodo_invalido_mantem_o_anterior(versao_publicada, inicio, fim, motivo):
    campanha = op.definir_periodo(op.criar_campanha("C", versao_publicada), INICIO, FIM)
    antes = linha(campanha)
    rejeita([motivo], op.definir_periodo, campanha, inicio, fim)
    assert linha(campanha) == antes


def test_datetime_no_lugar_de_date(versao_publicada):
    campanha = op.criar_campanha("C", versao_publicada)
    with pytest.raises(TypeError):
        op.definir_periodo(campanha, c.momento(2027, 4, 1), FIM)


def test_sem_periodo_padrao_e_redefinicao(versao_publicada):
    campanha = op.criar_campanha("C", versao_publicada)
    assert (campanha.inicio, campanha.fim) == (None, None)
    op.definir_periodo(campanha, INICIO, FIM)
    campanha = op.definir_periodo(campanha, date(2028, 3, 1), date(2028, 3, 31))
    assert (campanha.inicio, campanha.fim) == (date(2028, 3, 1), date(2028, 3, 31))


# --- US4: definição de critérios de ano ---------------------------------------------------


def test_anos_invertidos_mantem_os_criterios_anteriores(versao_publicada):
    campanha = op.definir_criterios(
        op.criar_campanha("C", versao_publicada), ano_minimo=2020, ano_maximo=2024
    )
    antes = linha(campanha)
    rejeita(
        [Motivo.ANOS_INVERTIDOS],
        op.definir_criterios,
        campanha,
        ano_minimo=2025,
        ano_maximo=2020,
    )
    assert linha(campanha) == antes


def test_definir_criterios_sem_argumentos_volta_a_populacao_ampla(versao_publicada):
    campanha = op.definir_criterios(
        op.criar_campanha("C", versao_publicada), ano_minimo=2020, unidades=["Serra"]
    )
    assert not campanha.populacao_ampla
    campanha = op.definir_criterios(campanha)
    assert Campanha.objects.get(pk=campanha.pk).populacao_ampla


def test_anos_sao_absolutos_e_nao_mudam_com_o_tempo(versao_publicada):
    campanha = op.definir_criterios(
        op.criar_campanha("C", versao_publicada), ano_minimo=2020, ano_maximo=2024
    )
    for agora in (c.momento(2027, 1, 1), c.momento(2035, 1, 1)):
        estado(campanha, agora=agora)
        gravada = Campanha.objects.get(pk=campanha.pk)
        assert (gravada.ano_minimo, gravada.ano_maximo) == (2020, 2024)


# --- US11: configurações inválidas; NULL × [] ----------------------------------------------


def test_todas_as_violacoes_numa_rejeicao(versao_publicada):
    campanha = op.definir_criterios(
        op.criar_campanha("C", versao_publicada), ano_minimo=2020, unidades=["Serra"]
    )
    antes = linha(campanha)
    violacoes = rejeita(
        [Motivo.ANO_INVALIDO, Motivo.ANO_INVALIDO, Motivo.CONJUNTO_VAZIO, Motivo.VALOR_VAZIO],
        op.definir_criterios,
        campanha,
        ano_minimo="2020",
        ano_maximo=True,
        unidades=[],
        niveis=["  "],
    )
    assert [v.campo for v in violacoes] == ["ano_minimo", "ano_maximo", "unidades", "niveis"]
    assert linha(campanha) == antes


@pytest.mark.parametrize("ano", [0, -1, 2020.0, 40000])
def test_ano_invalido(versao_publicada, ano):
    campanha = op.criar_campanha("C", versao_publicada)
    rejeita([Motivo.ANO_INVALIDO], op.definir_criterios, campanha, ano_minimo=ano)


@pytest.mark.parametrize("vazio", [[], (), set()])
def test_null_nao_restringe_e_conjunto_vazio_nunca_e_gravado(versao_publicada, vazio):
    campanha = op.definir_criterios(op.criar_campanha("C", versao_publicada), unidades=None)
    assert Campanha.objects.get(pk=campanha.pk).unidades is None
    rejeita([Motivo.CONJUNTO_VAZIO], op.definir_criterios, campanha, unidades=vazio)
    assert Campanha.objects.get(pk=campanha.pk).unidades is None


def test_conjunto_sem_duplicatas_em_ordem_estavel_sem_normalizacao(versao_publicada):
    campanha = op.definir_criterios(
        op.criar_campanha("C", versao_publicada),
        unidades=["Vitória", "Serra", "Serra"],
        niveis=[" Técnico"],
    )
    gravada = Campanha.objects.get(pk=campanha.pk)
    assert gravada.unidades == ["Serra", "Vitória"]
    assert gravada.niveis == [" Técnico"]


@pytest.mark.parametrize("valor", ["Serra", [1], 5])
def test_conjunto_de_tipo_errado(versao_publicada, valor):
    campanha = op.criar_campanha("C", versao_publicada)
    with pytest.raises(TypeError):
        op.definir_criterios(campanha, unidades=valor)


def test_tipo_errado_em_alterar_campanha_aberta_e_type_error(versao_publicada):
    campanha = op.definir_periodo(
        op.criar_campanha("C", versao_publicada), date(2027, 4, 1), date(2027, 6, 30)
    )
    op.abrir(campanha, agora=c.momento(2027, 4, 1))
    with pytest.raises(TypeError):
        op.alterar_campanha(campanha, versao=versao_publicada.pesquisa)
    with pytest.raises(TypeError):
        op.alterar_campanha(campanha, nome=None)

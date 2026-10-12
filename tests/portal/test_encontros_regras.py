"""Regras puras dos encontros, sem banco (031, incremento 1; T004, T010, T011)."""

from datetime import timedelta
from types import SimpleNamespace

import pytest

from tests.participacao import construcao as c
from tests.portal import construcao_encontros as ce
from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros import regras
from trajetoria.portal.encontros.governanca import (
    INSTITUCIONAL,
    escopo_da_decisao,
    modera,
    responsavel,
)
from trajetoria.portal.encontros.regras import Motivo, Nivel, Quem, Situacao

AGORA = c.NO_PERIODO
INICIO = AGORA + timedelta(days=10)


def _encontro(**campos):
    dados = {
        "inicio": INICIO, "termino": INICIO + timedelta(hours=1), "publicado_em": None,
        "recusado_em": None, "retirado_em": None, "cancelado_em": None,
        "publico_unidades": None,
    }
    dados.update(campos)
    return SimpleNamespace(**dados)


# --- Situação (FR-010; data-model, ordem) -----------------------------------------------------

@pytest.mark.parametrize(("campos", "agora", "esperada"), [
    ({}, AGORA, Situacao.EM_ANALISE),
    ({}, INICIO, Situacao.NAO_ANALISADO),
    ({"publicado_em": AGORA}, AGORA, Situacao.PUBLICADO),
    ({"publicado_em": AGORA}, INICIO + timedelta(minutes=30), Situacao.PUBLICADO),
    ({"publicado_em": AGORA}, INICIO + timedelta(hours=1), Situacao.ENCERRADO),
    ({"recusado_em": AGORA}, AGORA, Situacao.RECUSADO),
    ({"publicado_em": AGORA, "retirado_em": AGORA}, AGORA, Situacao.RETIRADO),
    ({"publicado_em": AGORA, "cancelado_em": AGORA}, AGORA, Situacao.CANCELADO),
    # O cancelamento prevalece até sobre o fim do encontro.
    ({"publicado_em": AGORA, "cancelado_em": AGORA}, INICIO + timedelta(days=1),
     Situacao.CANCELADO),
])
def test_situacao(campos, agora, esperada):
    assert regras.situacao(_encontro(**campos), agora) is esperada


def test_ativo_so_em_analise_e_publicado_antes_do_termino():
    assert regras.ativo(_encontro(), AGORA)
    assert regras.ativo(_encontro(publicado_em=AGORA), AGORA)
    assert not regras.ativo(_encontro(publicado_em=AGORA), INICIO + timedelta(hours=2))
    assert not regras.ativo(_encontro(recusado_em=AGORA), AGORA)
    assert not regras.ativo(_encontro(), INICIO)


def test_aceita_confirmacao_so_publicado_antes_do_inicio():
    assert regras.aceita_confirmacao(_encontro(publicado_em=AGORA), AGORA)
    assert not regras.aceita_confirmacao(_encontro(publicado_em=AGORA), INICIO)
    assert not regras.aceita_confirmacao(_encontro(), AGORA)


# --- Validação (FR-002, FR-003, FR-017; H-3101) -----------------------------------------------

def test_textos_obrigatorios_e_limites():
    assert regras.violacoes_de_texto("t" * 90, "d" * 400, "n" * 40) == []
    motivos = {v.motivo for v in regras.violacoes_de_texto("t" * 91, "", "n" * 41)}
    assert motivos == {Motivo.TITULO, Motivo.DESCRICAO, Motivo.NOME}


@pytest.mark.parametrize(("dias", "valida"), [(1, False), (2, True), (90, True), (91, False)])
def test_data_entre_2_e_90_dias(dias, valida):
    inicio = AGORA + timedelta(days=dias)
    violacoes = regras.violacoes_de_horario(inicio, inicio + timedelta(hours=1), AGORA)
    assert (Motivo.DATA not in {v.motivo for v in violacoes}) is valida


@pytest.mark.parametrize("termino", [
    INICIO, INICIO - timedelta(minutes=1), INICIO + timedelta(hours=3, minutes=1),
    INICIO + timedelta(days=1),
])
def test_termino_depois_do_inicio_no_mesmo_dia_ate_3_horas(termino):
    assert Motivo.HORARIO in {v.motivo for v in regras.violacoes_de_horario(
        INICIO, termino, AGORA)}


def test_tres_horas_e_aceito():
    assert regras.violacoes_de_horario(INICIO, INICIO + timedelta(hours=3), AGORA) == []


@pytest.mark.parametrize("link", [
    "http://meet.exemplo.org/x", "https://usuario:senha@meet.exemplo.org/x",
    "https://10.0.0.1/sala", "https://meet.exemplo.org/com espaço", "",
    "https://meet.exemplo.org/" + "a" * 500,
])
def test_link_com_a_validacao_da_025(link):
    assert regras.link_invalido(link)


def test_link_valido():
    assert not regras.link_invalido(ce.LINK)


def test_motivo_e_complemento():
    assert regras.violacoes_de_decisao("comercial", "") == []
    assert {v.motivo for v in regras.violacoes_de_decisao("outro", "")} == {Motivo.COMPLEMENTO}
    assert {v.motivo for v in regras.violacoes_de_decisao("inventado", "")} == {Motivo.MOTIVO}
    assert {v.motivo for v in regras.violacoes_de_decisao("comercial", "x" * 301)} == {
        Motivo.COMPLEMENTO}


# --- Visibilidade (FR-021, FR-024a; clarify 1; research R10) -----------------------------------

_CONTEUDO = {
    Situacao.EM_ANALISE: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.NAO_ANALISADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.RECUSADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.PUBLICADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO, Quem.EGRESSO},
    Situacao.RETIRADO: {Quem.ORGANIZADOR, Quem.MODERACAO},
    Situacao.CANCELADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO},
    Situacao.ENCERRADO: {Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO},
}


@pytest.mark.parametrize("atual", list(Situacao))
@pytest.mark.parametrize("quem", list(Quem))
def test_o_que_ver(atual, quem):
    nivel = regras.o_que_ver(atual, quem)
    if quem is Quem.ANONIMO:
        assert nivel is Nivel.NEUTRA
    elif quem is Quem.SEM_CONCLUSAO:
        assert nivel is Nivel.SO_PARA_EGRESSOS
    elif quem in _CONTEUDO[atual]:
        assert nivel is Nivel.CONTEUDO
    elif atual in (Situacao.RETIRADO, Situacao.CANCELADO, Situacao.ENCERRADO):
        assert nivel is Nivel.SITUACAO
    else:
        assert nivel is Nivel.INDISPONIVEL


@pytest.mark.parametrize("atual", list(Situacao))
@pytest.mark.parametrize("quem", list(Quem))
def test_link_so_publicado_e_so_para_quem_pode(atual, quem):
    esperado = atual is Situacao.PUBLICADO and quem in (
        Quem.ORGANIZADOR, Quem.MODERACAO, Quem.CONFIRMADO)
    assert regras.mostra_link(atual, quem) is esperado


# --- Governança (FR-016; H-3102; clarify 2) -----------------------------------------------------

def test_responsavel_pela_unidade_unica_ou_institucional():
    assert responsavel(["Vitória"]) == "Vitória"
    assert responsavel(["Vitória", "Serra"]) == INSTITUCIONAL
    assert responsavel(None) == INSTITUCIONAL


def test_quem_modera():
    unica, varias, todos = (_encontro(publico_unidades=["Vitória"]),
                            _encontro(publico_unidades=["Vitória", "Serra"]), _encontro())
    assert all(modera(ce.CPAEG, e) for e in (unica, varias, todos))
    assert modera(ce.VITORIA, unica)
    assert not modera(ce.VITORIA, varias) and not modera(ce.VITORIA, todos)
    assert not modera(ce.VILA_VELHA, unica)
    assert not modera(None, unica)


def test_escopo_gravado_e_o_de_quem_decidiu():
    unica = _encontro(publico_unidades=["Vitória"])
    assert escopo_da_decisao(ce.CPAEG, unica) == INSTITUCIONAL
    assert escopo_da_decisao(ce.VITORIA, unica) == "Vitória"


# --- Vocabulário (T011; ADR 0009, decisão 7) ----------------------------------------------------

def _textos():
    for nome in (n for n in dir(m) if n.isupper()):
        valor = getattr(m, nome)
        if isinstance(valor, str):
            yield valor
        elif isinstance(valor, tuple | list):
            yield from (v for v in valor if isinstance(v, str))
        elif isinstance(valor, dict):
            yield from (v for v in valor.values() if isinstance(v, str))


def test_vocabulario():
    textos = " ".join(_textos()).lower()
    for vedado in ("turma", "geração", "conectad", "inscrito", "comunidade"):
        assert vedado not in textos, vedado
    # A confirmação nunca é chamada de inscrição nem registra presença: as palavras só aparecem
    # na negação da ciência e, para os eventos do Ifes, na página oficial de quem oferece.
    assert textos.count("inscrição") == 2
    assert "não é inscrição" in textos and "inscrição estão na página oficial" in textos
    assert textos.count("presença") == 1 and "não registra presença" in textos

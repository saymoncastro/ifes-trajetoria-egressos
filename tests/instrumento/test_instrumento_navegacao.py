"""Navegação condicional e finalização: US7 e US8 (FR-048–FR-055).

O momento de aplicação da regra na jornada não é modelado (FR-053): os testes verificam
apenas destinos e percursos de Seções.
"""

import dataclasses

import pytest

from tests.instrumento.construcao import percursos_de_secoes
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import RegraNavegacao, conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Secao
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada

pytestmark = pytest.mark.django_db


def _secoes(versao, *titulos):
    """Seções com uma pergunta de texto cada; devolve dict título → Seção."""
    secoes = {}
    for posicao, titulo in enumerate(titulos, start=1):
        secao = op.adicionar_secao(versao, posicao, titulo=titulo)
        op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", f"{titulo}?", obrigatoria=True)
        secoes[titulo] = secao
    return secoes


def _escolha(secao, *opcoes, obrigatoria=True):
    posicao = secao.perguntas.count() + 1
    pergunta = op.adicionar_pergunta(
        secao, posicao, "ESCOLHA_UNICA", "Escolha?", obrigatoria=obrigatoria
    )
    criadas = {texto: op.adicionar_opcao(pergunta, n, texto) for n, texto in enumerate(opcoes, 1)}
    return pergunta, criadas


def _percursos(versao):
    return percursos_de_secoes(conteudo_da_versao(versao))


def _regra_lida(versao, opcao):
    for secao in conteudo_da_versao(versao).secoes:
        for pergunta in secao.perguntas:
            for lida in pergunta.opcoes:
                if lida.id == opcao.id:
                    return lida.regra
    raise LookupError(opcao.id)


# --- US7 ----------------------------------------------------------------------------


def test_regra_associada_a_pergunta_e_opcao(versao):
    s = _secoes(versao, "A", "B", "C")
    pergunta, opcoes = _escolha(s["A"], "Sim", "Não")
    op.definir_regra(pergunta, opcoes["Não"], s["C"])
    assert _regra_lida(versao, opcoes["Não"]) == RegraNavegacao(s["C"].id, False)
    assert _regra_lida(versao, opcoes["Sim"]) is None
    op.remover_regra(pergunta, opcoes["Não"])
    assert _regra_lida(versao, opcoes["Não"]) is None


def test_fluxo_padrao_sem_regras(versao):
    _secoes(versao, "A", "B", "C")
    assert _percursos(versao) == {("A", "B", "C", "FIM")}


def test_padrao_q14_quatro_ramos_que_convergem(versao):
    s = _secoes(versao, "Nível", "Ramo 1", "Ramo 2", "Ramo 3", "Ramo 4", "Comum")
    pergunta, opcoes = _escolha(s["Nível"], "1", "2", "3", "4")
    for n in "1234":
        op.definir_regra(pergunta, opcoes[n], s[f"Ramo {n}"])
        op.definir_encaminhamento(s[f"Ramo {n}"], s["Comum"])
    assert _percursos(versao) == {("Nível", f"Ramo {n}", "Comum", "FIM") for n in "1234"}


def test_padrao_q33_ramo_que_salta_o_outro(versao):
    s = _secoes(versao, "Avaliação", "Trabalha", "Não trabalha", "Estudo")
    pergunta, opcoes = _escolha(s["Avaliação"], "Sim", "Não")
    op.definir_regra(pergunta, opcoes["Sim"], s["Trabalha"])
    op.definir_regra(pergunta, opcoes["Não"], s["Não trabalha"])
    op.definir_encaminhamento(s["Trabalha"], s["Estudo"])
    assert _percursos(versao) == {
        ("Avaliação", "Trabalha", "Estudo", "FIM"),
        ("Avaliação", "Não trabalha", "Estudo", "FIM"),
    }


def test_padrao_q51_regra_igual_ao_fluxo_padrao(versao):
    s = _secoes(versao, "Estuda", "Impactos")
    pergunta, opcoes = _escolha(s["Estuda"], "Ifes", "Pública", "Privada")
    antes = _percursos(versao)
    op.definir_regra(pergunta, opcoes["Privada"], s["Impactos"])
    assert _regra_lida(versao, opcoes["Privada"]) == RegraNavegacao(s["Impactos"].id, False)
    assert _percursos(versao) == antes == {("Estuda", "Impactos", "FIM")}


def test_pergunta_opcional_sem_resposta_segue_o_padrao(versao):
    s = _secoes(versao, "A", "B", "C")
    pergunta, opcoes = _escolha(s["A"], "Sim", "Não", obrigatoria=False)
    op.definir_regra(pergunta, opcoes["Sim"], s["C"])
    op.definir_regra(pergunta, opcoes["Não"], s["C"])
    assert _percursos(versao) == {("A", "C", "FIM"), ("A", "B", "C", "FIM")}


def test_pergunta_com_regras_no_meio_da_secao_sem_momento_de_aplicacao(versao):
    # Padrão Q46 seguida de Q47 e Q48: representável; quando o desvio se aplica é decisão
    # da Feature 003 e da jornada (FR-053).
    estudo = op.adicionar_secao(versao, 1, titulo="Estudo")
    pergunta, opcoes = _escolha(estudo, "Sim", "Não")
    op.adicionar_pergunta(estudo, 2, "ESCOLHA_MULTIPLA", "Q47?", obrigatoria=True)
    op.adicionar_pergunta(estudo, 3, "TEXTO_CURTO", "Q48?", obrigatoria=False)
    s = {"Estudo": estudo}
    for posicao, titulo in ((2, "Estuda"), (3, "Impactos")):
        s[titulo] = op.adicionar_secao(versao, posicao, titulo=titulo)
    op.definir_regra(pergunta, opcoes["Sim"], s["Estuda"])
    op.definir_regra(pergunta, opcoes["Não"], s["Impactos"])
    assert [f.name for f in dataclasses.fields(RegraNavegacao)] == ["destino_secao_id", "finaliza"]
    for modelo, campos in (
        (Opcao, {"id", "pergunta", "posicao", "texto", "complemento_textual", "regra_destino",
                 "regra_finaliza"}),
        (Secao, {"id", "versao", "posicao", "titulo", "texto", "encaminhamento"}),
    ):
        assert {c.name for c in modelo._meta.get_fields() if c.concrete} == campos
    assert _percursos(versao) == {
        ("Estudo", "Estuda", "Impactos", "FIM"),
        ("Estudo", "Impactos", "FIM"),
    }


def test_destino_nao_posterior_e_aceito_em_rascunho(versao):
    s = _secoes(versao, "A", "B")
    pergunta, opcoes = _escolha(s["B"], "Sim", "Não")
    op.definir_regra(pergunta, opcoes["Sim"], s["B"])
    op.definir_encaminhamento(s["B"], s["A"])
    assert _regra_lida(versao, opcoes["Sim"]) == RegraNavegacao(s["B"].id, False)


def test_encaminhamento_removivel(versao):
    s = _secoes(versao, "A", "B", "C")
    op.definir_encaminhamento(s["A"], s["C"])
    assert _percursos(versao) == {("A", "C", "FIM")}
    op.definir_encaminhamento(s["A"], None)
    assert _percursos(versao) == {("A", "B", "C", "FIM")}


# --- US8: finalização ---------------------------------------------------------------


def _termos(versao):
    termos = op.adicionar_secao(versao, 1, titulo="Termos", texto="Termos e condições.")
    pergunta, opcoes = _escolha(termos, "Sim", "Não")
    restantes = _secoes_a_partir(versao, 2, "Pessoais", "Impactos")
    return pergunta, opcoes, restantes


def _secoes_a_partir(versao, inicio, *titulos):
    secoes = {}
    for posicao, titulo in enumerate(titulos, start=inicio):
        secao = op.adicionar_secao(versao, posicao, titulo=titulo)
        op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", f"{titulo}?", obrigatoria=True)
        secoes[titulo] = secao
    return secoes


def test_regra_de_finalizacao(versao):
    pergunta, opcoes, _ = _termos(versao)
    op.definir_regra(pergunta, opcoes["Não"], op.FINALIZAR)
    assert _regra_lida(versao, opcoes["Não"]) == RegraNavegacao(None, True)
    assert _percursos(versao) == {
        ("Termos", "FIM"),
        ("Termos", "Pessoais", "Impactos", "FIM"),
    }


def test_ultima_secao_finaliza_pelo_fluxo_padrao(versao):
    _secoes(versao, "Única")
    assert _percursos(versao) == {("Única", "FIM")}


def test_finalizacao_sem_secao_de_fim_e_publicavel(versao):
    pergunta, opcoes, _ = _termos(versao)
    op.alterar_versao(versao, texto_encerramento="Este formulário chegou ao fim!")
    op.definir_regra(pergunta, opcoes["Não"], op.FINALIZAR)
    assert op.publicar(versao) == op.SituacaoPublicacao.PUBLICADA
    conteudo = conteudo_da_versao(versao)
    assert all(secao.perguntas for secao in conteudo.secoes)
    assert conteudo.texto_encerramento == "Este formulário chegou ao fim!"


def test_finalizar_em_opcao_que_ja_tem_destino(versao):
    pergunta, opcoes, restantes = _termos(versao)
    op.definir_regra(pergunta, opcoes["Não"], restantes["Impactos"])
    with pytest.raises(OperacaoRejeitada) as erro:
        op.definir_regra(pergunta, opcoes["Não"], op.FINALIZAR)
    assert erro.value.motivos == (Motivo.REGRA_JA_DEFINIDA,)
    op.remover_regra(pergunta, opcoes["Não"])
    op.definir_regra(pergunta, opcoes["Não"], op.FINALIZAR)
    assert _regra_lida(versao, opcoes["Não"]) == RegraNavegacao(None, True)


def test_definir_regra_exige_secao_ou_finalizar(versao):
    s = _secoes(versao, "A", "B")
    pergunta, opcoes = _escolha(s["A"], "Sim", "Não")
    with pytest.raises(TypeError):
        op.definir_regra(pergunta, opcoes["Não"], None)  # para limpar, use remover_regra
    assert _regra_lida(versao, opcoes["Não"]) is None

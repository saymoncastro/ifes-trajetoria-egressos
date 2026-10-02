"""Auxiliares de ação do editor (research R6, R7; contracts/diagnostico.md §3)."""

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.editor import acoes
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada, Violacao

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


def test_proxima_posicao(versao):
    assert acoes.proxima_posicao(versao.secoes.all()) == 1
    op.adicionar_secao(versao, 1)
    op.adicionar_secao(versao, 7)
    assert acoes.proxima_posicao(versao.secoes.all()) == 8


def test_mover_nas_pontas_e_no_meio():
    assert acoes.mover(["a", "b", "c"], "a", "cima") is None
    assert acoes.mover(["a", "b", "c"], "c", "baixo") is None
    assert acoes.mover(["a", "b", "c"], "b", "cima") == ["b", "a", "c"]
    assert acoes.mover(["a", "b", "c"], "b", "baixo") == ["a", "c", "b"]
    assert acoes.mover(["a", "b", "c"], "a", "baixo") == ["b", "a", "c"]


def test_mover_e_reordenar_sem_posicao_repetida(versao):
    for p in (1, 4, 9):
        op.adicionar_secao(versao, p, titulo=f"S{p}")
    ordem = list(versao.secoes.order_by("posicao"))
    op.reordenar_secoes(versao, acoes.mover(ordem, ordem[2], "cima"))
    assert ce.ordem(versao.secoes) == ["S1", "S9", "S4"]
    assert ce.posicoes(versao.secoes) == [1, 2, 3]


@pytest.fixture
def navegavel(pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": 3})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    pergunta = ce.pergunta(versao, 1, 1)
    return versao, pergunta, ce.opcao(pergunta, "Não"), ce.opcao(pergunta, "Sim")


def _regra(opcao):
    opcao.refresh_from_db()
    return opcao.regra_destino_id, opcao.regra_finaliza


def test_definir_desvio_tabela(navegavel, monkeypatch):
    versao, pergunta, nao, sim = navegavel
    s2, s3 = ce.secao(versao, 2), ce.secao(versao, 3)
    # Igual ao atual → nenhuma operação.
    chamadas = []
    for nome in ("definir_regra", "remover_regra"):
        original = getattr(op, nome)
        monkeypatch.setattr(
            op, nome, lambda *a, _o=original, _n=nome: chamadas.append(_n) or _o(*a)
        )
    acoes.definir_desvio(pergunta, nao, s3)
    assert chamadas == []
    acoes.definir_desvio(pergunta, sim, None)
    assert chamadas == []
    # Sem regra → define.
    acoes.definir_desvio(pergunta, sim, s2)
    assert _regra(sim) == (s2.id, False)
    # Outra regra → substitui.
    acoes.definir_desvio(pergunta, nao, op.FINALIZAR)
    assert _regra(nao) == (None, True)
    # None → remove.
    acoes.definir_desvio(pergunta, nao, None)
    assert _regra(nao) == (None, False)
    assert chamadas == ["definir_regra", "remover_regra", "definir_regra", "remover_regra"]


def test_troca_de_desvio_e_atomica(navegavel, monkeypatch):
    versao, pergunta, nao, _ = navegavel
    antes = conteudo_da_versao(versao)

    def falha(*args):
        raise OperacaoRejeitada((Violacao(Motivo.REGRA_JA_DEFINIDA, None, "injetada"),))

    monkeypatch.setattr(op, "definir_regra", falha)
    with pytest.raises(OperacaoRejeitada):
        acoes.definir_desvio(pergunta, nao, op.FINALIZAR)
    assert conteudo_da_versao(versao) == antes
    assert _regra(nao) == (ce.secao(versao, 3).id, False)

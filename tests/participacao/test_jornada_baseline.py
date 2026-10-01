"""A jornada na estrutura real da baseline da 003 (US4, US5; FR-022 a FR-027; SC-001, SC-002).

Testes puros: `percorrer` sobre o conteúdo da baseline materializada numa transação desfeita
(fixture `baseline` da 003), com **todas** as Perguntas respondidas em memória — o que também
prova que respostas fora do percurso não interferem. Oráculo: `PERCURSOS` da 003, transcrito
da spec e usado só aqui, nunca em produção.

Testes de ponta a ponta: uma cópia da baseline publicada só no banco de teste.
"""

# As fixtures do manifesto são importadas pelo nome; o parâmetro do teste as "redefine".
# ruff: noqa: F401, F811

import pytest

from tests.instrumento.formulario_2024_esperado import PERCURSOS, baseline
from tests.participacao import construcao as c
from tests.participacao.construcao import (
    FIM,
    NO_PERIODO,
    Q14,
    chaves_baseline,
    combinacoes_baseline,
    escolhas_baseline,
    respondidas_baseline,
    rotulos,
    secoes_esperadas,
)
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.operacoes import iniciar_participacao, responder_escolha_multipla
from trajetoria.participacao.percurso import (
    Saida,
    finalizada,
    pendencias,
    percorrer,
    perguntas_do_percurso,
)


def _secao(conteudo, n):
    return conteudo.secoes[n - 1]


def _percorrer(conteudo, *combinacao, exceto=()):
    escolhas = escolhas_baseline(*combinacao)
    return percorrer(conteudo, respondidas_baseline(conteudo, escolhas, exceto=exceto))


def _esperado(conteudo, combinacao):
    secoes = (_secao(conteudo, n) for n in secoes_esperadas(*combinacao))
    return tuple(s.titulo or f"#{s.posicao}" for s in secoes) + (FIM,)


# --- US4: ramos e 17 percursos (puros) -------------------------------------------------------


def test_17_percursos_do_oraculo_da_003(baseline):
    obtidos = []
    for combinacao in combinacoes_baseline():
        obtido = rotulos(_percorrer(baseline, *combinacao))
        assert obtido == _esperado(baseline, combinacao)
        obtidos.append(obtido)
    assert set(obtidos) == set(PERCURSOS)
    assert len(set(obtidos)) == 17


def test_q1_sim_segue_para_s2_e_nao_finaliza(baseline):
    assert _percorrer(baseline, "Sim", Q14["medio"], "Sim", "Sim")[1].secao == _secao(baseline, 2)
    recusa = _percorrer(baseline, "Não")
    assert [p.secao for p in recusa] == [_secao(baseline, 1)]
    assert recusa[0].destino is Saida.FINALIZACAO
    assert finalizada(recusa)


@pytest.mark.parametrize("texto, ramo", [(t, 4 + i) for i, t in enumerate(Q14.values())])
def test_q14_quatro_destinos_convergem_em_s8(baseline, texto, ramo):
    secoes = [p.secao for p in _percorrer(baseline, "Sim", texto, "Sim", "Sim")]
    assert secoes[3:5] == [_secao(baseline, ramo), _secao(baseline, 8)]
    pulados = {4, 5, 6, 7} - {ramo}
    assert not [s for s in secoes if s.posicao in pulados]


@pytest.mark.parametrize("q33, ramo", [("Sim", 9), ("Não", 10)])
def test_q33_ramos_convergem_em_s11(baseline, q33, ramo):
    secoes = [p.secao for p in _percorrer(baseline, "Sim", Q14["graduacao"], q33, "Sim")]
    assert secoes[5:7] == [_secao(baseline, ramo), _secao(baseline, 11)]


@pytest.mark.parametrize("q46, final", [("Sim", [11, 12, 13]), ("Não", [11, 13])])
def test_q46_destinos(baseline, q46, final):
    passagens = _percorrer(baseline, "Sim", Q14["pos"], "Não", q46)
    assert [p.secao.posicao for p in passagens][-len(final) :] == final
    assert finalizada(passagens)


def test_q51_sem_regra_e_s12_sai_pelo_encaminhamento(baseline):
    # Regressão (003 E-07; FR-026): nenhuma regra em Q51; qualquer Opção leva a S13.
    s12 = _secao(baseline, 12)
    q51 = next(p for p in s12.perguntas if p.id == chaves_baseline(baseline)["Q51"])
    assert all(o.regra is None for o in q51.opcoes)
    for opcao in q51.opcoes:
        escolhas = escolhas_baseline("Sim", Q14["medio"], "Sim", "Sim") | {"Q51": opcao.texto}
        passagens = percorrer(baseline, respondidas_baseline(baseline, escolhas))
        (passagem_s12,) = [p for p in passagens if p.secao == s12]
        assert passagem_s12.destino == s12.encaminhamento_id == _secao(baseline, 13).id


def test_respostas_fora_do_percurso_nao_interferem(baseline):
    # Todas as Perguntas respondidas × só as do percurso: mesmas passagens.
    combinacao = ("Sim", Q14["tecnico"], "Não", "Não")
    completo = _percorrer(baseline, *combinacao)
    so_percurso = {
        pid: oid
        for pid, oid in respondidas_baseline(baseline, escolhas_baseline(*combinacao)).items()
        if pid in perguntas_do_percurso(completo)
    }
    assert percorrer(baseline, so_percurso) == completo


# --- US4: ponta a ponta na cópia publicada ---------------------------------------------------


@pytest.mark.django_db
def test_17_percursos_de_ponta_a_ponta():
    base = c.baseline_publicada()
    campanha = c.campanha_aberta(base.versao)
    for combinacao in combinacoes_baseline():
        participacao = iniciar_participacao(campanha, c.conclusao(), agora=NO_PERIODO).participacao
        c.preencher(
            participacao, base, secoes_esperadas(*combinacao), escolhas_baseline(*combinacao)
        )
        situacao = situacao_da_jornada(participacao, agora=NO_PERIODO)
        assert situacao.finalizada, combinacao
        esperado = tuple(
            base.s(n).titulo or f"#{n}" for n in secoes_esperadas(*combinacao)
        ) + (FIM,)
        assert rotulos(situacao.passagens) == esperado
        assert esperado in PERCURSOS


@pytest.mark.django_db
def test_nivel_da_conclusao_nao_decide_o_ramo():
    # FR-007: o percurso segue Q14 declarada, não o nível institucional da Conclusão.
    base = c.baseline_publicada()
    campanha = c.campanha_aberta(base.versao)
    conclusao = c.conclusao()
    conclusao.nivel = "Graduação"
    conclusao.save(update_fields=["nivel"])
    participacao = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    combinacao = ("Sim", Q14["pos"], "Sim", "Sim")
    c.preencher(participacao, base, [1, 2, 3, 7], escolhas_baseline(*combinacao))
    passagens = situacao_da_jornada(participacao, agora=NO_PERIODO).passagens
    assert [p.secao.posicao for p in passagens][:5] == [1, 2, 3, 7, 8]


# --- US5: Q46, Q47 e Q48 na mesma Seção, desvio só na saída (FR-010, FR-011, FR-025) --------

_ATE_S11 = ("Sim", Q14["graduacao"], "Sim")


def _ids(conteudo, *chaves):
    todas = chaves_baseline(conteudo)
    return tuple(todas[k] for k in chaves)


@pytest.mark.parametrize("q46", ["Sim", "Não"])
def test_q46_q47_q48_pertencem_a_s11(baseline, q46):
    s11 = _secao(baseline, 11)
    q46_, q47, q48 = _ids(baseline, "Q46", "Q47", "Q48")
    assert [p.id for p in s11.perguntas] == [q46_, q47, q48]
    assert [p.posicao for p in s11.perguntas] == [1, 2, 3]
    assert {q46_, q47, q48} <= perguntas_do_percurso(_percorrer(baseline, *_ATE_S11, q46))


def test_q47_obrigatoria_e_q48_opcional_na_versao(baseline):
    por_id = {p.id: p for p in _secao(baseline, 11).perguntas}
    q47, q48 = _ids(baseline, "Q47", "Q48")
    assert por_id[q47].obrigatoria
    assert not por_id[q48].obrigatoria


@pytest.mark.parametrize("q46, destino", [("Sim", 12), ("Não", 13)])
def test_responder_q46_nao_encerra_s11_sem_q47(baseline, q46, destino):
    (q47,) = _ids(baseline, "Q47")
    passagens = _percorrer(baseline, *_ATE_S11, q46, exceto=("Q47", "Q48"))
    ultima = passagens[-1]
    assert ultima.secao == _secao(baseline, 11)  # o percurso para em S11
    assert ultima.pendentes == (q47,)
    assert ultima.destino == _secao(baseline, destino).id  # já decidido, ainda não aplicado
    assert not [p for p in passagens if p.secao.posicao in (12, 13)]
    assert [v.motivo.name for v in pendencias(passagens)] == ["OBRIGATORIA_PENDENTE"]


def test_q48_vazia_nao_impede_a_saida_de_s11(baseline):
    passagens = _percorrer(baseline, *_ATE_S11, "Não", exceto=("Q48",))
    posicoes = [p.secao.posicao for p in passagens]
    assert posicoes[posicoes.index(11) + 1] == 13
    assert finalizada(passagens)
    (q48,) = _ids(baseline, "Q48")
    assert not [v for v in pendencias(passagens) if str(q48) in v.detalhe]


def test_so_depois_de_s11_satisfeita_q46_decide_a_seguinte(baseline):
    sem_q47 = _percorrer(baseline, *_ATE_S11, "Sim", exceto=("Q47",))
    com_q47 = _percorrer(baseline, *_ATE_S11, "Sim")
    assert sem_q47[-1].secao.posicao == 11
    posicoes = [p.secao.posicao for p in com_q47]
    assert posicoes[posicoes.index(11) + 1] == 12


@pytest.mark.django_db
def test_q46_sim_com_nao_estudei_mais_nao_e_contradicao():
    base = c.baseline_publicada()
    campanha = c.campanha_aberta(base.versao)
    participacao = iniciar_participacao(campanha, c.conclusao(), agora=NO_PERIODO).participacao
    combinacao = (*_ATE_S11, "Sim")
    c.preencher(participacao, base, secoes_esperadas(*combinacao), escolhas_baseline(*combinacao))
    responder_escolha_multipla(
        participacao, base.q(47), [base.opcao(47, "Não estudei mais")], agora=NO_PERIODO
    )
    situacao = situacao_da_jornada(participacao, agora=NO_PERIODO)
    assert situacao.finalizada
    assert situacao.impedimentos == ()

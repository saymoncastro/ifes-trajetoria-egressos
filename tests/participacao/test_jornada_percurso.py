"""Derivação pura do percurso (contracts/percurso.md; FR-010 a FR-021).

Sem `django_db`: o pytest-django bloqueia qualquer acesso ao banco nestes testes, o que
prova que `percurso.py` não faz I/O. As Versões são construídas em memória.
"""

import ast
from pathlib import Path
from uuid import uuid4

import pytest

from tests.participacao.construcao import (
    FIM,
    pergunta_id,
    pergunta_mem,
    respondidas,
    secao_mem,
    versao_mem,
)
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.participacao import percurso
from trajetoria.participacao.percurso import (
    Saida,
    finalizada,
    pendencias,
    percorrer,
    perguntas_do_percurso,
)
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

TEXTO = TipoPergunta.TEXTO_CURTO


def _linear():
    """Três Seções, sem regras nem encaminhamento; duas obrigatórias por Seção."""
    return versao_mem(
        *(secao_mem(pergunta_mem(tipo=TEXTO), pergunta_mem(tipo=TEXTO)) for _ in range(3))
    )


def _todas(conteudo, ate=None):
    return {
        (s, p): None
        for s, secao in enumerate(conteudo.secoes[:ate], 1)
        for p in range(1, len(secao.perguntas) + 1)
    }


# --- Pureza ----------------------------------------------------------------------------------


def test_percurso_nao_importa_orm_nem_consultas():
    fonte = Path(percurso.__file__).read_text(encoding="utf-8")
    modulos = set()
    nomes = set()
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.Import):
            modulos |= {a.name for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            modulos.add(no.module)
            nomes |= {a.name for a in no.names}
    assert not [m for m in modulos if m.startswith("django.db") or m.endswith(".models")]
    assert not {"trajetoria.participacao.consultas", "trajetoria.participacao.operacoes"} & modulos
    assert not {"conteudo_da_versao", "respostas_atuais", "transaction", "connection"} & nomes


# --- Percurso linear e parcial ---------------------------------------------------------------


def test_linear_completo_finaliza():
    conteudo = _linear()
    passagens = percorrer(conteudo, respondidas(conteudo, _todas(conteudo)))
    secoes = conteudo.secoes
    assert [p.secao for p in passagens] == list(secoes)
    assert [p.destino for p in passagens] == [secoes[1].id, secoes[2].id, Saida.FINALIZACAO]
    assert all(p.satisfeita for p in passagens)
    assert finalizada(passagens)


def test_sem_respostas_para_na_primeira_secao():
    conteudo = _linear()
    passagens = percorrer(conteudo, {})
    assert [p.secao for p in passagens] == [conteudo.secoes[0]]
    assert passagens[0].pendentes == (pergunta_id(conteudo, 1, 1), pergunta_id(conteudo, 1, 2))
    assert not finalizada(passagens)


def test_parcial_para_na_secao_atual_sem_secoes_futuras():
    conteudo = _linear()
    escolhas = _todas(conteudo, ate=1) | {(2, 1): None}
    passagens = percorrer(conteudo, respondidas(conteudo, escolhas))
    assert [p.secao for p in passagens] == list(conteudo.secoes[:2])
    assert passagens[-1].pendentes == (pergunta_id(conteudo, 2, 2),)
    assert not finalizada(passagens)


def test_respostas_alem_da_secao_atual_nao_mudam_o_resultado():
    conteudo = _linear()
    parcial = _todas(conteudo, ate=1) | {(2, 1): None}
    com_futuras = parcial | {(3, 1): None, (3, 2): None}
    assert percorrer(conteudo, respondidas(conteudo, parcial)) == percorrer(
        conteudo, respondidas(conteudo, com_futuras)
    )


def test_determinismo():
    conteudo = _linear()
    escolhas = _todas(conteudo)
    invertidas = dict(reversed(list(escolhas.items())))
    primeira = percorrer(conteudo, respondidas(conteudo, escolhas))
    assert primeira == percorrer(conteudo, respondidas(conteudo, invertidas))
    assert primeira == percorrer(conteudo, respondidas(conteudo, escolhas))


def test_perguntas_do_percurso_sao_as_das_secoes_das_passagens():
    conteudo = _linear()
    escolhas = _todas(conteudo, ate=1)
    passagens = percorrer(conteudo, respondidas(conteudo, escolhas))
    assert perguntas_do_percurso(passagens) == frozenset(
        p.id for s in conteudo.secoes[:2] for p in s.perguntas
    )


# --- Precedência de destino (US2; FR-012) ----------------------------------------------------
# (1) regra acionada; (2) Pergunta com regra obrigatória sem resposta → INDETERMINADA;
# (3) encaminhamento; (4) Seção seguinte; (5) finalização. Nada além disso.


def _com_regra(*, obrigatoria=True, regras=None, encaminhamento=None, secoes=4):
    """S1: Pergunta com regra (Sim/Não); S2..Sn: uma obrigatória de texto cada."""
    s1 = secao_mem(
        pergunta_mem(obrigatoria=obrigatoria, regras=regras), encaminhamento=encaminhamento
    )
    return versao_mem(s1, *(secao_mem(pergunta_mem(tipo=TEXTO)) for _ in range(secoes - 1)))


def _ids(conteudo, *indices):
    return [conteudo.secoes[i - 1].id for i in indices]


def test_1_regra_acionada_prevalece_sobre_encaminhamento_e_ordem():
    conteudo = _com_regra(regras={"Sim": 4}, encaminhamento=2)
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): "Sim"}))
    assert passagens[0].destino == conteudo.secoes[3].id
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1, 4)


def test_1_regra_de_finalizacao():
    conteudo = _com_regra(regras={"Não": FIM})
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): "Não"}))
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1)
    assert passagens[0].destino is Saida.FINALIZACAO
    assert finalizada(passagens)


def test_2_pergunta_com_regra_obrigatoria_sem_resposta_e_indeterminada():
    conteudo = _com_regra(regras={"Sim": 3}, encaminhamento=2)
    passagens = percorrer(conteudo, {})
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1)
    assert passagens[0].destino is Saida.INDETERMINADA
    assert not finalizada(passagens)


def test_3_opcao_sem_regra_segue_o_encaminhamento():
    conteudo = _com_regra(regras={"Sim": 4}, encaminhamento=3)
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): "Não"}))
    assert passagens[0].destino == conteudo.secoes[2].id


def test_3_pergunta_com_regra_opcional_sem_resposta_segue_o_padrao():
    com_encaminhamento = _com_regra(obrigatoria=False, regras={"Sim": 4}, encaminhamento=3)
    assert percorrer(com_encaminhamento, {})[0].destino == com_encaminhamento.secoes[2].id
    sem_encaminhamento = _com_regra(obrigatoria=False, regras={"Sim": 4})
    assert percorrer(sem_encaminhamento, {})[0].destino == sem_encaminhamento.secoes[1].id


def test_3_encaminhamento_prevalece_sobre_a_ordem():
    conteudo = versao_mem(
        secao_mem(pergunta_mem(tipo=TEXTO), encaminhamento=3),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): None, (3, 1): None}))
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1, 3)
    assert finalizada(passagens)


def test_convergencia_de_ramos_por_encaminhamento():
    conteudo = versao_mem(
        secao_mem(pergunta_mem(regras={"Sim": 2, "Não": 3})),
        secao_mem(pergunta_mem(tipo=TEXTO), encaminhamento=4),
        secao_mem(pergunta_mem(tipo=TEXTO), encaminhamento=4),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    for escolha, ramo in (("Sim", 2), ("Não", 3)):
        escolhas = {(1, 1): escolha, (2, 1): None, (3, 1): None, (4, 1): None}
        passagens = percorrer(conteudo, respondidas(conteudo, escolhas))
        assert [p.secao.id for p in passagens] == _ids(conteudo, 1, ramo, 4)
        assert finalizada(passagens)


def test_5_ultima_secao_satisfeita_finaliza():
    conteudo = _linear()
    passagens = percorrer(conteudo, respondidas(conteudo, _todas(conteudo)))
    assert passagens[-1].destino is Saida.FINALIZACAO


def test_destino_conhecido_mas_secao_nao_satisfeita():
    # A regra decide o destino; outra obrigatória pendente impede deixar a Seção (FR-011).
    conteudo = versao_mem(
        secao_mem(pergunta_mem(regras={"Sim": 3}), pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): "Sim"}))
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1)
    assert passagens[0].destino == conteudo.secoes[2].id
    assert passagens[0].pendentes == (pergunta_id(conteudo, 1, 2),)


def test_opcao_que_nao_e_da_pergunta_com_regra_e_rejeitada():
    conteudo = _com_regra(regras={"Sim": 3})
    with pytest.raises(ParticipacaoRejeitada) as erro:
        percorrer(conteudo, {pergunta_id(conteudo, 1, 1): uuid4()})
    assert erro.value.motivos == (Motivo.OPCAO_DE_OUTRA_PERGUNTA,)
    assert erro.value.violacoes[0].campo == "pergunta"


def test_regra_de_outra_secao_nao_influencia():
    # S1 com regra Sim→S3; S2 com regra que nunca é lida enquanto S2 não é alcançada.
    conteudo = versao_mem(
        secao_mem(pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(regras={"Sim": FIM})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    escolhas = {(1, 1): "Sim", (2, 1): "Sim", (3, 1): None}
    passagens = percorrer(conteudo, respondidas(conteudo, escolhas))
    assert [p.secao.id for p in passagens] == _ids(conteudo, 1, 3)
    assert finalizada(passagens)


# --- Obrigatoriedade (US3; FR-019 a FR-021) --------------------------------------------------

MULTIPLA = TipoPergunta.ESCOLHA_MULTIPLA


def test_pendencias_sao_as_obrigatorias_vazias_da_secao_atual_na_ordem():
    conteudo = versao_mem(
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(
            pergunta_mem(tipo=TEXTO),
            pergunta_mem(tipo=TEXTO, obrigatoria=False),
            pergunta_mem(tipo=TEXTO),
        ),
    )
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): None}))
    violacoes = pendencias(passagens)
    assert [v.motivo for v in violacoes] == [Motivo.OBRIGATORIA_PENDENTE] * 2
    assert all(v.campo == "pergunta" for v in violacoes)
    for violacao, p in zip(violacoes, (1, 3), strict=True):
        assert str(pergunta_id(conteudo, 2, p)) in violacao.detalhe
        assert str(conteudo.secoes[1].id) in violacao.detalhe


def test_opcional_nunca_e_pendente():
    conteudo = versao_mem(secao_mem(pergunta_mem(tipo=TEXTO, obrigatoria=False)))
    passagens = percorrer(conteudo, {})
    assert finalizada(passagens)
    assert pendencias(passagens) == ()


def test_obrigatoria_de_secao_pulada_nunca_e_pendente():
    conteudo = versao_mem(
        secao_mem(pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(tipo=TEXTO), pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): "Sim"}))
    pulada = {p.id for p in conteudo.secoes[1].perguntas}
    assert not [v for v in pendencias(passagens) if any(str(i) in v.detalhe for i in pulada)]
    assert [str(pergunta_id(conteudo, 3, 1)) in v.detalhe for v in pendencias(passagens)] == [
        True
    ]


def test_nunca_ha_pendencia_de_secao_anterior():
    conteudo = _linear()
    escolhas = _todas(conteudo, ate=2)
    passagens = percorrer(conteudo, respondidas(conteudo, escolhas))
    anteriores = {p.id for s in conteudo.secoes[:2] for p in s.perguntas}
    assert not [v for v in pendencias(passagens) if any(str(i) in v.detalhe for i in anteriores)]


def test_finalizada_nao_tem_pendencias():
    conteudo = _linear()
    assert pendencias(percorrer(conteudo, respondidas(conteudo, _todas(conteudo)))) == ()


def test_multipla_obrigatoria_respondida_satisfaz():
    conteudo = versao_mem(secao_mem(pergunta_mem(tipo=MULTIPLA, opcoes=("A", "B"))))
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): None}))
    assert passagens[0].satisfeita and finalizada(passagens)


def test_secao_so_com_opcionais_fica_satisfeita_ao_ser_alcancada():
    # Hipótese registrada na spec (Edge Cases): sem cursor, ela nunca é a Seção atual.
    conteudo = versao_mem(
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO, obrigatoria=False)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    passagens = percorrer(conteudo, respondidas(conteudo, {(1, 1): None}))
    assert [p.secao.posicao for p in passagens] == [1, 2, 3]
    assert passagens[1].satisfeita
    assert passagens[-1].secao.posicao == 3


# --- Estrutura não suportada (US12; FR-016) --------------------------------------------------


def _duas_regras_na_mesma_secao():
    return versao_mem(
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(regras={"Sim": 3}), pergunta_mem(regras={"Sim": 4})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )


def test_duas_perguntas_com_regra_na_mesma_secao_sao_rejeitadas():
    conteudo = _duas_regras_na_mesma_secao()
    for escolhas in ({}, {(1, 1): None}, {(1, 1): None, (2, 1): "Sim", (2, 2): "Sim"}):
        # Mesmo sem alcançar a Seção, e com respostas que levariam a destinos diferentes.
        with pytest.raises(ParticipacaoRejeitada) as erro:
            percorrer(conteudo, respondidas(conteudo, escolhas))
        (violacao,) = erro.value.violacoes
        assert violacao.motivo is Motivo.ESTRUTURA_NAO_SUPORTADA
        assert violacao.campo == "secao"
        assert str(conteudo.secoes[1].id) in violacao.detalhe


def test_uma_violacao_por_secao_nao_suportada():
    conteudo = versao_mem(
        secao_mem(pergunta_mem(regras={"Sim": 2}), pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(regras={"Sim": 3}), pergunta_mem(regras={"Não": FIM})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    with pytest.raises(ParticipacaoRejeitada) as erro:
        percorrer(conteudo, {})
    assert erro.value.motivos == (Motivo.ESTRUTURA_NAO_SUPORTADA,) * 2


def test_pergunta_com_regra_sem_opcao_registrada_e_valor_vazio():
    # Regressão (code review): Resposta de escolha única sem Opção (só por escrita fora das
    # operações) é VALOR_VAZIO, como na 005, e não "Opção de outra Pergunta".
    conteudo = _com_regra(regras={"Sim": 3})
    with pytest.raises(ParticipacaoRejeitada) as erro:
        percorrer(conteudo, {pergunta_id(conteudo, 1, 1): None})
    assert erro.value.motivos == (Motivo.VALOR_VAZIO,)
    assert str(pergunta_id(conteudo, 1, 1)) in erro.value.violacoes[0].detalhe

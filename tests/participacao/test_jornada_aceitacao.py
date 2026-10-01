"""Aceitação da Feature 006: as 11 perguntas de sucesso do solicitante (spec, "Cobertura") e o
escopo estrutural (SC-010, SC-012; FR-050, FR-052 a FR-054).

Os campos de `Campanha`, `ConclusaoAcademica`, `Pergunta` e `Opcao` continuam protegidos, sem
alteração, por `test_participacao_aceitacao.py::test_modelos_anteriores_sem_colunas_novas`.
"""

import inspect
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings

from tests.participacao import construcao as c
from tests.participacao.construcao import (
    DEPOIS_DO_FIM,
    NO_PERIODO,
    Q14,
    pergunta_de,
    pergunta_mem,
    secao_mem,
)
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import EstadoVersao, Opcao, Secao, TipoPergunta, Versao
from trajetoria.participacao import consultas, operacoes, percurso
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import (
    SituacaoConclusao,
    concluir,
    iniciar_participacao,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


@pytest.fixture
def base():
    return c.baseline_publicada()


@pytest.fixture
def pb(base, conclusao):
    campanha = c.campanha_aberta(base.versao)
    return iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao


def _completar(pb, base, *combinacao):
    secoes = c.secoes_esperadas(*combinacao)
    c.preencher(pb, base, secoes, c.escolhas_baseline(*combinacao))


_PADRAO = ("Sim", Q14["graduacao"], "Sim", "Não")


# --- As 11 perguntas de sucesso --------------------------------------------------------------


def test_1_o_sistema_sabe_o_percurso_atual(pb, base):
    c.preencher(pb, base, [1, 2], c.escolhas_baseline("Sim"))
    situacao = situacao_da_jornada(pb, agora=NO_PERIODO)
    assert [p.secao.posicao for p in situacao.passagens] == [1, 2, 3]
    assert situacao.secao_atual.posicao == 3


def test_2_apenas_perguntas_do_percurso_sao_exigidas(pb, base):
    _completar(pb, base, *_PADRAO)  # S9 escolhida; S10 (Q45 obrigatória) vazia
    assert situacao_da_jornada(pb, agora=NO_PERIODO).pode_concluir


def test_3_q46_q47_q48_reproduzem_a_semantica_atual(pb, base):
    _completar(pb, base, *_PADRAO)
    Resposta.objects.filter(participacao=pb, pergunta=base.q(47)).delete()
    situacao = situacao_da_jornada(pb, agora=NO_PERIODO)
    assert situacao.secao_atual == situacao.passagens[-1].secao
    assert situacao.secao_atual.posicao == 11
    assert situacao.passagens[-1].pendentes == (base.q(47).id,)


def test_4_q1_nao_encerra_a_jornada(pb, base):
    responder_escolha_unica(pb, base.q(1), base.opcao(1, "Não"), agora=NO_PERIODO)
    situacao = situacao_da_jornada(pb, agora=NO_PERIODO)
    assert situacao.finalizada and [p.secao.posicao for p in situacao.passagens] == [1]


def test_5_participacao_completa_pode_ser_concluida(pb, base):
    _completar(pb, base, *_PADRAO)
    assert concluir(pb, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA


def test_6_concluida_em_e_preservado(pb, base):
    _completar(pb, base, *_PADRAO)
    concluir(pb, agora=NO_PERIODO)
    concluir(pb, agora=c.momento(2027, 6, 1))
    assert Participacao.objects.get(pk=pb.pk).concluida_em == NO_PERIODO


def test_7_concluida_e_imutavel(pb, base):
    _completar(pb, base, *_PADRAO)
    concluir(pb, agora=NO_PERIODO)
    c.rejeita(
        [Motivo.PARTICIPACAO_CONCLUIDA],
        responder_texto,
        pb,
        base.q(3),
        "outra resposta fictícia",
        agora=NO_PERIODO,
    )


def test_8_trocar_de_ramo_remove_as_respostas_do_ramo_abandonado(pb, base):
    _completar(pb, base, *_PADRAO)
    responder_escolha_unica(pb, base.q(33), base.opcao(33, "Não"), agora=NO_PERIODO)
    c.preencher(pb, base, [10], {})
    concluir(pb, agora=NO_PERIODO)
    s9 = set(base.s(9).perguntas.values_list("id", flat=True))
    assert not Resposta.objects.filter(participacao=pb, pergunta_id__in=s9).exists()


def test_9_campanha_encerrada_impede_conclusao_tardia(pb, base):
    _completar(pb, base, *_PADRAO)
    c.rejeita([Motivo.COLETA_NAO_ADMITIDA], concluir, pb, agora=DEPOIS_DO_FIM)


def test_10_nenhum_conceito_de_sessao_workflow_ou_progresso():
    assert {m.__name__ for m in apps.get_app_config("participacao").get_models()} == {
        "Participacao",
        "Resposta",
        "RespostaOpcao",
    }
    campos = [f.name for f in Participacao._meta.concrete_fields]
    assert campos == ["id", "campanha", "conclusao", "iniciada_em", "concluida_em"]
    assert [f.name for f in Resposta._meta.concrete_fields] == [
        "id",
        "participacao",
        "pergunta",
        "opcao",
        "texto",
        "escala",
        "complemento",
    ]
    proibidos = (
        "journey", "jornadaestado", "estadojornada", "session", "sessao", "attempt",
        "tentativa", "step", "transition", "transicao", "submission", "submissao",
        "progress", "progresso", "workflow", "ruleengine", "cursor", "ativa",
    )  # fmt: skip
    nomes = {n.lower() for m in (percurso, consultas, operacoes) for n in vars(m)}
    assert not [n for n in nomes if any(n == p or n.startswith(p) for p in proibidos)]


def test_11_autenticacao_continua_fora_do_escopo():
    for funcao in (concluir, situacao_da_jornada):
        assert list(inspect.signature(funcao).parameters) == ["participacao", "agora"]
    app = Path(apps.get_app_config("participacao").path)
    assert not [n for n in ("admin.py", "urls.py", "views.py", "management") if (app / n).exists()]
    novos = [a for a in settings.INSTALLED_APPS if a.startswith("trajetoria.")]
    assert "trajetoria.jornada" not in novos


# --- Escopo estrutural -----------------------------------------------------------------------


def test_versao_posterior_nao_muda_o_percurso_da_campanha_anterior(conclusao):
    # SC-010: "2028" criada de "2027" com navegação diferente e publicada depois.
    versao_2027 = c.versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
        secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
    )
    campanha = c.campanha_aberta(versao_2027)
    p = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    q = pergunta_de(versao_2027, 1, 1)
    responder_escolha_unica(p, q, Opcao.objects.get(pergunta=q, texto="Sim"), agora=NO_PERIODO)
    antes = situacao_da_jornada(p, agora=NO_PERIODO).passagens

    versao_2028 = op.criar_versao_a_partir_de(versao_2027, "2028")
    q_2028 = pergunta_de(versao_2028, 1, 1)
    sim_2028 = Opcao.objects.get(pergunta=q_2028, texto="Sim")
    op.remover_regra(q_2028, sim_2028)
    op.definir_regra(q_2028, sim_2028, Secao.objects.get(versao=versao_2028, posicao=2))
    op.publicar(versao_2028)

    assert situacao_da_jornada(p, agora=NO_PERIODO).passagens == antes


def test_origem_dos_dados_na_consulta(pb, base):
    # FR-050: só Respostas (declaradas) na consulta; contexto acadêmico pela Conclusão.
    c.preencher(pb, base, [1, 2, 3], c.escolhas_baseline("Sim", Q14["pos"]))
    situacao = situacao_da_jornada(pb, agora=NO_PERIODO)
    assert all(isinstance(r, Resposta) for r in situacao.respostas.values())
    assert situacao.participacao.conclusao_id == pb.conclusao_id
    campos = set(situacao.__dataclass_fields__)
    assert not campos & {"curso", "unidade", "nivel", "modalidade", "ano_conclusao"}


def test_baseline_da_003_continua_rascunho(base):
    original = base.versao.origem
    assert Versao.objects.get(pk=original.pk).estado == EstadoVersao.RASCUNHO

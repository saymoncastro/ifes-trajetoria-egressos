"""Conclusão da Participação (contracts/conclusao.md; FR-032 a FR-046)."""

from dataclasses import dataclass

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import (
    DEPOIS_DO_FIM,
    NO_PERIODO,
    Q14,
    ULTIMO_DIA,
    opcao_de,
    pergunta_de,
    pergunta_mem,
    secao_mem,
)
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.models import Campanha
from trajetoria.instrumento.models import Opcao, Pergunta, Secao, TipoPergunta, Versao
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import (
    ResultadoConclusao,
    SituacaoConclusao,
    concluir,
    iniciar_participacao,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

pytestmark = pytest.mark.django_db

TEXTO = TipoPergunta.TEXTO_CURTO
MULTIPLA = TipoPergunta.ESCOLHA_MULTIPLA
ESCALA = TipoPergunta.ESCALA


@dataclass
class Ramificada:
    """S1: "Sim" → S2, "Não" → S3. S2 (texto obrigatório, múltipla obrigatória com "Outro:",
    escala opcional) → S4 por encaminhamento. S3 (texto obrigatório) → S4. S4: texto
    opcional, última."""

    versao: Versao

    def p(self, s, n=1) -> Pergunta:
        return pergunta_de(self.versao, s, n)


@pytest.fixture
def ramificada():
    return Ramificada(
        c.versao_publicada_de(
            secao_mem(pergunta_mem(regras={"Sim": 2, "Não": 3})),
            secao_mem(
                pergunta_mem(tipo=TEXTO),
                pergunta_mem(tipo=MULTIPLA, opcoes=("A", "B"), outro=True),
                pergunta_mem(tipo=ESCALA, obrigatoria=False),
                encaminhamento=4,
            ),
            secao_mem(pergunta_mem(tipo=TEXTO)),
            secao_mem(pergunta_mem(tipo=TEXTO, obrigatoria=False)),
        )
    )


@pytest.fixture
def campanha_r(ramificada):
    return c.campanha_aberta(ramificada.versao)


@pytest.fixture
def p(campanha_r, conclusao):
    return iniciar_participacao(campanha_r, conclusao, agora=NO_PERIODO).participacao


def _s1(p, r, texto):
    responder_escolha_unica(p, r.p(1), opcao_de(r.p(1), texto), agora=NO_PERIODO)


def _s2(p, r, *, texto=True):
    if texto:
        responder_texto(p, r.p(2, 1), "resposta fictícia", agora=NO_PERIODO)
    responder_escolha_multipla(p, r.p(2, 2), [opcao_de(r.p(2, 2), "A")], agora=NO_PERIODO)


def _s3(p, r):
    responder_texto(p, r.p(3), "resposta fictícia", agora=NO_PERIODO)


def _perguntas_respondidas(p):
    return set(Resposta.objects.filter(participacao=p).values_list("pergunta_id", flat=True))


def _linhas_das_respostas(p, perguntas):
    return list(
        Resposta.objects.filter(participacao=p, pergunta__in=perguntas).order_by("id").values()
    )


def _instrumento_e_contexto():
    return [
        list(m.objects.order_by("pk").values())
        for m in (Campanha, ConclusaoAcademica, Versao, Secao, Pergunta, Opcao)
    ]


# --- US6: conclusão válida -------------------------------------------------------------------


def test_conclusao_valida(p, ramificada):
    _s1(p, ramificada, "Sim")
    _s2(p, ramificada)
    no_percurso = [ramificada.p(1), ramificada.p(2, 1), ramificada.p(2, 2)]
    respostas_antes = _linhas_das_respostas(p, no_percurso)
    contexto_antes = _instrumento_e_contexto()

    resultado = concluir(p, agora=NO_PERIODO)

    assert isinstance(resultado, ResultadoConclusao)
    assert resultado.situacao is SituacaoConclusao.CONCLUIDA
    gravada = Participacao.objects.get(pk=p.pk)
    assert resultado.participacao.concluida_em == gravada.concluida_em == NO_PERIODO
    assert (gravada.iniciada_em, gravada.campanha_id, gravada.conclusao_id) == (
        p.iniciada_em,
        p.campanha_id,
        p.conclusao_id,
    )
    assert _linhas_das_respostas(p, no_percurso) == respostas_antes
    assert _instrumento_e_contexto() == contexto_antes


def test_conclusao_remove_respostas_fora_do_percurso(p, ramificada):
    _s1(p, ramificada, "Não")
    _s3(p, ramificada)
    _s1(p, ramificada, "Sim")
    _s2(p, ramificada)
    concluir(p, agora=NO_PERIODO)
    assert _perguntas_respondidas(p) == {
        ramificada.p(1).id,
        ramificada.p(2, 1).id,
        ramificada.p(2, 2).id,
    }


def test_pendencia_rejeita_sem_alterar_nada(p, ramificada):
    _s1(p, ramificada, "Não")
    _s3(p, ramificada)  # ficará fora do percurso
    _s1(p, ramificada, "Sim")
    _s2(p, ramificada, texto=False)
    antes = c.retrato(p)
    violacoes = c.rejeita([Motivo.OBRIGATORIA_PENDENTE], concluir, p, agora=NO_PERIODO)
    assert str(ramificada.p(2, 1).id) in violacoes[0].detalhe
    assert c.retrato(p) == antes
    assert Participacao.objects.get(pk=p.pk).concluida_em is None
    assert ramificada.p(3).id in _perguntas_respondidas(p)


def test_todas_as_violacoes_reunidas(p, ramificada, campanha_r):
    _s1(p, ramificada, "Sim")
    op_campanha.encerrar(campanha_r, agora=NO_PERIODO)
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA, Motivo.OBRIGATORIA_PENDENTE, Motivo.OBRIGATORIA_PENDENTE],
        concluir,
        p,
        agora=NO_PERIODO,
    )


def test_obrigatoria_fora_do_percurso_nao_bloqueia(p, ramificada):
    _s1(p, ramificada, "Sim")
    _s2(p, ramificada)  # S3 (obrigatória) vazia, fora do percurso
    assert concluir(p, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA


def test_outro_sem_complemento_e_escala_opcional_vazia_concluem(p, ramificada):
    _s1(p, ramificada, "Sim")
    responder_texto(p, ramificada.p(2, 1), "resposta fictícia", agora=NO_PERIODO)
    outro = opcao_de(ramificada.p(2, 2), "Outro:")
    responder_escolha_multipla(p, ramificada.p(2, 2), [outro], agora=NO_PERIODO)
    assert concluir(p, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA
    assert ramificada.p(2, 3).id not in _perguntas_respondidas(p)


def test_argumentos_estruturais(campanha_r, conclusao):
    with pytest.raises(TypeError):
        concluir("participação")
    nao_gravada = Participacao(campanha=campanha_r, conclusao=conclusao, iniciada_em=NO_PERIODO)
    c.rejeita([Motivo.PARTICIPACAO_INEXISTENTE], concluir, nao_gravada, agora=NO_PERIODO)


def test_escala_respondida_no_percurso_e_preservada(p, ramificada):
    _s1(p, ramificada, "Sim")
    _s2(p, ramificada)
    responder_escala(p, ramificada.p(2, 3), 4, agora=NO_PERIODO)
    concluir(p, agora=NO_PERIODO)
    assert Resposta.objects.get(participacao=p, pergunta=ramificada.p(2, 3)).escala == 4


# --- Baseline: ramos abandonados, Q1 = "Não", encerramento (US9, US10, US11) ----------------


@pytest.fixture
def base():
    return c.baseline_publicada()


@pytest.fixture
def campanha_b(base):
    return c.campanha_aberta(base.versao)


@pytest.fixture
def pb(campanha_b, conclusao):
    return iniciar_participacao(campanha_b, conclusao, agora=NO_PERIODO).participacao


def _preencher_percurso(pb, base, *combinacao, exceto=()):
    escolhas = c.escolhas_baseline(*combinacao)
    c.preencher(pb, base, c.secoes_esperadas(*combinacao), escolhas, exceto=exceto)


def _selecoes(resposta_ids):
    return RespostaOpcao.objects.filter(resposta_id__in=resposta_ids).count()


def test_troca_de_q33_remove_s9_na_conclusao(pb, base):
    _preencher_percurso(pb, base, "Sim", Q14["graduacao"], "Sim", "Sim")
    s9 = {p.id for p in base.s(9).perguntas.all()}
    assert s9 & _perguntas_respondidas(pb)
    responder_escolha_unica(pb, base.q(33), base.opcao(33, "Não"), agora=NO_PERIODO)
    c.preencher(pb, base, [10], {})
    finais = _perguntas_respondidas(pb) - s9
    linhas_finais = _linhas_das_respostas(pb, finais)

    concluir(pb, agora=NO_PERIODO)

    assert not s9 & _perguntas_respondidas(pb)
    assert _perguntas_respondidas(pb) == finais
    assert _linhas_das_respostas(pb, finais) == linhas_finais


def test_troca_de_q14_remove_q18_e_preserva_q19(pb, base):
    _preencher_percurso(pb, base, "Sim", Q14["graduacao"], "Sim", "Sim")
    responder_escolha_unica(pb, base.q(14), base.opcao(14, Q14["pos"]), agora=NO_PERIODO)
    c.preencher(pb, base, [7], {})
    concluir(pb, agora=NO_PERIODO)
    assert base.q(19).id in _perguntas_respondidas(pb)
    assert base.q(18).id not in _perguntas_respondidas(pb)


def test_rejeicao_por_pendencia_nao_remove_inativas(pb, base):
    _preencher_percurso(pb, base, "Sim", Q14["graduacao"], "Sim", "Sim")
    responder_escolha_unica(pb, base.q(33), base.opcao(33, "Não"), agora=NO_PERIODO)
    antes = c.retrato(pb)
    c.rejeita([Motivo.OBRIGATORIA_PENDENTE], concluir, pb, agora=NO_PERIODO)  # Q45 vazia
    assert c.retrato(pb) == antes


def test_q1_nao_cenario_completo(pb, base, campanha_b):
    # 1. respostas posteriores existem no rascunho (inclusive múltipla com seleções)
    _preencher_percurso(pb, base, "Sim", Q14["medio"], "Sim", "Sim")
    q26 = Resposta.objects.get(participacao=pb, pergunta=base.q(26))
    assert _selecoes([q26.id]) == 1
    # 2. Q1 passa para "Não"
    responder_escolha_unica(pb, base.q(1), base.opcao(1, "Não"), agora=NO_PERIODO)
    # 3. a jornada termina em S1; todas as outras ficam inativas
    situacao = situacao_da_jornada(pb, agora=NO_PERIODO)
    assert [p.secao.posicao for p in situacao.passagens] == [1]
    assert situacao.finalizada
    assert situacao.fora_do_percurso == _perguntas_respondidas(pb) - {base.q(1).id}
    # 4. nenhuma pendência
    assert situacao.impedimentos == ()
    # 5. conclusão válida com o percurso reduzido
    assert concluir(pb, agora=NO_PERIODO).situacao is SituacaoConclusao.CONCLUIDA
    # 6. inativas e seleções removidas na mesma operação
    assert _selecoes([q26.id]) == 0
    # 7. resta só Q1 = "Não"
    (q1,) = Resposta.objects.filter(participacao=pb)
    assert (q1.pergunta_id, q1.opcao_id) == (base.q(1).id, base.opcao(1, "Não").id)


def test_q1_nao_nao_e_consentimento_nem_bloqueio(pb, base, conclusao):
    from django.apps import apps

    responder_escolha_unica(pb, base.q(1), base.opcao(1, "Não"), agora=NO_PERIODO)
    concluir(pb, agora=NO_PERIODO)
    assert Resposta.objects.filter(participacao=pb).count() == 1
    assert {m.__name__ for m in apps.get_app_config("participacao").get_models()} == {
        "Participacao",
        "Resposta",
        "RespostaOpcao",
    }
    outra = c.campanha_aberta(base.versao)
    assert iniciar_participacao(outra, conclusao, agora=NO_PERIODO).situacao.value == "criada"


def test_campanha_encerrada_explicitamente_bloqueia_conclusao(pb, base, campanha_b):
    _preencher_percurso(pb, base, "Sim", Q14["tecnico"], "Não", "Não")
    op_campanha.encerrar(campanha_b, agora=NO_PERIODO)
    antes = c.retrato(pb)
    c.rejeita([Motivo.COLETA_NAO_ADMITIDA], concluir, pb, agora=NO_PERIODO)
    assert c.retrato(pb) == antes


def test_ultimo_dia_aceita_e_dia_seguinte_rejeita(campanha_b, base):
    combinacao = ("Não",)
    no_ultimo_dia, no_dia_seguinte = (
        iniciar_participacao(campanha_b, c.conclusao(), agora=NO_PERIODO).participacao
        for _ in range(2)
    )
    for participacao in (no_ultimo_dia, no_dia_seguinte):
        _preencher_percurso(participacao, base, *combinacao)
    assert concluir(no_ultimo_dia, agora=ULTIMO_DIA).situacao is SituacaoConclusao.CONCLUIDA
    c.rejeita([Motivo.COLETA_NAO_ADMITIDA], concluir, no_dia_seguinte, agora=DEPOIS_DO_FIM)
    assert Participacao.objects.get(pk=no_dia_seguinte.pk).concluida_em is None


# --- Estados inconsistentes (US12; FR-016, FR-045, FR-046) ----------------------------------


@pytest.fixture
def nao_suportada():
    return c.versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": 2}), pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )


def test_estrutura_nao_suportada_na_consulta_e_na_conclusao(nao_suportada, conclusao):
    from trajetoria.instrumento.conteudo import conteudo_da_versao

    campanha = c.campanha_aberta(nao_suportada)
    p = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    antes, versao_antes = c.retrato(p), conteudo_da_versao(nao_suportada)
    c.rejeita([Motivo.ESTRUTURA_NAO_SUPORTADA], situacao_da_jornada, p, agora=NO_PERIODO)
    c.rejeita([Motivo.ESTRUTURA_NAO_SUPORTADA], concluir, p, agora=NO_PERIODO)
    op_campanha.encerrar(campanha, agora=NO_PERIODO)
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA, Motivo.ESTRUTURA_NAO_SUPORTADA],
        concluir,
        p,
        agora=NO_PERIODO,
    )
    assert c.retrato(p) == antes
    assert conteudo_da_versao(nao_suportada) == versao_antes


def _completa(p, r):
    _s1(p, r, "Sim")
    _s2(p, r)
    responder_escala(p, r.p(2, 3), 4, agora=NO_PERIODO)


def test_respostas_incoerentes_gravadas_fora_das_operacoes(p, ramificada):
    _completa(p, ramificada)
    _s3(p, ramificada)  # inativa: deve continuar gravada após a rejeição
    da_outra_pergunta = opcao_de(ramificada.p(2, 2), "B")
    Resposta.objects.filter(participacao=p, pergunta=ramificada.p(1)).update(
        opcao=da_outra_pergunta
    )
    antes = c.retrato(p)
    # A Opção alheia na Pergunta com regra impede até de percorrer (contracts/percurso.md).
    (violacao,) = c.rejeita([Motivo.OPCAO_DE_OUTRA_PERGUNTA], concluir, p, agora=NO_PERIODO)
    assert violacao.campo == "pergunta"
    assert str(ramificada.p(1).id) in violacao.detalhe
    assert c.retrato(p) == antes


@pytest.mark.parametrize(
    "corromper, motivo",
    [
        ({"escala": 9}, Motivo.ESCALA_FORA_DOS_LIMITES),
        ({"texto": "   "}, Motivo.VALOR_VAZIO),
    ],
    ids=["escala", "texto"],
)
def test_resposta_incoerente_rejeita_com_o_motivo_da_005(p, ramificada, corromper, motivo):
    _completa(p, ramificada)
    _s3(p, ramificada)
    alvo = ramificada.p(2, 3) if "escala" in corromper else ramificada.p(2, 1)
    Resposta.objects.filter(participacao=p, pergunta=alvo).update(**corromper)
    antes = c.retrato(p)
    (violacao,) = c.rejeita([motivo], concluir, p, agora=NO_PERIODO)
    assert violacao.campo == "pergunta"
    assert str(alvo.id) in violacao.detalhe
    assert c.retrato(p) == antes
    assert Participacao.objects.get(pk=p.pk).concluida_em is None


def test_varias_incoerencias_reunidas_e_sem_valor_declarado(p, ramificada):
    _completa(p, ramificada)
    Resposta.objects.filter(participacao=p, pergunta=ramificada.p(2, 3)).update(escala=987654)
    Resposta.objects.filter(participacao=p, pergunta=ramificada.p(2, 1)).update(
        texto="   ", complemento=None
    )
    Resposta.objects.filter(participacao=p, pergunta=ramificada.p(2, 2)).update(
        complemento="segredo declarado"
    )
    with pytest.raises(ParticipacaoRejeitada) as erro:
        concluir(p, agora=NO_PERIODO)
    assert set(erro.value.motivos) == {
        Motivo.VALOR_VAZIO,
        Motivo.COMPLEMENTO_NAO_ADMITIDO,
        Motivo.ESCALA_FORA_DOS_LIMITES,
    }
    mensagem = str(erro.value)
    assert "987654" not in mensagem and "segredo declarado" not in mensagem


# --- Regressões do code review ---------------------------------------------------------------


def test_conclusao_tem_numero_fixo_de_consultas_ao_instrumento(pb, base):
    # A coerência usa as Opções já lidas por `respostas_atuais` (nenhuma consulta por
    # Resposta) e a Versão vem junto do bloqueio (nenhuma leitura avulsa antes do conteúdo).
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    _preencher_percurso(pb, base, "Sim", Q14["graduacao"], "Sim", "Não")
    assert Resposta.objects.filter(participacao=pb).count() > 40
    with CaptureQueriesContext(connection) as capturadas:
        concluir(pb, agora=NO_PERIODO)
    sqls = [q["sql"] for q in capturadas.captured_queries]
    assert len([s for s in sqls if 'FROM "instrumento_opcao"' in s]) <= 2
    assert len([s for s in sqls if 'FROM "instrumento_versao"' in s]) == 1


def test_violacao_de_coleta_e_a_mesma_em_todas_as_operacoes(p, ramificada, campanha_r):
    from trajetoria.participacao.regras import coleta_nao_admitida

    _s1(p, ramificada, "Sim")
    _s2(p, ramificada)
    (na_escrita,) = c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        responder_texto,
        p,
        ramificada.p(3),
        "resposta fictícia",
        agora=DEPOIS_DO_FIM,
    )
    (na_conclusao,) = c.rejeita([Motivo.COLETA_NAO_ADMITIDA], concluir, p, agora=DEPOIS_DO_FIM)
    (na_consulta,) = situacao_da_jornada(p, agora=DEPOIS_DO_FIM).impedimentos
    assert na_escrita == na_conclusao == na_consulta == coleta_nao_admitida()

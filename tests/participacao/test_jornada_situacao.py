"""Consulta da jornada (contracts/consultas.md; FR-047 a FR-050)."""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import (
    DEPOIS_DO_FIM,
    NO_PERIODO,
    pergunta_de,
    pergunta_mem,
    secao_mem,
)
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.participacao.consultas import admite_escrita, respostas_atuais, situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import (
    concluir,
    iniciar_participacao,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db

TEXTO = TipoPergunta.TEXTO_CURTO


@pytest.fixture
def linear():
    """Versão publicada com três Seções lineares, uma obrigatória de texto cada."""
    return c.versao_publicada_de(*(secao_mem(pergunta_mem(tipo=TEXTO)) for _ in range(3)))


@pytest.fixture
def jornada(linear, conclusao):
    campanha = c.campanha_aberta(linear)
    return iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao


def _responder(participacao, versao, s):
    responder_texto(participacao, pergunta_de(versao, s, 1), "resposta fictícia", agora=NO_PERIODO)


def test_participacao_sem_respostas(jornada, linear):
    situacao = situacao_da_jornada(jornada, agora=NO_PERIODO)
    assert [p.secao.posicao for p in situacao.passagens] == [1]
    assert situacao.secao_atual.posicao == 1
    assert not situacao.finalizada
    assert situacao.respostas == {}
    assert situacao.fora_do_percurso == frozenset()
    assert situacao.concluida_em is None
    assert situacao.admite_escrita


def test_avanca_com_as_respostas(jornada, linear):
    _responder(jornada, linear, 1)
    situacao = situacao_da_jornada(jornada, agora=NO_PERIODO)
    assert situacao.secao_atual.posicao == 2
    assert set(situacao.respostas) == {pergunta_de(linear, 1, 1).id}

    _responder(jornada, linear, 2)
    _responder(jornada, linear, 3)
    situacao = situacao_da_jornada(jornada, agora=NO_PERIODO)
    assert situacao.finalizada
    assert situacao.secao_atual is None
    assert [p.secao.posicao for p in situacao.passagens] == [1, 2, 3]


def test_consulta_nao_grava_e_e_repetivel(jornada, linear):
    _responder(jornada, linear, 1)
    antes = c.retrato(jornada)
    primeira = situacao_da_jornada(jornada, agora=NO_PERIODO)
    segunda = situacao_da_jornada(jornada, agora=NO_PERIODO)
    assert c.retrato(jornada) == antes
    assert primeira.passagens == segunda.passagens


def test_relê_a_participacao_do_banco(jornada):
    desatualizada = Participacao.objects.get(pk=jornada.pk)
    Participacao.objects.filter(pk=jornada.pk).update(concluida_em=NO_PERIODO)
    assert desatualizada.concluida_em is None
    assert situacao_da_jornada(desatualizada, agora=NO_PERIODO).concluida_em == NO_PERIODO


# --- Impedimentos (US3) ----------------------------------------------------------------------


def test_impedimentos_sao_as_pendencias_da_secao_atual(jornada, linear):
    _responder(jornada, linear, 1)
    situacao = situacao_da_jornada(jornada, agora=NO_PERIODO)
    assert [v.motivo for v in situacao.impedimentos] == [Motivo.OBRIGATORIA_PENDENTE]
    assert str(pergunta_de(linear, 2, 1).id) in situacao.impedimentos[0].detalhe
    assert not situacao.pode_concluir


def test_impedimentos_com_campanha_encerrada(jornada, linear):
    situacao = situacao_da_jornada(jornada, agora=DEPOIS_DO_FIM)
    assert [v.motivo for v in situacao.impedimentos] == [
        Motivo.COLETA_NAO_ADMITIDA,
        Motivo.OBRIGATORIA_PENDENTE,
    ]


def test_pode_concluir_so_finalizada_e_sem_impedimentos(jornada, linear):
    for s in (1, 2, 3):
        _responder(jornada, linear, s)
    assert situacao_da_jornada(jornada, agora=NO_PERIODO).pode_concluir
    assert not situacao_da_jornada(jornada, agora=DEPOIS_DO_FIM).pode_concluir


# --- Baseline (US8, US9, US11) ---------------------------------------------------------------

_ATE_S8 = ("Sim", c.Q14["graduacao"], "Sim", "Sim")


@pytest.fixture
def base():
    return c.baseline_publicada()


@pytest.fixture
def na_baseline(base, conclusao):
    campanha = c.campanha_aberta(base.versao)
    return iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao


def _posicoes(situacao):
    return [p.secao.posicao for p in situacao.passagens]


def test_retomada_reconstroi_a_mesma_jornada(base, na_baseline):
    escolhas = c.escolhas_baseline(*_ATE_S8)
    c.preencher(na_baseline, base, [1, 2, 3, 6, 8], escolhas)
    c.preencher(na_baseline, base, [9], escolhas, exceto=("Q35", "Q40"))
    antes = c.retrato(na_baseline)

    inicio = iniciar_participacao(na_baseline.campanha, na_baseline.conclusao, agora=NO_PERIODO)
    assert inicio.situacao.value == "ja_existente"
    pela_instancia = situacao_da_jornada(inicio.participacao, agora=NO_PERIODO)
    pelo_banco = situacao_da_jornada(
        Participacao.objects.get(pk=na_baseline.pk), agora=NO_PERIODO
    )

    assert pela_instancia.secao_atual.posicao == 9
    assert pela_instancia.passagens[-1].pendentes == (base.q(35).id, base.q(40).id)
    assert _posicoes(pela_instancia)[:-1] == [1, 2, 3, 6, 8]
    for campo in ("passagens", "fora_do_percurso", "impedimentos", "respostas"):
        assert getattr(pela_instancia, campo) == getattr(pelo_banco, campo)
    assert c.retrato(na_baseline) == antes  # nada gravado pela retomada


def test_nada_de_cursor_sessao_tentativa_ou_progresso():
    from trajetoria.participacao import consultas, percurso

    campos = consultas.SituacaoDaJornada.__dataclass_fields__
    nomes = set(vars(percurso)) | set(vars(consultas)) | set(campos)
    proibidos = ("cursor", "sessao", "tentativa", "progresso", "posicao_atual")
    assert not [n for n in nomes if any(p in n.lower() for p in proibidos)]


def test_troca_de_ramo_deixa_respostas_inativas_e_recuperaveis(base, na_baseline):
    escolhas = c.escolhas_baseline(*_ATE_S8)
    c.preencher(na_baseline, base, [1, 2, 3, 6, 8, 9], escolhas)
    s9 = {p.id for p in base.s(9).perguntas.all() if p.obrigatoria}
    s9_respondidas = s9 & set(respostas_atuais(na_baseline))
    assert s9_respondidas == s9

    responder_escolha_unica(na_baseline, base.q(33), base.opcao(33, "Não"), agora=NO_PERIODO)
    situacao = situacao_da_jornada(na_baseline, agora=NO_PERIODO)
    assert s9 <= set(respostas_atuais(na_baseline))  # persistidas e recuperáveis
    assert s9 <= situacao.fora_do_percurso
    assert 9 not in _posicoes(situacao)
    assert _posicoes(situacao)[-1] == 10
    assert situacao.passagens[-1].pendentes == (base.q(45).id,)  # S9 não satisfaz S10
    assert not [v for v in situacao.impedimentos if any(str(i) in v.detalhe for i in s9)]

    antes = list(Resposta.objects.filter(pergunta_id__in=s9).order_by("id").values())
    responder_escolha_unica(na_baseline, base.q(33), base.opcao(33, "Sim"), agora=NO_PERIODO)
    situacao = situacao_da_jornada(na_baseline, agora=NO_PERIODO)
    assert situacao.fora_do_percurso == frozenset()
    assert 9 in _posicoes(situacao) and situacao.secao_atual.posicao == 11
    assert list(Resposta.objects.filter(pergunta_id__in=s9).order_by("id").values()) == antes
    assert "ativa" not in {f.name for f in Resposta._meta.get_fields()}


def test_rascunho_de_campanha_encerrada_continua_legivel(base, na_baseline):
    escolhas = c.escolhas_baseline(*_ATE_S8)
    c.preencher(na_baseline, base, [1, 2, 3], escolhas)
    em_coleta = situacao_da_jornada(na_baseline, agora=NO_PERIODO)
    antes = c.retrato(na_baseline)
    encerrada = situacao_da_jornada(na_baseline, agora=DEPOIS_DO_FIM)
    assert encerrada.passagens == em_coleta.passagens
    assert not encerrada.admite_escrita
    assert Motivo.COLETA_NAO_ADMITIDA in [v.motivo for v in encerrada.impedimentos]
    assert c.retrato(na_baseline) == antes


def test_leitura_historica_da_concluida(base, na_baseline, monkeypatch):
    from trajetoria.participacao import consultas

    combinacao = ("Sim", c.Q14["pos"], "Não", "Não")
    secoes = c.secoes_esperadas(*combinacao)
    c.preencher(na_baseline, base, secoes, c.escolhas_baseline(*combinacao))
    concluir(na_baseline, agora=NO_PERIODO)  # (A) concluída em 2027
    em_2027 = situacao_da_jornada(na_baseline, agora=NO_PERIODO)
    respostas_2027 = c.retrato(na_baseline)

    def proibido(*args, **kwargs):
        raise AssertionError("a leitura da concluída não depende do estado da Campanha")

    monkeypatch.setattr(consultas, "estado", proibido)
    em_2030 = situacao_da_jornada(na_baseline, agora=c.momento(2030, 1, 1))  # (B), (C)
    assert em_2030.passagens == em_2027.passagens  # (D)
    assert c.rotulos(em_2030.passagens) == c.rotulos(em_2027.passagens)
    assert em_2030.concluida_em == NO_PERIODO  # (E)
    assert c.retrato(na_baseline) == respostas_2027
    assert not admite_escrita(na_baseline, agora=c.momento(2030, 1, 1))
    monkeypatch.undo()
    c.rejeita(  # (F)
        [Motivo.PARTICIPACAO_CONCLUIDA],
        responder_texto,
        na_baseline,
        base.q(3),
        "resposta fictícia",
        agora=c.momento(2030, 1, 1),
    )

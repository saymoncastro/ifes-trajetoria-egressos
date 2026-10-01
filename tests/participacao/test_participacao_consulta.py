"""Recuperar o estado atual de uma Participação (US9) e proveniência (FR-042 a FR-044)."""

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.participacao.consultas import (
    admite_escrita,
    localizar_participacao,
    respostas_atuais,
)
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import (
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)

pytestmark = pytest.mark.django_db


def _responder_algumas(participacao, inst):
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    responder_escolha_multipla(
        participacao,
        inst.multipla,
        [inst.opcao(inst.multipla, "C"), inst.opcao(inst.multipla, "Outro:")],
        complemento="Monitoria",
        agora=NO_PERIODO,
    )
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    responder_escala(participacao, inst.escala, 4, agora=NO_PERIODO)


def test_respostas_atuais_distingue_respondida_e_valores_por_tipo(participacao, inst):
    _responder_algumas(participacao, inst)

    atuais = respostas_atuais(participacao)

    assert set(atuais) == {inst.unica.id, inst.multipla.id, inst.texto.id, inst.escala.id}
    assert atuais[inst.unica.id].opcao == inst.opcao(inst.unica, "Sim")
    multipla = atuais[inst.multipla.id]
    assert {o.texto for o in multipla.opcoes.all()} == {"C", "Outro:"}
    assert multipla.complemento == "Monitoria"
    assert atuais[inst.texto.id].texto == "27"
    assert atuais[inst.escala.id].escala == 4


def test_cada_pergunta_da_versao_e_respondida_ou_nao(participacao, inst):
    _responder_algumas(participacao, inst)
    atuais = respostas_atuais(participacao)

    perguntas = {p.id for secao in participacao.versao.secoes.all() for p in secao.perguntas.all()}
    respondidas = {p for p in perguntas if p in atuais}
    nao_respondidas = perguntas - respondidas
    assert nao_respondidas == {inst.unica_outro.id, inst.campus.id, inst.posterior.id}


def test_respostas_atuais_sem_consultas_por_resposta(
    participacao, inst, django_assert_max_num_queries
):
    _responder_algumas(participacao, inst)
    with django_assert_max_num_queries(2):
        atuais = respostas_atuais(participacao)
        for r in atuais.values():
            r.pergunta.tipo, r.opcao, list(r.opcoes.all())


def test_localizar_nao_cria(inst, conclusao):
    preparacao = c.campanha_em_preparacao(inst.versao)
    aberta = c.campanha_aberta(inst.versao)
    encerrada = c.campanha_aberta(inst.versao)
    op_campanha.encerrar(encerrada, agora=NO_PERIODO)

    for campanha in (preparacao, aberta, encerrada):
        assert localizar_participacao(campanha, conclusao) is None
    assert not Participacao.objects.exists()


def test_localizar_existente(participacao):
    assert localizar_participacao(participacao.campanha, participacao.conclusao) == participacao


def test_admite_escrita_pelo_estado_da_campanha(participacao):
    assert admite_escrita(participacao, agora=NO_PERIODO)
    assert not admite_escrita(participacao, agora=DEPOIS_DO_FIM)


def test_declarado_e_institucional_coexistem(campanha, inst):
    """A unidade da Conclusão é "Serra"; o egresso declara "Campus Vitória". As duas
    permanecem, cada uma com sua origem, sem sobrescrita nem comparação (FR-043, DP-508)."""
    from trajetoria.participacao.operacoes import iniciar_participacao

    conclusao = c.conclusao(unidade="Serra")
    antes = ConclusaoAcademica.objects.filter(pk=conclusao.pk).values().get()
    participacao = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    # Nenhuma Resposta nasce da Conclusão (FR-042).
    assert not Resposta.objects.filter(participacao=participacao).exists()

    responder_escolha_unica(
        participacao, inst.campus, inst.opcao(inst.campus, "Campus Vitória"), agora=NO_PERIODO
    )
    _responder_algumas(participacao, inst)

    assert participacao.conclusao.unidade == "Serra"
    assert respostas_atuais(participacao)[inst.campus.id].opcao.texto == "Campus Vitória"
    assert ConclusaoAcademica.objects.filter(pk=conclusao.pk).values().get() == antes


def test_consultas_nao_gravam(participacao, inst):
    _responder_algumas(participacao, inst)
    antes = c.retrato(participacao)
    respostas_atuais(participacao)
    localizar_participacao(participacao.campanha, participacao.conclusao)
    admite_escrita(participacao, agora=NO_PERIODO)
    assert c.retrato(participacao) == antes

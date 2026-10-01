"""A mesma Conclusão em Campanhas diferentes (US10): Participações independentes."""

from datetime import date

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import NO_PERIODO, momento
from trajetoria.academico.models import Pessoa
from trajetoria.participacao.consultas import participacoes_da_conclusao, respostas_atuais
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import (
    SituacaoInicio,
    iniciar_participacao,
    responder_escala,
    responder_texto,
)

pytestmark = pytest.mark.django_db


def _rodada(inst, ano: int):
    """Campanha aberta em abril–junho do ano e o momento de referência no meio dela."""
    campanha = c.campanha_aberta(inst.versao, inicio=date(ano, 4, 1), fim=date(ano, 6, 30))
    return campanha, momento(ano, 5, 1)


def test_mesma_conclusao_em_tres_campanhas(inst):
    ads = c.conclusao(ano=2024)
    participacoes = []
    for ano in (2025, 2027, 2030):
        campanha, agora = _rodada(inst, ano)
        inicio = iniciar_participacao(campanha, ads, agora=agora)
        assert inicio.situacao is SituacaoInicio.CRIADA
        # Nada é copiado de Participação anterior (US10.3).
        assert respostas_atuais(inicio.participacao) == {}
        responder_texto(inicio.participacao, inst.texto, f"resposta {ano}", agora=agora)
        participacoes.append((inicio.participacao, agora))

    assert len({p.id for p, _ in participacoes}) == 3
    (p2025, _), (p2027, _), (p2030, agora2030) = participacoes
    antes = [c.retrato(p2025), c.retrato(p2027)]

    responder_texto(p2030, inst.texto, "alterada", agora=agora2030)
    responder_escala(p2030, inst.escala, 5, agora=agora2030)

    assert [c.retrato(p2025), c.retrato(p2027)] == antes
    assert respostas_atuais(p2025)[inst.texto.id].texto == "resposta 2025"

    # Todas devolvidas, em ordem determinística, nenhuma como "a atual" (US10.4).
    assert participacoes_da_conclusao(ads) == (p2025, p2027, p2030)


def test_duas_conclusoes_da_mesma_pessoa_na_mesma_campanha(campanha):
    pessoa = Pessoa.objects.create(fonte="teste-participacao", id_externo="TP-P-dupla")
    ads = c.conclusao(ano=2021, unidade="Serra", pessoa=pessoa)
    especializacao = c.conclusao(ano=2023, unidade="Cefor", pessoa=pessoa)

    p1 = iniciar_participacao(campanha, ads, agora=NO_PERIODO).participacao
    p2 = iniciar_participacao(campanha, especializacao, agora=NO_PERIODO).participacao

    assert p1.id != p2.id
    assert p1.pessoa == p2.pessoa == pessoa
    assert (p1.conclusao_id, p2.conclusao_id) == (ads.id, especializacao.id)


def test_campanhas_sobrepostas_uma_participacao_em_cada(inst, conclusao):
    a = c.campanha_aberta(inst.versao)
    b = c.campanha_aberta(inst.versao)
    pa = iniciar_participacao(a, conclusao, agora=NO_PERIODO).participacao
    pb = iniciar_participacao(b, conclusao, agora=NO_PERIODO).participacao
    assert pa.id != pb.id
    assert Participacao.objects.filter(conclusao=conclusao).count() == 2

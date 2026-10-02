"""Os quatro indicadores e as taxas, por consulta direta (Feature 011; spec FR-030 a FR-039;
US2, US6; casos H, I, J, K)."""

from decimal import Decimal

from tests.acompanhamento import construcao as k
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.acompanhamento.apresentacao import Indicadores
from trajetoria.acompanhamento.consultas import indicadores_da_campanha
from trajetoria.campanha.consultas import populacao_no_momento
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.participacao.models import Resposta

INSTITUCIONAL = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())


def test_totais_institucionais(ref):
    assert indicadores_da_campanha(ref.I, INSTITUCIONAL) == Indicadores(7, 4, 2)


def test_elegiveis_sao_a_populacao_da_004(ref):
    for campanha in (ref.I, ref.R, ref.P, ref.E):
        esperado = populacao_no_momento(campanha).count()
        assert indicadores_da_campanha(campanha, INSTITUCIONAL).elegiveis == esperado


def test_participacao_sem_resposta_conta_como_iniciada(ref):
    """007/DP-703 continua aberta: a 011 conta a existência da Participação."""
    assert not Resposta.objects.filter(participacao=ref.participacoes["n1"]).exists()
    assert indicadores_da_campanha(ref.I, INSTITUCIONAL).iniciadas == 4


def test_concluida_por_recusa_conta_como_concluida(ref):
    """006/DP-601 continua aberta: `concluida_em` preenchido basta."""
    assert ref.participacoes["v1"].concluida_em is not None
    assert indicadores_da_campanha(ref.I, INSTITUCIONAL).concluidas == 2


def test_campanha_sem_participacoes(ref):
    indicadores = indicadores_da_campanha(ref.R, INSTITUCIONAL)
    assert (indicadores.iniciadas, indicadores.concluidas, indicadores.nao_concluidas) == (0, 0, 0)
    assert indicadores.elegiveis == 4
    assert indicadores.taxa_inicio == Decimal("0.0")


def test_elegiveis_zero_taxas_nao_se_aplicam(ref):
    vazia = k.campanha(ref.inst.versao, unidades=["Unidade inexistente"])
    indicadores = indicadores_da_campanha(vazia, INSTITUCIONAL)
    assert indicadores == Indicadores(0, 0, 0)
    assert indicadores.taxa_inicio is None and indicadores.taxa_conclusao is None


def test_nova_conclusao_elegivel_aparece_na_consulta_seguinte(ref):
    antes = indicadores_da_campanha(ref.I, INSTITUCIONAL).elegiveis
    k.conclusao(unidade="Serra", ano=2024)
    assert indicadores_da_campanha(ref.I, INSTITUCIONAL).elegiveis == antes + 1


def test_participacao_concluida_aparece_na_consulta_seguinte(ref):
    from tests.participacao.construcao import preencher_instrumento
    from trajetoria.participacao.operacoes import concluir

    antes = indicadores_da_campanha(ref.I, INSTITUCIONAL)
    participacao = ref.participacoes["n1"]
    preencher_instrumento(participacao, ref.inst, agora=None)
    concluir(participacao, agora=None)
    depois = indicadores_da_campanha(ref.I, INSTITUCIONAL)
    assert depois.concluidas == antes.concluidas + 1
    assert depois.nao_concluidas == antes.nao_concluidas - 1


def test_taxa_acima_de_cem_por_cento_sem_teto(inst):
    """Simula 001/DP-005 (correção acadêmica) alterando a Conclusão por ORM **só no teste**:
    a Participação não é reavaliada pela elegibilidade atual (FR-038)."""
    x = k.conclusao(unidade="Vitória", ano=2020)
    y = k.conclusao(unidade="Vitória", ano=2021)
    n = k.campanha(inst.versao, ano_minimo=2020)
    k.concluida(n, x, inst)
    k.concluida(n, y, inst)
    ConclusaoAcademica.objects.filter(pk=x.pk).update(ano_conclusao=2018)
    indicadores = indicadores_da_campanha(n, INSTITUCIONAL)
    assert indicadores == Indicadores(1, 2, 2)
    assert indicadores.taxa_inicio == Decimal("200.0")
    assert indicadores.taxa_conclusao == Decimal("200.0")
    ConclusaoAcademica.objects.filter(pk=y.pk).update(ano_conclusao=2018)
    sem_elegiveis = indicadores_da_campanha(n, INSTITUCIONAL)
    assert sem_elegiveis == Indicadores(0, 2, 2)
    assert sem_elegiveis.taxa_conclusao is None

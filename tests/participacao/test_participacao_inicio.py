"""Iniciar Participação (US1) e unicidade por Campanha × Conclusão (US2)."""

from datetime import date

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO, momento, rejeita
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.participacao import operacoes
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import SituacaoInicio, iniciar_participacao
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


# --- US1: iniciar ------------------------------------------------------------------------


def test_inicio_valido(campanha, conclusao):
    inicio = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)

    assert inicio.situacao is SituacaoInicio.CRIADA
    p = inicio.participacao
    assert (p.campanha_id, p.conclusao_id, p.iniciada_em) == (
        campanha.id,
        conclusao.id,
        NO_PERIODO,
    )
    assert not Resposta.objects.filter(participacao=p).exists()
    # Pessoa, Versão e Pesquisa derivadas, sem coluna própria (US1.2, FR-004).
    assert p.pessoa == conclusao.pessoa
    assert p.versao == campanha.versao
    assert p.pesquisa == campanha.versao.pesquisa


def test_conclusao_nao_elegivel(campanha):
    fora = c.conclusao(ano=2010)
    (violacao,) = rejeita(
        [Motivo.CONCLUSAO_NAO_ELEGIVEL], iniciar_participacao, campanha, fora, agora=NO_PERIODO
    )
    assert "ano_conclusao" in violacao.detalhe
    assert "2010" not in violacao.detalhe
    assert not Participacao.objects.exists()


def test_campanha_em_preparacao(inst, conclusao):
    preparacao = c.campanha_em_preparacao(inst.versao)
    rejeita(
        [Motivo.COLETA_NAO_ADMITIDA], iniciar_participacao, preparacao, conclusao, agora=NO_PERIODO
    )
    assert not Participacao.objects.exists()


def test_campanha_encerrada_explicitamente(campanha, conclusao):
    op_campanha.encerrar(campanha, agora=momento(2027, 4, 15))
    rejeita(
        [Motivo.COLETA_NAO_ADMITIDA], iniciar_participacao, campanha, conclusao, agora=NO_PERIODO
    )
    assert not Participacao.objects.exists()


def test_campanha_encerrada_pelo_fim_do_periodo(campanha, conclusao):
    rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        iniciar_participacao,
        campanha,
        conclusao,
        agora=DEPOIS_DO_FIM,
    )
    assert not Participacao.objects.exists()


def test_encerrada_e_nao_elegivel_reune_as_duas_violacoes(campanha):
    rejeita(
        [Motivo.COLETA_NAO_ADMITIDA, Motivo.CONCLUSAO_NAO_ELEGIVEL],
        iniciar_participacao,
        campanha,
        c.conclusao(ano=2010),
        agora=DEPOIS_DO_FIM,
    )
    assert not Participacao.objects.exists()


def test_inicio_sem_convite(inst):
    # Só Versão, Campanha e Conclusão existem: nenhum convite, token ou sessão (US1.6).
    campanha = c.campanha_aberta(inst.versao)
    inicio = iniciar_participacao(campanha, c.conclusao(), agora=NO_PERIODO)
    assert inicio.situacao is SituacaoInicio.CRIADA


@pytest.mark.parametrize(
    "argumentos",
    [
        {"campanha": "campanha"},
        {"conclusao": object()},
        {"agora": date(2027, 5, 1)},
        {"agora": NO_PERIODO.replace(tzinfo=None)},
    ],
)
def test_argumento_de_tipo_errado(campanha, conclusao, argumentos):
    kwargs = {"campanha": campanha, "conclusao": conclusao, "agora": NO_PERIODO, **argumentos}
    with pytest.raises(TypeError):
        iniciar_participacao(kwargs["campanha"], kwargs["conclusao"], agora=kwargs["agora"])
    assert not Participacao.objects.exists()


# --- US2: unicidade e idempotência ---------------------------------------------------------


def test_inicio_repetido_devolve_a_existente(campanha, conclusao):
    primeira = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    antes = c.retrato(primeira)

    inicio = iniciar_participacao(campanha, conclusao, agora=momento(2027, 6, 1))

    assert inicio.situacao is SituacaoInicio.JA_EXISTENTE
    assert inicio.participacao.id == primeira.id
    assert inicio.participacao.iniciada_em == NO_PERIODO
    assert c.retrato(primeira) == antes
    assert Participacao.objects.count() == 1


def test_inicio_repetido_com_campanha_encerrada_pela_data(participacao):
    antes = c.retrato(participacao)
    inicio = iniciar_participacao(
        participacao.campanha, participacao.conclusao, agora=DEPOIS_DO_FIM
    )
    assert (inicio.situacao, inicio.participacao.id) == (
        SituacaoInicio.JA_EXISTENTE,
        participacao.id,
    )
    assert c.retrato(participacao) == antes


def test_inicio_repetido_com_campanha_encerrada_explicitamente(participacao):
    op_campanha.encerrar(participacao.campanha, agora=momento(2027, 5, 15))
    antes = c.retrato(participacao)
    inicio = iniciar_participacao(
        participacao.campanha, participacao.conclusao, agora=momento(2027, 5, 20)
    )
    assert (inicio.situacao, inicio.participacao.id) == (
        SituacaoInicio.JA_EXISTENTE,
        participacao.id,
    )
    assert c.retrato(participacao) == antes


def test_inicio_repetido_apos_conclusao_sair_dos_criterios(participacao):
    # Simula uma correção futura de dado acadêmico (001/DP-005): a elegibilidade só vale
    # na criação (FR-034, DP-507).
    conclusao = participacao.conclusao
    conclusao.ano_conclusao = 2010
    conclusao.save(update_fields=["ano_conclusao"])

    inicio = iniciar_participacao(participacao.campanha, conclusao, agora=NO_PERIODO)
    assert (inicio.situacao, inicio.participacao.id) == (
        SituacaoInicio.JA_EXISTENTE,
        participacao.id,
    )


def test_nao_existe_reinicio_nem_tentativa():
    assert set(operacoes.__all__) == {
        "Inicio",
        "SituacaoInicio",
        "SituacaoRemocao",
        "iniciar_participacao",
        "remover_resposta",
        "responder_escala",
        "responder_escolha_multipla",
        "responder_escolha_unica",
        "responder_texto",
    }


# --- Regressões do code review ---------------------------------------------------------------


def test_campanha_ou_conclusao_nao_gravada_e_value_error(campanha, conclusao):
    from trajetoria.academico.models import ConclusaoAcademica
    from trajetoria.campanha.models import Campanha

    nao_gravada = Campanha(nome="x", versao=campanha.versao)
    with pytest.raises(ValueError):
        iniciar_participacao(nao_gravada, conclusao, agora=NO_PERIODO)
    with pytest.raises(ValueError):
        iniciar_participacao(
            campanha, ConclusaoAcademica(pessoa=conclusao.pessoa), agora=NO_PERIODO
        )
    assert not Participacao.objects.exists()


def test_violacoes_de_admissao_equivalem_a_admite_participacao(inst):
    """A admissão é derivada uma vez, pelos contratos `estado` e `avaliar` da 004, e coincide
    com `admite_participacao` em todos os estados e elegibilidades."""
    from trajetoria.campanha.consultas import admite_participacao

    preparacao = c.campanha_em_preparacao(inst.versao, ano_minimo=2020)
    aberta = c.campanha_aberta(inst.versao, ano_minimo=2020)
    encerrada = c.campanha_aberta(inst.versao, ano_minimo=2020)
    op_campanha.encerrar(encerrada, agora=momento(2027, 4, 15))
    conclusoes = [c.conclusao(ano=2022), c.conclusao(ano=2010), c.conclusao(ano=None)]

    for campanha in (preparacao, aberta, encerrada):
        for conclusao in conclusoes:
            for agora in (NO_PERIODO, DEPOIS_DO_FIM):
                admite = admite_participacao(campanha, conclusao, agora=agora)
                violacoes = operacoes._violacoes_de_admissao(campanha, conclusao, agora)
                assert admite == (not violacoes), (campanha.nome, conclusao.ano_conclusao, agora)

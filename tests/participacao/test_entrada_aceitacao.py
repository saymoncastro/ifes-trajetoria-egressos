"""Aceitação da Feature 007: as 12 perguntas de sucesso do solicitante e as fronteiras.

A escrita é protegida por **comportamento** (linhas do banco, dublês de
`iniciar_participacao`), nunca por inspeção do código-fonte.
"""

import inspect
from dataclasses import fields
from datetime import date
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.urls import get_resolver

from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.participacao import entrada as modulo_entrada
from trajetoria.participacao.entrada import (
    Entrada,
    Formacao,
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    SituacaoDeEntrada,
    entrar,
    situacao_de_entrada,
)
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import Inicio, SituacaoInicio, iniciar_participacao

S = SituacaoDaFormacao
R = ResolucaoDaEntrada
NO_PERIODO = c.NO_PERIODO
RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "trajetoria" / "participacao"

PROIBIDOS = (
    "entrysession",
    "contextsession",
    "selection",
    "selecao",
    "enrollment",
    "eligibleformation",
    "campaignassignment",
    "campaignresolver",
    "personresolver",
    "identityresolver",
    "identityprovider",
    "authenticationprovider",
    "personmatcher",
    "portaluser",
    "usuario",
    "credential",
    "login",
    "sessao",
    "token",
    "reabr",
    "prioridade",
    "ranking",
    "campanha_escolhida",
    "dashboard",
    "indicador",
    "exporta",
)


# --- As 12 perguntas de sucesso (spec, "Cobertura") ---------------------------------------------


@pytest.mark.django_db
def test_01_sabemos_quais_formacoes_a_pessoa_concluiu(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0004")
    pessoa = ce.pessoa_da_fonte("SIM-P-0004")
    formacoes = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert {f.conclusao.pk for f in formacoes} == set(
        pessoa.conclusoes.values_list("pk", flat=True)
    )


@pytest.mark.django_db
def test_02_sabemos_quais_tem_pesquisa_disponivel_agora(inst):
    pessoa = ce.pessoa()
    antiga, recente = ce.formacao(pessoa, ano=2010), ce.formacao(pessoa, ano=2022)
    c.campanha_aberta(inst.versao, ano_minimo=2020)
    por_pk = {f.conclusao.pk: f for f in situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes}
    assert por_pk[antiga.pk].situacao is S.SEM_PESQUISA
    assert por_pk[recente.pk].situacao is S.DISPONIVEL_PARA_INICIAR


@pytest.mark.django_db
def test_03_unica_formacao_aplicavel_sem_escolha_artificial(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    assert entrar(pessoa, agora=NO_PERIODO).participacao.conclusao_id == conclusao.pk


@pytest.mark.django_db
def test_04_multiplas_formacoes_continuam_distintas(inst):
    pessoa = ce.pessoa()
    a, b = ce.formacao(pessoa, ano=2021), ce.formacao(pessoa, ano=2022)
    c.campanha_aberta(inst.versao)
    assert situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao is R.SELECAO_NECESSARIA
    pa = entrar(pessoa, a, agora=NO_PERIODO).participacao
    pb = entrar(pessoa, b, agora=NO_PERIODO).participacao
    assert (pa.conclusao_id, pb.conclusao_id) == (a.pk, b.pk)


def test_05_o_egresso_escolhe_formacao_nao_campanha():
    assert list(inspect.signature(entrar).parameters) == ["pessoa", "formacao", "agora"]


@pytest.mark.django_db
def test_06_campanhas_sobrepostas_sem_prioridade_inventada(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    c.campanha_aberta(inst.versao, inicio=date(2027, 4, 20))
    (f,) = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert (f.situacao, f.campanha, f.participacao) == (S.AMBIGUIDADE_OPERACIONAL, None, None)
    assert entrar(pessoa, f.conclusao, agora=NO_PERIODO).participacao is None
    assert not Participacao.objects.exists()


@pytest.mark.django_db
def test_07_participacao_existente_retomada_sem_duplicacao(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    primeira = entrar(pessoa, agora=NO_PERIODO).participacao
    assert entrar(pessoa, agora=NO_PERIODO).participacao == primeira
    assert Participacao.objects.count() == 1


@pytest.mark.django_db
def test_08_campanha_futura_gera_nova_participacao(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    ce.participacao_concluida(c.campanha_aberta(inst.versao), conclusao, inst)
    c.campanha_aberta(inst.versao, inicio=date(2030, 4, 1), fim=date(2030, 6, 30))
    assert entrar(pessoa, agora=c.momento(2030, 5, 1)).criada is True
    assert Participacao.objects.filter(conclusao=conclusao).count() == 2


@pytest.mark.django_db
def test_09_nenhum_dado_institucional_virou_resposta(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    entrar(pessoa, agora=NO_PERIODO)
    assert not Resposta.objects.exists()


def _rotas(padroes):
    for padrao in padroes:
        if hasattr(padrao, "url_patterns"):
            yield from _rotas(padrao.url_patterns)
        else:
            yield padrao


def test_10_nenhum_mecanismo_de_autenticacao():
    # Nenhuma app, middleware ou backend de autenticação ou sessão no projeto.
    assert not {"django.contrib.auth", "django.contrib.sessions"} & set(settings.INSTALLED_APPS)
    middleware = " ".join(getattr(settings, "MIDDLEWARE", [])).lower()
    assert "session" not in middleware and "auth" not in middleware
    assert not hasattr(settings, "AUTHENTICATION_BACKENDS") or not settings.is_overridden(
        "AUTHENTICATION_BACKENDS"
    )
    # Nenhuma rota expõe a entrada (nem nada da participação).
    rotas = [getattr(r, "lookup_str", "") for r in _rotas(get_resolver().url_patterns)]
    assert not [r for r in rotas if r.startswith("trajetoria.participacao")]
    for app in RAIZ.glob("trajetoria/*/"):
        for nome in ("urls.py", "views.py", "admin.py", "forms.py", "middleware.py"):
            assert not (app / nome).exists(), app / nome
    publicos = [n.lower() for n in modulo_entrada.__all__]
    assert not [n for n in publicos if any(p in n for p in PROIBIDOS)]


def test_11_nenhum_modelo_novo():
    assert {m.__name__ for m in apps.get_app_config("participacao").get_models()} == {
        "Participacao",
        "Resposta",
        "RespostaOpcao",
    }
    todos = [m.__name__.lower() for m in apps.get_models()]
    assert not [n for n in todos if any(p in n for p in PROIBIDOS)]


def test_12_nada_de_gen_ou_dashboard():
    # A API pública é exatamente a de entrada (test_api_publica_exata); aqui, nenhum modelo
    # analítico em app algum.
    analiticos = ("dashboard", "indicador", "agregacao", "snapshot", "exportacao", "grafico")
    modelos = [m.__name__.lower() for m in apps.get_models()]
    assert not [n for n in modelos if any(p in n for p in analiticos)]


# --- Persistência: zero modelos e migrações ---------------------------------------------------


@pytest.mark.django_db
def test_makemigrations_sem_mudancas():
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


def test_migracoes_da_participacao_inalteradas():
    arquivos = {p.name for p in (APP / "migrations").glob("0*.py")}
    assert arquivos == {"0001_initial.py", "0002_participacao_concluida_em.py"}


# --- Escrita protegida por comportamento -------------------------------------------------------


def _montagens(inst):
    """Uma Pessoa por situação de entrada, com Participações existentes quando cabe."""
    campanha = c.campanha_aberta(inst.versao, unidades=["Serra", "Cefor"])
    c.campanha_aberta(inst.versao, unidades=["Cefor"], inicio=date(2027, 4, 20))
    sem_formacao = ce.pessoa()
    sem_pesquisa = ce.pessoa()
    ce.formacao(sem_pesquisa, unidade="Vitória")
    resolvida = ce.pessoa()
    ce.formacao(resolvida)
    selecao = ce.pessoa()
    ce.formacao(selecao, ano=2021)
    ce.participacao_em_rascunho(campanha, ce.formacao(selecao, ano=2022))
    concluida = ce.pessoa()
    ce.participacao_concluida(campanha, ce.formacao(concluida), inst)
    ambigua = ce.pessoa()
    ce.formacao(ambigua, unidade="Cefor")
    return {
        R.SEM_FORMACAO: sem_formacao,
        R.SEM_PESQUISA: sem_pesquisa,
        R.ENTRADA_RESOLVIDA: resolvida,
        R.SELECAO_NECESSARIA: selecao,
        R.SEM_ENTRADA_PENDENTE: concluida,
        "ambigua": ambigua,
    }


@pytest.mark.django_db
def test_consulta_nao_altera_nenhuma_linha(inst):
    montagens = _montagens(inst)
    antes = ce.linhas()
    for esperada, pessoa in montagens.items():
        resolucao = situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao
        if isinstance(esperada, ResolucaoDaEntrada):
            assert resolucao is esperada
    assert ce.linhas() == antes


@pytest.mark.django_db
def test_entrar_nao_persiste_participacao_por_caminho_proprio(inst, monkeypatch):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    # Participação de outro par, já existente, devolvida por um dublê que não grava.
    alheia = ce.participacao_em_rascunho(campanha, ce.formacao(ce.pessoa()))
    monkeypatch.setattr(
        modulo_entrada,
        "iniciar_participacao",
        lambda *a, **k: Inicio(alheia, SituacaoInicio.JA_EXISTENTE),
    )
    total = Participacao.objects.count()
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert Participacao.objects.count() == total
    assert entrada.participacao is alheia


@pytest.mark.django_db
@pytest.mark.parametrize("rascunho", [False, True])
def test_delegacao_deterministica_a_005(inst, monkeypatch, rascunho):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    if rascunho:
        ce.participacao_em_rascunho(campanha, conclusao)
    antes = set(Participacao.objects.values_list("pk", flat=True))
    chamadas, devolvidas = [], []

    def registrador(campanha_, conclusao_, *, agora=None):
        chamadas.append((campanha_.pk, conclusao_.pk, agora))
        inicio = iniciar_participacao(campanha_, conclusao_, agora=agora)
        devolvidas.append(inicio.participacao.pk)
        return inicio

    monkeypatch.setattr(modulo_entrada, "iniciar_participacao", registrador)
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert chamadas == [(campanha.pk, conclusao.pk, NO_PERIODO)]
    assert devolvidas == [entrada.participacao.pk]
    novas = set(Participacao.objects.values_list("pk", flat=True)) - antes
    assert novas == (set() if rascunho else {entrada.participacao.pk})


@pytest.mark.django_db
def test_nada_a_iniciar_nada_chamado(inst, fonte_simulada, monkeypatch):
    montagens = _montagens(inst)
    ce.incorporar(fonte_simulada, "SIM-P-0010", "SIM-P-0011")
    alheia = ce.pessoa_da_fonte("SIM-P-0011").conclusoes.get()

    def falha(*args, **kwargs):
        raise AssertionError("iniciar_participacao não deveria ser chamada")

    monkeypatch.setattr(modulo_entrada, "iniciar_participacao", falha)
    antes = ce.linhas()
    for chave in (
        R.SEM_FORMACAO,
        R.SEM_PESQUISA,
        R.SEM_ENTRADA_PENDENTE,
        R.SELECAO_NECESSARIA,
    ):
        assert entrar(montagens[chave], agora=NO_PERIODO).participacao is None
    for chave in (R.SEM_PESQUISA, R.SEM_ENTRADA_PENDENTE, "ambigua"):
        pessoa = montagens[chave]
        (f,) = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
        entrar(pessoa, f.conclusao, agora=NO_PERIODO)
    with pytest.raises(modulo_entrada.FormacaoDeOutraPessoa):
        entrar(ce.pessoa_da_fonte("SIM-P-0010"), alheia, agora=NO_PERIODO)
    assert ce.linhas() == antes


# --- YAGNI das estruturas --------------------------------------------


def test_api_publica_exata():
    assert set(modulo_entrada.__all__) == {
        "SituacaoDaFormacao",
        "Formacao",
        "ResolucaoDaEntrada",
        "SituacaoDeEntrada",
        "Entrada",
        "FormacaoDeOutraPessoa",
        "situacao_de_entrada",
        "entrar",
    }
    assert [f.name for f in fields(Formacao)] == [
        "conclusao",
        "situacao",
        "campanhas",
        "participacao",
    ]
    assert [f.name for f in fields(SituacaoDeEntrada)] == ["formacoes", "resolucao"]
    assert [f.name for f in fields(Entrada)] == ["situacao", "participacao", "criada"]
    assert {s.name for s in S} == {
        "SEM_PESQUISA",
        "DISPONIVEL_PARA_INICIAR",
        "DISPONIVEL_PARA_RETOMAR",
        "JA_CONCLUIDA",
        "AMBIGUIDADE_OPERACIONAL",
    }
    assert {r.name for r in R} == {
        "SEM_FORMACAO",
        "SEM_PESQUISA",
        "SEM_ENTRADA_PENDENTE",
        "ENTRADA_RESOLVIDA",
        "SELECAO_NECESSARIA",
    }

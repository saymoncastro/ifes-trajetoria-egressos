"""Situação de entrada (Feature 007): classificação por formação e resolução global.

A primeira parte testa as regras puras, **sem banco**: instâncias não gravadas de
`ConclusaoAcademica`, `Campanha` e `Participacao` bastam, e o pytest-django bloquearia
qualquer consulta. A segunda parte testa `situacao_de_entrada` de ponta a ponta.
"""

from dataclasses import FrozenInstanceError
from datetime import date
from itertools import combinations_with_replacement

import pytest

from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from tests.participacao.construcao import momento
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.models import Campanha
from trajetoria.fonte_academica import cenarios
from trajetoria.participacao import entrada as modulo_entrada
from trajetoria.participacao.entrada import (
    Entrada,
    Formacao,
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    SituacaoDeEntrada,
    _classificar,
    _resolver,
    situacao_de_entrada,
)
from trajetoria.participacao.models import Participacao

S = SituacaoDaFormacao
R = ResolucaoDaEntrada

# --- Regras puras (sem banco) -----------------------------------------------------------------


def _campanhas(n: int) -> tuple[Campanha, ...]:
    return tuple(Campanha(nome=f"C{i}") for i in range(n))


def _rascunho() -> Participacao:
    return Participacao(concluida_em=None)


def _concluida() -> Participacao:
    return Participacao(concluida_em=momento(2027, 5, 20))


def _formacao(situacao: SituacaoDaFormacao) -> Formacao:
    """Formação em memória numa situação dada, montada pela própria regra."""
    conclusao = ConclusaoAcademica()
    if situacao is S.SEM_PESQUISA:
        return _classificar(conclusao, (), None)
    if situacao is S.AMBIGUIDADE_OPERACIONAL:
        return _classificar(conclusao, _campanhas(2), None)
    participacao = {
        S.DISPONIVEL_PARA_INICIAR: None,
        S.DISPONIVEL_PARA_RETOMAR: _rascunho(),
        S.JA_CONCLUIDA: _concluida(),
    }[situacao]
    return _classificar(conclusao, _campanhas(1), participacao)


def test_zero_campanhas_sem_pesquisa_nao_pendente():
    f = _classificar(ConclusaoAcademica(), (), None)
    assert (f.situacao, f.situacao.pendente, f.participacao, f.campanha) == (
        S.SEM_PESQUISA,
        False,
        None,
        None,
    )


def test_uma_campanha_sem_participacao_disponivel_para_iniciar_pendente():
    (campanha,) = _campanhas(1)
    f = _classificar(ConclusaoAcademica(), (campanha,), None)
    assert (f.situacao, f.situacao.pendente, f.participacao) == (
        S.DISPONIVEL_PARA_INICIAR,
        True,
        None,
    )
    assert f.campanha is campanha


def test_uma_campanha_rascunho_disponivel_para_retomar_pendente():
    p = _rascunho()
    f = _classificar(ConclusaoAcademica(), _campanhas(1), p)
    assert (f.situacao, f.situacao.pendente) == (S.DISPONIVEL_PARA_RETOMAR, True)
    assert f.participacao is p


def test_uma_campanha_concluida_ja_concluida_nao_pendente():
    p = _concluida()
    f = _classificar(ConclusaoAcademica(), _campanhas(1), p)
    assert (f.situacao, f.situacao.pendente) == (S.JA_CONCLUIDA, False)
    assert f.participacao is p


@pytest.mark.parametrize("n", [2, 3])
@pytest.mark.parametrize("participacao", [None, _rascunho(), _concluida()])
def test_duas_ou_mais_campanhas_ambiguidade_nunca_desempatada_por_participacao(n, participacao):
    campanhas = _campanhas(n)
    f = _classificar(ConclusaoAcademica(), campanhas, participacao)
    assert (f.situacao, f.situacao.pendente) == (S.AMBIGUIDADE_OPERACIONAL, False)
    # A Participação recebida é descartada: o estado dela não resolve a ambiguidade.
    assert f.participacao is None
    assert f.campanha is None
    assert f.campanhas == campanhas  # todas, na ordem recebida (a da 004)


def test_pendente_so_para_as_duas_situacoes_disponiveis():
    assert {s for s in S if s.pendente} == {S.DISPONIVEL_PARA_INICIAR, S.DISPONIVEL_PARA_RETOMAR}


def _situacao(*situacoes):
    formacoes = tuple(_formacao(s) for s in situacoes)
    return formacoes, _resolver(formacoes)


def test_a_uma_pendente_resolucao_automatica():
    formacoes, resolucao = _situacao(S.DISPONIVEL_PARA_INICIAR)
    assert resolucao is R.ENTRADA_RESOLVIDA
    assert SituacaoDeEntrada(formacoes, resolucao).pendentes == formacoes


@pytest.mark.parametrize("pendente", [S.DISPONIVEL_PARA_INICIAR, S.DISPONIVEL_PARA_RETOMAR])
def test_b_concluida_mais_pendente_resolve_a_pendente(pendente):
    formacoes, resolucao = _situacao(S.JA_CONCLUIDA, pendente)
    situacao = SituacaoDeEntrada(formacoes, resolucao)
    assert resolucao is R.ENTRADA_RESOLVIDA
    assert situacao.pendentes == (formacoes[1],)


def test_c_ambigua_mais_pendente_resolve_a_pendente_e_preserva_a_ambiguidade():
    formacoes, resolucao = _situacao(S.AMBIGUIDADE_OPERACIONAL, S.DISPONIVEL_PARA_RETOMAR)
    situacao = SituacaoDeEntrada(formacoes, resolucao)
    assert resolucao is R.ENTRADA_RESOLVIDA
    assert situacao.pendentes == (formacoes[1],)
    assert situacao.formacoes[0].situacao is S.AMBIGUIDADE_OPERACIONAL


@pytest.mark.parametrize(
    "par",
    [
        (S.DISPONIVEL_PARA_INICIAR, S.DISPONIVEL_PARA_INICIAR),
        (S.DISPONIVEL_PARA_INICIAR, S.DISPONIVEL_PARA_RETOMAR),
        (S.DISPONIVEL_PARA_RETOMAR, S.DISPONIVEL_PARA_RETOMAR),
    ],
)
def test_d_duas_pendentes_selecao_necessaria(par):
    formacoes, resolucao = _situacao(*par)
    assert resolucao is R.SELECAO_NECESSARIA
    assert SituacaoDeEntrada(formacoes, resolucao).pendentes == formacoes


def test_e_todas_concluidas_sem_entrada_pendente():
    assert _situacao(S.JA_CONCLUIDA, S.JA_CONCLUIDA)[1] is R.SEM_ENTRADA_PENDENTE


def test_f_todas_sem_campanha_sem_pesquisa():
    assert _situacao(S.SEM_PESQUISA, S.SEM_PESQUISA)[1] is R.SEM_PESQUISA


def test_g_concluidas_e_ambiguas_sem_pendente_sem_entrada_pendente():
    assert _situacao(S.JA_CONCLUIDA, S.AMBIGUIDADE_OPERACIONAL)[1] is R.SEM_ENTRADA_PENDENTE


def test_nenhuma_formacao_sem_formacao():
    assert _resolver(()) is R.SEM_FORMACAO


@pytest.mark.parametrize(
    "situacoes",
    [
        (S.AMBIGUIDADE_OPERACIONAL, S.AMBIGUIDADE_OPERACIONAL),
        (S.JA_CONCLUIDA, S.SEM_PESQUISA),
        (S.AMBIGUIDADE_OPERACIONAL, S.SEM_PESQUISA),
        (S.JA_CONCLUIDA, S.AMBIGUIDADE_OPERACIONAL, S.SEM_PESQUISA),
    ],
)
def test_pesquisa_aplicavel_sem_pendente_sem_entrada_pendente(situacoes):
    assert _situacao(*situacoes)[1] is R.SEM_ENTRADA_PENDENTE


def test_concluidas_e_ambiguas_nao_aumentam_alternativas():
    formacoes, resolucao = _situacao(
        S.DISPONIVEL_PARA_INICIAR,
        S.JA_CONCLUIDA,
        S.AMBIGUIDADE_OPERACIONAL,
        S.DISPONIVEL_PARA_RETOMAR,
    )
    assert resolucao is R.SELECAO_NECESSARIA
    assert SituacaoDeEntrada(formacoes, resolucao).pendentes == (formacoes[0], formacoes[3])


def _esperada(situacoes) -> ResolucaoDaEntrada:
    """Oráculo independente, escrito a partir da tabela do data-model."""
    if not situacoes:
        return R.SEM_FORMACAO
    pendentes = sum(s.pendente for s in situacoes)
    if pendentes == 1:
        return R.ENTRADA_RESOLVIDA
    if pendentes >= 2:
        return R.SELECAO_NECESSARIA
    if all(s is S.SEM_PESQUISA for s in situacoes):
        return R.SEM_PESQUISA
    return R.SEM_ENTRADA_PENDENTE


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_resolucao_exaustiva_e_exclusiva_ate_tres_formacoes(n):
    for situacoes in combinations_with_replacement(list(S), n):
        for ordem in (situacoes, situacoes[::-1]):
            formacoes, resolucao = _situacao(*ordem)
            assert resolucao is _esperada(ordem), ordem
            assert isinstance(resolucao, ResolucaoDaEntrada)
            pendentes = SituacaoDeEntrada(formacoes, resolucao).pendentes
            assert pendentes == tuple(f for f in formacoes if f.situacao.pendente)


def test_valores_imutaveis():
    f = _formacao(S.SEM_PESQUISA)
    s = SituacaoDeEntrada((f,), R.SEM_PESQUISA)
    e = Entrada(s, None, False)
    for valor, campo in ((f, "situacao"), (s, "resolucao"), (e, "criada")):
        with pytest.raises(FrozenInstanceError):
            setattr(valor, campo, None)


# --- situacao_de_entrada: formações da Pessoa (US1) ----------------------------------------


NO_PERIODO = momento(2027, 5, 1)


@pytest.mark.django_db
def test_formacoes_sao_as_conclusoes_da_pessoa_sem_copia(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0004")
    pessoa = ce.pessoa_da_fonte("SIM-P-0004")
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    conclusoes = list(pessoa.conclusoes.all())
    assert len(situacao.formacoes) == 3
    assert [f.conclusao.pk for f in situacao.formacoes] == [x.pk for x in conclusoes]
    for f, conclusao in zip(situacao.formacoes, conclusoes, strict=True):
        assert isinstance(f.conclusao, ConclusaoAcademica)
        assert (f.conclusao.curso, f.conclusao.unidade, f.conclusao.ano_conclusao) == (
            conclusao.curso,
            conclusao.unidade,
            conclusao.ano_conclusao,
        )
    outra = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert [f.conclusao.pk for f in outra.formacoes] == [x.pk for x in conclusoes]


@pytest.mark.django_db
def test_todas_as_pessoas_dos_cenarios(fonte_simulada):
    ce.incorporar(fonte_simulada)
    ids = {p.id_externo for p in cenarios.PESSOAS}
    pessoas = Pessoa.objects.filter(fonte="simulada", id_externo__in=ids)
    assert pessoas.exists()
    for pessoa in pessoas:
        pks = [f.conclusao.pk for f in situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes]
        assert len(pks) == len(set(pks))
        assert set(pks) == set(pessoa.conclusoes.values_list("pk", flat=True))


@pytest.mark.django_db
def test_unidades_diferentes_lidas_de_cada_conclusao(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0003")
    pessoa = ce.pessoa_da_fonte("SIM-P-0003")
    formacoes = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert {f.conclusao.unidade for f in formacoes} == {"Serra", "Cefor"}
    nomes_academicos = {"curso", "unidade", "nivel", "modalidade", "forma_oferta", "campus"}
    assert not nomes_academicos & {campo.name for campo in Pessoa._meta.get_fields()}


@pytest.mark.django_db
def test_nao_informado_preservado(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0001")
    (formacao,) = situacao_de_entrada(ce.pessoa_da_fonte("SIM-P-0001"), agora=NO_PERIODO).formacoes
    assert formacao.conclusao.forma_oferta is None


@pytest.mark.django_db
def test_atributos_identicos_nao_fundem_formacoes(inst):
    pessoa = ce.pessoa()
    a = ce.formacao(pessoa, ano=2022, unidade="Serra")
    b = ce.formacao(pessoa, ano=2022, unidade="Serra")
    vazia = ConclusaoAcademica.objects.create(
        pessoa=pessoa, fonte="teste-entrada", id_externo="TE-C-VAZIA"
    )
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert {f.conclusao.pk for f in situacao.formacoes} == {a.pk, b.pk, vazia.pk}
    (sem_atributos,) = [f for f in situacao.formacoes if f.conclusao.pk == vazia.pk]
    atributos = ("curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao")
    assert all(getattr(sem_atributos.conclusao, n) is None for n in atributos)

    c.campanha_aberta(inst.versao, ano_minimo=2020)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SELECAO_NECESSARIA
    assert {f.conclusao.pk for f in situacao.pendentes} == {a.pk, b.pk}
    assert not hasattr(situacao.formacoes[0], "rotulo")


@pytest.mark.django_db
def test_sem_campanhas_sem_pesquisa(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0004")
    situacao = situacao_de_entrada(ce.pessoa_da_fonte("SIM-P-0004"), agora=NO_PERIODO)
    assert situacao.resolucao is R.SEM_PESQUISA
    assert {f.situacao for f in situacao.formacoes} == {S.SEM_PESQUISA}


@pytest.mark.django_db
def test_consulta_nao_grava(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0003", "SIM-P-0004")
    antes = ce.linhas()
    for id_externo in ("SIM-P-0003", "SIM-P-0004"):
        situacao_de_entrada(ce.pessoa_da_fonte(id_externo), agora=NO_PERIODO)
    assert ce.linhas() == antes


@pytest.mark.django_db
def test_erros_de_uso(fonte_simulada):
    ce.incorporar(fonte_simulada, "SIM-P-0001")
    pessoa = ce.pessoa_da_fonte("SIM-P-0001")
    with pytest.raises(TypeError):
        situacao_de_entrada(pessoa.conclusoes.first(), agora=NO_PERIODO)
    with pytest.raises(TypeError):
        situacao_de_entrada(pessoa, agora=date(2027, 5, 1))
    with pytest.raises(TypeError):
        situacao_de_entrada(pessoa, agora=NO_PERIODO.replace(tzinfo=None))
    with pytest.raises(ValueError):
        situacao_de_entrada(Pessoa(fonte="x", id_externo="y"), agora=NO_PERIODO)


# --- situacao_de_entrada: situação de cada formação (US2) ----------------------------------


def _mestrado(situacao):
    (f,) = [f for f in situacao.formacoes if f.conclusao.ano_conclusao == 2020]
    return f


@pytest.mark.django_db
def test_mestrado_iniciar_retomar_concluida(fonte_simulada, inst):
    ce.incorporar(fonte_simulada, "SIM-P-0004")
    pessoa = ce.pessoa_da_fonte("SIM-P-0004")
    campanha = c.campanha_aberta(inst.versao, ano_minimo=2020, ano_maximo=2020)

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    mestrado = _mestrado(situacao)
    assert (mestrado.situacao, mestrado.campanhas) == (S.DISPONIVEL_PARA_INICIAR, (campanha,))
    outras = [f for f in situacao.formacoes if f is not mestrado]
    assert {f.situacao for f in outras} == {S.SEM_PESQUISA}
    assert situacao.resolucao is R.ENTRADA_RESOLVIDA

    rascunho = ce.participacao_em_rascunho(campanha, mestrado.conclusao)
    antes = ce.linhas()
    mestrado = _mestrado(situacao_de_entrada(pessoa, agora=NO_PERIODO))
    assert (mestrado.situacao, mestrado.participacao) == (S.DISPONIVEL_PARA_RETOMAR, rascunho)
    assert ce.linhas() == antes

    concluida = ce.participacao_concluida(campanha, mestrado.conclusao, inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    mestrado = _mestrado(situacao)
    assert (mestrado.situacao, mestrado.participacao) == (S.JA_CONCLUIDA, concluida)
    assert mestrado.participacao.concluida_em == concluida.concluida_em
    assert situacao.resolucao is R.SEM_ENTRADA_PENDENTE


@pytest.mark.django_db
def test_campanha_em_preparacao_ou_encerrada_sem_pesquisa(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_em_preparacao(inst.versao)
    assert situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao is R.SEM_PESQUISA

    campanha = c.campanha_aberta(inst.versao)
    assert situacao_de_entrada(pessoa, agora=c.ULTIMO_DIA).resolucao is R.ENTRADA_RESOLVIDA
    assert situacao_de_entrada(pessoa, agora=c.DEPOIS_DO_FIM).resolucao is R.SEM_PESQUISA

    op_campanha.encerrar(campanha, agora=momento(2027, 5, 10))
    assert situacao_de_entrada(pessoa, agora=momento(2027, 5, 11)).resolucao is R.SEM_PESQUISA


@pytest.mark.django_db
def test_atributo_nao_informado_em_criterio_sem_pesquisa(inst):
    pessoa = ce.pessoa()
    conclusao = c.conclusao(pessoa=pessoa, unidade=None)
    c.campanha_aberta(inst.versao, unidades=["Serra"])
    (f,) = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert (f.conclusao.pk, f.situacao, f.campanhas, f.participacao) == (
        conclusao.pk,
        S.SEM_PESQUISA,
        (),
        None,
    )
    # Nada sobre critérios ou pendências da 004 é exposto.
    assert set(vars(f)) == {"conclusao", "situacao", "campanhas", "participacao"}


@pytest.mark.django_db
def test_participacao_de_campanha_anterior_nao_e_a_da_formacao(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    anterior = c.campanha_aberta(inst.versao)
    ce.participacao_concluida(anterior, conclusao, inst)
    nova = c.campanha_aberta(inst.versao, inicio=date(2030, 4, 1), fim=date(2030, 6, 30))
    (f,) = situacao_de_entrada(pessoa, agora=momento(2030, 5, 1)).formacoes
    assert (f.situacao, f.campanhas, f.participacao) == (
        S.DISPONIVEL_PARA_INICIAR,
        (nova,),
        None,
    )


@pytest.mark.django_db
def test_consultas_no_maximo_3_mais_n(inst, django_assert_max_num_queries):
    pessoa = ce.pessoa()
    conclusoes = [ce.formacao(pessoa, ano=ano) for ano in (2020, 2021, 2022)]
    campanha = c.campanha_aberta(inst.versao)
    ce.participacao_em_rascunho(campanha, conclusoes[0])
    with django_assert_max_num_queries(3 + len(conclusoes)):
        situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
        # Ler a situação e a Participação devolvidas não dispara consulta nova.
        [(f.situacao, f.participacao and f.participacao.concluida_em) for f in situacao.formacoes]
    assert situacao.resolucao is R.SELECAO_NECESSARIA


@pytest.mark.django_db
def test_classificacao_segue_so_a_004(inst, monkeypatch):
    pessoa = ce.pessoa()
    sem, uma, duas = (ce.formacao(pessoa, ano=ano) for ano in (2020, 2021, 2022))
    # Campanhas gravadas mas nunca abertas: só o dublê as torna "aplicáveis".
    c1 = c.campanha_em_preparacao(inst.versao)
    c2 = c.campanha_em_preparacao(inst.versao)
    devolve = {sem.pk: (), uma.pk: (c1,), duas.pk: (c1, c2)}
    chamadas = []

    def duble(conclusao, *, agora=None):
        chamadas.append((conclusao.pk, agora))
        return devolve[conclusao.pk]

    monkeypatch.setattr(modulo_entrada, "campanhas_em_coleta_para", duble)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert sorted(chamadas) == sorted((pk, NO_PERIODO) for pk in devolve)
    por_pk = {f.conclusao.pk: f for f in situacao.formacoes}
    assert por_pk[sem.pk].situacao is S.SEM_PESQUISA
    assert (por_pk[uma.pk].situacao, por_pk[uma.pk].campanhas) == (
        S.DISPONIVEL_PARA_INICIAR,
        (c1,),
    )
    assert (por_pk[duas.pk].situacao, por_pk[duas.pk].campanhas) == (
        S.AMBIGUIDADE_OPERACIONAL,
        (c1, c2),
    )

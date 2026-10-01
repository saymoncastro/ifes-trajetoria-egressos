"""Entrada na pesquisa (Feature 007): `entrar`, de ponta a ponta.

Casos S-A a S-L são os do solicitante (plan, "Estratégia de testes"); a correspondência
com os "Casos de referência" A–O da spec está nas Notes do tasks.md. Todo teste passa
`agora` explícito. Somente dados fictícios.
"""

import threading
from datetime import date

import pytest
from django.db import connection

from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.participacao import entrada as modulo_entrada
from trajetoria.participacao.consultas import admite_escrita, situacao_da_jornada
from trajetoria.participacao.entrada import (
    FormacaoDeOutraPessoa,
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    entrar,
    situacao_de_entrada,
)
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.participacao.operacoes import iniciar_participacao

pytestmark = pytest.mark.django_db

S = SituacaoDaFormacao
R = ResolucaoDaEntrada
NO_PERIODO = c.NO_PERIODO


def _registrar_inicio(monkeypatch):
    """Substitui `iniciar_participacao` em `entrada` por um registrador que delega à 005."""
    chamadas = []

    def registrador(campanha, conclusao, *, agora=None):
        chamadas.append((campanha.pk, conclusao.pk, agora))
        return iniciar_participacao(campanha, conclusao, agora=agora)

    monkeypatch.setattr(modulo_entrada, "iniciar_participacao", registrador)
    return chamadas


def _proibir_inicio(monkeypatch):
    def falha(*args, **kwargs):
        raise AssertionError("iniciar_participacao não deveria ser chamada")

    monkeypatch.setattr(modulo_entrada, "iniciar_participacao", falha)


def _par(participacao):
    return (participacao.campanha_id, participacao.conclusao_id)


# --- US3: resolução automática da única entrada pendente -----------------------------------


def test_s_a_uma_formacao_sem_participacao_inicia_sem_selecao(inst, monkeypatch):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    assert situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao is R.ENTRADA_RESOLVIDA

    chamadas = _registrar_inicio(monkeypatch)
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert entrada.criada is True
    assert _par(entrada.participacao) == (campanha.pk, conclusao.pk)
    assert chamadas == [(campanha.pk, conclusao.pk, NO_PERIODO)]
    assert Participacao.objects.count() == 1


def test_tres_formacoes_so_uma_aplicavel_resolvida(fonte_simulada, inst):
    ce.incorporar(fonte_simulada, "SIM-P-0004")
    pessoa = ce.pessoa_da_fonte("SIM-P-0004")
    campanha = c.campanha_aberta(inst.versao, ano_minimo=2020, ano_maximo=2020)
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert entrada.situacao.resolucao is R.ENTRADA_RESOLVIDA
    assert entrada.participacao.campanha_id == campanha.pk
    assert entrada.participacao.conclusao.ano_conclusao == 2020
    outras = [f for f in entrada.situacao.formacoes if f.conclusao.ano_conclusao != 2020]
    assert {f.situacao for f in outras} == {S.SEM_PESQUISA}


def test_s_d_concluida_mais_rascunho_retoma_o_rascunho(inst):
    pessoa = ce.pessoa()
    a, b = ce.formacao(pessoa, ano=2021), ce.formacao(pessoa, ano=2022)
    campanha = c.campanha_aberta(inst.versao)
    concluida = ce.participacao_concluida(campanha, a, inst)
    rascunho = ce.participacao_em_rascunho(campanha, b)
    antes_a = c.retrato(concluida)

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.ENTRADA_RESOLVIDA
    assert [f.conclusao.pk for f in situacao.pendentes] == [b.pk]
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert (entrada.participacao, entrada.criada) == (rascunho, False)
    (fa,) = [f for f in entrada.situacao.formacoes if f.conclusao.pk == a.pk]
    assert (fa.situacao, fa.participacao) == (S.JA_CONCLUIDA, concluida)
    assert c.retrato(concluida) == antes_a


def test_s_e_concluida_mais_sem_participacao_inicia_a_pendente(inst):
    pessoa = ce.pessoa()
    a, b = ce.formacao(pessoa, ano=2021), ce.formacao(pessoa, ano=2022)
    campanha = c.campanha_aberta(inst.versao)
    ce.participacao_concluida(campanha, a, inst)
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert entrada.criada is True
    assert _par(entrada.participacao) == (campanha.pk, b.pk)
    assert Participacao.objects.filter(conclusao=a).count() == 1


def _ambigua_e_pendente(inst):
    """A (Cefor) com duas Campanhas aplicáveis; B (Serra) com uma."""
    pessoa = ce.pessoa()
    a = ce.formacao(pessoa, ano=2021, unidade="Cefor")
    b = ce.formacao(pessoa, ano=2022, unidade="Serra")
    ampla = c.campanha_aberta(inst.versao)
    so_cefor = c.campanha_aberta(inst.versao, unidades=["Cefor"])
    return pessoa, a, b, ampla, so_cefor


def test_ambigua_mais_pendente_resolve_a_pendente_e_preserva_a_ambiguidade(inst):
    pessoa, a, b, ampla, so_cefor = _ambigua_e_pendente(inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.ENTRADA_RESOLVIDA
    assert [f.conclusao.pk for f in situacao.pendentes] == [b.pk]
    (fa,) = [f for f in situacao.formacoes if f.conclusao.pk == a.pk]
    assert (fa.situacao, set(fa.campanhas)) == (S.AMBIGUIDADE_OPERACIONAL, {ampla, so_cefor})

    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert _par(entrada.participacao) == (ampla.pk, b.pk)
    assert not Participacao.objects.filter(conclusao=a).exists()
    (fa,) = [f for f in entrada.situacao.formacoes if f.conclusao.pk == a.pk]
    assert fa.situacao is S.AMBIGUIDADE_OPERACIONAL


def test_informar_a_formacao_resolvida_da_o_mesmo_resultado(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    primeira = entrar(pessoa, conclusao, agora=NO_PERIODO)
    segunda = entrar(pessoa, agora=NO_PERIODO)
    assert primeira.participacao == segunda.participacao
    assert (primeira.criada, segunda.criada) == (True, False)


# --- US4: seleção necessária com múltiplas entradas pendentes -------------------------------


@pytest.mark.parametrize("rascunhos", [(), ("a",), ("a", "b")])
def test_s_f_duas_pendentes_exigem_selecao(inst, rascunhos):
    pessoa = ce.pessoa()
    formacoes = {"a": ce.formacao(pessoa, ano=2021), "b": ce.formacao(pessoa, ano=2022)}
    campanha = c.campanha_aberta(inst.versao)
    for nome in rascunhos:
        ce.participacao_em_rascunho(campanha, formacoes[nome])

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SELECAO_NECESSARIA
    assert [f.conclusao.pk for f in situacao.pendentes] == [
        formacoes["a"].pk,
        formacoes["b"].pk,
    ]
    antes = ce.linhas()
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert (entrada.participacao, entrada.criada) == (None, False)
    assert entrada.situacao.resolucao is R.SELECAO_NECESSARIA
    assert ce.linhas() == antes


def test_cada_formacao_informada_leva_a_sua_participacao(inst):
    pessoa = ce.pessoa()
    a, b = ce.formacao(pessoa, ano=2021), ce.formacao(pessoa, ano=2022)
    campanha = c.campanha_aberta(inst.versao)
    pa = entrar(pessoa, a, agora=NO_PERIODO).participacao
    pb = entrar(pessoa, b, agora=NO_PERIODO).participacao
    assert (_par(pa), _par(pb)) == ((campanha.pk, a.pk), (campanha.pk, b.pk))
    assert pa.pk != pb.pk


def test_pendentes_em_campanhas_diferentes_continuam_selecao(inst):
    pessoa = ce.pessoa()
    serra = ce.formacao(pessoa, ano=2021, unidade="Serra")
    cefor = ce.formacao(pessoa, ano=2022, unidade="Cefor")
    da_serra = c.campanha_aberta(inst.versao, unidades=["Serra"])
    do_cefor = c.campanha_aberta(inst.versao, unidades=["Cefor"])
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SELECAO_NECESSARIA
    assert _par(entrar(pessoa, serra, agora=NO_PERIODO).participacao) == (da_serra.pk, serra.pk)
    assert _par(entrar(pessoa, cefor, agora=NO_PERIODO).participacao) == (do_cefor.pk, cefor.pk)


def test_concluida_nao_aumenta_as_alternativas(inst):
    pessoa = ce.pessoa()
    a, b, z = (ce.formacao(pessoa, ano=ano) for ano in (2020, 2021, 2022))
    campanha = c.campanha_aberta(inst.versao)
    ce.participacao_concluida(campanha, z, inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SELECAO_NECESSARIA
    assert [f.conclusao.pk for f in situacao.pendentes] == [a.pk, b.pk]


def test_nenhuma_ordem_nova_alem_da_001(inst):
    pessoa = ce.pessoa()
    recente, antiga = ce.formacao(pessoa, ano=2024), ce.formacao(pessoa, ano=2010)
    c.campanha_aberta(inst.versao)
    pendentes = situacao_de_entrada(pessoa, agora=NO_PERIODO).pendentes
    ordem_001 = [c_.pk for c_ in pessoa.conclusoes.all()]
    assert [f.conclusao.pk for f in pendentes] == ordem_001 == [antiga.pk, recente.pk]


# --- US5: iniciar pela 005, sem Respostas ----------------------------------------------------


def test_participacao_iniciada_pela_005(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    p = entrar(pessoa, agora=NO_PERIODO).participacao
    assert (p.campanha_id, p.conclusao_id, p.iniciada_em, p.concluida_em) == (
        campanha.pk,
        conclusao.pk,
        NO_PERIODO,
        None,
    )


def test_s_l_dados_da_conclusao_nao_geram_resposta(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa, unidade="Serra")
    c.campanha_aberta(inst.versao)
    situacao_de_entrada(pessoa, agora=NO_PERIODO)
    entrada = entrar(pessoa, agora=NO_PERIODO)
    # Nem a Pergunta "campus" do instrumento de teste (análoga a Q11) recebe a unidade.
    assert not Resposta.objects.exists()
    campos = {f.name for f in Participacao._meta.concrete_fields}
    assert campos == {"id", "campanha", "conclusao", "iniciada_em", "concluida_em"}
    jornada = situacao_da_jornada(entrada.participacao, agora=NO_PERIODO)
    assert jornada.respostas == {}
    assert jornada.secao_atual.id == conteudo_da_versao(inst.versao).secoes[0].id


def test_entrada_repetida_uma_so_participacao(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    entradas = [entrar(pessoa, agora=NO_PERIODO) for _ in range(3)]
    assert Participacao.objects.count() == 1
    assert len({e.participacao.pk for e in entradas}) == 1
    assert [e.criada for e in entradas] == [True, False, False]


@pytest.mark.django_db(transaction=True)
def test_entradas_simultaneas_em_threads_uma_so_participacao(inst):
    # Opcional, como na 005/006: a garantia principal é a unicidade do par na 005.
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    barreira = threading.Barrier(2)
    resultados, erros = [], []

    def tentar():
        try:
            barreira.wait(timeout=10)
            resultados.append(entrar(pessoa, agora=NO_PERIODO))
        except Exception as erro:  # noqa: BLE001 — o teste exibe qualquer falha da thread
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=tentar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not erros
    assert Participacao.objects.count() == 1
    assert len({r.participacao.pk for r in resultados}) == 1
    assert sorted(r.criada for r in resultados) == [False, True]


# --- US6: retomar sem duplicar -----------------------------------------------------------------


def test_s_b_rascunho_retomado_sem_alteracao(inst):
    from trajetoria.participacao.operacoes import responder_texto

    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    rascunho = ce.participacao_em_rascunho(campanha, conclusao)
    responder_texto(rascunho, inst.texto, "27", agora=NO_PERIODO)
    antes = c.retrato(rascunho)

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    (f,) = situacao.formacoes
    assert (situacao.resolucao, f.situacao, f.participacao) == (
        R.ENTRADA_RESOLVIDA,
        S.DISPONIVEL_PARA_RETOMAR,
        rascunho,
    )
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert (entrada.participacao, entrada.criada) == (rascunho, False)
    assert c.retrato(rascunho) == antes


def test_participacao_criada_em_outra_requisicao_entre_consulta_e_entrada(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    (f,) = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert f.situacao is S.DISPONIVEL_PARA_INICIAR

    da_outra = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert (entrada.participacao, entrada.criada) == (da_outra, False)
    assert Participacao.objects.count() == 1


# --- US7: concluída é informação, não alternativa; nunca reaberta ----------------------------


def test_s_c_uma_formacao_concluida_sem_entrada_pendente(inst, monkeypatch):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    concluida = ce.participacao_concluida(campanha, conclusao, inst)
    antes = c.retrato(concluida)

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    (f,) = situacao.formacoes
    assert (situacao.resolucao, situacao.pendentes) == (R.SEM_ENTRADA_PENDENTE, ())
    assert (f.situacao, f.participacao) == (S.JA_CONCLUIDA, concluida)

    _proibir_inicio(monkeypatch)
    sem_formacao = entrar(pessoa, agora=NO_PERIODO)
    assert (sem_formacao.participacao, sem_formacao.criada) == (None, False)
    informada = entrar(pessoa, conclusao, agora=NO_PERIODO)
    assert (informada.participacao, informada.criada) == (concluida, False)
    assert informada.participacao.concluida_em == concluida.concluida_em
    assert c.retrato(concluida) == antes
    assert Participacao.objects.count() == 1


def test_todas_concluidas_sem_entrada_pendente_sem_selecao(fonte_simulada, inst):
    ce.incorporar(fonte_simulada, "SIM-P-0003")
    pessoa = ce.pessoa_da_fonte("SIM-P-0003")
    campanha = c.campanha_aberta(inst.versao)
    for conclusao in pessoa.conclusoes.all():
        ce.participacao_concluida(campanha, conclusao, inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert (situacao.resolucao, situacao.pendentes) == (R.SEM_ENTRADA_PENDENTE, ())
    assert {f.situacao for f in situacao.formacoes} == {S.JA_CONCLUIDA}


def test_concluida_nunca_e_reaberta(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    concluida = ce.participacao_concluida(campanha, conclusao, inst)
    antes = c.retrato(concluida)
    for _ in range(2):
        entrar(pessoa, agora=NO_PERIODO)
        entrar(pessoa, conclusao, agora=NO_PERIODO)
    assert c.retrato(concluida) == antes
    assert admite_escrita(concluida, agora=NO_PERIODO) is False
    assert not [n for n in modulo_entrada.__all__ if "reabr" in n.lower()]


def test_concluida_entre_a_avaliacao_e_o_inicio(inst, monkeypatch):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    rascunho = ce.participacao_em_rascunho(campanha, conclusao)
    anterior = situacao_de_entrada(pessoa, agora=NO_PERIODO)  # ainda em rascunho
    assert anterior.formacoes[0].situacao is S.DISPONIVEL_PARA_RETOMAR

    # Concluída "em outro dispositivo" depois de a entrada avaliar a situação.
    c.preencher_instrumento(rascunho, inst, NO_PERIODO)
    from trajetoria.participacao.operacoes import concluir

    concluida = concluir(rascunho, agora=NO_PERIODO).participacao
    antes = c.retrato(concluida)
    monkeypatch.setattr(modulo_entrada, "situacao_de_entrada", lambda *a, **k: anterior)

    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert entrada.participacao.pk == concluida.pk
    assert entrada.participacao.concluida_em == concluida.concluida_em
    assert entrada.criada is False
    assert c.retrato(concluida) == antes


# --- US8: Pessoa sem Conclusões ------------------------------------------------------------------


def test_s_h_pessoa_sem_conclusoes_sem_formacao(inst):
    pessoa = ce.pessoa()
    c.campanha_aberta(inst.versao)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert (situacao.resolucao, situacao.formacoes) == (R.SEM_FORMACAO, ())
    antes = ce.linhas()
    entrada = entrar(pessoa, agora=NO_PERIODO)
    assert (entrada.participacao, entrada.situacao.resolucao) == (None, R.SEM_FORMACAO)
    assert ce.linhas() == antes


def test_pessoa_nao_gravada_ou_removida_e_erro_de_uso():
    removida = ce.pessoa()
    Pessoa.objects.filter(pk=removida.pk).delete()
    for pessoa in (Pessoa(fonte="x", id_externo="nunca-gravada"), removida):
        with pytest.raises(ValueError):
            situacao_de_entrada(pessoa, agora=NO_PERIODO)
        with pytest.raises(ValueError):
            entrar(pessoa, agora=NO_PERIODO)


def test_conclusao_inelegivel_e_sem_pesquisa_nao_sem_formacao(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa, ano=2010)
    c.campanha_aberta(inst.versao, ano_minimo=2020)
    assert situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao is R.SEM_PESQUISA


# --- US9: formações sem pesquisa disponível --------------------------------------------


def test_s_g_formacoes_sem_campanha_sem_pesquisa(fonte_simulada, inst, monkeypatch):
    ce.incorporar(fonte_simulada, "SIM-P-0002")
    pessoa = ce.pessoa_da_fonte("SIM-P-0002")
    _proibir_inicio(monkeypatch)
    for criterio in ({}, {"unidades": ["Alegre"]}):
        if criterio:
            c.campanha_aberta(inst.versao, **criterio)
        situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
        assert situacao.resolucao is R.SEM_PESQUISA
        assert [f.situacao for f in situacao.formacoes] == [S.SEM_PESQUISA, S.SEM_PESQUISA]
        assert entrar(pessoa, agora=NO_PERIODO).participacao is None
        for f in situacao.formacoes:
            assert entrar(pessoa, f.conclusao, agora=NO_PERIODO).participacao is None
    assert not Participacao.objects.exists()


def test_rascunho_de_campanha_encerrada_nao_e_oferecido(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    antigo = ce.participacao_em_rascunho(campanha, conclusao)
    situacao = situacao_de_entrada(pessoa, agora=c.DEPOIS_DO_FIM)
    assert situacao.formacoes[0].situacao is S.SEM_PESQUISA
    entrada = entrar(pessoa, conclusao, agora=c.DEPOIS_DO_FIM)
    assert entrada.participacao is None
    assert Participacao.objects.filter(pk=antigo.pk).exists()


def test_campanha_encerrada_entre_consulta_e_entrada(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    assert situacao_de_entrada(pessoa, agora=NO_PERIODO).resolucao is R.ENTRADA_RESOLVIDA
    op_campanha.encerrar(campanha, agora=c.momento(2027, 5, 10))
    entrada = entrar(pessoa, agora=c.momento(2027, 5, 11))
    assert (entrada.participacao, entrada.situacao.resolucao) == (None, R.SEM_PESQUISA)
    assert not Participacao.objects.exists()


# --- US10: ambiguidade operacional local, nunca desempatada ----------------------------------


def _duas_campanhas_amplas(inst, *, invertidas=False):
    """Duas Campanhas de população ampla, ambas EM COLETA em NO_PERIODO."""
    cedo = dict(inicio=date(2027, 4, 1))
    tarde = dict(inicio=date(2027, 4, 20))
    if invertidas:
        segunda = c.campanha_aberta(inst.versao, **tarde)
        primeira = c.campanha_aberta(inst.versao, **cedo)
    else:
        primeira = c.campanha_aberta(inst.versao, **cedo)
        segunda = c.campanha_aberta(inst.versao, **tarde)
    return primeira, segunda


@pytest.mark.parametrize("invertidas", [False, True])
@pytest.mark.parametrize("existente", [None, "rascunho", "concluida"])
def test_s_i_campanha_sobreposta_nunca_escolhida(inst, monkeypatch, invertidas, existente):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    primeira, segunda = _duas_campanhas_amplas(inst, invertidas=invertidas)
    participacao = None
    if existente == "rascunho":
        participacao = ce.participacao_em_rascunho(segunda, conclusao)
    elif existente == "concluida":
        participacao = ce.participacao_concluida(segunda, conclusao, inst)
    antes = ce.linhas()

    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    (f,) = situacao.formacoes
    assert (f.situacao, f.campanhas, f.participacao) == (
        S.AMBIGUIDADE_OPERACIONAL,
        (primeira, segunda),  # ordem (inicio, id) da 004, sem preferência
        None,
    )
    assert (situacao.resolucao, situacao.pendentes) == (R.SEM_ENTRADA_PENDENTE, ())

    _proibir_inicio(monkeypatch)
    assert entrar(pessoa, agora=NO_PERIODO).participacao is None
    informada = entrar(pessoa, conclusao, agora=NO_PERIODO)
    assert (informada.participacao, informada.criada) == (None, False)
    assert informada.situacao.formacoes[0].situacao is S.AMBIGUIDADE_OPERACIONAL
    assert ce.linhas() == antes
    if participacao is not None:
        assert Participacao.objects.get(pk=participacao.pk) == participacao


def test_todas_ambiguas_sem_entrada_pendente(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa, ano=2021)
    ce.formacao(pessoa, ano=2022)
    _duas_campanhas_amplas(inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert (situacao.resolucao, situacao.pendentes) == (R.SEM_ENTRADA_PENDENTE, ())
    assert {f.situacao for f in situacao.formacoes} == {S.AMBIGUIDADE_OPERACIONAL}


def test_ambigua_mais_concluida_sem_entrada_pendente(inst):
    pessoa, a, b, ampla, _ = _ambigua_e_pendente(inst)
    ce.participacao_concluida(ampla, b, inst)
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SEM_ENTRADA_PENDENTE
    assert {f.situacao for f in situacao.formacoes} == {
        S.AMBIGUIDADE_OPERACIONAL,
        S.JA_CONCLUIDA,
    }


def test_ambigua_mais_duas_pendentes_selecao_entre_as_pendentes(inst, monkeypatch):
    pessoa, a, b, _, _ = _ambigua_e_pendente(inst)
    outra = ce.formacao(pessoa, ano=2023, unidade="Serra")
    situacao = situacao_de_entrada(pessoa, agora=NO_PERIODO)
    assert situacao.resolucao is R.SELECAO_NECESSARIA
    assert {f.conclusao.pk for f in situacao.pendentes} == {b.pk, outra.pk}
    _proibir_inicio(monkeypatch)
    assert entrar(pessoa, a, agora=NO_PERIODO).participacao is None


def test_nova_campanha_torna_a_formacao_ambigua_entre_consulta_e_entrada(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    (f,) = situacao_de_entrada(pessoa, agora=NO_PERIODO).formacoes
    assert f.situacao is S.DISPONIVEL_PARA_INICIAR

    c.campanha_aberta(inst.versao, inicio=date(2027, 4, 20))
    entrada = entrar(pessoa, conclusao, agora=NO_PERIODO)
    assert entrada.participacao is None
    assert entrada.situacao.formacoes[0].situacao is S.AMBIGUIDADE_OPERACIONAL
    assert not Participacao.objects.exists()


# --- US11: formação de outra Pessoa, proveniência e longitudinalidade ------------------------


def test_s_j_formacao_de_outra_pessoa_rejeitada_antes_da_005(fonte_simulada, inst, monkeypatch):
    ce.incorporar(fonte_simulada, "SIM-P-0010", "SIM-P-0011")
    pessoa = ce.pessoa_da_fonte("SIM-P-0010")
    alheia = ConclusaoAcademica.objects.get(fonte="simulada", id_externo="SIM-C-0013")
    c.campanha_aberta(inst.versao)  # a Conclusão alheia é elegível e EM COLETA
    _proibir_inicio(monkeypatch)
    antes = ce.linhas()

    with pytest.raises(FormacaoDeOutraPessoa) as erro:
        entrar(pessoa, alheia, agora=NO_PERIODO)

    mensagem = str(erro.value)
    dono = alheia.pessoa
    for dado in (
        alheia.curso,
        alheia.unidade,
        alheia.id_externo,
        str(alheia.pk),
        dono.nome,
        dono.id_externo,
        str(dono.pk),
    ):
        assert dado not in mensagem
    assert ce.linhas() == antes


def test_formacao_inexistente_indistinguivel_da_alheia(inst, monkeypatch):
    # A rejeição não revela se um identificador é Conclusão de outra Pessoa (FR-045).
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    alheia = ce.formacao(ce.pessoa())
    c.campanha_aberta(inst.versao)
    _proibir_inicio(monkeypatch)
    inexistente = ConclusaoAcademica(pessoa=pessoa, fonte="x", id_externo="y")
    mensagens = []
    for formacao in (alheia, inexistente):
        with pytest.raises(FormacaoDeOutraPessoa) as erro:
            entrar(pessoa, formacao, agora=NO_PERIODO)
        mensagens.append(str(erro.value))
    assert mensagens[0] == mensagens[1]
    assert not Participacao.objects.exists()


def test_formacao_de_tipo_errado_e_erro_de_uso(inst):
    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    c.campanha_aberta(inst.versao)
    with pytest.raises(TypeError):
        entrar(pessoa, pessoa, agora=NO_PERIODO)
    assert not Participacao.objects.exists()


def test_sem_agora_a_005_julga_no_proprio_instante(inst, monkeypatch):
    # Campanha encerrada entre a avaliação e o início: a 005, chamada sem `agora`, lê o
    # relógio de novo e rejeita, em vez de criar Participação julgada no instante antigo.
    from django.utils import timezone

    from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

    pessoa = ce.pessoa()
    ce.formacao(pessoa)
    campanha = c.campanha_aberta(inst.versao)
    relogio = {"agora": NO_PERIODO}
    monkeypatch.setattr(timezone, "now", lambda: relogio["agora"])
    chamadas = []

    def encerra_no_meio(campanha_, conclusao_, *, agora=None):
        chamadas.append(agora)
        op_campanha.encerrar(campanha, agora=c.momento(2027, 5, 1, 13))
        relogio["agora"] = c.momento(2027, 5, 1, 14)
        return iniciar_participacao(campanha_, conclusao_, agora=agora)

    monkeypatch.setattr(modulo_entrada, "iniciar_participacao", encerra_no_meio)
    with pytest.raises(ParticipacaoRejeitada) as erro:
        entrar(pessoa)
    assert chamadas == [None]
    assert erro.value.motivos == (Motivo.COLETA_NAO_ADMITIDA,)
    assert not Participacao.objects.exists()


def test_participacao_aponta_a_formacao_e_a_campanha_aplicavel(inst):
    pessoa = ce.pessoa()
    serra = ce.formacao(pessoa, ano=2021, unidade="Serra")
    ce.formacao(pessoa, ano=2022, unidade="Cefor")
    da_serra = c.campanha_aberta(inst.versao, unidades=["Serra"])
    c.campanha_aberta(inst.versao, unidades=["Cefor"])
    p = entrar(pessoa, serra, agora=NO_PERIODO).participacao
    assert (p.conclusao_id, p.campanha_id, p.pessoa) == (serra.pk, da_serra.pk, pessoa)


def test_s_k_mesma_conclusao_em_campanha_futura_nova_participacao(inst):
    pessoa = ce.pessoa()
    conclusao = ce.formacao(pessoa)
    de_2027 = c.campanha_aberta(inst.versao)
    anterior = ce.participacao_concluida(de_2027, conclusao, inst)
    antes = c.retrato(anterior)
    de_2030 = c.campanha_aberta(inst.versao, inicio=date(2030, 4, 1), fim=date(2030, 6, 30))
    em_2030 = c.momento(2030, 5, 1)

    (f,) = situacao_de_entrada(pessoa, agora=em_2030).formacoes
    assert (f.situacao, f.campanhas) == (S.DISPONIVEL_PARA_INICIAR, (de_2030,))
    entrada = entrar(pessoa, agora=em_2030)
    assert entrada.criada is True
    assert _par(entrada.participacao) == (de_2030.pk, conclusao.pk)
    assert c.retrato(anterior) == antes
    assert Participacao.objects.filter(conclusao=conclusao).count() == 2

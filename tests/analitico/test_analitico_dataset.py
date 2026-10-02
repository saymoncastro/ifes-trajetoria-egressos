"""Fronteira de leitura mínima do snapshot (US7, US12; spec FR-070 a FR-077; casos C a F, O)."""

import dataclasses
from types import MappingProxyType

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.analitico import construcao as c
from tests.participacao.construcao import (
    FIM,
    Q14,
    baseline_publicada,
    instrumento,
    opcao_de,
    pergunta_de,
    pergunta_mem,
    secao_mem,
    versao_publicada_de,
)
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.analitico.consultas import (
    ContextoCongelado,
    LinhaDoDataset,
    ParticipacaoNoDataset,
    RespostaNoDataset,
    linhas_do_dataset,
)
from trajetoria.analitico.models import RegistroDoSnapshot
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta, TipoPergunta
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import (
    responder_escolha_multipla,
    responder_escolha_unica,
)

pytestmark = pytest.mark.django_db

_PROIBIDOS = (Resposta, RespostaOpcao, Participacao, RegistroDoSnapshot, ConclusaoAcademica, Pessoa)


def _linhas(snapshot) -> dict:
    return {linha.conclusao_id: linha for linha in linhas_do_dataset(snapshot)}


def _valores(objeto):
    """Todos os valores alcançáveis a partir de um objeto entregue, inclusive aninhados."""
    if dataclasses.is_dataclass(objeto):
        for campo in dataclasses.fields(objeto):
            yield from _valores(getattr(objeto, campo.name))
    elif isinstance(objeto, (dict, MappingProxyType)):
        for valor in objeto.values():
            yield from _valores(valor)
    elif isinstance(objeto, (tuple, list, frozenset, set)):
        for valor in objeto:
            yield from _valores(valor)
    yield objeto


# --- Linhas e Participações -------------------------------------------------------------------


def test_uma_linha_por_registro_em_ordem_de_conclusao(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    linhas = list(linhas_do_dataset(snapshot))
    assert all(isinstance(linha, LinhaDoDataset) for linha in linhas)
    ids = [linha.conclusao_id for linha in linhas]
    assert ids == sorted(ids)
    assert set(ids) == set(snapshot.registros.values_list("conclusao_id", flat=True))


def test_concluida_normalmente(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_info.pk]
    assert isinstance(linha.participacao, ParticipacaoNoDataset)
    assert linha.participacao.concluida is True
    assert linha.participacao.id == cenario.concluida.pk
    gravadas = set(
        Resposta.objects.filter(participacao=cenario.concluida).values_list(
            "pergunta_id", flat=True
        )
    )
    assert set(linha.respostas) == gravadas
    assert linha.fora_do_percurso == frozenset()


def test_concluida_por_recusa(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.vitoria_info.pk]
    assert linha.participacao.concluida is True
    unica = cenario.inst.unica
    assert linha.respostas[unica.pk].opcao.texto == "Não"
    assert linha.fora_do_percurso == frozenset()


def test_rascunho_distingue_respostas_ativas_e_fora_do_percurso(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_eng.pk]
    posterior, unica = cenario.inst.posterior, cenario.inst.unica
    assert linha.participacao.concluida is False
    assert {posterior.pk, unica.pk} <= set(linha.respostas)
    assert linha.respostas[posterior.pk].texto == "comentário fictício"
    assert linha.fora_do_percurso == situacao_da_jornada(cenario.rascunho).fora_do_percurso
    assert posterior.pk in linha.fora_do_percurso  # preservada, inativa
    assert unica.pk not in linha.fora_do_percurso  # ativa no percurso


def test_rascunho_com_estrutura_nao_suportada_e_nao_determinavel(inst):
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": FIM}), pergunta_mem(regras={"Não": FIM}))
    )
    campanha = c.campanha_aberta_no_passado(versao)
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    pergunta = pergunta_de(versao, 1, 1)
    responder_escolha_unica(participacao, pergunta, opcao_de(pergunta, "Sim"), agora=c.na_coleta())
    linha = _linhas(capturar_snapshot(campanha))[conclusao.pk]
    assert linha.participacao.concluida is False
    assert linha.fora_do_percurso is None
    assert set(linha.respostas) == {pergunta.pk}


def test_elegivel_sem_participacao(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.vitoria_sem_atributos.pk]
    assert linha.participacao is None
    assert dict(linha.respostas) == {}
    assert linha.fora_do_percurso == frozenset()


# --- Respostas ---------------------------------------------------------------------------------


def test_respostas_sao_objetos_de_valor_com_os_valores_gravados(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_info.pk]
    gravadas = {
        r.pergunta_id: r
        for r in Resposta.objects.filter(participacao=cenario.concluida).select_related(
            "pergunta", "opcao"
        )
    }
    for pergunta_id, resposta in linha.respostas.items():
        assert isinstance(resposta, RespostaNoDataset)
        original = gravadas[pergunta_id]
        assert resposta.pergunta.pk == original.pergunta_id
        assert resposta.opcao_id == original.opcao_id
        assert (resposta.texto, resposta.escala, resposta.complemento) == (
            original.texto,
            original.escala,
            original.complemento,
        )


def test_escolha_multipla_e_a_tupla_das_opcoes_na_ordem_do_instrumento(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao)
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    opcoes = list(Opcao.objects.filter(pergunta=inst.multipla).order_by("-posicao")[:2])
    responder_escolha_multipla(participacao, inst.multipla, opcoes, agora=c.na_coleta())
    resposta = _linhas(capturar_snapshot(campanha))[conclusao.pk].respostas[inst.multipla.pk]
    assert isinstance(resposta.opcoes, tuple)
    assert [o.pk for o in resposta.opcoes] == [
        o.pk for o in sorted(opcoes, key=lambda o: o.posicao)
    ]
    assert resposta.opcao is None and resposta.opcao_id is None


def test_q14_declarada_fica_separada_do_nivel_congelado():
    base = baseline_publicada()
    campanha = c.campanha_aberta_no_passado(base.versao)
    conclusao = c.conclusao(unidade="Serra", nivel="Técnico")
    participacao = c.iniciada(campanha, conclusao)
    responder_escolha_unica(
        participacao, base.q(14), base.opcao(14, Q14["graduacao"]), agora=c.na_coleta()
    )
    linha = _linhas(capturar_snapshot(campanha))[conclusao.pk]
    assert linha.respostas[base.q(14).pk].opcao.texto == Q14["graduacao"]
    assert linha.contexto.nivel == "Técnico"


def test_pergunta_academica_declarada_fica_separada_da_unidade(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_info.pk]
    assert linha.respostas[cenario.inst.campus.pk].opcao.texto == "Campus Serra"
    assert linha.contexto.unidade == "Serra"


def test_respostas_associadas_a_versao_aplicada(cenario):
    for linha in linhas_do_dataset(capturar_snapshot(cenario.campanha)):
        for resposta in linha.respostas.values():
            assert resposta.pergunta.secao.versao_id == cenario.campanha.versao_id


# --- Sem estado atual, sem navegação, sem N+1, sem escrita ---------------------------------------


def test_contexto_e_o_congelado_e_a_001_nao_e_lida(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    c.simular_correcao(cenario.serra_info, unidade="Cefor", curso="Outro")  # simula 001/DP-005
    with CaptureQueriesContext(connection) as consultas:
        linhas = _linhas(snapshot)
    linha = linhas[cenario.serra_info.pk]
    assert isinstance(linha.contexto, ContextoCongelado)
    assert (linha.contexto.unidade, linha.contexto.curso) == ("Serra", "Técnico em Informática")
    sql = " ".join(q["sql"] for q in consultas.captured_queries)
    for tabela in (ConclusaoAcademica._meta.db_table, Pessoa._meta.db_table):
        assert tabela not in sql


def test_nenhum_objeto_entregue_leva_ao_estado_transacional(cenario):
    for linha in linhas_do_dataset(capturar_snapshot(cenario.campanha)):
        for valor in _valores(linha):
            assert not isinstance(valor, _PROIBIDOS), type(valor)
            if isinstance(valor, (Pergunta, Opcao)):
                # Sem acessor reverso (related_name="+" na 005): nada leva à Resposta.
                acessiveis = {
                    r.related_model for r in type(valor)._meta.related_objects if not r.hidden
                }
                assert not acessiveis & {Resposta, RespostaOpcao}


def _consultas_do_dataset(inst, n):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=[f"Dataset {n}"])
    for _ in range(n):
        c.concluida(campanha, c.conclusao(unidade=f"Dataset {n}"), inst)
    snapshot = capturar_snapshot(campanha)
    with CaptureQueriesContext(connection) as consultas:
        list(linhas_do_dataset(snapshot))
    return len(consultas)


def test_dataset_sem_consulta_por_linha(inst):
    assert _consultas_do_dataset(inst, 3) == _consultas_do_dataset(inst, 30)


def test_dataset_nao_grava_nada(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = c.contagens()
    list(linhas_do_dataset(snapshot))
    assert c.contagens() == antes


def test_tipo_de_pergunta_preservado(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_info.pk]
    assert linha.respostas[cenario.inst.escala.pk].pergunta.tipo == TipoPergunta.ESCALA
    assert linha.respostas[cenario.inst.escala.pk].escala == 3


def test_rascunho_com_respostas_incoerentes_nao_interrompe_a_leitura(cenario):
    # Resposta sem Opção na Pergunta com regra: só por escrita fora das operações (ADR 0002).
    snapshot = capturar_snapshot(cenario.campanha)
    Resposta.objects.filter(participacao=cenario.rascunho, pergunta=cenario.inst.unica).update(
        opcao=None
    )
    linhas = _linhas(snapshot)
    assert len(linhas) == len(cenario.elegiveis)  # todas as linhas, inclusive as seguintes
    rascunho = linhas[cenario.serra_eng.pk]
    assert rascunho.fora_do_percurso is None  # não determinável
    assert cenario.inst.posterior.pk in rascunho.respostas  # nada descartado
    assert linhas[cenario.serra_info.pk].participacao.concluida is True


# --- Perguntas do percurso (acréscimo da Feature 013, research R6) ------------------------------


def _secao(inst, posicao: int) -> set:
    return set(
        Pergunta.objects.filter(secao__versao=inst.versao, secao__posicao=posicao).values_list(
            "pk", flat=True
        )
    )


def test_perguntas_do_percurso_e_o_ultimo_campo_com_padrao_none():
    ultimo = dataclasses.fields(LinhaDoDataset)[-1]
    assert ultimo.name == "perguntas_do_percurso"
    assert ultimo.default is None


def test_perguntas_do_percurso_de_concluida(cenario):
    # "Sim" não tem regra: o percurso segue para a Seção 2 (opcional) e finaliza.
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_info.pk]
    inst = cenario.inst
    assert linha.perguntas_do_percurso == frozenset(_secao(inst, 1) | _secao(inst, 2))
    assert linha.fora_do_percurso == frozenset()  # inalterado


def test_perguntas_do_percurso_de_recusa(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.vitoria_info.pk]
    assert linha.perguntas_do_percurso == frozenset(_secao(cenario.inst, 1))


def test_perguntas_do_percurso_de_rascunho_exclui_as_fora_do_percurso(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.serra_eng.pk]
    posterior = cenario.inst.posterior.pk
    assert linha.perguntas_do_percurso == frozenset(_secao(cenario.inst, 1))
    assert posterior in linha.fora_do_percurso
    assert posterior not in linha.perguntas_do_percurso
    assert linha.fora_do_percurso == frozenset(linha.respostas) - linha.perguntas_do_percurso


def test_perguntas_do_percurso_sem_participacao(cenario):
    linha = _linhas(capturar_snapshot(cenario.campanha))[cenario.vitoria_sem_atributos.pk]
    assert linha.perguntas_do_percurso is None


def test_perguntas_do_percurso_com_estrutura_nao_suportada(inst):
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": FIM}), pergunta_mem(regras={"Não": FIM}))
    )
    campanha = c.campanha_aberta_no_passado(versao)
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    pergunta = pergunta_de(versao, 1, 1)
    responder_escolha_unica(participacao, pergunta, opcao_de(pergunta, "Sim"), agora=c.na_coleta())
    linha = _linhas(capturar_snapshot(campanha))[conclusao.pk]
    assert linha.perguntas_do_percurso is None
    assert linha.fora_do_percurso is None


def test_conteudo_ja_lido_e_reutilizado_sem_nova_leitura(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    conteudo = conteudo_da_versao(cenario.campanha.versao)
    with CaptureQueriesContext(connection) as sem:
        esperado = list(linhas_do_dataset(snapshot))
    with CaptureQueriesContext(connection) as com:
        reutilizado = list(linhas_do_dataset(snapshot, conteudo=conteudo))
    assert reutilizado == esperado
    assert len(com.captured_queries) < len(sem.captured_queries)
    assert not [q for q in com.captured_queries if "instrumento_secao" in q["sql"]]


def test_conteudo_de_outra_versao_e_recusado(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    with pytest.raises(ValueError):
        list(linhas_do_dataset(snapshot, conteudo=conteudo_da_versao(instrumento("outra").versao)))

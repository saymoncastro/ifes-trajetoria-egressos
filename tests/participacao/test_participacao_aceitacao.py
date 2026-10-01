"""Aceitação ponta a ponta: as 11 perguntas de sucesso do solicitante (spec, "Cobertura") e
o escopo da feature, verificado por app e por modelo, sem proibição global por nome
(research R16)."""

import pytest
from django.apps import apps

from tests.participacao import construcao as c
from tests.participacao.construcao import DEPOIS_DO_FIM, NO_PERIODO, momento
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.models import Campanha
from trajetoria.formulario_2024.materializacao import materializar
from trajetoria.instrumento.models import EstadoVersao, Opcao, Pergunta
from trajetoria.participacao import consultas, operacoes
from trajetoria.participacao.consultas import respostas_atuais
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import (
    SituacaoInicio,
    iniciar_participacao,
    remover_resposta,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo

pytestmark = pytest.mark.django_db


# --- As 11 perguntas de sucesso -----------------------------------------------------------


def test_1_conclusao_elegivel_inicia_participacao(campanha, conclusao):
    inicio = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)
    assert inicio.situacao is SituacaoInicio.CRIADA


def test_2_repetir_inicio_nao_cria_duplicata(campanha, conclusao):
    for _ in range(3):
        iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)
    assert Participacao.objects.filter(campanha=campanha, conclusao=conclusao).count() == 1


def test_3_mesma_conclusao_em_campanhas_diferentes(inst, conclusao):
    a, b = c.campanha_aberta(inst.versao), c.campanha_aberta(inst.versao)
    pa = iniciar_participacao(a, conclusao, agora=NO_PERIODO).participacao
    pb = iniciar_participacao(b, conclusao, agora=NO_PERIODO).participacao
    assert pa.id != pb.id


def test_4_quatro_tipos_representaveis(participacao, inst):
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
    )
    responder_escolha_multipla(
        participacao, inst.multipla, [inst.opcao(inst.multipla, "B")], agora=NO_PERIODO
    )
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    responder_escala(participacao, inst.escala, 2, agora=NO_PERIODO)
    atuais = respostas_atuais(participacao)
    assert atuais[inst.unica.id].opcao.texto == "Sim"
    assert [o.texto for o in atuais[inst.multipla.id].opcoes.all()] == ["B"]
    assert atuais[inst.texto.id].texto == "27"
    assert atuais[inst.escala.id].escala == 2


def test_5_valor_invalido_para_o_tipo_e_rejeitado(participacao, inst):
    c.rejeita(
        [Motivo.VALOR_INCOMPATIVEL],
        responder_escala,
        participacao,
        inst.escala,
        "5",
        agora=NO_PERIODO,
    )


def test_6_pergunta_ou_opcao_de_outra_versao_e_rejeitada(participacao, inst):
    inst28 = c.instrumento_derivado(inst)
    c.rejeita(
        [Motivo.PERGUNTA_DE_OUTRA_VERSAO],
        responder_texto,
        participacao,
        inst28.texto,
        "27",
        agora=NO_PERIODO,
    )
    c.rejeita(
        [Motivo.OPCAO_DE_OUTRA_PERGUNTA],
        responder_escolha_unica,
        participacao,
        inst.unica,
        inst28.opcao(inst28.unica, "Sim"),
        agora=NO_PERIODO,
    )


def test_7_rascunho_modificavel(participacao, inst):
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    responder_texto(participacao, inst.texto, "28", agora=NO_PERIODO)
    assert respostas_atuais(participacao)[inst.texto.id].texto == "28"
    remover_resposta(participacao, inst.texto, agora=NO_PERIODO)
    assert inst.texto.id not in respostas_atuais(participacao)


def test_8_declarado_e_institucional_distintos(campanha, inst):
    conclusao = c.conclusao(unidade="Serra")
    p = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    responder_escolha_unica(
        p, inst.campus, inst.opcao(inst.campus, "Campus Vitória"), agora=NO_PERIODO
    )
    assert ConclusaoAcademica.objects.get(pk=conclusao.pk).unidade == "Serra"
    assert respostas_atuais(p)[inst.campus.id].opcao.texto == "Campus Vitória"


def test_9_encerramento_impede_alteracoes(participacao, inst):
    responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
    c.rejeita(
        [Motivo.COLETA_NAO_ADMITIDA],
        responder_texto,
        participacao,
        inst.texto,
        "28",
        agora=DEPOIS_DO_FIM,
    )
    assert respostas_atuais(participacao)[inst.texto.id].texto == "27"


def test_10_nenhuma_jornada_ou_conclusao_antecipada():
    publicas = set(operacoes.__all__) | set(consultas.__all__)
    proibidas = ("concluir", "concluida", "submet", "progresso", "proxima", "obrigat", "naveg")
    assert not [n for n in publicas if any(p in n.lower() for p in proibidas)]
    for atributo in ("estado", "concluida_em", "submetida_em", "progresso"):
        assert not hasattr(Participacao, atributo)


def test_11_nenhuma_abstracao_generica_de_formulario():
    # Exatamente três modelos no app, com campos explícitos (sem JSON, tipo ou estado).
    assert {m.__name__ for m in apps.get_app_config("participacao").get_models()} == {
        "Participacao",
        "Resposta",
        "RespostaOpcao",
    }


# --- Escopo por app e por modelo --------------------------------------------------------------


def _campos(modelo) -> list[str]:
    return [f.name for f in modelo._meta.concrete_fields]


def test_campos_dos_modelos_novos():
    assert _campos(Participacao) == ["id", "campanha", "conclusao", "iniciada_em"]
    assert _campos(Resposta) == [
        "id",
        "participacao",
        "pergunta",
        "opcao",
        "texto",
        "escala",
        "complemento",
    ]
    assert _campos(RespostaOpcao) == ["id", "resposta", "opcao"]


def test_modelos_anteriores_sem_colunas_novas():
    assert _campos(Campanha) == [
        "id",
        "nome",
        "versao",
        "inicio",
        "fim",
        "ano_minimo",
        "ano_maximo",
        "unidades",
        "niveis",
        "modalidades",
        "formas_oferta",
        "aberta_em",
        "encerrada_em",
    ]
    assert _campos(ConclusaoAcademica) == [
        "id",
        "pessoa",
        "fonte",
        "id_externo",
        "curso",
        "unidade",
        "nivel",
        "modalidade",
        "forma_oferta",
        "ano_conclusao",
        "data_conclusao",
        "incorporado_em",
    ]
    assert _campos(Pergunta) == [
        "id",
        "secao",
        "posicao",
        "tipo",
        "texto",
        "texto_explicativo",
        "obrigatoria",
        "escala_inicio",
        "escala_fim",
        "escala_rotulo_inicio",
        "escala_rotulo_fim",
    ]
    assert _campos(Opcao) == [
        "id",
        "pergunta",
        "posicao",
        "texto",
        "complemento_textual",
        "regra_destino",
        "regra_finaliza",
    ]


def test_modelos_anteriores_sem_acesso_reverso():
    for modelo in (Campanha, ConclusaoAcademica, Pergunta, Opcao):
        relacionados = {
            f.related_model._meta.app_label
            for f in modelo._meta.get_fields()
            if f.is_relation and f.related_model is not None
        }
        assert "participacao" not in relacionados, modelo


def test_baseline_da_003_continua_rascunho(participacao):
    baseline = materializar().versao
    baseline.refresh_from_db()
    assert baseline.estado == EstadoVersao.RASCUNHO
    assert baseline.publicada_em is None


def test_uso_ao_longo_do_periodo(inst):
    """Ponta a ponta: início, escrita em datas diferentes do período, leitura após o fim."""
    campanha = c.campanha_aberta(inst.versao)
    conclusao = c.conclusao()
    p = iniciar_participacao(campanha, conclusao, agora=momento(2027, 4, 2)).participacao
    responder_texto(p, inst.texto, "27", agora=momento(2027, 4, 2))
    responder_texto(p, inst.texto, "28", agora=momento(2027, 6, 30))
    assert respostas_atuais(p)[inst.texto.id].texto == "28"
    assert p.iniciada_em == momento(2027, 4, 2)

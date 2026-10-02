"""Auxiliares dos testes do snapshot analítico (Feature 012; não são testes).

Somente dados fictícios. Conclusões por ORM (como nos testes da 004, 005 e 011); Campanhas,
Participações e Respostas pelas operações da 004, 005 e 006.

A captura lê o relógio real (research R8): as Campanhas a capturar têm a coleta **no
passado**, relativo a hoje, e as operações de coleta recebem `agora=na_coleta()`. As
constantes de 2027 de `tests/participacao/construcao.py` não servem para elas.

Imports de `trajetoria.analitico.*` ficam dentro das funções, para que este módulo importe
antes de os modelos existirem.
"""

from dataclasses import dataclass
from datetime import timedelta
from itertools import count

from tests.acompanhamento.construcao import campanha as campanha_011
from tests.acompanhamento.construcao import (
    conclusao,  # noqa: F401 — reexportado aos testes
    hoje,
    momento_em,
)
from tests.participacao.construcao import Instrumento, preencher_instrumento
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.models import Campanha
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import (
    concluir,
    iniciar_participacao,
    responder_escolha_unica,
    responder_texto,
)

_sequencia = count(1)


# --- Campanhas ----------------------------------------------------------------------------------


def na_coleta():
    """Instante dentro da coleta das Campanhas abertas no passado (hoje − 20 dias)."""
    return momento_em(hoje() - timedelta(days=20))


def campanha_aberta_no_passado(versao, *, fim_no_passado=True, **criterios):
    """Aberta em hoje − 30. Com `fim_no_passado`, o período termina em hoje − 5 e a Campanha
    já está ENCERRADA pelo fim do período; senão, termina em hoje + 30 e continua EM COLETA
    até `encerrar_no_passado`."""
    c = op_campanha.criar_campanha(f"Campanha analítica {next(_sequencia)}", versao)
    if criterios:
        op_campanha.definir_criterios(c, **criterios)
    d = hoje()
    fim = d - timedelta(days=5) if fim_no_passado else d + timedelta(days=30)
    op_campanha.definir_periodo(c, d - timedelta(days=40), fim)
    op_campanha.abrir(c, agora=momento_em(d - timedelta(days=30)))
    c.refresh_from_db()
    return c


def encerrar_no_passado(c):
    """Encerramento explícito em hoje − 10, depois da coleta de `na_coleta()`."""
    op_campanha.encerrar(c, agora=momento_em(hoje() - timedelta(days=10)))
    c.refresh_from_db()
    return c


def campanha_em_coleta(versao, **criterios):
    return campanha_011(versao, estado="em_coleta", **criterios)


def campanha_nunca_aberta(versao, *, expirada=False, **criterios):
    estado = "expirada_sem_abertura" if expirada else "em_preparacao"
    return campanha_011(versao, estado=estado, **criterios)


# --- Participações ------------------------------------------------------------------------------


def iniciada(c, conclusao_):
    return iniciar_participacao(c, conclusao_, agora=na_coleta()).participacao


def concluida(c, conclusao_, inst):
    participacao = iniciada(c, conclusao_)
    preencher_instrumento(participacao, inst, agora=na_coleta())
    return concluir(participacao, agora=na_coleta()).participacao


def concluida_por_recusa(c, conclusao_, inst):
    """Q1 = "Não" no instrumento de teste da 005 (regra de finalização); conta como
    concluída (011 FR-033; 006/DP-601)."""
    participacao = iniciada(c, conclusao_)
    preencher_instrumento(participacao, inst, agora=na_coleta())
    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=na_coleta()
    )
    return concluir(participacao, agora=na_coleta()).participacao


def rascunho_com_resposta_fora_do_percurso(c, conclusao_, inst):
    """ "Sim" leva à Seção 2; o Comentário da Seção 2 é respondido; depois "Não" finaliza na
    Seção 1, e o Comentário fica fora do percurso, preservado (006 FR-030, FR-033)."""
    participacao = iniciada(c, conclusao_)
    sim, nao = inst.opcao(inst.unica, "Sim"), inst.opcao(inst.unica, "Não")
    responder_escolha_unica(participacao, inst.unica, sim, agora=na_coleta())
    responder_texto(participacao, inst.posterior, "comentário fictício", agora=na_coleta())
    responder_escolha_unica(participacao, inst.unica, nao, agora=na_coleta())
    return participacao


# --- Simulação e comparação ---------------------------------------------------------------------


def simular_correcao(conclusao_, **atributos):
    """Simula 001/DP-005 (correção acadêmica futura) por escrita direta no teste. Nenhuma
    operação de produção de correção existe nem é criada (spec FR-132)."""
    ConclusaoAcademica.objects.filter(pk=conclusao_.pk).update(**atributos)


def retrato(snapshot) -> dict:
    """`{conclusao_id: (elegivel_no_snapshot, *contexto)}`, lido dos registros gravados."""
    from trajetoria.analitico.models import RegistroDoSnapshot

    linhas = RegistroDoSnapshot.objects.filter(snapshot=snapshot).values_list(
        "conclusao_id", "elegivel_no_snapshot", *CAMPOS_DE_CONTEXTO
    )
    return {conclusao_id: tuple(resto) for conclusao_id, *resto in linhas}


def contagens() -> dict:
    """Linhas de todas as tabelas do domínio, para provar que nada foi gravado."""
    from django.apps import apps

    modelos = [
        m
        for nome in ("academico", "campanha", "participacao", "instrumento", "analitico")
        for m in apps.get_app_config(nome).get_models()
    ]
    return {m._meta.label: m.objects.count() for m in modelos}


# --- Cenário de referência (compartilhado pelas Features 012 e 013) ----------------------------


@dataclass
class Cenario:
    inst: Instrumento
    campanha: Campanha
    serra_info: ConclusaoAcademica  # concluída
    vitoria_info: ConclusaoAcademica  # concluída por recusa; curso homônimo
    serra_eng: ConclusaoAcademica  # rascunho com Resposta fora do percurso
    vitoria_sem_atributos: ConclusaoAcademica  # elegível sem Participação
    serra_sem_participacao: ConclusaoAcademica  # elegível sem Participação
    cefor: ConclusaoAcademica  # fora do critério
    sem_unidade: ConclusaoAcademica  # fora do critério
    concluida: Participacao
    recusa: Participacao
    rascunho: Participacao

    @property
    def elegiveis(self):
        return {
            self.serra_info.pk,
            self.vitoria_info.pk,
            self.serra_eng.pk,
            self.vitoria_sem_atributos.pk,
            self.serra_sem_participacao.pk,
        }


def cenario_de_referencia(inst) -> Cenario:
    campanha = campanha_aberta_no_passado(inst.versao, unidades=["Serra", "Vitória"])
    serra_info = conclusao(
        unidade="Serra",
        curso="Técnico em Informática",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Subsequente",
        ano=2022,
    )
    vitoria_info = conclusao(
        unidade="Vitória",
        curso="Técnico em Informática",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Integrado",
        ano=2021,
    )
    serra_eng = conclusao(
        unidade="Serra", curso="Engenharia", nivel="Graduação", modalidade="Presencial", ano=2020
    )
    vitoria_sem_atributos = conclusao(unidade="Vitória")
    serra_sem_participacao = conclusao(unidade="Serra", curso="Engenharia", ano=2022)
    cefor = conclusao(unidade="Cefor", curso="Especialização", ano=2022)
    sem_unidade = conclusao(curso="Técnico em Informática", ano=2022)
    return Cenario(
        inst=inst,
        campanha=campanha,
        serra_info=serra_info,
        vitoria_info=vitoria_info,
        serra_eng=serra_eng,
        vitoria_sem_atributos=vitoria_sem_atributos,
        serra_sem_participacao=serra_sem_participacao,
        cefor=cefor,
        sem_unidade=sem_unidade,
        concluida=concluida(campanha, serra_info, inst),
        recusa=concluida_por_recusa(campanha, vitoria_info, inst),
        rascunho=rascunho_com_resposta_fora_do_percurso(campanha, serra_eng, inst),
    )

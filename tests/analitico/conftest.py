"""Cenário de referência fictício do snapshot analítico (spec, "Dados de referência").

Campanha E: critério de unidades {Serra, Vitória}, aberta no passado e já ENCERRADA pelo fim
do período. Universo esperado: as cinco Conclusões de Serra e Vitória (elegíveis); Cefor e
"sem unidade" ficam fora (não elegíveis e sem Participação).
"""

from dataclasses import dataclass

import pytest

from tests.analitico import construcao as c
from tests.participacao.construcao import Instrumento, instrumento
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.models import Campanha
from trajetoria.participacao.models import Participacao


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


@pytest.fixture
def inst():
    return instrumento()


@pytest.fixture
def cenario(inst) -> Cenario:
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra", "Vitória"])
    serra_info = c.conclusao(
        unidade="Serra",
        curso="Técnico em Informática",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Subsequente",
        ano=2022,
    )
    vitoria_info = c.conclusao(
        unidade="Vitória",
        curso="Técnico em Informática",
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Integrado",
        ano=2021,
    )
    serra_eng = c.conclusao(
        unidade="Serra", curso="Engenharia", nivel="Graduação", modalidade="Presencial", ano=2020
    )
    vitoria_sem_atributos = c.conclusao(unidade="Vitória")
    serra_sem_participacao = c.conclusao(unidade="Serra", curso="Engenharia", ano=2022)
    cefor = c.conclusao(unidade="Cefor", curso="Especialização", ano=2022)
    sem_unidade = c.conclusao(curso="Técnico em Informática", ano=2022)
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
        concluida=c.concluida(campanha, serra_info, inst),
        recusa=c.concluida_por_recusa(campanha, vitoria_info, inst),
        rascunho=c.rascunho_com_resposta_fora_do_percurso(campanha, serra_eng, inst),
    )


@pytest.fixture
def campanha_v(inst):
    """Encerrada, sem Participações, com elegíveis."""
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Cefor"])
    c.conclusao(unidade="Cefor", ano=2020)
    c.conclusao(unidade="Cefor", ano=2021)
    return campanha


@pytest.fixture
def campanha_c(inst):
    return c.campanha_em_coleta(inst.versao)


@pytest.fixture
def campanha_p(inst):
    return c.campanha_nunca_aberta(inst.versao)


@pytest.fixture
def campanha_x(inst):
    return c.campanha_nunca_aberta(inst.versao, expirada=True)

"""Fixtures dos testes do acompanhamento da coleta (Feature 011).

O acompanhamento só existe no modo de demonstração; aqui ele fica ligado por padrão, e o teste
que verifica o modo desligado o desliga explicitamente.

**Cenário de referência** (`ref`), somente fictício:

| Conclusão | Unidade | Curso | Nível | Modalidade | Forma | Ano |
|-----------|---------|-------|-------|------------|-------|-----|
| s1 | Serra | Técnico em Informática | Técnico | Presencial | Integrado | 2020 |
| s2 | Serra | Técnico em Informática | Técnico | Presencial | Subsequente | 2021 |
| s3 | Serra | TADS | Graduação | Presencial | — | 2022 |
| v1 | Vitória | Técnico em Informática | Técnico | Presencial | Integrado | 2019 |
| v2 | Vitória | Engenharia Civil | graduação | Presencial | — | 2020 |
| c1 | Cefor | Especialização em Informática na Educação | Pós-graduação | A distância | — | 2023 |
| n1 | — | — | — | — | — | — |

Campanhas: **I** (em coleta, sem critério), **R** (em coleta, unidades Serra e Cefor), **P**
(em preparação, Versão em rascunho), **E** (encerrada explicitamente).

Participações em I: s1 iniciada (com texto declarado fictício), s2 concluída, v1 concluída
por recusa (Q1 = "Não"), n1 iniciada. Totais de I: 7 elegíveis, 4 iniciadas, 2 concluídas.
"""

from types import SimpleNamespace

import pytest
from django.test import Client

from tests.acompanhamento import construcao as k
from tests.campanha.construcao import versao_rascunho
from tests.participacao.construcao import instrumento
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

TEXTO_DECLARADO = "RESPOSTA-DECLARADA-FICTICIA-011"
TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
TI = "Técnico em Informática"


@pytest.fixture(autouse=True)
def modo_demonstracao(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


@pytest.fixture
def inst(db):
    return instrumento()


@pytest.fixture
def ref(inst):
    c = k.conclusao
    conclusoes = {
        "s1": c(unidade="Serra", curso=TI, nivel="Técnico", modalidade="Presencial",
                forma_oferta="Integrado", ano=2020),
        "s2": c(unidade="Serra", curso=TI, nivel="Técnico", modalidade="Presencial",
                forma_oferta="Subsequente", ano=2021),
        "s3": c(unidade="Serra", curso=TADS, nivel="Graduação", modalidade="Presencial",
                ano=2022),
        "v1": c(unidade="Vitória", curso=TI, nivel="Técnico", modalidade="Presencial",
                forma_oferta="Integrado", ano=2019),
        "v2": c(unidade="Vitória", curso="Engenharia Civil", nivel="graduação",
                modalidade="Presencial", ano=2020),
        "c1": c(unidade="Cefor", curso="Especialização em Informática na Educação",
                nivel="Pós-graduação", modalidade="A distância", ano=2023),
        "n1": c(),
    }  # fmt: skip
    I = k.campanha(inst.versao, nome="Campanha I")  # noqa: E741
    R = k.campanha(inst.versao, nome="Campanha R", unidades=["Serra", "Cefor"])
    P = k.campanha(versao_rascunho("Rascunho de teste"), estado="em_preparacao", nome="Campanha P")
    E = k.campanha(inst.versao, estado="encerrada_explicita", nome="Campanha E")
    participacoes = {
        "s1": k.com_texto_declarado(k.iniciada(I, conclusoes["s1"]), inst, TEXTO_DECLARADO),
        "s2": k.concluida(I, conclusoes["s2"], inst),
        "v1": k.concluida_por_recusa(I, conclusoes["v1"], inst),
        "n1": k.iniciada(I, conclusoes["n1"]),
    }
    return SimpleNamespace(I=I, R=R, P=P, E=E, inst=inst, **conclusoes, participacoes=participacoes)


def _cliente(identificador, *vinculos):
    for papel, unidade in vinculos:
        registrar_vinculo(identificador, papel, unidade)
    return k.atuar_como(Client(), identificador)


@pytest.fixture
def cliente_cpaeg(db):
    return _cliente(k.A, (Papel.CPAEG, ""))


@pytest.fixture
def cliente_csaeg_vitoria(db):
    return _cliente(k.B, (Papel.CSAEG, "Vitória"))


@pytest.fixture
def cliente_csaeg_serra(db):
    return _cliente(k.B, (Papel.CSAEG, "Serra"))


@pytest.fixture
def cliente_duas_csaeg(db):
    return _cliente(k.B, (Papel.CSAEG, "Serra"), (Papel.CSAEG, "Vitória"))


@pytest.fixture
def cliente_cpaeg_e_csaeg(db):
    return _cliente(k.A, (Papel.CPAEG, ""), (Papel.CSAEG, "Serra"))


@pytest.fixture
def cliente_sem_vinculo(db):
    return k.atuar_como(Client(), k.C)


@pytest.fixture
def cliente_nao_identificado(db):
    return Client()

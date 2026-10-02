"""Indicadores derivados, não persistidos; nenhuma Resposta lida; proteção contra N+1
(Feature 011; US6; spec FR-001, FR-070 a FR-073, FR-090; SC-007 a SC-009)."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.acompanhamento import construcao as k
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha.models import Campanha
from trajetoria.governanca.models import VinculoDeGovernanca
from trajetoria.instrumento.models import Versao
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao

RECORTES = ("unidade", "curso", "nivel", "modalidade", "forma-oferta", "ano-conclusao")
MODELOS = (
    Pessoa, ConclusaoAcademica, Campanha, Versao, Participacao, Resposta, RespostaOpcao,
    VinculoDeGovernanca,
)  # fmt: skip


def _todas_as_paginas(cliente, ref):
    respostas = [cliente.get("/acompanhamento/")]
    for campanha in (ref.I, ref.R, ref.P, ref.E):
        respostas += [k.detalhe(cliente, campanha, r) for r in RECORTES]
    return respostas


def _linhas():
    return {
        m.__name__: list(m.objects.order_by("pk").values_list("pk", flat=True)) for m in MODELOS
    }


@pytest.mark.parametrize("perfil", ["cliente_cpaeg", "cliente_duas_csaeg"])
def test_nenhuma_escrita(ref, perfil, request):
    cliente = request.getfixturevalue(perfil)
    antes = _linhas()
    retrato = list(Participacao.objects.order_by("pk").values())
    with CaptureQueriesContext(connection) as capturadas:
        _todas_as_paginas(cliente, ref)
    assert _linhas() == antes
    assert list(Participacao.objects.order_by("pk").values()) == retrato
    escritas = ("INSERT", "UPDATE", "DELETE")
    assert not [q["sql"] for q in capturadas if q["sql"].lstrip().upper().startswith(escritas)]


@pytest.mark.parametrize("perfil", ["cliente_cpaeg", "cliente_csaeg_vitoria"])
def test_nenhuma_resposta_consultada(ref, perfil, request):
    cliente = request.getfixturevalue(perfil)
    with CaptureQueriesContext(connection) as capturadas:
        respostas = _todas_as_paginas(cliente, ref)
    assert all(r.status_code in (200, 403) for r in respostas)
    for consulta in capturadas:
        assert "participacao_resposta" not in consulta["sql"], consulta["sql"]


def _consultas(cliente, endereco):
    with CaptureQueriesContext(connection) as capturadas:
        assert cliente.get(endereco).status_code == 200
    return len(capturadas)


def test_detalhe_sem_n_mais_1_por_linha_de_recorte(inst, cliente_cpaeg):
    """Protege o desenho atual contra N+1; não é contrato da spec."""
    campanha = k.campanha(inst.versao)
    endereco = f"/acompanhamento/campanhas/{campanha.pk}/?recorte=curso"
    for i in range(3):
        k.iniciada(campanha, k.conclusao(unidade="Serra", curso=f"Curso {i}", ano=2020))
    com_tres = _consultas(cliente_cpaeg, endereco)
    for i in range(3, 30):
        k.iniciada(campanha, k.conclusao(unidade="Serra", curso=f"Curso {i}", ano=2020))
    assert _consultas(cliente_cpaeg, endereco) == com_tres


def test_detalhe_busca_a_campanha_uma_vez(ref, cliente_cpaeg):
    """Regressão do code review: a Campanha visível é obtida numa só consulta; a verificação
    de existência só ocorre quando ela não é visível."""
    with CaptureQueriesContext(connection) as capturadas:
        assert k.detalhe(cliente_cpaeg, ref.I).status_code == 200
    de_campanha = [q for q in capturadas if q["sql"].lstrip().startswith("SELECT") and
                   'FROM "campanha_campanha"' in q["sql"]]  # fmt: skip
    assert len(de_campanha) == 1


def test_um_so_agora_por_requisicao(ref, cliente_cpaeg, monkeypatch):
    """Regressão do code review: o estado das Campanhas e o momento exibido usam o mesmo
    relógio lido uma vez na view."""
    from django.utils import timezone as tz

    from trajetoria.acompanhamento import views

    leituras = []
    original = tz.now

    def contar():
        leituras.append(1)
        return original()

    monkeypatch.setattr(views.timezone, "now", contar)
    for resposta in (cliente_cpaeg.get("/acompanhamento/"), k.detalhe(cliente_cpaeg, ref.I)):
        assert resposta.status_code == 200
    assert len(leituras) == 2


def test_lista_proporcional_ao_numero_de_campanhas(inst, cliente_cpaeg):
    """Protege o desenho atual contra N+1; não é contrato da spec. Cada Campanha custa no máximo
    duas consultas; nenhuma consulta por Conclusão ou Participação."""
    primeira = k.campanha(inst.versao)
    for _ in range(5):
        k.iniciada(primeira, k.conclusao(unidade="Serra", ano=2020))
    com_uma = _consultas(cliente_cpaeg, "/acompanhamento/")
    k.campanha(inst.versao)
    k.campanha(inst.versao)
    assert _consultas(cliente_cpaeg, "/acompanhamento/") <= com_uma + 2 * 2

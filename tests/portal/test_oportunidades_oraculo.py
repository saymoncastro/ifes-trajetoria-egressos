"""Oráculo por persona (025 SC-002; contracts/pertinencia.md; T031).

Prepara a demonstração de verdade (o catálogo entra pelo sinal do cenário) com D fixo pelo
relógio dos testes e compara, para cada persona, a página e o destaque do Início com a
tabela escrita antes da implementação.
"""

import html as html_lib
import re
from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command

from tests.portal import construcao as cp
from trajetoria.academico.models import Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db

O1 = "Curso de extensão a distância em Ciência de Dados"
O2 = "Especialização em Segurança da Informação"
O3 = "Mestrado Profissional em Educação: seleção aberta"
O4 = "Encontro de egressos das engenharias e edificações"
O6 = "Programa de estágio em laboratórios parceiros"
O7 = "Feira de empreendedorismo e inovação"
TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
TODOS = ("Para todos os egressos", [(O1, "Aberta a todos os egressos do Ifes.")])

ORACULO = {
    "SIM-P-0001": ([("Pela sua formação", [
        (O2, f"Aparece porque você concluiu {TADS} (Serra, 2022)."),
    ]), TODOS], O2),
    "SIM-P-0002": ([("Pela sua formação", [
        (O4, "Aparece porque você concluiu Técnico em Edificações na unidade Vitória (2014) e "
             "Bacharelado em Engenharia Civil na unidade Vitória (2020)."),
    ]), TODOS], O4),
    "SIM-P-0003": ([("Pela sua formação", [
        (O2, f"Aparece porque você concluiu {TADS} (Serra, 2022)."),
        (O3, "Aparece porque você concluiu Especialização em Informática na Educação, formação "
             "de Pós-graduação (Cefor, 2025)."),
    ]), TODOS], O2),
    "SIM-P-0004": ([("Pela sua formação", [
        (O6, "Aparece porque você concluiu Técnico em Química, formação de Técnico na unidade "
             "Vila Velha (2012)."),
        (O3, "Aparece porque você concluiu Mestrado Profissional em Química, formação de "
             "Pós-graduação (Vila Velha, 2020)."),
    ]), TODOS], O6),
    "SIM-P-0007": ([TODOS], O1),
    "SIM-P-0010": ([("Pela sua formação", [
        (O4, "Aparece porque você concluiu Licenciatura em Pedagogia na unidade Vitória (2016)."),
    ]), TODOS], O4),
    "SIM-P-0011": ([("Pela sua formação", [
        (O2, "Aparece porque você concluiu Tecnologia em Redes de Computadores (Serra, 2023)."),
    ]), TODOS], O2),
}


@pytest.fixture
def demonstracao():
    call_command("preparar_demonstracao", stdout=StringIO())


def _pessoa(id_externo):
    return Pessoa.objects.get(fonte=FonteSimulada.codigo, id_externo=id_externo)


def _texto(fragmento: str) -> str:
    return html_lib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragmento))).strip()


def _grupos(pagina: str):
    grupos = []
    for secao in re.findall(r'<section class="oportunidades-grupo".*?</section>', pagina, re.S):
        titulo = _texto(re.search(r"<h2[^>]*>(.*?)</h2>", secao, re.S).group(1))
        itens = [
            (_texto(t), _texto(e))
            for t, e in re.findall(
                r'<h3 class="oportunidade-titulo"><a [^>]*>(.*?)<span.*?'
                r'<p class="oportunidade-por-que">(.*?)</p>', secao, re.S,
            )
        ]
        grupos.append((titulo, itens))
    return grupos


def _destaque(inicio: str) -> str | None:
    achado = re.search(
        r'<section class="inicio-oportunidades.*?'
        r'<p class="oportunidade-titulo"><a [^>]*>(.*?)<span',
        inicio, re.S,
    )
    return _texto(achado.group(1)) if achado else None


@pytest.mark.parametrize("id_externo", sorted(ORACULO))
def test_pagina_e_destaque_por_persona(client, demonstracao, id_externo):
    grupos, destaque = ORACULO[id_externo]
    cp.entrar(client, _pessoa(id_externo))
    pagina = client.get("/oportunidades/").content.decode()
    assert _grupos(pagina) == grupos
    assert _destaque(client.get("/inicio/").content.decode()) == destaque
    for invisivel in ("Ciclo de palestras", "Curso livre de fotografia", "Oficina de currículo",
                      O7, "Programa de mentoria"):
        assert invisivel not in pagina


def test_em_d_mais_11_entra_o7_e_em_d_mais_61_sai_o1(client, demonstracao, relogio):
    ana = _pessoa("SIM-P-0001")
    relogio.agora += timedelta(days=11)
    cp.entrar(client, ana)
    todos = dict(_grupos(client.get("/oportunidades/").content.decode()))["Para todos os egressos"]
    assert [t for t, _ in todos] == [O7, O1]
    relogio.agora += timedelta(days=50)
    cp.entrar(client, ana)
    todos = dict(_grupos(client.get("/oportunidades/").content.decode())).get(
        "Para todos os egressos", [])
    assert O1 not in [t for t, _ in todos]


def test_preparo_idempotente(demonstracao):
    from trajetoria.portal.models import Oportunidade

    antes = Oportunidade.objects.count()
    call_command("preparar_demonstracao", stdout=StringIO())
    assert antes == 10 and Oportunidade.objects.count() == 10


def test_catalogo_recusado_desfaz_o_preparo_e_orienta(monkeypatch):
    """Recusa de uma operação do catálogo: o comando termina com a mensagem orientada do
    preparo (não com traceback) e nada fica gravado (code review do PR #49)."""
    from django.core.management.base import CommandError

    from trajetoria.portal.models import Oportunidade
    from trajetoria.portal.oportunidades import demonstracao as catalogo

    monkeypatch.setattr(catalogo, "_DOMINIO", "http://oportunidades.example/")
    with pytest.raises(CommandError, match="catálogo de oportunidades.*Recrie o banco local"):
        call_command("preparar_demonstracao", stdout=StringIO())
    assert not Oportunidade.objects.exists() and not Pessoa.objects.exists()

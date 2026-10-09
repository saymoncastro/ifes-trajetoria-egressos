"""Auxiliares dos testes da Feature 025 (não são testes). As oportunidades são criadas só
pelas operações, como o catálogo da demonstração."""

from datetime import timedelta

from django.utils import timezone

from tests.participacao import construcao as c
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.portal.oportunidades import operacoes

OPERADOR_A = "demonstracao:operador-a"
OPERADOR_B = "demonstracao:operador-b"
ESCOPO_A = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
ESCOPO_B = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vitória"}))
HOJE = timezone.localdate(c.NO_PERIODO)
ENDERECO = "https://oportunidades.example/teste"


def dados(titulo="Oportunidade de teste", **extra) -> dict:
    base = {
        "titulo": titulo, "resumo": "Resumo de teste.", "categoria": "cursos",
        "unidade_responsavel": "", "endereco": ENDERECO,
        "inicio": HOJE - timedelta(days=1), "fim": HOJE + timedelta(days=30),
    }
    return {**base, **extra}


def rascunho(titulo="Oportunidade de teste", *, escopo=ESCOPO_A, operador=OPERADOR_A, **extra):
    return operacoes.cadastrar(dados(titulo, **extra), operador=operador, escopo=escopo, hoje=HOJE)


def publicada(titulo="Oportunidade de teste", *, escopo=ESCOPO_A, operador=OPERADOR_A, **extra):
    oportunidade = rascunho(titulo, escopo=escopo, operador=operador, **extra)
    return operacoes.publicar(oportunidade.pk, operador=operador, escopo=escopo,
                              agora=c.NO_PERIODO)

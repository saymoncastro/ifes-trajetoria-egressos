"""Consulta de vínculos ativos (Feature 010; contracts/governanca.md, "Consulta")."""

import pytest

from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.models import VinculoDeGovernanca

A = "demonstracao:operador-a"


def test_sem_identificador_nao_consulta_o_banco(db, django_assert_num_queries):
    with django_assert_num_queries(0):
        assert vinculos_ativos(None) == [] and vinculos_ativos("") == []


@pytest.mark.django_db
def test_so_ativos_do_operador_em_ordem(django_assert_num_queries):
    for papel, unidade, ativo in (
        ("CSAEG", "Vitória", True),
        ("CPAEG", "", True),
        ("CSAEG", "Serra", False),
    ):
        VinculoDeGovernanca.objects.create(
            identificador_operador=A, papel=papel, unidade=unidade, ativo=ativo
        )
    VinculoDeGovernanca.objects.create(identificador_operador="outro", papel="CPAEG")
    with django_assert_num_queries(1):
        vinculos = vinculos_ativos(A)
    assert [(v.papel, v.unidade) for v in vinculos] == [("CPAEG", ""), ("CSAEG", "Vitória")]
    assert vinculos_ativos(" " + A) == []

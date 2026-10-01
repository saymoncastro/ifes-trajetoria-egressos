"""Fixtures comuns dos testes do instrumento, criadas pelas operações públicas.

`test_instrumento_modelo.py` sobrescreve `pesquisa` e `versao` com escrita direta no ORM,
porque testa as restrições do banco fora das operações.
"""

import pytest

from trajetoria.instrumento import operacoes as op


@pytest.fixture
def pesquisa():
    return op.criar_pesquisa("Pesquisa Institucional de Egressos")


@pytest.fixture
def versao(pesquisa):
    return op.criar_versao(pesquisa, "2024")

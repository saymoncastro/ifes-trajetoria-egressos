from types import SimpleNamespace

import pytest

from trajetoria.comunicacao.contatos import contato_ficticio


@pytest.mark.parametrize(
    "id_,esperado",
    [("SIM-P-0001", "sim-p-0001@example.invalid"), ("SIM-P-0010", None), ("novo", None)],
)
def test_mapa(id_, esperado):
    p = SimpleNamespace(fonte="simulada", id_externo=id_, nome="Nome não é contato")
    assert contato_ficticio(p) == esperado
    p.nome = None
    assert contato_ficticio(p) == esperado


def test_fonte_real_nao_recebe_contato():
    assert contato_ficticio(SimpleNamespace(fonte="real", id_externo="SIM-P-0001")) is None

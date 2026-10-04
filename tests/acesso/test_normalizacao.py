from datetime import date

import pytest


@pytest.mark.parametrize(
    "texto", ["000.000.001-91", "00000000191", " 000 000 001 91 ", "111.444.777-35"]
)
def test_cpf_aceito(texto):
    from trajetoria.acesso.normalizacao import cpf_utilizavel, normalizar_cpf

    assert cpf_utilizavel(normalizar_cpf(texto))


@pytest.mark.parametrize(
    "texto", ["00000000192", "111.111.111-11", "1234567890", "123456789012", "a00000000191", ""]
)
def test_cpf_recusado(texto):
    from trajetoria.acesso.normalizacao import normalizar_cpf

    assert normalizar_cpf(texto) is None


@pytest.mark.parametrize(
    "texto,esperada",
    [
        ("12/04/1998", date(1998, 4, 12)),
        ("12041998", date(1998, 4, 12)),
        ("31/02/2000", None),
        ("01/01/1899", None),
        ("1998-04-12", None),
        ("01/01/2100", None),
        ("", None),
    ],
)
def test_data(texto, esperada):
    from trajetoria.acesso.normalizacao import normalizar_data

    assert normalizar_data(texto, date(2026, 10, 4)) == esperada

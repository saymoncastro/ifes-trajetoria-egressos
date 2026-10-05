"""Normalização única de e-mail (020 research R4; T004)."""

import pytest

from trajetoria.contato.endereco import EnderecoInvalido, email_valido, normalizar_email


def test_normaliza_espacos_externos_e_dominio():
    assert normalizar_email("  Fulana.Tal@Example.INVALID ") == "Fulana.Tal@example.invalid"


@pytest.mark.parametrize(
    "valor",
    [
        "", "   ", "sem-arroba", "a@b", "a b@example.invalid", "a@example.invalid\r\nBcc: x@y.z",
        "a@example.invalid\n", "<a@example.invalid>", "a@example.invalid, b@example.invalid",
        "a;b@example.invalid", "a\t@example.invalid", None, 42, "x" * 250 + "@example.invalid",
    ],
)
def test_recusa_invalidos_sem_ecoar_o_valor(valor):
    with pytest.raises(EnderecoInvalido) as erro:
        normalizar_email(valor)
    assert str(erro.value) == "endereco_invalido"
    assert not email_valido(valor)


def test_nao_exige_dominio_de_demonstracao():
    # A restrição a example.invalid é barreira do transporte de demonstração, não daqui.
    assert normalizar_email("pessoa@exemplo.org") == "pessoa@exemplo.org"

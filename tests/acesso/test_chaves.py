import hashlib
import hmac
from dataclasses import replace

import pytest

from tests.acesso.construcao import ANA


def test_vetores_e_separacao():
    from trajetoria.acesso.chaves import (
        chave_de_origem,
        chaves_de_acesso,
        identificador_cpf,
        verificador,
    )

    c = chaves_de_acesso()
    for obtido, chave, mensagem in (
        (identificador_cpf(ANA.cpf11, c), c.localizacao, "cpf:" + ANA.cpf11),
        (
            verificador(ANA.cpf11, ANA.data, c),
            c.verificacao,
            "cpf-nascimento:" + ANA.cpf11 + ":" + ANA.data.isoformat(),
        ),
        (chave_de_origem(ANA.cpf11, c), c.localizacao, "origem:" + ANA.cpf11),
    ):
        assert obtido == hmac.new(chave.encode(), mensagem.encode(), hashlib.sha256).hexdigest()
    assert identificador_cpf(ANA.cpf11, c) != chave_de_origem(ANA.cpf11, c)
    novo = replace(c, verificacao="c3" * 32)
    assert identificador_cpf(ANA.cpf11, c) == identificador_cpf(ANA.cpf11, novo)
    assert verificador(ANA.cpf11, ANA.data, c) != verificador(ANA.cpf11, ANA.data, novo)
    assert "a1" * 32 not in repr(c)


@pytest.mark.parametrize("valor", ["", "x" * 31, "b2" * 32, "secret", "pseudo"])
def test_chaves_recusadas(settings, valor):
    from trajetoria.acesso.chaves import ChavesInvalidas, chaves_de_acesso

    settings.SECRET_KEY = "secret"
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "pseudo"
    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = valor
    with pytest.raises(ChavesInvalidas) as e:
        chaves_de_acesso()
    assert not valor or valor not in str(e.value)

"""Fixtures dos testes do editor (Feature 009).

O editor só existe no modo de demonstração; aqui ele fica ligado por padrão, e o teste que
verifica o modo desligado o desliga explicitamente.

**Baseline intocada** (tasks, convenções): `baseline` é lida e copiada, nunca escrita. A
publicação de `publicada` acontece só no arranjo do teste — o editor nunca publica.
"""

import pytest

from trajetoria.formulario_2024 import materializar
from trajetoria.instrumento import operacoes as op


@pytest.fixture(autouse=True)
def modo_demonstracao(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


@pytest.fixture
def pesquisa(db):
    return op.criar_pesquisa("Pesquisa fictícia de teste")


@pytest.fixture
def versao(pesquisa):
    return op.criar_versao(pesquisa, "Teste 1")


@pytest.fixture
def baseline(db):
    """A Versão materializada pela 003 — somente leitura nos testes."""
    return materializar().versao


@pytest.fixture
def copia(baseline):
    return op.criar_versao_a_partir_de(baseline, "Cópia de teste")


@pytest.fixture
def publicada(baseline):
    """Cópia da baseline publicada só no arranjo do teste (não é publicação institucional)."""
    versao = op.criar_versao_a_partir_de(baseline, "Cópia publicada de teste")
    op.publicar(versao)
    versao.refresh_from_db()
    return versao

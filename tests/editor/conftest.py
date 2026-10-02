"""Fixtures dos testes do editor (Features 009 e 010).

O editor só existe no modo de demonstração; aqui ele fica ligado por padrão, e o teste que
verifica o modo desligado o desliga explicitamente.

**Operador** (010): a fixture `client` atua como o operador fictício A com vínculo CPAEG
ativo, de modo que os testes da 009 provam que, para a CPAEG, o editor é o mesmo (SC-003).
`cliente_csaeg`, `cliente_sem_vinculo`, `cliente_inativo` e `cliente_nao_identificado` são
os demais perfis. A identificação é o cookie assinado do adaptador de demonstração; o que
cada um pode fazer vem só dos vínculos.

**Baseline intocada** (tasks, convenções): `baseline` é lida e copiada, nunca escrita. A
publicação de `publicada` acontece só no arranjo do teste — o editor nunca publica.
"""

import pytest
from django.test import Client

from tests.editor.construcao_editor import A, B, C, atuar_como
from trajetoria.formulario_2024 import materializar
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import desativar_vinculo, registrar_vinculo
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


# --- Operadores (010) -------------------------------------------------------------------------


@pytest.fixture
def vinculo_cpaeg(db):
    return registrar_vinculo(A, Papel.CPAEG)


@pytest.fixture
def client(client, vinculo_cpaeg):
    return atuar_como(client, A)


@pytest.fixture
def cliente_csaeg(db):
    registrar_vinculo(B, Papel.CSAEG, "Vitória")
    return atuar_como(Client(), B)


@pytest.fixture
def cliente_sem_vinculo(db):
    return atuar_como(Client(), C)


@pytest.fixture
def cliente_inativo(db):
    desativar_vinculo(registrar_vinculo(A, Papel.CPAEG))
    return atuar_como(Client(), A)


@pytest.fixture
def cliente_nao_identificado(db):
    return Client()

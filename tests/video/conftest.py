"""Fixtures dos testes da Feature 022 (vídeo da Minha trajetória).

Reaproveita o modo de demonstração, o relógio e o cenário da 021. Os testes que precisam do
Node levam o marcador `precisa_renderizador`: sem o renderizador, são pulados com o motivo;
no CI (`CI=true`), a ausência é falha, para que a mídia nunca deixe de ser verificada.
"""

import os

import pytest

from tests.narrativa.conftest import cenario, modo_demonstracao, referencia, relogio  # noqa: F401

# MP4 mínimo aceito pela validação de saída do renderizador (assinatura `ftyp`).
MP4_FALSO = b"\x00\x00\x00\x18ftypisom" + b"0" * 64


def pytest_runtest_setup(item):
    if item.get_closest_marker("precisa_renderizador") is None:
        return
    from trajetoria.video import renderizador

    if renderizador.disponivel():
        return
    motivo = "renderizador de vídeo indisponível (npm ci --prefix video; garantir-navegador)"
    if os.environ.get("CI") == "true":
        pytest.fail(motivo)
    pytest.skip(motivo)


@pytest.fixture
def renderizador_falso(monkeypatch):
    """Substitui o render real; registra as composições recebidas."""
    from trajetoria.video import renderizador

    chamadas = []

    def renderizar(composicao):
        chamadas.append(composicao)
        return MP4_FALSO

    monkeypatch.setattr(renderizador, "renderizar", renderizar)
    monkeypatch.setattr(renderizador, "disponivel", lambda: True)
    return chamadas


@pytest.fixture
def renderizador_com_falha(monkeypatch):
    from trajetoria.video import renderizador

    def renderizar(composicao):
        raise renderizador.FalhaDeRenderizacao("codigo_1")

    monkeypatch.setattr(renderizador, "renderizar", renderizar)
    monkeypatch.setattr(renderizador, "disponivel", lambda: True)

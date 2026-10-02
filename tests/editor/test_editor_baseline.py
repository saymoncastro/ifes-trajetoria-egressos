"""Baseline da 003: rascunho comum, sem exceção pelo nome, nunca editada nos testes
(FR-009, FR-099, FR-100; DP-902; SC-008)."""

import re
from pathlib import Path

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.formulario_2024 import declaracao, materializar

pytestmark = pytest.mark.django_db
EDITOR = Path(__file__).resolve().parents[2] / "trajetoria" / "editor"


def test_baseline_oferece_edicao_como_qualquer_rascunho(client, baseline):
    antes = ce.retrato(baseline)
    html = client.get(f"/editor/versoes/{baseline.pk}/").content.decode()
    assert f"/editor/versoes/{baseline.pk}/dados/" in html
    assert f"/editor/versoes/{baseline.pk}/secoes/nova/" in html
    assert "crie uma nova Versão a partir dela" in ce.texto_visivel(
        client.get(f"/editor/versoes/{baseline.pk}/")
    )
    assert ce.retrato(baseline) == antes


def test_fluxos_na_copia_preservam_a_referencia(client, copia):
    pergunta = ce.pergunta(copia, 1, 1)
    client.post(
        f"/editor/perguntas/{pergunta.pk}/editar/", {"texto": "Outro texto", "obrigatoria": "nao"}
    )
    client.post(f"/editor/secoes/{ce.secao(copia, 13).pk}/mover/", {"direcao": "cima"})
    resultado = materializar()  # recusaria com BaselineDivergente se a referência mudasse
    assert resultado.criada is False


def test_nenhuma_regra_pelo_nome_ou_conteudo_da_baseline():
    textos = {
        t
        for s in declaracao.SECOES
        for p in s.perguntas
        for t in (p.texto, *p.opcoes)
        if len(t) >= 12
    }
    for arquivo in EDITOR.rglob("*"):
        if arquivo.suffix not in (".py", ".html", ".css"):
            continue
        conteudo = arquivo.read_text()
        assert declaracao.NOME_PESQUISA not in conteudo, arquivo.name
        assert declaracao.DESIGNACAO not in conteudo, arquivo.name
        assert not re.search(r"\bQ\d{1,2}\b", conteudo), arquivo.name
        assert not [t for t in textos if t in conteudo], arquivo.name

"""Fronteira Python ↔ Node (022; contracts/renderizador.md; FR-027, FR-038).

O renderizador real é substituído por scripts falsos no lugar do `node`: a fronteira é
verificada sem o Remotion. Nenhum log pode conter a composição nem a saída do processo.
"""

import os
import re
import stat
from pathlib import Path

import pytest

from tests.video.construcao import NOME, composicao
from trajetoria.video import renderizador

RAIZ = Path(__file__).resolve().parents[2]
PERMITIDOS = {RAIZ / "trajetoria/video/renderizador.py"}
CHAMADA_EXTERNA = re.compile(r"\bsubprocess\b|\bnpx\b|\bPopen\b|os\.system")


def test_so_o_renderizador_chama_processos_externos():
    infratores = [
        str(caminho.relative_to(RAIZ))
        for caminho in (RAIZ / "trajetoria").rglob("*.py")
        if caminho not in PERMITIDOS and CHAMADA_EXTERNA.search(caminho.read_text("utf-8"))
    ]
    assert infratores == []


def test_opcoes_do_remotion_so_no_projeto_node():
    for caminho in (RAIZ / "trajetoria").rglob("*.py"):
        texto = caminho.read_text("utf-8")
        for opcao in ("renderMedia", "colorSpace", "pixelFormat", "chrome-headless-shell"):
            if caminho in PERMITIDOS and opcao == "chrome-headless-shell":
                continue
            assert opcao not in texto, f"{opcao} em {caminho}"


def _node_falso(tmp_path, corpo: str) -> str:
    """Script executável que faz o papel do `node`; recebe `renderizar.mjs entrada saida`."""
    script = tmp_path / "node-falso"
    script.write_text(f"#!/bin/sh\n{corpo}\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return str(script)


@pytest.fixture
def ambiente(settings, tmp_path, monkeypatch):
    settings.TRAJETORIA_VIDEO_TEMPO_MAXIMO = 5
    monkeypatch.setattr(renderizador, "_diretorio_temporario", lambda: tmp_path / "trabalho")
    return settings


def _sem_resto(tmp_path):
    return not (tmp_path / "trabalho").exists()


def test_codigo_1_vira_falha_sem_vazar_conteudo(ambiente, tmp_path, caplog):
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(tmp_path, 'cat "$2" >&2; cat "$2"; exit 1')
    with pytest.raises(renderizador.FalhaDeRenderizacao) as erro:
        renderizador.renderizar(composicao("maria", NOME))
    assert erro.value.motivo == "codigo_1"
    assert NOME not in caplog.text and "Tecnologia" not in caplog.text
    assert "codigo_1" in caplog.text
    assert _sem_resto(tmp_path)


@pytest.mark.parametrize(("codigo", "motivo"), [(2, "entrada_invalida"), (3, "navegador_ausente")])
def test_codigos_do_contrato(ambiente, tmp_path, codigo, motivo):
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(tmp_path, f"exit {codigo}")
    with pytest.raises(renderizador.FalhaDeRenderizacao) as erro:
        renderizador.renderizar(composicao("ana"))
    assert erro.value.motivo == motivo
    assert _sem_resto(tmp_path)


def test_tempo_esgotado(ambiente, tmp_path):
    ambiente.TRAJETORIA_VIDEO_TEMPO_MAXIMO = 1
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(tmp_path, "sleep 5")
    with pytest.raises(renderizador.FalhaDeRenderizacao) as erro:
        renderizador.renderizar(composicao("ana"))
    assert erro.value.motivo == "tempo_esgotado"
    assert _sem_resto(tmp_path)


@pytest.mark.parametrize("conteudo", ["", "isto não é um mp4"])
def test_saida_invalida(ambiente, tmp_path, conteudo):
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(tmp_path, f'printf "{conteudo}" > "$3"')
    with pytest.raises(renderizador.FalhaDeRenderizacao) as erro:
        renderizador.renderizar(composicao("ana"))
    assert erro.value.motivo == "saida_invalida"
    assert _sem_resto(tmp_path)


def test_sucesso_devolve_bytes_e_recebe_a_composicao(ambiente, tmp_path):
    copia = tmp_path / "entrada-recebida.json"
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(
        tmp_path, f'cp "$2" "{copia}"; printf "\\000\\000\\000\\030ftypisom0000" > "$3"'
    )
    video = renderizador.renderizar(composicao("ana"))
    assert video[4:8] == b"ftyp"
    assert '"template":"trajetoria-v1"' in copia.read_text("utf-8")
    assert _sem_resto(tmp_path)


def test_ambiente_minimo(ambiente, tmp_path, monkeypatch):
    monkeypatch.setenv("TRAJETORIA_CHAVE_ACESSO_VERIFICACAO", "segredo")
    variaveis = tmp_path / "variaveis"
    ambiente.TRAJETORIA_VIDEO_NODE = _node_falso(
        tmp_path, f'env > "{variaveis}"; printf "\\000\\000\\000\\030ftypisom" > "$3"'
    )
    renderizador.renderizar(composicao("ana"))
    assert "segredo" not in variaveis.read_text()


def test_indisponivel_sem_node(settings):
    renderizador.disponivel.cache_clear()
    settings.TRAJETORIA_VIDEO_NODE = ""
    try:
        assert renderizador.disponivel() is False
    finally:
        renderizador.disponivel.cache_clear()


def test_indisponivel_sem_projeto(settings, tmp_path):
    renderizador.disponivel.cache_clear()
    settings.TRAJETORIA_VIDEO_PROJETO = tmp_path
    try:
        assert renderizador.disponivel() is False
    finally:
        renderizador.disponivel.cache_clear()


def test_indisponivel_sem_navegador(settings, tmp_path):
    (tmp_path / "node_modules" / "remotion").mkdir(parents=True)
    renderizador.disponivel.cache_clear()
    settings.TRAJETORIA_VIDEO_PROJETO = tmp_path
    settings.TRAJETORIA_VIDEO_NAVEGADOR = ""
    try:
        assert renderizador.disponivel() is False
    finally:
        renderizador.disponivel.cache_clear()


def test_falha_sem_node(settings):
    settings.TRAJETORIA_VIDEO_NODE = ""
    with pytest.raises(renderizador.FalhaDeRenderizacao) as erro:
        renderizador.renderizar(composicao("ana"))
    assert erro.value.motivo == "indisponivel"


assert os.sep == "/", "os scripts falsos usam /bin/sh"


def test_node_pelo_nome_do_comando(settings):
    """`TRAJETORIA_VIDEO_NODE=node` (sem caminho) é resolvido pelo PATH (code review)."""
    settings.TRAJETORIA_VIDEO_NODE = "sh"
    assert renderizador._node().endswith("/sh")
    settings.TRAJETORIA_VIDEO_NODE = "comando-que-nao-existe"
    assert renderizador._node() is None

"""Fronteira Python ↔ Node do vídeo (Feature 022; contracts/renderizador.md; ADR 0007).

Único módulo do projeto que chama um processo externo. Entra a composição visual (JSON),
sai o MP4 ou uma `FalhaDeRenderizacao` com motivo técnico curto. O domínio não conhece o
Remotion: as opções de vídeo ficam em `video/renderizar.mjs`.

A saída do processo (`stdout`, `stderr`) pode ecoar a composição, com nome e cursos: ela
nunca é logada (FR-027). O processo roda sem shell, com ambiente mínimo, num grupo próprio;
ao esgotar o tempo, o grupo inteiro (Node e Chrome) é encerrado.
"""

import json
import logging
import os
import shutil
import signal
import subprocess
import tempfile
from functools import cache
from pathlib import Path

from django.conf import settings

logger = logging.getLogger("trajetoria.video")

ENTRADA_INVALIDA, NAVEGADOR_AUSENTE = 2, 3
NAVEGADOR_PROVISIONADO = Path("node_modules") / ".remotion" / "chrome-headless-shell"


class FalhaDeRenderizacao(Exception):
    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo


def _node() -> str | None:
    """O executável do Node: caminho ou nome de comando, resolvido pelo PATH."""
    return shutil.which(settings.TRAJETORIA_VIDEO_NODE) if settings.TRAJETORIA_VIDEO_NODE else None


@cache
def disponivel() -> bool:
    """Node, o projeto `video/` instalado e o navegador provisionado (research R12)."""
    node = _node()
    projeto = Path(settings.TRAJETORIA_VIDEO_PROJETO)
    navegador = settings.TRAJETORIA_VIDEO_NAVEGADOR
    provisionado = Path(navegador).is_file() if navegador else (
        projeto / NAVEGADOR_PROVISIONADO
    ).is_dir()
    return bool(
        node
        and (projeto / "node_modules" / "remotion").is_dir()
        and provisionado
    )


def _diretorio_temporario() -> Path:
    return Path(tempfile.mkdtemp(prefix="trajetoria-video-"))


def _ambiente() -> dict[str, str]:
    ambiente = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "TRAJETORIA_VIDEO_CONCORRENCIA": str(settings.TRAJETORIA_VIDEO_CONCORRENCIA),
    }
    if settings.TRAJETORIA_VIDEO_NAVEGADOR:
        ambiente["TRAJETORIA_VIDEO_NAVEGADOR"] = settings.TRAJETORIA_VIDEO_NAVEGADOR
    return ambiente


def _executar(composicao: dict, pasta: Path, saida: Path, extras: list[str]) -> None:
    node = _node()
    if not node:
        raise FalhaDeRenderizacao("indisponivel")
    entrada = pasta / "entrada.json"
    entrada.write_text(
        json.dumps(composicao, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    projeto = Path(settings.TRAJETORIA_VIDEO_PROJETO)
    try:
        processo = subprocess.Popen(
            [node, str(projeto / "renderizar.mjs"), str(entrada), str(saida), *extras],
            cwd=projeto if projeto.is_dir() else pasta,
            env=_ambiente(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as erro:
        raise FalhaDeRenderizacao("indisponivel") from erro
    try:
        codigo = processo.wait(timeout=settings.TRAJETORIA_VIDEO_TEMPO_MAXIMO)
    except subprocess.TimeoutExpired as erro:
        os.killpg(processo.pid, signal.SIGKILL)
        processo.wait()
        raise FalhaDeRenderizacao("tempo_esgotado") from erro
    if codigo == ENTRADA_INVALIDA:
        raise FalhaDeRenderizacao("entrada_invalida")
    if codigo == NAVEGADOR_AUSENTE:
        raise FalhaDeRenderizacao("navegador_ausente")
    if codigo != 0:
        raise FalhaDeRenderizacao(f"codigo_{codigo}")


def _com_log(funcao):
    def envolvida(*args, **kwargs):
        try:
            return funcao(*args, **kwargs)
        except FalhaDeRenderizacao as falha:
            # Só o fato técnico (FR-027).
            logger.warning("video: falha na geração (%s)", falha.motivo)
            raise

    return envolvida


@_com_log
def renderizar(composicao: dict) -> bytes:
    """O MP4 da composição (contracts/renderizador.md)."""
    pasta = _diretorio_temporario()
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        saida = pasta / "video.mp4"
        _executar(composicao, pasta, saida, [])
        video = saida.read_bytes() if saida.is_file() else b""
        if video[4:8] != b"ftyp":
            raise FalhaDeRenderizacao("saida_invalida")
        return video
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


@_com_log
def quadros(composicao: dict, pedidos) -> dict[str, bytes]:
    """PNGs de quadros (`30`, `120`, `fim`…), só para testes e referências."""
    pasta = _diretorio_temporario()
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        destino = pasta / "quadros"
        destino.mkdir()
        pedidos = [str(p) for p in pedidos]
        _executar(composicao, pasta, destino, ["--quadros", ",".join(pedidos)])
        resultado = {}
        for pedido in pedidos:
            arquivo = destino / f"quadro-{pedido}.png"
            if not arquivo.is_file():
                raise FalhaDeRenderizacao("saida_invalida")
            resultado[pedido] = arquivo.read_bytes()
        return resultado
    finally:
        shutil.rmtree(pasta, ignore_errors=True)

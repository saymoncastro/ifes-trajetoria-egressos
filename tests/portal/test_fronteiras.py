"""Fronteira da camada do Portal (024 FR-028, FR-029; Constituição 2.1.0, "Camada de
relacionamento"): o núcleo não depende do Portal, o Portal não tem modelo e não grava."""

import re
import tomllib
from pathlib import Path

import pytest

from tests.dependencias import DEPENDENCIAS_APROVADAS
from tests.portal import construcao as cp

RAIZ = Path(__file__).resolve().parents[2]
PORTAL = RAIZ / "trajetoria/portal"
MENCAO = re.compile(r"portal", re.I)


def test_nucleo_nao_menciona_o_portal():
    infratores = [
        str(caminho.relative_to(RAIZ))
        for sufixo in ("*.py", "*.html", "*.css")
        for caminho in (RAIZ / "trajetoria").rglob(sufixo)
        if PORTAL not in caminho.parents and MENCAO.search(caminho.read_text("utf-8"))
    ]
    assert infratores == []


def test_portal_sem_modelo_nem_migracao():
    assert not (PORTAL / "models.py").exists()
    assert not (PORTAL / "migrations").exists()


def test_nenhuma_dependencia_nova():
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text("utf-8"))
    assert projeto["project"]["dependencies"] == DEPENDENCIAS_APROVADAS


@pytest.mark.django_db
def test_portal_nao_grava(client, cenario):
    """FR-029; FR-033, item 10; SC-006."""
    maria = cenario.pessoa("SIM-P-0003")
    antes = cp.contagens()
    for url in ("/", "/entrar/", "/inicio/"):
        client.get(url)
    cp.entrar(client, maria)
    for url in ("/", "/entrar/", "/inicio/"):
        client.get(url)
    assert cp.contagens() == antes

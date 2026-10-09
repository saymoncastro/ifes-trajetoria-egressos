"""Fronteira da camada do Portal (024 FR-028, FR-029; 025 FR-036, FR-037; Constituição 2.1.0,
"Camada de relacionamento"): o núcleo não depende do Portal; o Portal tem um único modelo,
sem chave para o núcleo, e as telas do egresso não gravam."""

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


def test_portal_um_modelo_sem_fk_para_o_nucleo():
    """Revisado pela 025 (research R1): a 024 não tinha modelo; a 025 traz exatamente um,
    `Oportunidade`, com migrações só aditivas e nenhuma chave estrangeira."""
    from django.apps import apps
    from django.db import models

    modelos = list(apps.get_app_config("portal").get_models())
    assert [m.__name__ for m in modelos] == ["Oportunidade"]
    assert not any(isinstance(c, models.ForeignKey | models.OneToOneField | models.ManyToManyField)
                   for c in modelos[0]._meta.get_fields())
    operacoes = re.findall(r"migrations\.(\w+)\(",
                           "".join(p.read_text("utf-8")
                                   for p in (PORTAL / "migrations").glob("0*.py")))
    assert operacoes and set(operacoes) <= {"CreateModel", "AddField", "AddConstraint"}


def test_nenhuma_dependencia_nova():
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text("utf-8"))
    assert projeto["project"]["dependencies"] == DEPENDENCIAS_APROVADAS


@pytest.mark.django_db
def test_portal_nao_grava(client, cenario):
    """FR-029; FR-033, item 10; SC-006."""
    maria = cenario.pessoa("SIM-P-0003")
    antes = cp.contagens()
    for url in ("/", "/entrar/", "/inicio/", "/oportunidades/"):
        client.get(url)
    cp.entrar(client, maria)
    for url in ("/", "/entrar/", "/inicio/", "/oportunidades/"):  # 025 FR-015
        client.get(url)
    assert cp.contagens() == antes

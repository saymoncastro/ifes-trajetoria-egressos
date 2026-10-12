"""Fronteira da camada do Portal (024 FR-028, FR-029; 025 FR-036, FR-037; 026 FR-015, FR-017;
Constituição 2.1.0, "Camada de relacionamento"): o núcleo não depende do Portal; o Portal tem
dois modelos, sem chave para o núcleo; as telas do egresso só gravam pela contribuição
(026), e nunca ao abrir uma página."""

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


def test_portal_dois_modelos_sem_fk_para_o_nucleo():
    """Revisado pela 025 (research R1) e pela 026 (plan R2): a 024 não tinha modelo; a 025
    traz a `Oportunidade` e a 026 a `Manifestacao`, com migrações só aditivas e nenhuma
    chave estrangeira.

    Revisado pela 031 (incremento 1; research R2): entram `Encontro` e `Confirmacao`. A regra
    da ADR 0008 é não depender do núcleo: chaves estrangeiras só podem apontar para modelos
    da própria camada (a Confirmação aponta para o Encontro)."""
    from django.apps import apps
    from django.db import models

    modelos = list(apps.get_app_config("portal").get_models())
    assert sorted(m.__name__ for m in modelos) == [
        "Confirmacao", "Encontro", "Manifestacao", "Oportunidade"]
    relacoes = [c for modelo in modelos for c in modelo._meta.get_fields()
                if isinstance(c, models.ForeignKey | models.OneToOneField | models.ManyToManyField)]
    assert all(r.related_model._meta.app_label == "portal" for r in relacoes)
    assert [f"{r.model.__name__}.{r.name}" for r in relacoes] == ["Confirmacao.encontro"]
    operacoes = re.findall(r"migrations\.(\w+)\(",
                           "".join(p.read_text("utf-8")
                                   for p in (PORTAL / "migrations").glob("0*.py")))
    assert operacoes and set(operacoes) <= {"CreateModel", "AddField", "AddConstraint"}


def test_nenhuma_dependencia_nova():
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text("utf-8"))
    assert projeto["project"]["dependencies"] == DEPENDENCIAS_APROVADAS


@pytest.mark.django_db
def test_portal_nao_grava(client, cenario):
    """FR-029; FR-033, item 10; SC-006. Revisado pela 026: abrir as telas da contribuição
    também não grava; só enviar e retirar gravam (test_contribuicao_fronteira.py)."""
    maria = cenario.pessoa("SIM-P-0003")
    antes = cp.contagens()
    # Revisado pela 031: abrir os encontros também não grava; só propor, decidir, confirmar e
    # cancelar gravam (test_encontros_operacoes.py).
    telas = ("/", "/entrar/", "/inicio/", "/oportunidades/", "/contribuir/", "/contribuicoes/",
             "/encontros/", "/encontros/propor/", "/encontros/seus/")
    for url in telas:
        client.get(url)
    cp.entrar(client, maria)
    for url in telas:  # 025 FR-015
        client.get(url)
    assert cp.contagens() == antes

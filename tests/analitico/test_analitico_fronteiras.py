"""Fronteiras do app analítico (US12; spec FR-001, FR-015, FR-048, FR-050, FR-100 a FR-122;
SC-008, SC-009). Verificações estruturais: modelos, campos, imports e integridade
referencial, sem procurar palavras soltas no código."""

import ast
import importlib.util
import tomllib
from pathlib import Path

import pytest
from django.apps import apps
from django.db.models import ProtectedError
from django.urls import get_resolver

import trajetoria.analitico
from tests.analitico import construcao as c
from trajetoria.academico.models import Pessoa
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.governanca import regras as governanca
from trajetoria.instrumento.models import EstadoVersao

pytestmark = pytest.mark.django_db

RAIZ = Path(trajetoria.analitico.__file__).parent
MODULOS = sorted(p for p in RAIZ.rglob("*.py") if "migrations" not in p.parts)
PERMITIDOS = {
    "trajetoria.analitico",
    "trajetoria.campanha",
    "trajetoria.participacao",
    "trajetoria.academico",
    "trajetoria.instrumento",
    "trajetoria.fonte_academica",
}


def _importados(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
        elif isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
    return nomes


# --- US12: nenhum modelo de cópia --------------------------------------------------------------


def test_exatamente_dois_modelos():
    assert {m.__name__ for m in apps.get_app_config("analitico").get_models()} == {
        "SnapshotAnalitico",
        "RegistroDoSnapshot",
    }


def test_nenhum_campo_guarda_instrumento_pessoa_ou_identificador_externo():
    proibidos = {
        "nome", "cpf", "email", "telefone", "matricula", "endereco", "fonte", "id_externo",
        "pessoa", "hash", "pseudonimo", "texto", "titulo", "designacao", "pergunta", "opcao",
        "opcoes", "secao", "versao", "resposta", "participacao", "escala", "complemento",
    }  # fmt: skip
    for modelo in (SnapshotAnalitico, RegistroDoSnapshot):
        campos = {f.name for f in modelo._meta.get_fields() if f.concrete}
        assert not campos & proibidos, modelo
        for campo in modelo._meta.get_fields():
            if campo.is_relation and campo.concrete:
                assert campo.related_model is not Pessoa


def test_versao_alcancada_pela_campanha_e_a_publicada(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    assert snapshot.campanha.versao_id == cenario.inst.versao.pk
    assert snapshot.campanha.versao.estado == EstadoVersao.PUBLICADA


# --- Integridade referencial (só por ORM no teste; nenhuma operação de remoção existe) ----------


def test_conclusao_referenciada_nao_pode_ser_removida(cenario):
    snapshot = capturar_snapshot(cenario.campanha)
    antes = c.retrato(snapshot)
    with pytest.raises(ProtectedError):
        cenario.serra_sem_participacao.delete()  # sem Participação: só o registro protege
    assert c.retrato(snapshot) == antes


def test_campanha_com_snapshot_nao_pode_ser_removida(campanha_v):
    capturar_snapshot(campanha_v)
    with pytest.raises(ProtectedError):
        campanha_v.delete()


def test_remover_snapshot_remove_so_os_seus_registros(cenario):
    a = capturar_snapshot(cenario.campanha)
    b = capturar_snapshot(cenario.campanha)
    retrato_b = c.retrato(b)
    a.delete()
    assert not RegistroDoSnapshot.objects.filter(snapshot_id=a.pk).exists()
    assert c.retrato(b) == retrato_b


# --- Escopo e privacidade ------------------------------------------------------------------------


def test_imports_so_das_features_permitidas():
    assert MODULOS
    for arquivo in MODULOS:
        for nome in _importados(arquivo):
            if nome.startswith("trajetoria"):
                assert any(nome == p or nome.startswith(p + ".") for p in PERMITIDOS), (
                    arquivo.name,
                    nome,
                )


def test_sem_interface_nem_comando():
    for sufixo in ("views", "urls", "admin", "management", "forms", "api", "serializers"):
        assert importlib.util.find_spec(f"trajetoria.analitico.{sufixo}") is None, sufixo
    assert not (RAIZ / "templates").exists()


def test_nenhuma_rota_leva_ao_analitico():
    def modulos(padroes):
        for padrao in padroes:
            if hasattr(padrao, "url_patterns"):
                yield from modulos(padrao.url_patterns)
            else:
                yield padrao.callback.__module__

    assert not [m for m in modulos(get_resolver().url_patterns) if "analitico" in m]


def test_sem_dependencia_nova():
    raiz_do_projeto = Path(__file__).resolve().parents[2]
    projeto = tomllib.loads((raiz_do_projeto / "pyproject.toml").read_text())["project"]
    assert projeto["dependencies"] == ["Django>=5.2,<5.3", "psycopg[binary]>=3.2,<3.4"]


def test_nenhuma_regra_de_governanca_nova():
    assert set(governanca.__all__) == {
        "EscopoDeAcompanhamento",
        "escopo_de_acompanhamento",
        "pode_acompanhar_coleta",
        "pode_consultar_publicado",
        "pode_consultar_rascunho",
        "pode_elaborar_instrumento",
    }


def test_captura_nunca_automatica():
    for arquivo in MODULOS:
        importados = _importados(arquivo)
        assert "django.db.models.signals" not in importados, arquivo.name
        assert "django.dispatch" not in importados, arquivo.name
    config = ast.parse((RAIZ / "apps.py").read_text())
    metodos = {n.name for n in ast.walk(config) if isinstance(n, ast.FunctionDef)}
    assert "ready" not in metodos

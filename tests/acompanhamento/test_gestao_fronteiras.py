import ast
from pathlib import Path

from tests.acompanhamento import construcao as k
from tests.acompanhamento.test_gestao_criar_editar import NOVA, editar_url
from tests.editor.construcao_editor import texto_visivel
from trajetoria.campanha.regras import Motivo

RAIZ = Path(__file__).resolve().parents[2]


def test_sem_operacoes_ou_autoria_proibidas():
    for arquivo in (RAIZ / "trajetoria/acompanhamento/gestao").glob("*.py"):
        arvore = ast.parse(arquivo.read_text())
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call):
                nome = getattr(no.func, "attr", getattr(no.func, "id", ""))
                assert nome not in {
                    "publicar",
                    "definir_criterios",
                    "remover_campanha",
                    "save",
                    "create",
                    "update",
                    "delete",
                }
            if isinstance(no, ast.Name):
                assert no.id not in {"logger", "identificador_operador", "registrar_autoria"}


def test_formularios_sem_criterios_ou_dados_tecnicos(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    for endereco in (NOVA, editar_url(c)):
        r = cliente_cpaeg.get(endereco)
        assert set(r.context["formulario"].fields) == {"nome", "versao", "inicio", "fim"}
        texto = texto_visivel(r)
        assert str(c.pk) not in texto and str(inst.versao.pk) not in texto
        assert all(m.name not in texto for m in Motivo)


def test_sem_modelos_novos():
    assert not list((RAIZ / "trajetoria/acompanhamento/gestao").glob("*model*"))
    assert not (RAIZ / "trajetoria/acompanhamento/gestao/migrations").exists()

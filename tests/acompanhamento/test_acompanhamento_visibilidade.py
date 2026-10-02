"""Campanhas visíveis por escopo (Feature 011; US3; spec FR-020 a FR-022; casos C, D, E, I)."""

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel
from trajetoria.acompanhamento.consultas import campanhas_visiveis
from trajetoria.campanha.models import Campanha
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo
from trajetoria.governanca.regras import EscopoDeAcompanhamento

LISTA = "/acompanhamento/"


def _nomes(cliente):
    texto = texto_visivel(cliente.get(LISTA))
    return {n for n in Campanha.objects.values_list("nome", flat=True) if n in texto}


def test_csaeg_vitoria_ve_irrestritas_e_nao_ve_restrita_a_outras_unidades(
    ref, cliente_csaeg_vitoria
):
    assert _nomes(cliente_csaeg_vitoria) == {"Campanha I", "Campanha P", "Campanha E"}


def test_csaeg_serra_ve_campanha_que_inclui_sua_unidade(ref, cliente_csaeg_serra):
    assert {"Campanha I", "Campanha R"} <= _nomes(cliente_csaeg_serra)


def test_relevante_com_zero_elegiveis_continua_visivel(ref, cliente_csaeg_serra):
    so_serra = k.campanha(ref.inst.versao, nome="Campanha Serra 2030", unidades=["Serra"],
                          ano_minimo=2030)  # fmt: skip
    assert so_serra.nome in _nomes(cliente_csaeg_serra)
    texto = texto_visivel(k.detalhe(cliente_csaeg_serra, so_serra))
    assert "não se aplica" in texto


def test_sem_criterio_de_unidade_e_com_criterio_de_nivel_e_visivel(ref, cliente_csaeg_vitoria):
    pos = k.campanha(ref.inst.versao, nome="Campanha Pós", niveis=["Pós-graduação"])
    assert pos.nome in _nomes(cliente_csaeg_vitoria)


def test_grafia_diferente_nao_e_normalizada(ref):
    registrar_vinculo(k.B, Papel.CSAEG, "Campus Serra")
    cliente = k.atuar_como(__import__("django.test").test.Client(), k.B)
    assert "Campanha R" not in _nomes(cliente)


def test_preparacao_e_encerrada_visiveis_quando_relevantes(ref, cliente_csaeg_serra):
    assert {"Campanha P", "Campanha E"} <= _nomes(cliente_csaeg_serra)


def test_institucional_ve_todas(ref):
    institucional = EscopoDeAcompanhamento(True, frozenset())
    assert set(campanhas_visiveis(institucional)) == set(Campanha.objects.all())
    vitoria = EscopoDeAcompanhamento(False, frozenset({"Vitória"}))
    assert ref.R not in set(campanhas_visiveis(vitoria))

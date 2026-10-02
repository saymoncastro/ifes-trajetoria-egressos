"""As três regras de capacidade do editor (Feature 010; data-model §5; spec, "Matriz mínima
de capacidades") e a regra de acompanhamento da coleta (Feature 011; contracts/governanca.md),
todas puras, sobre vínculos não gravados."""

import inspect

import pytest

from trajetoria.governanca import regras
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.regras import (
    EscopoDeAcompanhamento,
    escopo_de_acompanhamento,
    pode_acompanhar_coleta,
    pode_consultar_publicado,
    pode_consultar_rascunho,
    pode_elaborar_instrumento,
)

REGRAS = (pode_consultar_publicado, pode_consultar_rascunho, pode_elaborar_instrumento)


def _v(papel, unidade="", ativo=True):
    return VinculoDeGovernanca(
        identificador_operador="demonstracao:operador-a", papel=papel, unidade=unidade, ativo=ativo
    )


CPAEG = _v(Papel.CPAEG)
CSAEG_VITORIA = _v(Papel.CSAEG, "Vitória")
CSAEG_SERRA = _v(Papel.CSAEG, "Serra")


def _matriz(vinculos):
    return tuple(regra(vinculos) for regra in REGRAS)


@pytest.mark.parametrize(
    ("vinculos", "esperado"),
    [
        ([], (False, False, False)),
        ([CSAEG_VITORIA], (True, False, False)),
        ([CSAEG_VITORIA, CSAEG_SERRA], (True, False, False)),
        ([CPAEG], (True, True, True)),
        ([CPAEG, CSAEG_VITORIA], (True, True, True)),
        ([_v(Papel.CPAEG, ativo=False), _v(Papel.CSAEG, "Vitória", ativo=False)], (False,) * 3),
        ([_v(Papel.CPAEG, ativo=False), CSAEG_VITORIA], (True, False, False)),
    ],
)
def test_matriz(vinculos, esperado):
    assert _matriz(vinculos) == esperado


def test_unidade_nao_altera_resultado():
    assert _matriz([_v(Papel.CSAEG, "Cefor")]) == _matriz([CSAEG_VITORIA])


def test_regras_dependem_so_dos_vinculos(settings):
    for regra in REGRAS:
        assert list(inspect.signature(regra).parameters) == ["vinculos"]
    settings.TRAJETORIA_DEMONSTRACAO = True
    ligado = _matriz([CSAEG_VITORIA])
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert _matriz([CSAEG_VITORIA]) == ligado


def test_tres_regras_do_editor_e_a_regra_de_acompanhamento():
    publicas = {
        n
        for n, o in vars(regras).items()
        if inspect.isfunction(o) and n[0] != "_" and o.__module__ == regras.__name__
    }
    acompanhamento = {pode_acompanhar_coleta.__name__, escopo_de_acompanhamento.__name__}
    assert publicas == {r.__name__ for r in REGRAS} | acompanhamento
    assert set(regras.__all__) == publicas | {"EscopoDeAcompanhamento"}


# --- Acompanhamento da coleta (Feature 011) ----------------------------------------------------

ACOMPANHAMENTO = (pode_acompanhar_coleta, escopo_de_acompanhamento)
SERRA = _v(Papel.CSAEG, "Serra")


def _escopo(vinculos):
    escopo = escopo_de_acompanhamento(vinculos)
    return None if escopo is None else (escopo.institucional, set(escopo.unidades))


MATRIZ_ACOMPANHAMENTO = [
    ([], False, None),
    ([CSAEG_VITORIA], True, (False, {"Vitória"})),
    ([CSAEG_VITORIA, SERRA], True, (False, {"Vitória", "Serra"})),
    ([CPAEG], True, (True, set())),
    ([CPAEG, CSAEG_VITORIA], True, (True, set())),
    ([_v(Papel.CPAEG, ativo=False), CSAEG_VITORIA], True, (False, {"Vitória"})),
    ([_v(Papel.CPAEG, ativo=False), _v(Papel.CSAEG, "Vitória", ativo=False)], False, None),
]


@pytest.mark.parametrize(("vinculos", "pode", "escopo"), MATRIZ_ACOMPANHAMENTO)
def test_matriz_de_acompanhamento(vinculos, pode, escopo):
    assert pode_acompanhar_coleta(vinculos) is pode
    assert _escopo(vinculos) == escopo


@pytest.mark.parametrize(("vinculos", "pode", "escopo"), MATRIZ_ACOMPANHAMENTO)
def test_acompanhar_equivale_a_ter_escopo(vinculos, pode, escopo):
    assert pode_acompanhar_coleta(vinculos) == (escopo_de_acompanhamento(vinculos) is not None)


def test_papel_nao_listado_nao_concede_acompanhamento():
    """A regra nomeia CPAEG e CSAEG: não é "qualquer vínculo ativo"."""
    desconhecido = _v("OUTRO")
    assert pode_acompanhar_coleta([desconhecido]) is False
    assert escopo_de_acompanhamento([desconhecido]) is None


def test_escopo_e_valor_imutavel():
    escopo = escopo_de_acompanhamento([CSAEG_VITORIA])
    assert isinstance(escopo, EscopoDeAcompanhamento)
    assert isinstance(escopo.unidades, frozenset)
    with pytest.raises(AttributeError):
        escopo.institucional = True


def test_acompanhamento_depende_so_dos_vinculos(settings):
    for regra in ACOMPANHAMENTO:
        assert list(inspect.signature(regra).parameters) == ["vinculos"]
    settings.TRAJETORIA_DEMONSTRACAO = True
    ligado = _escopo([CSAEG_VITORIA, SERRA])
    settings.TRAJETORIA_DEMONSTRACAO = False
    assert _escopo([CSAEG_VITORIA, SERRA]) == ligado

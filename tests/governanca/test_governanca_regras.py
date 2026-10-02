"""As três regras de capacidade, puras, sobre vínculos não gravados (Feature 010;
data-model §5; spec, "Matriz mínima de capacidades")."""

import inspect

import pytest

from trajetoria.governanca import regras
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.regras import (
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


def test_exatamente_tres_regras_publicas():
    publicas = {n for n, o in vars(regras).items() if inspect.isfunction(o) and n[0] != "_"}
    assert publicas == {r.__name__ for r in REGRAS}
    assert set(regras.__all__) == publicas

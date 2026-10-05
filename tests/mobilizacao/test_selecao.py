"""Seleção do Lote (020 FR-016 a FR-018; T015)."""

import pytest

from tests.contato.conftest import contato
from tests.mobilizacao.conftest import INSTITUCIONAL, SERRA, VITORIA, agora, pessoa
from trajetoria.academico.models import Pessoa
from trajetoria.mobilizacao.selecao import Filtros, FiltrosInvalidos, selecionar

pytestmark = pytest.mark.django_db


def _ids(selecao):
    return {Pessoa.objects.get(pk=p).id_externo for p, _ in selecao.pessoas}


def test_campanha_ampla_institucional(ampla):
    s = selecionar(ampla, INSTITUCIONAL, Filtros(), agora())
    # SIM-P-0006 e SIM-P-0008 não têm Conclusão; SIM-P-0012 não foi preparada.
    assert _ids(s) == {f"SIM-P-00{n:02}" for n in (1, 2, 3, 4, 5, 7, 9, 10, 11)}
    assert s.conclusoes == 13
    assert s.excluidas == 0


def test_varias_conclusoes_viram_um_membro(ampla):
    s = selecionar(ampla, INSTITUCIONAL, Filtros.de(unidades=["Vila Velha"]), agora())
    assert _ids(s) == {"SIM-P-0004"}  # Diego: três Conclusões em Vila Velha
    assert s.conclusoes == 3


def test_escopo_antes_dos_filtros(ampla):
    # Maria tem Serra e Cefor: CSAEG Serra a seleciona por Serra; CSAEG Vitória não a vê.
    assert "SIM-P-0003" in _ids(selecionar(ampla, SERRA, Filtros.de(unidades=["Serra"]), agora()))
    vitoria = selecionar(ampla, VITORIA, Filtros.de(unidades=["Serra", "Vitória"]), agora())
    assert _ids(vitoria) == {"SIM-P-0002", "SIM-P-0010"}


def test_filtros_nivel_ano_e_curso(ampla):
    nivel = selecionar(ampla, INSTITUCIONAL, Filtros.de(nivel="Pós-graduação"), agora())
    assert _ids(nivel) == {"SIM-P-0003", "SIM-P-0004"}
    anos = selecionar(ampla, INSTITUCIONAL, Filtros.de(ano_minimo="2021", ano_maximo=2022),
                      agora())
    assert _ids(anos) == {"SIM-P-0001", "SIM-P-0003", "SIM-P-0009"}
    curso = selecionar(
        ampla, INSTITUCIONAL, Filtros.de(curso="Licenciatura em Pedagogia"), agora()
    )
    assert _ids(curso) == {"SIM-P-0010"}
    assert not selecionar(
        ampla, INSTITUCIONAL, Filtros.de(curso="licenciatura em pedagogia"), agora()
    ).pessoas  # igualdade textual, sem normalização (010/DP-1005)


def test_abrangencia_e_o_primeiro_recorte(demo):
    from trajetoria.campanha.models import Campanha

    sobreposta = Campanha.objects.get(nome="Demonstração — coleta sobreposta")
    s = selecionar(sobreposta, INSTITUCIONAL, Filtros(), agora())
    # Só a pós-graduação de Vila Velha está na abrangência; Diego entra por ela.
    assert _ids(s) == {"SIM-P-0004"} and s.conclusoes == 1


def test_sem_contato_continua_membro_e_nada_deduplica_por_nome_ou_email(ampla):
    s = selecionar(ampla, INSTITUCIONAL, Filtros.de(unidades=["Vitória"]), agora())
    por_id = {Pessoa.objects.get(pk=p).id_externo: c for p, c in s.pessoas}
    assert por_id["SIM-P-0010"] is None
    # Homônimas (Carla) continuam Pessoas distintas; mesmo e-mail não funde ninguém.
    contato(pessoa("SIM-P-0011"), "sim-p-0002@example.invalid", "EGRESSO")
    s = selecionar(ampla, INSTITUCIONAL, Filtros(), agora())
    assert {"SIM-P-0010", "SIM-P-0011", "SIM-P-0002"} <= _ids(s)


@pytest.mark.parametrize(
    "campos",
    [dict(ano_minimo="x"), dict(ano_minimo=2020, ano_maximo=2010), dict(curso="a\nb"),
     dict(ano_maximo=1800)],
)
def test_filtros_invalidos(campos):
    with pytest.raises(FiltrosInvalidos):
        Filtros.de(**campos)

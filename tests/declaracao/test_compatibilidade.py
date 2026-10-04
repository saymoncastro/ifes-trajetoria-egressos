import pytest

from tests.declaracao.construcao import DADOS
from tests.participacao import construcao as c
from trajetoria.campanha.consultas import populacao_no_momento
from trajetoria.declaracao.operacoes import campanhas_compativeis

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "criterios,compativel",
    [
        (
            {"unidades": {"Serra"}, "niveis": {"Técnico"}, "ano_minimo": 2004, "ano_maximo": 2004},
            True,
        ),
        ({"unidades": {"Vitória"}}, False),
        ({"niveis": {"Graduação"}}, False),
        ({"ano_minimo": 2005}, False),
        ({"ano_maximo": 2003}, False),
        ({"modalidades": {"Presencial"}, "formas_oferta": {"Integrado"}}, True),
    ],
)
def test_criterios(criterios, compativel):
    campanha = c.campanha_aberta(c.instrumento().versao, **criterios)
    assert bool(campanhas_compativeis(DADOS, agora=c.NO_PERIODO)) is compativel
    assert not populacao_no_momento(campanha).exists()

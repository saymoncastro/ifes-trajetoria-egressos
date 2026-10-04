import pytest

from tests.declaracao.construcao import declaracao_concluida, validar
from tests.participacao import construcao as c
from trajetoria.participacao.entrada import SituacaoDaFormacao, situacao_de_entrada

pytestmark = pytest.mark.django_db


def test_entrada_quarentena_e_validada(campanha, conclusao):
    f = declaracao_concluida(campanha)
    assert (
        situacao_de_entrada(conclusao.pessoa, agora=c.NO_PERIODO).formacoes[0].situacao
        == SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR
    )
    validar(f, conclusao)
    assert (
        situacao_de_entrada(conclusao.pessoa, agora=c.NO_PERIODO).formacoes[0].situacao
        == SituacaoDaFormacao.JA_CONCLUIDA
    )

import pytest

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.seguranca import validar_origem

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("modelo", [Pessoa, ConclusaoAcademica])
def test_origem_indevida_recusada_integralmente(campanha, modelo, caplog):
    modelo.objects.all().update(fonte="origem-real-sentinela")
    with pytest.raises(RecusaComunicacao) as erro:
        validar_origem()
    assert erro.value.status == 422
    assert "origem-real-sentinela" not in caplog.text + str(erro.value)


def test_origem_simulada(campanha):
    validar_origem()

import pytest

from tests.editor.construcao_editor import A, B, C
from trajetoria.comunicacao.acesso import RecusaComunicacao, autorizar_operador, campanha_autorizada
from trajetoria.governanca.models import VinculoDeGovernanca

pytestmark = pytest.mark.django_db


def test_escopo_e_revogacao(campanha):
    assert autorizar_operador(A).escopo.institucional
    assert autorizar_operador(B).escopo.unidades == frozenset({"Vitória"})
    VinculoDeGovernanca.objects.filter(identificador_operador=A).update(ativo=False)
    with pytest.raises(RecusaComunicacao):
        autorizar_operador(A)


@pytest.mark.parametrize("operador", [None, C, "real", "demonstracao:inexistente"])
def test_identidade_e_capacidade(campanha, operador):
    with pytest.raises(RecusaComunicacao):
        autorizar_operador(operador)


def test_modo_off(campanha, settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    with pytest.raises(RecusaComunicacao):
        autorizar_operador(A)


def test_visibilidade(campanha):
    contexto = autorizar_operador(B)
    assert campanha_autorizada(campanha.pk, contexto).pk == campanha.pk
    outra = campanha.__class__.objects.get(nome="Demonstração — coleta sobreposta")
    with pytest.raises(RecusaComunicacao) as erro:
        campanha_autorizada(outra.pk, contexto)
    assert erro.value.status == 403

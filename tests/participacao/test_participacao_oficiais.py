import pytest

from tests.declaracao.construcao import declaracao_concluida, validar
from tests.participacao import construcao as c
from trajetoria.participacao.consultas import (
    atributo_efetivo,
    participacoes_oficiais,
    situacao_analitica,
)
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def test_seis_situacoes(campanha, conclusao):
    institucional = Participacao.objects.create(
        campanha=campanha, conclusao=conclusao, iniciada_em=c.NO_PERIODO
    )
    assert situacao_analitica(institucional) == "INSTITUCIONAL"
    oficiais = {institucional.pk}
    for esperado, resultado, fora, conflito in [
        ("DECLARADA_PENDENTE", None, False, False),
        ("DECLARADA_NAO_CONFIRMADA", "NAO_CONFIRMADA", False, False),
        ("DECLARADA_FORA_DA_ABRANGENCIA", "CONFIRMADA", True, False),
        ("DECLARADA_EM_CONFLITO", "CONFIRMADA", False, True),
        ("DECLARADA_VALIDADA", "CONFIRMADA", False, False),
    ]:
        f = declaracao_concluida(campanha)
        if resultado:
            validar(f, conclusao if resultado == "CONFIRMADA" else None, resultado, fora, conflito)
        assert situacao_analitica(f.participacao) == esperado
        if esperado == "DECLARADA_VALIDADA":
            oficiais.add(f.participacao.pk)
    qs = participacoes_oficiais().annotate(unidade_efetiva=atributo_efetivo("unidade"))
    assert set(qs.values_list("pk", flat=True)) == oficiais
    assert set(qs.values_list("conclusao_efetiva_id", flat=True)) == {conclusao.pk}
    assert set(qs.values_list("unidade_efetiva", flat=True)) == {conclusao.unidade}

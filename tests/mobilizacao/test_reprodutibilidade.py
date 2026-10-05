"""Histórico reproduzível: o Lote guarda o contato efetivamente usado (020 FR-021, FR-022,
FR-038, E6; US5; T050). Cenário 04/10 → 05/10 → 06/10 da spec."""

from datetime import UTC, datetime

import pytest
from django.core import mail

from tests.contato.conftest import contato
from tests.editor.construcao_editor import A
from tests.mobilizacao.conftest import pessoa
from trajetoria.contato.models import ContatoDaPessoa, Origem
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote

pytestmark = pytest.mark.django_db
D4, D5 = datetime(2026, 10, 4, 12, tzinfo=UTC), datetime(2026, 10, 5, 12, tzinfo=UTC)
VITORIA = {"unidades": ["Vitória"]}


def test_contato_congelado_e_historico_preservado(ampla, clientes):
    bruno = pessoa("SIM-P-0002")
    ContatoDaPessoa.objects.filter(pessoa=bruno).delete()  # cenário controlado
    antigo = contato(bruno, "antigo@example.invalid", em=D4)
    a = confirmar_lote(ampla.pk, A, "A", VITORIA)
    membro = a.membros.get(pessoa=bruno)
    assert membro.contato == antigo

    novo = contato(bruno, "novo@example.invalid", Origem.EGRESSO, em=D5)
    detalhe = f"/acompanhamento/campanhas/{ampla.pk}/lotes/{a.pk}/"
    antes = clientes[A].get(detalhe).context["contagens"]
    enviar_lote(a.pk, A)
    assert [m.to for m in mail.outbox] == [["antigo@example.invalid"]]
    membro.refresh_from_db()
    assert (membro.contato, membro.contato.origem, membro.contato.obtido_em) == (
        antigo, Origem.FONTE_ACADEMICA, D4,
    )
    depois = clientes[A].get(detalhe).context["contagens"]
    assert depois["membros"] == antes["membros"] and depois["submetidos"] == 1

    # Lote B, depois de 05/10, para quem não foi mobilizado nesta Campanha.
    carla = pessoa("SIM-P-0010")
    informado = contato(carla, "carla.nova@example.invalid", Origem.EGRESSO, em=D5)
    b = confirmar_lote(ampla.pk, A, "B", VITORIA)
    assert b.membros.get(pessoa=carla).contato == informado
    assert not b.membros.filter(pessoa=bruno).exists()
    assert novo.pk not in set(b.membros.values_list("contato", flat=True))


def test_telas_sem_lista_individual(ampla, clientes):
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    for url in (f"/acompanhamento/campanhas/{ampla.pk}/lotes/",
                f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/"):
        html = clientes[A].get(url).content.decode()
        for proibido in ("example.invalid", "Exemplo", "SIM-P-", "Bruno", "Carla"):
            assert proibido not in html

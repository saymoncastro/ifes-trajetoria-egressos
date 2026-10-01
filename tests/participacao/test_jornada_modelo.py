"""O campo `concluida_em` e a migração da Feature 006 (FR-001, FR-002; data-model)."""

import pytest
from django.db import connection, migrations, models
from django.db.migrations.loader import MigrationLoader

from tests.participacao.construcao import NO_PERIODO
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import iniciar_participacao

pytestmark = pytest.mark.django_db


def test_concluida_em_anulavel_sem_default():
    campo = Participacao._meta.get_field("concluida_em")
    assert isinstance(campo, models.DateTimeField)
    assert campo.null
    assert not campo.has_default()
    assert not campo.auto_now and not campo.auto_now_add


def test_participacao_nasce_em_rascunho(campanha, conclusao):
    participacao = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao
    assert Participacao.objects.get(pk=participacao.pk).concluida_em is None


def test_migracao_0002_so_acrescenta_o_campo():
    migracao = MigrationLoader(connection).get_migration(
        "participacao", "0002_participacao_concluida_em"
    )
    assert migracao.dependencies == [("participacao", "0001_initial")]
    assert len(migracao.operations) == 1
    (operacao,) = migracao.operations
    assert isinstance(operacao, migrations.AddField)
    assert (operacao.model_name, operacao.name) == ("participacao", "concluida_em")
    assert operacao.field.null

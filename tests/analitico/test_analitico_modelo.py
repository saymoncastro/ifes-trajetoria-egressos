"""Persistência do snapshot analítico (data-model §1; research R3 a R6)."""

import pytest
from django.db import IntegrityError, models, transaction
from django.db.models.fields import NOT_PROVIDED
from django.utils import timezone

from tests.analitico import construcao as c
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO
from trajetoria.instrumento.models import Opcao, Pergunta, Secao, Versao
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db


def _campos(modelo) -> set[str]:
    return {f.name for f in modelo._meta.get_fields() if f.concrete}


def test_campos_exatos_do_snapshot():
    assert _campos(SnapshotAnalitico) == {"id", "campanha", "capturado_em"}


def test_campos_exatos_do_registro():
    assert _campos(RegistroDoSnapshot) == {
        "id",
        "snapshot",
        "conclusao",
        "elegivel_no_snapshot",
        *CAMPOS_DE_CONTEXTO,
    }


def test_contexto_do_registro_espelha_a_conclusao():
    for campo in CAMPOS_DE_CONTEXTO:
        no_registro = RegistroDoSnapshot._meta.get_field(campo)
        na_conclusao = ConclusaoAcademica._meta.get_field(campo)
        assert type(no_registro) is type(na_conclusao), campo
        assert no_registro.null is True, campo


def test_capturado_em_sem_default_nem_auto():
    campo = SnapshotAnalitico._meta.get_field("capturado_em")
    assert isinstance(campo, models.DateTimeField)
    assert campo.null is False
    assert campo.default is NOT_PROVIDED
    assert not campo.auto_now and not campo.auto_now_add


def test_elegibilidade_obrigatoria_sem_default():
    campo = RegistroDoSnapshot._meta.get_field("elegivel_no_snapshot")
    assert isinstance(campo, models.BooleanField)
    assert campo.null is False
    assert campo.default is NOT_PROVIDED


def test_on_delete_e_related_name():
    campanha = SnapshotAnalitico._meta.get_field("campanha")
    snapshot = RegistroDoSnapshot._meta.get_field("snapshot")
    conclusao = RegistroDoSnapshot._meta.get_field("conclusao")
    assert campanha.remote_field.on_delete is models.PROTECT
    assert snapshot.remote_field.on_delete is models.CASCADE
    assert conclusao.remote_field.on_delete is models.PROTECT
    assert campanha.remote_field.related_name == "+"
    assert conclusao.remote_field.related_name == "+"
    assert snapshot.remote_field.related_name == "registros"


def test_unica_constraint_e_a_do_grao():
    assert [c.name for c in RegistroDoSnapshot._meta.constraints] == [
        "registro_conclusao_unica_no_snapshot"
    ]
    (unica,) = RegistroDoSnapshot._meta.constraints
    assert isinstance(unica, models.UniqueConstraint)
    assert tuple(unica.fields) == ("snapshot", "conclusao")
    assert SnapshotAnalitico._meta.constraints == []


def test_ordem_do_snapshot_e_so_determinismo():
    assert SnapshotAnalitico._meta.ordering == ["capturado_em", "id"]


def test_nenhuma_fk_para_dados_que_nao_derivam():
    proibidos = {Pessoa, Participacao, Resposta, Versao, Secao, Pergunta, Opcao}
    for modelo in (SnapshotAnalitico, RegistroDoSnapshot):
        for campo in modelo._meta.get_fields():
            if campo.is_relation and campo.concrete:
                assert campo.related_model not in proibidos, (modelo, campo.name)


def test_mesma_conclusao_duas_vezes_no_snapshot_e_rejeitada(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao)
    conclusao = c.conclusao(unidade="Serra")
    snapshot = SnapshotAnalitico.objects.create(campanha=campanha, capturado_em=timezone.now())
    RegistroDoSnapshot.objects.create(
        snapshot=snapshot, conclusao=conclusao, elegivel_no_snapshot=True
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        RegistroDoSnapshot.objects.create(
            snapshot=snapshot, conclusao=conclusao, elegivel_no_snapshot=True
        )


def test_varios_snapshots_da_mesma_campanha_gravam(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao)
    agora = timezone.now()
    SnapshotAnalitico.objects.create(campanha=campanha, capturado_em=agora)
    SnapshotAnalitico.objects.create(campanha=campanha, capturado_em=agora)
    assert SnapshotAnalitico.objects.filter(campanha=campanha).count() == 2

from uuid import uuid4

import pytest
from django.apps import apps
from django.utils import timezone

from tests.declaracao.construcao import CPF, DADOS, DATA
from tests.governanca.test_governanca_regras import CPAEG
from tests.participacao import construcao as c
from trajetoria.declaracao.models import AcessoAosDadosDeConsulta
from trajetoria.declaracao.operacoes import iniciar_participacao_declarada, revelar_dados

pytestmark = pytest.mark.django_db


def test_banco_sessao_logs_exportacao_revelacao(client, caplog, settings):
    from trajetoria.analitico.operacoes import capturar_snapshot
    from trajetoria.campanha.operacoes import encerrar
    from trajetoria.exportacao.dataset import dataset_exportado

    campanha = c.campanha_aberta(c.instrumento().versao)
    p, _ = iniciar_participacao_declarada(
        DADOS, CPF, DATA, uuid4(), origem="local", agora=c.NO_PERIODO
    )
    f = p.formacao_declarada
    valores = " ".join(str(row) for m in apps.get_models() for row in m.objects.values())
    for valor in (CPF, DATA.isoformat(), DATA.strftime("%d/%m/%Y")):
        assert valor not in valores and valor not in caplog.text
    assert revelar_dados(f, vinculos=[CPAEG], operador="A", agora=timezone.now()) == (
        f.nome,
        CPF,
        DATA,
    )
    assert {c.name for c in AcessoAosDadosDeConsulta._meta.fields} == {
        "id",
        "formacao",
        "operador",
        "acessado_em",
    }
    assert CPF not in repr(AcessoAosDadosDeConsulta.objects.get())
    encerrar(campanha, agora=c.NO_PERIODO)
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "p" * 64
    pacote = dataset_exportado(capturar_snapshot(campanha))
    assert CPF not in repr(pacote) and DATA.isoformat() not in repr(pacote)

    for valor in (CPF, DATA.isoformat(), DATA.strftime("%d/%m/%Y")):
        assert valor not in caplog.text

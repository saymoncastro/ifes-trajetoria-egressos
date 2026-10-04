import importlib
from types import SimpleNamespace

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from tests.participacao import construcao as c


@pytest.mark.django_db(transaction=True)
def test_preenchimento_historico():
    executor = MigrationExecutor(connection)
    finais = executor.loader.graph.leaf_nodes()
    anterior = [("analitico", "0001_initial"), ("participacao", "0002_participacao_concluida_em")]
    executor.migrate(anterior)
    try:
        apps = executor.loader.project_state(anterior).apps
        Pessoa = apps.get_model("academico", "Pessoa")
        Conclusao = apps.get_model("academico", "ConclusaoAcademica")
        Pesquisa = apps.get_model("instrumento", "Pesquisa")
        Versao = apps.get_model("instrumento", "Versao")
        Campanha = apps.get_model("campanha", "Campanha")
        Participacao = apps.get_model("participacao", "Participacao")
        Snapshot = apps.get_model("analitico", "SnapshotAnalitico")
        Registro = apps.get_model("analitico", "RegistroDoSnapshot")
        pessoa = Pessoa.objects.create(
            fonte="simulada", id_externo="historica", incorporado_em=c.NO_PERIODO
        )
        x = Conclusao.objects.create(
            pessoa=pessoa, fonte="simulada", id_externo="X", incorporado_em=c.NO_PERIODO
        )
        y = Conclusao.objects.create(
            pessoa=pessoa, fonte="simulada", id_externo="Y", incorporado_em=c.NO_PERIODO
        )
        pesquisa = Pesquisa.objects.create(nome="Histórica")
        versao = Versao.objects.create(
            pesquisa=pesquisa, designacao="1", estado="PUBLICADA", publicada_em=c.NO_PERIODO
        )
        campanha = Campanha.objects.create(
            nome="Histórica",
            versao=versao,
            inicio=c.INICIO,
            fim="2027-06-30",
            aberta_em=c.NO_PERIODO,
            encerrada_em=c.NO_PERIODO,
        )
        p = Participacao.objects.create(campanha=campanha, conclusao=x, iniciada_em=c.NO_PERIODO)
        s = Snapshot.objects.create(campanha=campanha, capturado_em=c.NO_PERIODO)
        a = Registro.objects.create(snapshot=s, conclusao=x, elegivel_no_snapshot=True)
        b = Registro.objects.create(snapshot=s, conclusao=y, elegivel_no_snapshot=True)
        campos_anteriores = [campo.name for campo in Registro._meta.concrete_fields]
        linhas_antes = list(Registro.objects.order_by("id").values(*campos_anteriores))
        totais_antes = (2, 1, 0)  # elegíveis, iniciadas, concluídas no contrato anterior
        executor = MigrationExecutor(connection)
        executor.migrate(finais)
        Registro = executor.loader.project_state(finais).apps.get_model(
            "analitico", "RegistroDoSnapshot"
        )
        assert Registro.objects.get(pk=a.pk).participacao_id == p.pk
        assert Registro.objects.get(pk=a.pk).origem_formacao == "institucional"
        assert Registro.objects.get(pk=b.pk).participacao_id is None
        assert Registro.objects.get(pk=b.pk).origem_formacao is None
        assert list(Registro.objects.order_by("id").values(*campos_anteriores)) == linhas_antes
        from trajetoria.analitico.consultas import indicadores_do_snapshot
        from trajetoria.analitico.models import SnapshotAnalitico

        indicadores = indicadores_do_snapshot(SnapshotAnalitico.objects.get(pk=s.pk))
        assert (
            indicadores.elegiveis, indicadores.iniciadas, indicadores.concluidas
        ) == totais_antes
    finally:
        MigrationExecutor(connection).migrate(finais)


def test_aborta_ambiguidade():
    modulo = importlib.import_module("trajetoria.analitico.migrations.0002_registro_participacao")
    par = SimpleNamespace(campanha_id="C", conclusao_id="X", pk="P")
    with pytest.raises(RuntimeError):
        modulo.verificar_pares([par, par])

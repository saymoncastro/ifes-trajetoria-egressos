"""Captura do snapshot (US1, US2; spec FR-010 a FR-016, FR-052, FR-053; casos A, B, L, M)."""

import inspect

import pytest
from django.utils import timezone

from tests.analitico import construcao as c
from trajetoria.analitico import operacoes
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.analitico.regras import CapturaInconsistente, Motivo, SnapshotRecusado
from trajetoria.instrumento.models import EstadoVersao, Versao
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def _nada_gravado():
    assert not SnapshotAnalitico.objects.exists()
    assert not RegistroDoSnapshot.objects.exists()


# --- US1: captura permitida ------------------------------------------------------------------


def test_captura_campanha_aberta_e_encerrada_explicitamente(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao, fim_no_passado=False)
    conclusao = c.conclusao(unidade="Serra")
    c.concluida(campanha, conclusao, inst)
    c.encerrar_no_passado(campanha)

    antes = timezone.now()
    snapshot = capturar_snapshot(campanha)
    depois = timezone.now()

    gravado = SnapshotAnalitico.objects.get(pk=snapshot.pk)
    assert gravado.campanha_id == campanha.pk
    assert antes <= gravado.capturado_em <= depois
    assert list(gravado.registros.values_list("conclusao_id", flat=True)) == [conclusao.pk]


def test_captura_campanha_encerrada_pelo_fim_do_periodo(cenario):
    assert cenario.campanha.encerrada_em is None
    snapshot = capturar_snapshot(cenario.campanha)
    assert snapshot.registros.count() == len(cenario.elegiveis)


def test_a_operacao_nao_aceita_momento_informado():
    parametros = inspect.signature(capturar_snapshot).parameters
    assert list(parametros) == ["campanha"]


def test_argumento_que_nao_e_campanha_e_erro_de_programacao(django_assert_num_queries):
    with django_assert_num_queries(0), pytest.raises(TypeError):
        capturar_snapshot("campanha")


def test_campanha_encerrada_sem_participacoes(campanha_v):
    snapshot = capturar_snapshot(campanha_v)
    assert not Participacao.objects.filter(campanha=campanha_v).exists()
    assert snapshot.registros.count() == 2
    assert set(snapshot.registros.values_list("elegivel_no_snapshot", flat=True)) == {True}


def test_populacao_vazia_sem_participacoes_gera_snapshot_vazio(inst):
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Unidade inexistente"])
    snapshot = capturar_snapshot(campanha)
    assert SnapshotAnalitico.objects.filter(pk=snapshot.pk).exists()
    assert snapshot.registros.count() == 0


def test_a_captura_nao_altera_nada_existente(cenario):
    antes = c.contagens()
    dados = {
        "campanha": list(type(cenario.campanha).objects.values()),
        "conclusoes": list(type(cenario.cefor).objects.order_by("id").values()),
        "participacoes": list(Participacao.objects.order_by("id").values()),
    }
    capturar_snapshot(cenario.campanha)
    depois = c.contagens()
    assert depois["analitico.SnapshotAnalitico"] == 1
    assert depois["analitico.RegistroDoSnapshot"] == len(cenario.elegiveis)
    for modelo, n in antes.items():
        if not modelo.startswith("analitico."):
            assert depois[modelo] == n, modelo
    assert dados == {
        "campanha": list(type(cenario.campanha).objects.values()),
        "conclusoes": list(type(cenario.cefor).objects.order_by("id").values()),
        "participacoes": list(Participacao.objects.order_by("id").values()),
    }


# --- US1: atomicidade -------------------------------------------------------------------------


def test_falha_na_gravacao_dos_registros_nao_deixa_nada(cenario, monkeypatch):
    def falha(*args, **kwargs):
        raise RuntimeError("falha simulada na gravação")

    monkeypatch.setattr(operacoes.RegistroDoSnapshot.objects, "bulk_create", falha)
    with pytest.raises(RuntimeError, match="falha simulada"):
        capturar_snapshot(cenario.campanha)
    _nada_gravado()


def test_participacao_confirmada_depois_da_leitura_faz_a_captura_falhar(cenario, monkeypatch):
    # Simula escrita concorrente iniciada antes do encerramento e confirmada depois da leitura
    # do universo (spec FR-054): uma Participação de Conclusão fora do universo aparece.
    original = operacoes._universo

    def com_escrita_tardia(campanha):
        universo = original(campanha)
        Participacao.objects.create(
            campanha=campanha, conclusao=cenario.cefor, iniciada_em=c.na_coleta()
        )
        return universo

    monkeypatch.setattr(operacoes, "_universo", com_escrita_tardia)
    with pytest.raises(CapturaInconsistente):
        capturar_snapshot(cenario.campanha)
    _nada_gravado()
    assert not Participacao.objects.filter(conclusao=cenario.cefor).exists()


def test_versao_nao_publicada_e_inconsistencia(cenario):
    # Impossível pelas operações da 004; forçado só para exercitar a guarda de integridade.
    Versao.objects.filter(pk=cenario.campanha.versao_id).update(
        estado=EstadoVersao.RASCUNHO, publicada_em=None
    )
    with pytest.raises(CapturaInconsistente):
        capturar_snapshot(cenario.campanha)
    _nada_gravado()


# --- US2: momento permitido -------------------------------------------------------------------


def _recusa(campanha, motivo):
    with pytest.raises(SnapshotRecusado) as erro:
        capturar_snapshot(campanha)
    assert erro.value.motivo is motivo
    assert erro.value.campanha_id == campanha.pk
    _nada_gravado()
    return str(erro.value)


def test_campanha_em_coleta_e_recusada(campanha_c):
    texto = _recusa(campanha_c, Motivo.COLETA_NAO_ENCERRADA)
    assert "a coleta ainda não terminou" in texto
    assert str(campanha_c.pk) in texto


def test_campanha_nunca_aberta_e_recusada(campanha_p):
    texto = _recusa(campanha_p, Motivo.CAMPANHA_NUNCA_ABERTA)
    assert "a Campanha nunca entrou em coleta" in texto


def test_campanha_nunca_aberta_e_expirada_e_recusada_como_nunca_aberta(campanha_x):
    _recusa(campanha_x, Motivo.CAMPANHA_NUNCA_ABERTA)


def test_campanha_com_abertura_futura_nao_esta_encerrada(inst):
    from datetime import timedelta

    from tests.acompanhamento.construcao import hoje, momento_em
    from trajetoria.campanha import operacoes as op_campanha

    campanha = op_campanha.criar_campanha("Campanha futura", inst.versao)
    d = hoje()
    op_campanha.definir_periodo(campanha, d + timedelta(days=10), d + timedelta(days=40))
    op_campanha.abrir(campanha, agora=momento_em(d + timedelta(days=11)))
    campanha.refresh_from_db()
    _recusa(campanha, Motivo.COLETA_NAO_ENCERRADA)


def test_mensagem_de_recusa_sem_valores_academicos(inst):
    campanha = c.campanha_em_coleta(inst.versao, unidades=["Unidade Muito Especifica"])
    c.conclusao(unidade="Unidade Muito Especifica", curso="Curso Muito Especifico")
    texto = _recusa(campanha, Motivo.COLETA_NAO_ENCERRADA)
    assert "Especific" not in texto


def test_participacao_de_elegivel_sem_registro_faz_a_captura_falhar(cenario, monkeypatch):
    # Regressão (code review da 019): o universo tem registros sem Participação
    # (`participacao_id` NULL). A escrita tardia de uma oficial para um desses elegíveis não
    # pode escapar da verificação final por causa do NULL dentro do `NOT IN`.
    original = operacoes._participantes_por_conclusao

    def com_escrita_tardia(campanha):
        participantes = original(campanha)
        Participacao.objects.create(
            campanha=campanha, conclusao=cenario.serra_sem_participacao, iniciada_em=c.na_coleta()
        )
        return participantes

    monkeypatch.setattr(operacoes, "_participantes_por_conclusao", com_escrita_tardia)
    with pytest.raises(CapturaInconsistente):
        capturar_snapshot(cenario.campanha)
    _nada_gravado()
    assert not Participacao.objects.filter(conclusao=cenario.serra_sem_participacao).exists()

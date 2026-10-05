"""Prévia e confirmação do Lote (020 FR-015, FR-019 a FR-023; T016)."""

import pytest
from django.utils import timezone

from tests.editor.construcao_editor import A, B, C
from tests.mobilizacao.conftest import pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.mobilizacao.acesso import RecusaDeLote
from trajetoria.mobilizacao.models import LoteDeMobilizacao, MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.operacoes import confirmar_lote, previa

pytestmark = pytest.mark.django_db
S = SituacaoDoMembro
VITORIA = {"unidades": ["Vitória"]}


def _recusa(categoria, status, fn, *args, **kwargs):
    with pytest.raises(RecusaDeLote) as exc:
        fn(*args, **kwargs)
    assert (exc.value.categoria, exc.value.status) == (categoria, status)


def test_previa_nao_grava(ampla):
    p = previa(ampla.pk, A, VITORIA)
    assert (p.pessoas, p.com_contato, p.sem_contato, p.excluidas) == (2, 1, 1, 0)
    assert not LoteDeMobilizacao.objects.exists() and not MembroDoLote.objects.exists()


def test_confirmacao_grava_lote_e_membros(ampla):
    lote = confirmar_lote(ampla.pk, A, "  Vitória — 1ª onda ", VITORIA)
    assert lote.nome == "Vitória — 1ª onda"
    assert (lote.unidades, lote.escopo_institucional, lote.operador) == (["Vitória"], True, A)
    membros = {m.pessoa.id_externo: m for m in lote.membros.select_related("pessoa", "contato")}
    assert set(membros) == {"SIM-P-0002", "SIM-P-0010"}
    assert membros["SIM-P-0002"].situacao == S.NAO_TENTADO
    assert membros["SIM-P-0002"].contato.valor == "sim-p-0002@example.invalid"
    assert membros["SIM-P-0010"].situacao == S.SEM_CONTATO
    assert membros["SIM-P-0010"].contato is None
    assert all(m.campanha_id == ampla.pk for m in membros.values())


def test_csaeg_registra_escopo(ampla):
    lote = confirmar_lote(ampla.pk, B, "Vitória", VITORIA)
    assert (lote.escopo_institucional, lote.escopo_unidades) == (False, ["Vitória"])


def test_estado_da_campanha(ampla, em_preparacao):
    assert confirmar_lote(em_preparacao.pk, A, "Antes da coleta", VITORIA)
    op_campanha.encerrar(ampla)
    _recusa("campanha_encerrada", 409, confirmar_lote, ampla.pk, A, "Tarde", VITORIA)
    assert not LoteDeMobilizacao.objects.filter(campanha=ampla).exists()


def test_lote_vazio_nao_e_gravado(ampla):
    _recusa("lote_vazio", 422, confirmar_lote, ampla.pk, A, "Vazio", {"curso": "Inexistente"})
    assert not LoteDeMobilizacao.objects.exists()


def test_sem_filtros_exige_confirmacao_de_abrangencia(ampla):
    assert previa(ampla.pk, A, {}).exige_confirmacao_de_abrangencia
    _recusa("confirmacao_de_abrangencia", 422, confirmar_lote, ampla.pk, A, "Todos", {})
    lote = confirmar_lote(ampla.pk, A, "Todos", {}, True)
    assert lote.membros.count() == 9
    assert lote.unidades is None


@pytest.mark.parametrize("nome", ["", "   ", "x" * 121, "a\nb", None])
def test_nome_invalido(ampla, nome):
    _recusa("nome_invalido", 422, confirmar_lote, ampla.pk, A, nome, VITORIA)


def test_operador_e_capacidade_revalidados(ampla, settings):
    for operador in (C, "real", None):
        _recusa("sem_autorizacao", 403, confirmar_lote, ampla.pk, operador, "x", VITORIA)
    settings.TRAJETORIA_DEMONSTRACAO = False
    _recusa("modo_desligado", 404, confirmar_lote, ampla.pk, A, "x", VITORIA)


def test_cliente_nao_define_lista_nem_contato(ampla, clientes):
    resposta = clientes[A].post(
        f"/acompanhamento/campanhas/{ampla.pk}/lotes/confirmar/",
        {"nome": "Vitória", "unidade": "Vitória", "pessoa": str(pessoa("SIM-P-0001").pk),
         "contato": "real@external.test", "destinatario": "real@external.test"},
    )
    assert resposta.status_code == 303
    lote = LoteDeMobilizacao.objects.get()
    assert resposta["Location"] == f"/acompanhamento/campanhas/{ampla.pk}/lotes/{lote.pk}/"
    assert set(lote.membros.values_list("pessoa__id_externo", flat=True)) == {
        "SIM-P-0002", "SIM-P-0010",
    }


def test_confirmacao_usa_o_instante_informado(ampla):
    agora = timezone.now()
    assert confirmar_lote(ampla.pk, A, "x", VITORIA, agora=agora).confirmado_em == agora

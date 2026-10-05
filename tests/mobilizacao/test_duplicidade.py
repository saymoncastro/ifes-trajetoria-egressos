"""Uma abordagem por Pessoa e Campanha (020 FR-024; T035)."""

import pytest
from django.utils import timezone

from tests.contato.conftest import contato
from tests.editor.construcao_editor import A
from tests.mobilizacao.conftest import pessoa
from trajetoria.contato.models import Origem
from trajetoria.mobilizacao.models import MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote, previa

pytestmark = pytest.mark.django_db
S = SituacaoDoMembro
VITORIA = {"unidades": ["Vitória"]}


def _membros(lote):
    return set(lote.membros.values_list("pessoa__id_externo", flat=True))


@pytest.mark.parametrize(
    "situacao",
    [S.NAO_TENTADO, S.EM_TENTATIVA, S.SUBMETIDO_AO_TRANSPORTE, S.FALHA_DE_TRANSPORTE],
)
def test_abordada_ou_pendente_e_excluida(ampla, situacao):
    a = confirmar_lote(ampla.pk, A, "A", VITORIA)
    agora = timezone.now()
    instantes = {
        S.NAO_TENTADO: {},
        S.EM_TENTATIVA: {"tentativa_iniciada_em": agora},
    }.get(situacao, {"tentativa_iniciada_em": agora, "resultado_em": agora})
    a.membros.filter(pessoa__id_externo="SIM-P-0002").update(situacao=situacao, **instantes)
    p = previa(ampla.pk, A, {"unidades": ["Vitória", "Serra"]})
    assert p.excluidas == 1
    b = confirmar_lote(ampla.pk, A, "B", {"unidades": ["Vitória", "Serra"]})
    assert "SIM-P-0002" not in _membros(b)
    assert b.excluidas_por_mobilizacao == 1


def test_sem_contato_pode_voltar_com_o_email_informado(ampla):
    a = confirmar_lote(ampla.pk, A, "A", VITORIA)
    assert a.membros.get(pessoa__id_externo="SIM-P-0010").situacao == S.SEM_CONTATO
    enviar_lote(a.pk, A)
    informado = contato(pessoa("SIM-P-0010"), "carla@example.invalid", Origem.EGRESSO)
    b = confirmar_lote(ampla.pk, A, "B", VITORIA)
    assert _membros(b) == {"SIM-P-0010"}
    membro = b.membros.get()
    assert (membro.situacao, membro.contato) == (S.NAO_TENTADO, informado)


def test_outra_campanha_nao_influi(ampla, em_preparacao):
    a = confirmar_lote(ampla.pk, A, "A", VITORIA)
    enviar_lote(a.pk, A)
    b = confirmar_lote(em_preparacao.pk, A, "B", VITORIA)
    assert _membros(b) == {"SIM-P-0002", "SIM-P-0010"} and b.excluidas_por_mobilizacao == 0


def test_tudo_ja_abordado_resulta_em_lote_vazio(ampla):
    confirmar_lote(ampla.pk, A, "A", {"unidades": ["Serra"]})
    from trajetoria.mobilizacao.acesso import RecusaDeLote

    with pytest.raises(RecusaDeLote) as exc:
        confirmar_lote(ampla.pk, A, "B", {"unidades": ["Serra"]})
    assert exc.value.categoria == "lote_vazio"
    assert MembroDoLote.objects.filter(lote__nome="B").count() == 0

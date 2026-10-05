"""Concorrência entre Lotes (020 FR-024, FR-025, SC-001; research R6, R7, R14; T036).

Transações reais e duas threads: o banco e os locks garantem no máximo uma abordagem por
Pessoa e Campanha, sem gravação parcial.
"""

import threading
from io import StringIO

import pytest
from django.core import mail
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction

from tests.editor.construcao_editor import A
from trajetoria.campanha.models import Campanha
from trajetoria.mobilizacao import operacoes
from trajetoria.mobilizacao.acesso import RecusaDeLote
from trajetoria.mobilizacao.models import LoteDeMobilizacao, MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.operacoes import confirmar_lote, enviar_lote

pytestmark = pytest.mark.django_db(transaction=True)
S = SituacaoDoMembro


@pytest.fixture
def ampla_real():
    call_command("preparar_demonstracao", stdout=StringIO())
    return Campanha.objects.get(nome="Demonstração — coleta ampla")


def _em_paralelo(*funcoes):
    barreira = threading.Barrier(len(funcoes))
    resultados = [None] * len(funcoes)

    def rodar(i, f):
        try:
            barreira.wait()
            resultados[i] = f()
        except Exception as exc:  # noqa: BLE001 — o teste inspeciona
            resultados[i] = exc
        finally:
            connection.close()

    threads = [threading.Thread(target=rodar, args=(i, f)) for i, f in enumerate(funcoes)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    return resultados


def test_confirmacoes_simultaneas_sobrepostas(ampla_real):
    filtros = {"unidades": ["Vitória", "Serra"]}
    resultados = _em_paralelo(
        lambda: confirmar_lote(ampla_real.pk, A, "Um", filtros),
        lambda: confirmar_lote(ampla_real.pk, A, "Dois", filtros),
    )
    assert all(isinstance(r, LoteDeMobilizacao) for r in resultados)
    primeiro, segundo = sorted(resultados, key=lambda lote: lote.excluidas_por_mobilizacao)
    # O segundo, serializado pelo lock da Campanha, exclui todos os abordados do primeiro e
    # só repete quem ficou sem contato (que ninguém abordou).
    abordados_no_primeiro = primeiro.membros.exclude(situacao=S.SEM_CONTATO).count()
    assert segundo.excluidas_por_mobilizacao == abordados_no_primeiro > 0
    assert set(segundo.membros.values_list("situacao", flat=True)) == {S.SEM_CONTATO}
    abordados = MembroDoLote.objects.exclude(situacao=S.SEM_CONTATO)
    assert abordados.count() == abordados.values("pessoa").distinct().count()


def test_envios_simultaneos_do_mesmo_lote(ampla_real, settings):
    settings.TRAJETORIA_LOTE_ENVIO_POR_ACAO = 100
    lote = confirmar_lote(ampla_real.pk, A, "Todos", {}, True)
    resultados = _em_paralelo(lambda: enviar_lote(lote.pk, A), lambda: enviar_lote(lote.pk, A))
    assert not [r for r in resultados if isinstance(r, Exception)]
    assert sum(r.processados for r in resultados) == 8
    destinos = [m.to[0] for m in mail.outbox]
    assert len(destinos) == len(set(destinos)) == 8


def test_banco_recusa_segunda_abordagem(ampla_real):
    lote = confirmar_lote(ampla_real.pk, A, "Vitória", {"unidades": ["Vitória"]})
    outro = LoteDeMobilizacao.objects.create(
        campanha=ampla_real, nome="Manual", escopo_institucional=True,
        confirmado_em=lote.confirmado_em, operador=A,
    )
    abordado = lote.membros.get(situacao=S.NAO_TENTADO)
    with pytest.raises(IntegrityError), transaction.atomic():
        MembroDoLote.objects.create(
            lote=outro, campanha=ampla_real, pessoa=abordado.pessoa,
            contato=abordado.contato, situacao=S.NAO_TENTADO,
        )


def test_colisao_vira_recusa_sem_gravacao_parcial(ampla_real, monkeypatch):
    """FR-025: seleção calculada antes de outro Lote gravar; a restrição recusa tudo."""
    filtros = {"unidades": ["Vitória"]}
    original = operacoes.selecionar
    congelada = original(
        ampla_real, operacoes.contexto_do_operador(A).escopo,
        operacoes.Filtros.de(**filtros), operacoes.timezone.now(),
    )
    confirmar_lote(ampla_real.pk, A, "Primeiro", filtros)
    monkeypatch.setattr(operacoes, "selecionar", lambda *a, **k: congelada)
    with pytest.raises(RecusaDeLote) as exc:
        confirmar_lote(ampla_real.pk, A, "Concorrente", filtros)
    assert (exc.value.categoria, exc.value.status) == ("mobilizacao_concorrente", 409)
    assert not LoteDeMobilizacao.objects.filter(nome="Concorrente").exists()

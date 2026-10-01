"""Concorrência no início da Participação (FR-006, FR-053; research R11, R17).

O teste determinístico força o ramo em que a busca não encontra a Participação e o insert
viola a unicidade do par, como acontece quando outra transação a cria entre a busca e o
insert. É a proteção principal; não depende de escalonamento de threads.
"""

import threading

import pytest
from django.db import IntegrityError, connection

from tests.participacao.construcao import NO_PERIODO
from trajetoria.participacao import operacoes
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import SituacaoInicio, iniciar_participacao

pytestmark = pytest.mark.django_db


def test_corrida_perdida_devolve_a_participacao_da_outra_transacao(
    campanha, conclusao, monkeypatch
):
    # "Outra transação" já gravou a Participação; a busca desta ainda não a viu.
    da_outra = Participacao.objects.create(
        campanha=campanha, conclusao=conclusao, iniciada_em=NO_PERIODO
    )
    monkeypatch.setattr(operacoes, "_participacao_existente", lambda *args: None)

    inicio = iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)

    assert inicio.situacao is SituacaoInicio.JA_EXISTENTE
    assert inicio.participacao.id == da_outra.id
    assert Participacao.objects.count() == 1


def test_integrity_error_alheio_ao_par_e_relancado(campanha, conclusao, monkeypatch):
    # Se o insert falhar por outro motivo e não houver Participação do par, o erro original
    # não é mascarado como JA_EXISTENTE (tasks, U1).
    def falha(*args, **kwargs):
        raise IntegrityError("outra restrição")

    monkeypatch.setattr(operacoes.Participacao.objects, "create", falha)
    with pytest.raises(IntegrityError, match="outra restrição"):
        iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)
    assert not Participacao.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_inicios_simultaneos_em_threads_criam_uma_so_participacao(campanha, conclusao):
    # Opcional (research R17): prova com transações reais; o teste determinístico acima é
    # a proteção suficiente. Remover se ficar instável no CI.
    barreira = threading.Barrier(2)
    resultados, erros = [], []

    def iniciar():
        try:
            barreira.wait(timeout=10)
            resultados.append(iniciar_participacao(campanha, conclusao, agora=NO_PERIODO))
        except Exception as erro:  # noqa: BLE001 — o teste exibe qualquer falha da thread
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=iniciar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not erros
    assert Participacao.objects.count() == 1
    assert len({r.participacao.id for r in resultados}) == 1
    assert sorted(r.situacao.value for r in resultados) == ["criada", "ja_existente"]

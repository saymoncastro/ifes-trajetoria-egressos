"""Lote e membros (020 data-model §§2–3; T011)."""

from datetime import UTC, datetime

import pytest
from django.db import IntegrityError, transaction

from tests.contato.conftest import contato
from tests.mobilizacao.conftest import lote_direto, pessoa
from trajetoria.mobilizacao.models import MembroDoLote, SituacaoDoMembro

pytestmark = pytest.mark.django_db
S = SituacaoDoMembro
T1 = datetime(2026, 10, 4, 13, tzinfo=UTC)
T2 = datetime(2026, 10, 4, 14, tzinfo=UTC)


def _recusa(fabrica):
    with pytest.raises(IntegrityError), transaction.atomic():
        fabrica()


def _membro(lote, p, situacao, contato_=None, **campos):
    return MembroDoLote.objects.create(
        lote=lote, campanha=lote.campanha, pessoa=p, situacao=situacao, contato=contato_, **campos
    )


def test_lote_checks(ampla):
    _recusa(lambda: lote_direto(ampla, nome=""))
    _recusa(lambda: lote_direto(ampla, operador=""))
    _recusa(lambda: lote_direto(ampla, unidades=[]))
    _recusa(lambda: lote_direto(ampla, nivel=""))
    _recusa(lambda: lote_direto(ampla, curso=""))
    _recusa(lambda: lote_direto(ampla, ano_minimo=2020, ano_maximo=2010))
    _recusa(lambda: lote_direto(ampla, escopo_unidades=["Vitória"]))
    _recusa(lambda: lote_direto(ampla, escopo_institucional=False, escopo_unidades=["Vitória"]))
    _recusa(lambda: lote_direto(ampla, escopo_institucional=False, unidades=["Vitória"]))
    lote_direto(ampla, escopo_institucional=False, unidades=["Vitória"],
                escopo_unidades=["Vitória"])


def test_membro_checks_e_unicidades(ampla):
    lote = lote_direto(ampla)
    ana = pessoa("SIM-P-0001")
    c = contato(ana, "x@example.invalid")
    _recusa(lambda: _membro(lote, ana, S.SEM_CONTATO, c))
    _recusa(lambda: _membro(lote, ana, S.NAO_TENTADO))
    _recusa(lambda: _membro(lote, ana, "ENTREGUE", c))
    _recusa(lambda: _membro(lote, ana, S.NAO_TENTADO, c, tentativa_iniciada_em=T1))
    _recusa(lambda: _membro(lote, ana, S.EM_TENTATIVA, c))
    _recusa(lambda: _membro(lote, ana, S.SUBMETIDO_AO_TRANSPORTE, c, tentativa_iniciada_em=T1))
    _recusa(lambda: _membro(lote, ana, S.FALHA_DE_TRANSPORTE, c, tentativa_iniciada_em=T2,
                            resultado_em=T1))
    _membro(lote, ana, S.SUBMETIDO_AO_TRANSPORTE, c, tentativa_iniciada_em=T1, resultado_em=T2)
    _recusa(lambda: _membro(lote, ana, S.SEM_CONTATO))  # uma vez por Lote


def test_uma_abordagem_por_pessoa_e_campanha(ampla, em_preparacao):
    a, b = lote_direto(ampla), lote_direto(ampla)
    ana = pessoa("SIM-P-0001")
    c = contato(ana, "x@example.invalid")
    _membro(a, ana, S.NAO_TENTADO, c)
    _recusa(lambda: _membro(b, ana, S.NAO_TENTADO, c))
    _membro(b, ana, S.SEM_CONTATO)  # sem contato não é abordagem
    _membro(lote_direto(em_preparacao), ana, S.NAO_TENTADO, c)  # outra Campanha não conta

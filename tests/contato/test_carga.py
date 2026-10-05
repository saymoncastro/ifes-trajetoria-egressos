"""Carga de contatos da fonte (020 contracts/fonte-de-contatos.md; research R2; T038)."""

import logging

import pytest

from tests.contato.conftest import T0, depois
from trajetoria.academico.models import Pessoa
from trajetoria.contato.carga import SituacaoDaCarga, carregar_contatos
from trajetoria.contato.models import ContatoDaPessoa, Origem
from trajetoria.demonstracao.cenario import preparar
from trajetoria.fonte_academica.contatos_simulados import ContatosSimulados

pytestmark = pytest.mark.django_db
S = SituacaoDaCarga


def _fonte(*emails, indisponivel=False):
    return ContatosSimulados({"TESTE-P-1": emails}, indisponivel=indisponivel)


def _gravados(pessoa):
    return list(
        ContatoDaPessoa.objects.filter(pessoa=pessoa)
        .order_by("obtido_em", "posicao")
        .values_list("valor", "posicao", "obtido_em")
    )


def test_primeira_carga_grava_uma_observacao(pessoa):
    r = carregar_contatos(_fonte("A@Example.Invalid", "b@example.invalid"), pessoa, agora=T0)
    assert (r.situacao, r.gravados) == (S.CARREGADO, 2)
    assert _gravados(pessoa) == [("A@example.invalid", 0, T0), ("b@example.invalid", 1, T0)]
    assert set(ContatoDaPessoa.objects.values_list("origem", "fonte")) == {
        (Origem.FONTE_ACADEMICA, "simulada")
    }


def test_mesma_lista_nao_grava(pessoa):
    fonte = _fonte("a@example.invalid", "b@example.invalid")
    carregar_contatos(fonte, pessoa, agora=T0)
    r = carregar_contatos(fonte, pessoa, agora=depois(5))
    assert r.situacao is S.INALTERADO
    assert ContatoDaPessoa.objects.count() == 2


def test_reordenacao_e_valor_novo_gravam_observacao_preservando_a_anterior(pessoa):
    carregar_contatos(_fonte("a@example.invalid", "b@example.invalid"), pessoa, agora=T0)
    carregar_contatos(_fonte("b@example.invalid", "a@example.invalid"), pessoa, agora=depois(1))
    carregar_contatos(_fonte("c@example.invalid"), pessoa, agora=depois(2))
    assert _gravados(pessoa) == [
        ("a@example.invalid", 0, T0), ("b@example.invalid", 1, T0),
        ("b@example.invalid", 0, depois(1)), ("a@example.invalid", 1, depois(1)),
        ("c@example.invalid", 0, depois(2)),
    ]


def test_lista_vazia_nao_grava_nem_apaga(pessoa):
    carregar_contatos(_fonte("a@example.invalid"), pessoa, agora=T0)
    assert carregar_contatos(_fonte(), pessoa, agora=depois(1)).situacao is S.SEM_EMAIL
    assert ContatoDaPessoa.objects.count() == 1


def test_indisponivel_nao_grava_e_nao_e_sem_email(pessoa, caplog):
    with caplog.at_level(logging.WARNING, logger="trajetoria"):
        r = carregar_contatos(_fonte("a@example.invalid", indisponivel=True), pessoa, agora=T0)
    assert r.situacao is S.INDISPONIVEL
    assert not ContatoDaPessoa.objects.exists()
    assert "simulada" in caplog.text and "@" not in caplog.text


def test_invalido_ignorado_sem_valor_no_log(pessoa, caplog):
    with caplog.at_level(logging.WARNING, logger="trajetoria"):
        r = carregar_contatos(_fonte("marcador invalido@x", "ok@example.invalid"), pessoa,
                              agora=T0)
    assert (r.situacao, r.gravados, r.ignorados_invalidos) == (S.CARREGADO, 1, 1)
    assert "marcador" not in caplog.text
    assert _gravados(pessoa) == [("ok@example.invalid", 0, T0)]


def test_preparo_carrega_contatos_ficticios_e_e_idempotente(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar()
    diego = Pessoa.objects.get(id_externo="SIM-P-0004")
    assert list(
        ContatoDaPessoa.objects.filter(pessoa=diego).order_by("posicao").values_list("valor")
    ) == [("sim-p-0004@example.invalid",), ("sim-p-0004.alternativo@example.invalid",)]
    assert not ContatoDaPessoa.objects.filter(pessoa__id_externo="SIM-P-0010").exists()
    assert all(v.endswith("@example.invalid") for v in
               ContatoDaPessoa.objects.values_list("valor", flat=True))
    antes = ContatoDaPessoa.objects.count()
    preparar()
    assert ContatoDaPessoa.objects.count() == antes


def test_falha_numa_pessoa_nao_afeta_as_demais(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True

    class Quebradica(ContatosSimulados):
        def obter_emails(self, id_externo):
            if id_externo == "SIM-P-0001":
                raise RuntimeError("falha inesperada")
            return super().obter_emails(id_externo)

    preparar(fonte_de_contatos=Quebradica())
    assert not ContatoDaPessoa.objects.filter(pessoa__id_externo="SIM-P-0001").exists()
    assert ContatoDaPessoa.objects.filter(pessoa__id_externo="SIM-P-0002").exists()

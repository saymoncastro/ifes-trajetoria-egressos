"""Carga do contexto da trajetória (021 contracts/contexto-da-trajetoria.md, tabela "Carga";
FR-048, FR-049, FR-056, FR-057, FR-062)."""

from datetime import date

import pytest

from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.contexto_trajetoria.carga import SituacaoDaCarga, carregar_contexto
from trajetoria.contexto_trajetoria.models import (
    ComplementoDaConclusao,
    ContextoInstitucionalAgregado,
)
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db
APURACAO = date(2026, 1, 31)


class Espia:
    codigo = "simulada"

    def __init__(self, interna=None):
        self.chamadas = []
        self.interna = interna or ContextoSimulado()

    def obter_contexto(self, ids):
        self.chamadas.append(ids)
        return self.interna.obter_contexto(ids)


@pytest.fixture
def pessoas():
    ce.incorporar(FonteSimulada(), "SIM-P-0001", "SIM-P-0003", "SIM-P-0004")
    return {i: ce.pessoa_da_fonte(i) for i in ("SIM-P-0001", "SIM-P-0003", "SIM-P-0004")}


def _estado():
    return (
        list(Pessoa.objects.order_by("pk").values()),
        list(ConclusaoAcademica.objects.order_by("pk").values()),
    )


def test_pessoa_sem_conclusoes_daquela_fonte_nao_consulta(pessoas):
    espia = Espia()
    espia.codigo = "outra"
    assert carregar_contexto(espia, pessoas["SIM-P-0001"]).situacao is (
        SituacaoDaCarga.SEM_CONCLUSOES
    )
    assert espia.chamadas == []


def test_indisponivel_nao_grava_nem_propaga(pessoas):
    antes = _estado()
    resultado = carregar_contexto(ContextoSimulado(indisponivel=True), pessoas["SIM-P-0001"])
    assert resultado.situacao is SituacaoDaCarga.INDISPONIVEL
    assert not ComplementoDaConclusao.objects.exists()
    assert not ContextoInstitucionalAgregado.objects.exists()
    assert _estado() == antes


def test_ana_cria_complemento_e_agregados(pessoas):
    resultado = carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    assert (resultado.complementos_criados, resultado.agregados_criados) == (1, 2)
    complemento = ComplementoDaConclusao.objects.get()
    assert complemento.conclusao.id_externo == "SIM-C-0001" and complemento.ano_ingresso == 2019


def test_idempotente(pessoas):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    de_novo = carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    assert (de_novo.complementos_criados, de_novo.agregados_criados, de_novo.sinais) == (0, 0, ())
    assert ComplementoDaConclusao.objects.count() == 1
    assert ContextoInstitucionalAgregado.objects.count() == 2


def test_complemento_diferente_so_sinaliza(pessoas, caplog, django_capture_on_commit_callbacks):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    outra = ContextoSimulado(complementos={"SIM-C-0001": (2018, None)})
    with django_capture_on_commit_callbacks(execute=True):
        resultado = carregar_contexto(outra, pessoas["SIM-P-0001"])
    assert [s.tipo for s in resultado.sinais] == ["complemento_diferente"]
    assert ComplementoDaConclusao.objects.get().ano_ingresso == 2019
    assert "simulada:SIM-C-0001 (campos: ano_ingresso)" in caplog.text
    assert "2018" not in caplog.text and "Ana" not in caplog.text


def test_complemento_acrescentado_depois(pessoas):
    carregar_contexto(ContextoSimulado(complementos={}), pessoas["SIM-P-0001"])
    assert not ComplementoDaConclusao.objects.exists()
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    assert ComplementoDaConclusao.objects.get().ano_ingresso == 2019


def test_mesmo_recorte_de_duas_pessoas_um_registro(pessoas):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    resultado = carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0003"])  # Maria: TADS/2022
    assert resultado.agregados_criados == 0
    assert ContextoInstitucionalAgregado.objects.count() == 2


def test_mesma_chave_valor_diferente_e_erro_de_fonte(
    pessoas, caplog, django_capture_on_commit_callbacks
):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    divergente = tuple(
        (m, c, u, a, v + 1 if m == "conclusoes_curso_unidade_ano" else v, ap)
        for m, c, u, a, v, ap in cenarios.AGREGADOS
    )
    with django_capture_on_commit_callbacks(execute=True):
        resultado = carregar_contexto(ContextoSimulado(agregados=divergente), pessoas["SIM-P-0003"])
    assert [s.tipo for s in resultado.sinais] == ["agregado_divergente"]
    assert ContextoInstitucionalAgregado.objects.get(curso=cenarios.TADS).valor == 27
    assert "conclusoes_curso_unidade_ano" in caplog.text and "Maria" not in caplog.text


def test_nova_apuracao_e_registro_novo(pessoas):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    nova = tuple((m, c, u, a, v, date(2027, 1, 31)) for m, c, u, a, v, _ in cenarios.AGREGADOS)
    carregar_contexto(ContextoSimulado(agregados=nova), pessoas["SIM-P-0001"])
    assert ContextoInstitucionalAgregado.objects.count() == 4
    assert ContextoInstitucionalAgregado.objects.filter(apurado_em=APURACAO).count() == 2


def test_logs_so_depois_do_commit(pessoas, caplog, django_capture_on_commit_callbacks):
    carregar_contexto(ContextoSimulado(), pessoas["SIM-P-0001"])
    outra = ContextoSimulado(complementos={"SIM-C-0001": (2018, None)})
    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        carregar_contexto(outra, pessoas["SIM-P-0001"])
        assert "complemento_diferente" not in caplog.text
    assert len(callbacks) == 1


def test_ignora_complemento_de_conclusao_nao_pedida(pessoas):
    class Fora:
        codigo = "simulada"

        def obter_contexto(self, ids):
            from trajetoria.fonte_academica.contexto_da_trajetoria import (
                ComplementoNaFonte,
                ContextoDaTrajetoriaNaFonte,
            )

            return ContextoDaTrajetoriaNaFonte((ComplementoNaFonte("SIM-C-0004", 2018),), ())

    carregar_contexto(Fora(), pessoas["SIM-P-0001"])  # SIM-C-0004 é da Maria
    assert not ComplementoDaConclusao.objects.exists()

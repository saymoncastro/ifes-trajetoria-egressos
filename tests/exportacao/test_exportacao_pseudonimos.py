"""Pseudônimos analíticos (spec FR-026 a FR-029; research R5)."""

import hashlib
import hmac
import re
from uuid import UUID

import pytest

from tests.analitico import construcao as c
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao.contrato import ESQUEMA_PSEUDONIMIZACAO
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import exportar_csv, exportar_xlsx
from trajetoria.exportacao.pseudonimos import chave_de_pseudonimizacao, pseudonimo
from trajetoria.exportacao.regras import ExportacaoInconsistente, ExportacaoRecusada, Motivo
from trajetoria.participacao.models import Resposta

UUID_FIXO = UUID("12345678-1234-5678-1234-567812345678")
CHAVE_FIXA = "chave-de-teste-fixa-com-mais-de-32-caracteres"


# --- Fundação -------------------------------------------------------------------------------------


def test_vetor_fixo_e_hmac_sha256_com_dominio():
    esperado = hmac.new(
        CHAVE_FIXA.encode("utf-8"), f"conclusao:{UUID_FIXO}".encode(), hashlib.sha256
    ).hexdigest()
    assert pseudonimo("conclusao", UUID_FIXO, CHAVE_FIXA) == esperado


def test_resultado_opaco_sem_o_uuid():
    valor = pseudonimo("pessoa", UUID_FIXO, CHAVE_FIXA)
    assert re.fullmatch(r"[0-9a-f]{64}", valor)
    assert UUID_FIXO.hex not in valor and str(UUID_FIXO) not in valor


def test_separacao_de_dominio():
    assert pseudonimo("pessoa", UUID_FIXO, CHAVE_FIXA) != pseudonimo(
        "conclusao", UUID_FIXO, CHAVE_FIXA
    )


def test_dominio_desconhecido():
    with pytest.raises(ValueError):
        pseudonimo("participacao", UUID_FIXO, CHAVE_FIXA)


def test_chave_ausente(settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = ""
    with pytest.raises(ExportacaoRecusada) as erro:
        chave_de_pseudonimizacao()
    assert erro.value.motivo is Motivo.CHAVE_AUSENTE


def test_chave_curta(settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "x" * 31
    with pytest.raises(ExportacaoRecusada) as erro:
        chave_de_pseudonimizacao()
    assert erro.value.motivo is Motivo.CHAVE_INADEQUADA


def test_chave_igual_ao_segredo_da_aplicacao(settings):
    settings.SECRET_KEY = "s" * 40
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "s" * 40
    with pytest.raises(ExportacaoRecusada) as erro:
        chave_de_pseudonimizacao()
    assert erro.value.motivo is Motivo.CHAVE_INADEQUADA


def test_chave_adequada(settings):
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "k" * 32
    assert chave_de_pseudonimizacao() == "k" * 32


def test_esquema():
    assert ESQUEMA_PSEUDONIMIZACAO == "hmac-sha256-v1"


# --- US12: vínculo longitudinal ------------------------------------------------------------------


def _ids(snapshot) -> list[tuple[str, str]]:
    return [(linha[0], linha[1]) for linha in dataset_exportado(snapshot).dados.linhas]


@pytest.fixture
def duas_campanhas(inst):
    """A mesma Conclusão (e uma segunda da mesma Pessoa) em duas Campanhas encerradas."""
    primeira = c.conclusao(unidade="Serra", curso="A")
    segunda = c.conclusao(unidade="Serra", curso="B", pessoa=primeira.pessoa)
    snapshots = []
    for _ in range(2):
        campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
        c.iniciada(campanha, primeira)
        snapshots.append(capturar_snapshot(campanha))
    return snapshots, primeira, segunda


@pytest.mark.django_db
def test_mesma_conclusao_em_campanhas_diferentes_com_a_mesma_chave(duas_campanhas):  # caso U
    (a, b), _, _ = duas_campanhas
    assert set(_ids(a)) == set(_ids(b))


@pytest.mark.django_db
def test_mesma_pessoa_duas_conclusoes(duas_campanhas, chave_ficticia):
    (a, _), primeira, segunda = duas_campanhas
    por_conclusao = dict(_ids(a))
    p1 = por_conclusao[pseudonimo("conclusao", primeira.pk, chave_ficticia)]
    p2 = por_conclusao[pseudonimo("conclusao", segunda.pk, chave_ficticia)]
    assert p1 == p2 == pseudonimo("pessoa", primeira.pessoa_id, chave_ficticia)


@pytest.mark.django_db
def test_outra_chave_rompe_a_ligacao(duas_campanhas, settings):
    (a, b), _, _ = duas_campanhas
    antes = {x for par in _ids(a) for x in par}
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "outra-chave-ficticia-de-teste-0000000000002"
    depois = {x for par in _ids(b) for x in par}
    assert not antes & depois


@pytest.mark.django_db
@pytest.mark.parametrize(
    "chave, motivo",
    [
        ("", Motivo.CHAVE_AUSENTE),
        ("zq9-ficticia", Motivo.CHAVE_INADEQUADA),
        (None, Motivo.CHAVE_INADEQUADA),
    ],
    ids=["ausente", "curta", "igual-ao-segredo"],
)
def test_sem_chave_adequada_nada_e_exportado(snapshot, settings, chave, motivo):  # caso V
    configurada = settings.SECRET_KEY if chave is None else chave
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = configurada
    for exportar in (exportar_csv, exportar_xlsx):
        with pytest.raises(ExportacaoRecusada) as erro:
            exportar(snapshot)
        assert erro.value.motivo is motivo
        # nem a chave nem o segredo da aplicação aparecem na mensagem (vazio: nada a vazar)
        for segredo in (configurada, settings.SECRET_KEY):
            assert not segredo or segredo not in str(erro.value)


@pytest.mark.django_db
def test_erros_nao_carregam_pseudonimos(snapshot, cenario, chave_ficticia):
    Resposta.objects.filter(participacao=cenario.concluida, pergunta=cenario.inst.escala).update(
        escala=None, texto="x"
    )
    with pytest.raises(ExportacaoInconsistente) as erro:
        dataset_exportado(snapshot)
    for conclusao in (cenario.serra_info, cenario.vitoria_info, cenario.serra_eng):
        assert pseudonimo("conclusao", conclusao.pk, chave_ficticia) not in str(erro.value)
        assert str(conclusao.pk) not in str(erro.value)

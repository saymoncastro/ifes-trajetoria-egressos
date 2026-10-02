"""Vocabulário de erro da exportação (contracts/exportacao.md; spec FR-090 a FR-093)."""

import pytest

from trajetoria.exportacao.regras import (
    ExportacaoInconsistente,
    ExportacaoRecusada,
    Motivo,
    ValorNaoRepresentavel,
)

SENTINELA = "valor-sentinela-que-nunca-aparece"


def test_motivos_exatos():
    assert {m.name: m.value for m in Motivo} == {
        "SNAPSHOT_NAO_GRAVADO": "snapshot_nao_gravado",
        "CHAVE_AUSENTE": "chave_ausente",
        "CHAVE_INADEQUADA": "chave_inadequada",
    }


@pytest.mark.parametrize("motivo", list(Motivo))
def test_recusa_expoe_o_motivo(motivo):
    recusa = ExportacaoRecusada(motivo)
    assert recusa.motivo is motivo
    assert motivo.name in str(recusa)


def test_inconsistencia_e_recusa_sao_distintas():
    assert not issubclass(ExportacaoInconsistente, ExportacaoRecusada)
    assert not issubclass(ExportacaoRecusada, ExportacaoInconsistente)


def test_valor_nao_representavel_localiza_sem_o_valor():
    erro = ValorNaoRepresentavel(formato="xlsx", tabela="dados", coluna="pergunta_x", linha=7)
    assert isinstance(erro, ExportacaoInconsistente)
    assert (erro.formato, erro.tabela, erro.coluna, erro.linha) == (
        "xlsx",
        "dados",
        "pergunta_x",
        7,
    )
    assert "pergunta_x" in str(erro) and "7" in str(erro)
    assert SENTINELA not in str(erro)


def test_mensagens_nao_carregam_valores():
    assert SENTINELA not in str(ExportacaoRecusada(Motivo.CHAVE_AUSENTE))
    assert SENTINELA not in str(ExportacaoInconsistente("snapshot X: forma incompatível"))

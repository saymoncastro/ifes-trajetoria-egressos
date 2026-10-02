"""Vocabulário de recusa da captura (contracts/operacoes.md, "Vocabulário")."""

from uuid import uuid4

from trajetoria.analitico.regras import CapturaInconsistente, Motivo, SnapshotRecusado


def test_motivos_sao_exatamente_dois():
    assert {m.name: m.value for m in Motivo} == {
        "CAMPANHA_NUNCA_ABERTA": "campanha_nunca_aberta",
        "COLETA_NAO_ENCERRADA": "coleta_nao_encerrada",
    }


def test_recusa_expoe_motivo_campanha_e_texto_da_spec():
    campanha_id = uuid4()
    nunca = SnapshotRecusado(Motivo.CAMPANHA_NUNCA_ABERTA, campanha_id)
    coleta = SnapshotRecusado(Motivo.COLETA_NAO_ENCERRADA, campanha_id)
    assert nunca.motivo is Motivo.CAMPANHA_NUNCA_ABERTA
    assert nunca.campanha_id == campanha_id
    assert "a Campanha nunca entrou em coleta" in str(nunca)
    assert "a coleta ainda não terminou" in str(coleta)
    assert str(campanha_id) in str(nunca) and str(campanha_id) in str(coleta)


def test_inconsistencia_e_distinta_da_recusa():
    assert not issubclass(CapturaInconsistente, SnapshotRecusado)
    assert not issubclass(SnapshotRecusado, CapturaInconsistente)

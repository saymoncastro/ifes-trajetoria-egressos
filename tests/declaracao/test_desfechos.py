import pytest

from tests.declaracao.construcao import declaracao_concluida
from tests.governanca.test_governanca_regras import CPAEG
from tests.participacao import construcao as c
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.declaracao.consultas import fila
from trajetoria.declaracao.operacoes import registrar_validacao
from trajetoria.participacao.consultas import participacoes_oficiais, situacao_analitica
from trajetoria.participacao.operacoes import SituacaoInicio, iniciar_participacao

pytestmark = pytest.mark.django_db


def _candidata(f, unidade="Serra"):
    x = c.conclusao(unidade=unidade)
    MaterialDeVerificacao.objects.create(
        pessoa=x.pessoa, identificador_cpf=f.identificador_cpf, atualizado_em=c.NO_PERIODO
    )
    return x


def test_nao_confirmada_preservada():
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    antes = c.retrato(f.participacao)
    registrar_validacao(
        f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="NAO_CONFIRMADA"
    )
    f.refresh_from_db()
    assert situacao_analitica(f.participacao) == "DECLARADA_NAO_CONFIRMADA"
    assert not participacoes_oficiais().exists() and c.retrato(f.participacao) == antes


def test_fora_abrangencia_sem_conflito():
    campanha = c.campanha_aberta(c.instrumento().versao, unidades={"Vitória"})
    f = declaracao_concluida(campanha, unidade="Vitória")
    x = _candidata(f)
    v = registrar_validacao(
        f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="CONFIRMADA", candidata=x
    )
    assert v.fora_da_abrangencia_na_validacao and not v.conflito_detectado_na_validacao
    assert situacao_analitica(f.participacao) == "DECLARADA_FORA_DA_ABRANGENCIA"
    assert not participacoes_oficiais().exists()


@pytest.mark.parametrize("institucional", [True, False])
def test_conflito_preserva_anterior(institucional):
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    x = _candidata(f)
    if institucional:
        anterior = iniciar_participacao(campanha, x, agora=c.NO_PERIODO).participacao
    else:
        outro = declaracao_concluida(campanha)
        registrar_validacao(
            outro,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            candidata=x,
        )
        anterior = outro.participacao
    retrato = c.retrato(anterior)
    v = registrar_validacao(
        f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="CONFIRMADA", candidata=x
    )
    assert v.conflito_detectado_na_validacao
    assert list(participacoes_oficiais()) == [anterior]
    assert c.retrato(anterior) == retrato and f in fila([CPAEG])
    assert situacao_analitica(f.participacao) == "DECLARADA_EM_CONFLITO"


def test_iniciar_reencontra_declarada():
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    x = _candidata(f)
    registrar_validacao(
        f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="CONFIRMADA", candidata=x
    )
    inicio = iniciar_participacao(campanha, x, agora=c.NO_PERIODO)
    assert inicio.participacao == f.participacao and inicio.situacao == SituacaoInicio.JA_EXISTENTE

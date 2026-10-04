import pytest

from tests.declaracao.construcao import CPF, DATA, declaracao_concluida
from tests.governanca.test_governanca_regras import CPAEG, CSAEG_VITORIA
from tests.participacao import construcao as c
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.declaracao.models import AcessoAosDadosDeConsulta
from trajetoria.declaracao.operacoes import (
    ForaDaFila,
    ForaDoEscopo,
    JaDecidida,
    registrar_validacao,
    revelar_dados,
)
from trajetoria.participacao.consultas import participacoes_oficiais

pytestmark = pytest.mark.django_db


def test_candidata_e_preservacao():
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    x = c.conclusao()
    MaterialDeVerificacao.objects.create(
        pessoa=x.pessoa, identificador_cpf=f.identificador_cpf, atualizado_em=c.NO_PERIODO
    )
    antes = c.retrato(f.participacao)
    v = registrar_validacao(
        f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="CONFIRMADA", candidata=x
    )
    assert v.conclusao == x and v.operador == "A" and v.registrada_em == c.NO_PERIODO
    assert c.retrato(f.participacao) == antes
    assert participacoes_oficiais().get().pk == f.participacao.pk
    with pytest.raises(JaDecidida):
        registrar_validacao(
            f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="NAO_CONFIRMADA"
        )


def test_recusas_e_revelacao():
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    with pytest.raises(ForaDoEscopo):
        revelar_dados(f, vinculos=[CSAEG_VITORIA], operador="B", agora=c.NO_PERIODO)
    assert not AcessoAosDadosDeConsulta.objects.exists()
    assert revelar_dados(f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO) == (
        f.nome,
        CPF,
        DATA,
    )
    assert AcessoAosDadosDeConsulta.objects.count() == 1
    with pytest.raises(ForaDoEscopo):
        registrar_validacao(
            f,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            candidata=c.conclusao(),
        )
    p = f.participacao
    p.concluida_em = None
    p.save()
    with pytest.raises(ForaDaFila):
        registrar_validacao(
            f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="NAO_CONFIRMADA"
        )

import threading
from uuid import uuid4

import pytest
from django.db import connection

from tests.declaracao.construcao import CPF, DADOS, DATA, declaracao_concluida
from tests.governanca.test_governanca_regras import CPAEG
from tests.participacao import construcao as c
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.declaracao.operacoes import (
    JaDecidida,
    iniciar_participacao_declarada,
    registrar_validacao,
)
from trajetoria.participacao.consultas import participacoes_oficiais
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import iniciar_participacao

pytestmark = pytest.mark.django_db(transaction=True)


def corrida(*funcoes):
    barreira = threading.Barrier(len(funcoes))
    resultados = []
    erros = []

    def executar(fn):
        try:
            barreira.wait(timeout=10)
            resultados.append(fn())
        except Exception as erro:
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=executar, args=(fn,)) for fn in funcoes]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    assert not any(t.is_alive() for t in threads)
    return resultados, erros


def test_inicio_declarado_idempotente_concorrente():
    campanha = c.campanha_aberta(c.instrumento().versao)
    chave = uuid4()

    def fn():
        return iniciar_participacao_declarada(
            DADOS, CPF, DATA, chave, origem="local", agora=c.NO_PERIODO
        )

    resultados, erros = corrida(fn, fn)
    assert not erros and len({p.pk for p, _ in resultados}) == 1
    assert Participacao.objects.filter(campanha=campanha).count() == 1


def test_confirmacao_e_inicio_institucional_concorrentes():
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    x = c.conclusao()
    MaterialDeVerificacao.objects.create(
        pessoa=x.pessoa, identificador_cpf=f.identificador_cpf, atualizado_em=c.NO_PERIODO
    )

    def validar():
        return registrar_validacao(
            f,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            candidata=x,
        )

    def iniciar():
        return iniciar_participacao(campanha, x, agora=c.NO_PERIODO)

    _, erros = corrida(validar, iniciar)
    assert not erros
    assert (
        participacoes_oficiais().filter(campanha=campanha, conclusao_efetiva_id=x.pk).count() == 1
    )


def test_decisao_concorrente_unica():
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))

    def fn():
        return registrar_validacao(
            f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO, resultado="NAO_CONFIRMADA"
        )

    resultados, erros = corrida(fn, fn)
    assert len(resultados) == 1 and len(erros) == 1 and isinstance(erros[0], JaDecidida)

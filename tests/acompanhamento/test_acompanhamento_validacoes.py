import pytest

from tests.acompanhamento.construcao import A, B, atuar_como
from tests.declaracao.construcao import declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.declaracao.consultas import fila
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

pytestmark = pytest.mark.django_db


def test_indicador_no_escopo(client, settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    declaracao_concluida(campanha, unidade="Vitória")
    registrar_vinculo(A, Papel.CPAEG)
    registrar_vinculo(B, Papel.CSAEG, unidade="Vitória")
    for operador in (A, B):
        atuar_como(client, operador)
        r = client.get(f"/acompanhamento/campanhas/{campanha.pk}/")
        assert r.status_code == 200
        n = fila(vinculos_ativos(operador)).count()
        assert f"Validações de formação: {n} na fila" in r.content.decode()
        assert f.nome not in r.content.decode()


def test_indicador_conta_so_a_campanha_exibida(client, settings):
    # Regressão (code review da 019): itens de outra Campanha não entram no número.
    settings.TRAJETORIA_DEMONSTRACAO = True
    versao = c.instrumento().versao
    exibida = c.campanha_aberta(versao)
    outra = c.campanha_aberta(versao)
    declaracao_concluida(exibida)
    declaracao_concluida(outra)
    declaracao_concluida(outra)
    registrar_vinculo(A, Papel.CPAEG)
    atuar_como(client, A)
    html = client.get(f"/acompanhamento/campanhas/{exibida.pk}/").content.decode()
    assert "Validações de formação: 1 na fila" in html

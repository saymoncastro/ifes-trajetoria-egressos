import pytest

from tests.acompanhamento.construcao import A, B, C, atuar_como
from tests.declaracao.construcao import CPF, declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.declaracao.models import AcessoAosDadosDeConsulta, ValidacaoDaFormacao
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

pytestmark = pytest.mark.django_db


def test_fila_escopo_revelacao_e_confirmacao(client):
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    registrar_vinculo(A, Papel.CPAEG)
    registrar_vinculo(B, Papel.CSAEG, unidade="Vitória")
    atuar_como(client, B)
    assert client.get(f"/validacoes-formacao/{f.pk}/").status_code == 404
    atuar_como(client, C)
    assert client.get("/validacoes-formacao/").status_code == 403
    atuar_como(client, A)
    fila = client.get("/validacoes-formacao/")
    assert fila.status_code == 200
    assert CPF not in fila.content.decode() and f.verificador not in fila.content.decode()
    url = f"/validacoes-formacao/{f.pk}/"
    assert client.get(url + "revelar/").status_code == 405
    assert not AcessoAosDadosDeConsulta.objects.exists()
    r = client.post(url + "revelar/")
    assert r.status_code == 200 and CPF in r.content.decode()
    assert "no-store" in r["Cache-Control"]
    assert AcessoAosDadosDeConsulta.objects.count() == 1
    r = client.post(url + "registrar/", {"resultado": "nao_confirmada"})
    assert r.status_code == 200 and not ValidacaoDaFormacao.objects.exists()
    r = client.post(url + "registrar/", {"resultado": "nao_confirmada", "confirmar": "1"})
    assert r.status_code == 303 and ValidacaoDaFormacao.objects.count() == 1


def test_revelacao_indisponivel(client, settings):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    registrar_vinculo(A, Papel.CPAEG)
    atuar_como(client, A)
    settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO = ""
    r = client.post(f"/validacoes-formacao/{f.pk}/revelar/")
    assert r.status_code == 200 and "indisponível" in r.content.decode()
    assert not AcessoAosDadosDeConsulta.objects.exists()

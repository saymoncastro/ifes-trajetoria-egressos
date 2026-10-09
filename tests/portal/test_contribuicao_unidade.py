"""A unidade recebe (026 US3; FR-009, FR-010, FR-005a; T014)."""

import csv
import io
from datetime import timedelta

import pytest
from django.test import Client

from tests.editor.construcao_editor import atuar_como
from tests.participacao import construcao as c
from tests.portal import construcao_contribuicao as cc
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo
from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.regras import ManifestacaoRejeitada, Motivo
from trajetoria.portal.models import Manifestacao

pytestmark = pytest.mark.django_db

LISTA = "/curadoria/contribuicoes/"
CSV = "/curadoria/contribuicoes/exportar.csv"


@pytest.fixture
def vinculos(cenario):
    registrar_vinculo(cc.OPERADOR_A, Papel.CPAEG)
    registrar_vinculo(cc.OPERADOR_B, Papel.CSAEG, "Vitória")


@pytest.fixture
def manifestacoes(cenario):
    """Diego (Vila Velha) e Bruno (Vitória), mais uma retirada do Bruno."""
    diego, bruno = cenario.pessoa("SIM-P-0004"), cenario.pessoa("SIM-P-0002")
    retirada = cc.registrar(bruno, forma="parceria", mensagem="Retirada.")
    operacoes.retirar(bruno, retirada.pk, agora=c.NO_PERIODO)
    return {
        "diego": cc.registrar(diego, cc.conclusao(diego, "Licenciatura em Química")),
        "bruno": cc.registrar(bruno, forma="mentoria", mensagem="=1+1"),
        "retirada": retirada,
    }


def _operador(identificador) -> Client:
    return atuar_como(Client(), identificador)


def _linhas_do_csv(resposta) -> list[list[str]]:
    texto = resposta.content.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(texto)))


# --- Acesso e escopo (US3.1, US3.4; SC-003) ---------------------------------------------------

def test_sem_operador_vai_para_a_escolha_e_volta(client, vinculos):
    resposta = client.get(LISTA)
    assert resposta["Location"] == "/demonstracao/operador/?destino=contribuicoes"
    escolha = client.post("/demonstracao/operador/escolher/",
                          {"operador": cc.OPERADOR_B, "destino": "contribuicoes"})
    assert escolha["Location"] == LISTA


def test_operador_sem_vinculo_e_recusado(vinculos, manifestacoes):
    operador = _operador(cc.OPERADOR_C)
    for url in (LISTA, CSV, f"{LISTA}{manifestacoes['diego'].pk}/contato/"):
        resposta = operador.get(url)
        assert resposta.status_code == 403, url
        assert m.UNIDADE_RECUSA in resposta.content.decode()


def test_csaeg_ve_so_as_ativas_da_propria_unidade(vinculos, manifestacoes):
    html = _operador(cc.OPERADOR_B).get(LISTA).content.decode()
    assert str(manifestacoes["bruno"].pk) in html and "Bruno Exemplo" in html
    assert str(manifestacoes["diego"].pk) not in html and "Diego Exemplo" not in html
    assert str(manifestacoes["retirada"].pk) not in html and "Retirada." not in html
    assert cc.EMAIL in html and m.REGISTRAR_CONTATO in html
    assert html.count("<h1") == 1


def test_cpaeg_ve_todas_as_ativas(vinculos, manifestacoes):
    html = _operador(cc.OPERADOR_A).get(LISTA).content.decode()
    assert "Bruno Exemplo" in html and "Diego Exemplo" in html
    assert "Licenciatura em Química · Vila Velha · 2017" in html
    assert str(manifestacoes["retirada"].pk) not in html


def test_lista_vazia(vinculos):
    html = _operador(cc.OPERADOR_B).get(LISTA).content.decode()
    assert m.UNIDADE_VAZIA in html and CSV not in html


# --- CSV (US3.2; FR-010) ----------------------------------------------------------------------

def test_csv_so_ativas_do_escopo_sem_cpf_nem_nascimento(vinculos, manifestacoes, cenario):
    resposta = _operador(cc.OPERADOR_B).get(CSV)
    assert resposta.status_code == 200
    assert resposta["Content-Type"].startswith("text/csv")
    assert "attachment" in resposta["Content-Disposition"]
    cabecalho, *linhas = _linhas_do_csv(resposta)
    assert cabecalho == list(m.CSV_CABECALHO)
    assert len(linhas) == 1
    (linha,) = linhas
    assert linha[1:5] == ["Bruno Exemplo", "Técnico em Edificações", "Vitória", "Mentoria"]
    assert linha[5] == "'=1+1"  # fórmula neutralizada
    assert linha[6] == cc.EMAIL and linha[7] == m.SEM_CONTATO
    bruto = resposta.content.decode("utf-8-sig")
    assert "11144477735" not in bruto and "1990" not in bruto  # CPF e nascimento do Bruno
    todas = _linhas_do_csv(_operador(cc.OPERADOR_A).get(CSV))
    assert len(todas) == 3  # cabeçalho, Diego e Bruno; a retirada fica de fora


# --- Contato feito (US3.3; FR-005a; SC-004a) --------------------------------------------------

def test_registrar_contato_com_confirmacao(vinculos, manifestacoes):
    operador = _operador(cc.OPERADOR_B)
    bruno = manifestacoes["bruno"]
    url = f"{LISTA}{bruno.pk}/contato/"
    pagina = operador.get(url).content.decode()
    assert m.CONTATO_TEXTO.format(destino="a unidade Vitória") in pagina
    assert Manifestacao.objects.get(pk=bruno.pk).contato_registrado_em is None
    resposta = operador.post(url)
    assert resposta["Location"] == f"{LISTA}?aviso=contato"
    linha = Manifestacao.objects.get(pk=bruno.pk)
    assert linha.contato_registrado_em == c.NO_PERIODO
    assert linha.contato_registrado_por == cc.OPERADOR_B
    html = operador.get(resposta["Location"]).content.decode()
    assert m.CONTATO_AVISO in html and url not in html
    assert cc.OPERADOR_B not in html  # o identificador nunca vai ao template
    assert operador.post(url).status_code == 409  # uma única vez
    assert Manifestacao.objects.get(pk=bruno.pk).contato_registrado_em == c.NO_PERIODO
    (linha_csv,) = _linhas_do_csv(operador.get(CSV))[1:]
    assert linha_csv[7].startswith("Contato registrado em ")


def test_contato_fora_do_escopo_e_404(vinculos, manifestacoes):
    operador = _operador(cc.OPERADOR_B)
    url = f"{LISTA}{manifestacoes['diego'].pk}/contato/"
    assert operador.get(url).status_code == 404
    assert operador.post(url).status_code == 404
    assert Manifestacao.objects.get(pk=manifestacoes["diego"].pk).contato_registrado_em is None
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.registrar_contato(manifestacoes["diego"].pk, operador=cc.OPERADOR_B,
                                    escopo=cc.ESCOPO_VITORIA, agora=c.NO_PERIODO)
    assert erro.value.motivos == (Motivo.FORA_DO_ESCOPO,)


def test_contato_em_retirada_e_conflito(vinculos, manifestacoes):
    operador = _operador(cc.OPERADOR_A)
    url = f"{LISTA}{manifestacoes['retirada'].pk}/contato/"
    for resposta in (operador.get(url), operador.post(url)):
        assert resposta.status_code == 409
        assert m.CONFLITO in resposta.content.decode()
    with pytest.raises(ManifestacaoRejeitada) as erro:
        operacoes.registrar_contato(manifestacoes["retirada"].pk, operador=cc.OPERADOR_A,
                                    escopo=cc.ESCOPO_A, agora=c.NO_PERIODO)
    assert erro.value.motivos == (Motivo.ESTADO,)


def test_retirada_depois_do_contato_sai_da_lista(vinculos, manifestacoes, cenario):
    """US2.2: a retirada sai da lista e do CSV mesmo com contato registrado."""
    bruno = manifestacoes["bruno"]
    operacoes.registrar_contato(bruno.pk, operador=cc.OPERADOR_B, escopo=cc.ESCOPO_VITORIA,
                                agora=c.NO_PERIODO)
    operacoes.retirar(cenario.pessoa("SIM-P-0002"), bruno.pk,
                      agora=c.NO_PERIODO + timedelta(days=1))
    operador = _operador(cc.OPERADOR_B)
    assert str(bruno.pk) not in operador.get(LISTA).content.decode()
    assert len(_linhas_do_csv(operador.get(CSV))) == 1


def test_operador_exigido_na_operacao(manifestacoes):
    with pytest.raises(TypeError):
        operacoes.registrar_contato(manifestacoes["bruno"].pk, operador="",
                                    escopo=cc.ESCOPO_A, agora=c.NO_PERIODO)


def test_curadoria_de_oportunidades_leva_as_contribuicoes(vinculos):
    html = _operador(cc.OPERADOR_B).get("/curadoria/oportunidades/").content.decode()
    assert f'href="{LISTA}"' in html

"""Cenário de demonstração da Feature 011 (spec FR-142; research R14; quickstart).

Os operadores fictícios da 010 não mudam: A = CPAEG, B = CSAEG Vitória, C = sem vínculo. O
preparo acrescenta **uma** Campanha fictícia nunca aberta, sem período, com a Versão de
referência em rascunho e critério {Serra, Vitória}. Ela não admite Participação e não altera a
jornada da 007/008; a regressão completa da tabela R17 é
`tests/interface/test_interface_cenario.py::test_situacoes_da_tabela_r17`, inalterada.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.test import Client

from tests.acompanhamento import construcao as k
from tests.campanha.construcao import conclusao_da_fonte
from tests.editor.construcao_editor import texto_visivel
from trajetoria.campanha.consultas import EstadoCampanha, campanhas_em_coleta_para, estado
from trajetoria.campanha.models import Campanha
from trajetoria.formulario_2024 import materializar
from trajetoria.governanca.models import VinculoDeGovernanca
from trajetoria.instrumento.models import EstadoVersao
from trajetoria.participacao.entrada import ResolucaoDaEntrada, situacao_de_entrada
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import iniciar_participacao
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

NOME = "Demonstração — acompanhamento Serra e Vitória"
AMPLA = "Demonstração — coleta ampla"
VITORIA = ("SIM-C-0002", "SIM-C-0003", "SIM-C-0012")

pytestmark = pytest.mark.django_db


@pytest.fixture
def preparado():
    call_command("preparar_demonstracao", stdout=StringIO())
    return Campanha.objects.get(nome=NOME)


def test_campanha_ficticia_nunca_aberta_sem_periodo_com_a_baseline(preparado):
    assert preparado.aberta_em is None and preparado.encerrada_em is None
    assert preparado.inicio is None and preparado.fim is None
    assert preparado.versao == materializar().versao
    assert preparado.versao.estado == EstadoVersao.RASCUNHO
    assert preparado.unidades == ["Serra", "Vitória"]
    assert (preparado.niveis, preparado.modalidades, preparado.formas_oferta) == (None,) * 3
    assert (preparado.ano_minimo, preparado.ano_maximo) == (None, None)
    assert estado(preparado) is EstadoCampanha.EM_PREPARACAO


def test_preparo_idempotente_e_operadores_da_010_preservados(preparado):
    call_command("preparar_demonstracao", stdout=StringIO())
    assert Campanha.objects.filter(nome=NOME).count() == 1
    vinculos = sorted(
        VinculoDeGovernanca.objects.values_list(
            "identificador_operador", "papel", "unidade", "ativo"
        )
    )
    assert vinculos == [(k.A, "CPAEG", "", True), (k.B, "CSAEG", "Vitória", True)]


def test_nao_admite_participacao_nem_muda_a_entrada(preparado):
    for id_externo in VITORIA:
        conclusao = conclusao_da_fonte(id_externo)
        with pytest.raises(ParticipacaoRejeitada) as erro:
            iniciar_participacao(preparado, conclusao)
        assert Motivo.COLETA_NAO_ADMITIDA in erro.value.motivos
        assert preparado not in campanhas_em_coleta_para(conclusao)
    assert not Participacao.objects.exists()
    for id_externo in ("SIM-P-0002", "SIM-P-0010"):
        pessoa = conclusao_da_fonte(VITORIA[0]).pessoa.__class__.objects.get(id_externo=id_externo)
        assert situacao_de_entrada(pessoa).resolucao is ResolucaoDaEntrada.SEM_PESQUISA


def _cliente(identificador):
    return k.atuar_como(Client(), identificador)


def test_b_csaeg_vitoria_exercita_o_acompanhamento(preparado):
    b = _cliente(k.B)
    texto = texto_visivel(b.get("/acompanhamento/"))
    assert NOME in texto
    assert AMPLA not in texto and "coleta sobreposta" not in texto
    resposta = k.detalhe(b, preparado)
    assert k.resumo_em_numeros(resposta)["Elegíveis atuais"] == "3"
    texto = texto_visivel(resposta)
    assert "Instrumento ainda não publicado" in texto
    assert "A coleta ainda não começou." in texto
    assert "Serra" not in texto[texto.index("Resumo") :]
    assert "?recorte=unidade" not in resposta.content.decode()
    ampla = Campanha.objects.get(nome=AMPLA)
    assert k.detalhe(b, ampla).status_code == 403


def test_a_cpaeg_ve_as_tres_campanhas(preparado):
    a = _cliente(k.A)
    texto = texto_visivel(a.get("/acompanhamento/"))
    assert NOME in texto and AMPLA in texto and "coleta sobreposta" in texto
    ampla = Campanha.objects.get(nome=AMPLA)
    assert k.resumo_em_numeros(k.detalhe(a, ampla))["Elegíveis atuais"] == "9"
    resposta = k.detalhe(a, preparado, "unidade")
    assert k.resumo_em_numeros(resposta)["Elegíveis atuais"] == "6"
    assert [linha[:2] for linha in k.tabela_do_recorte(resposta)["linhas"]] == [
        ["Serra", "3"],
        ["Vitória", "3"],
    ]
    assert f'href="/editor/versoes/{preparado.versao.pk}/"' in resposta.content.decode()


def test_c_sem_vinculo_recusado(preparado):
    assert _cliente(k.C).get("/acompanhamento/").status_code == 403

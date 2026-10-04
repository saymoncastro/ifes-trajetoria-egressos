"""Estados da Campanha (004) e instrumento aplicado (Feature 011; US10, US11; spec FR-042 a
FR-046; caso L)."""

from datetime import timedelta

from tests.acompanhamento import construcao as k
from tests.campanha.construcao import versao_rascunho
from tests.editor.construcao_editor import texto_visivel
from trajetoria.acompanhamento.consultas import campanha_acompanhada
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.governanca.regras import EscopoDeAcompanhamento

AVISO_POPULACAO_ATUAL = (
    "A população elegível apresentada corresponde aos dados institucionais atuais e pode "
    "diferir da população existente quando a coleta foi encerrada."
)
INSTITUCIONAL = EscopoDeAcompanhamento(True, frozenset())


def _texto(cliente, campanha):
    return texto_visivel(k.detalhe(cliente, campanha))


# --- Encerrada (US10) --------------------------------------------------------------------------


def test_encerrada_explicitamente(ref, cliente_cpaeg):
    texto = _texto(cliente_cpaeg, ref.E)
    assert AVISO_POPULACAO_ATUAL in texto
    assert "Encerrada em" in texto and "(antecipadamente)" in texto
    assert "Iniciadas e não concluídas" in texto
    assert "Em andamento" not in texto


def test_encerrada_com_participacao_nao_concluida(inst, cliente_cpaeg):
    campanha = k.campanha(inst.versao)
    k.iniciada(campanha, k.conclusao(unidade="Serra", ano=2020))
    op_campanha.encerrar(campanha)
    numeros = k.resumo_em_numeros(k.detalhe(cliente_cpaeg, campanha))
    assert numeros["Iniciadas e não concluídas"] == "1"
    assert "coleta foi encerrada" in _texto(cliente_cpaeg, campanha)


def test_encerrada_pelo_fim_do_periodo(inst, cliente_cpaeg):
    campanha = k.campanha(inst.versao, estado="encerrada_por_periodo")
    texto = _texto(cliente_cpaeg, campanha)
    assert "(ao fim do período)" in texto
    assert AVISO_POPULACAO_ATUAL in texto


def test_encerrada_por_consulta_direta_com_agora_posterior(ref):
    depois = k.momento_em(ref.I.fim + timedelta(days=1))
    item = campanha_acompanhada(ref.I, INSTITUCIONAL, pode_consultar_rascunho=True, agora=depois)
    assert item.estado.name == "ENCERRADA"
    assert AVISO_POPULACAO_ATUAL in item.avisos
    assert item.rotulo_nao_concluidas == "Iniciadas e não concluídas"


def test_nunca_aberta_e_expirada(inst, cliente_cpaeg):
    campanha = k.campanha(inst.versao, estado="expirada_sem_abertura")
    texto = _texto(cliente_cpaeg, campanha)
    assert "Período encerrado — Campanha nunca aberta" in texto
    assert "Esta Campanha não chegou a entrar em coleta." in texto
    assert "Aberta em" not in texto and "Encerrada em" in texto


def test_encerrada_continua_com_populacao_atual(ref, cliente_cpaeg):
    antes = k.resumo_em_numeros(k.detalhe(cliente_cpaeg, ref.E))["Elegíveis atuais"]
    k.conclusao(unidade="Serra", ano=2025)
    depois = k.resumo_em_numeros(k.detalhe(cliente_cpaeg, ref.E))["Elegíveis atuais"]
    assert int(depois) == int(antes) + 1
    assert AVISO_POPULACAO_ATUAL in _texto(cliente_cpaeg, ref.E)


# --- Preparação e coleta (US11) ----------------------------------------------------------------


def test_em_preparacao(ref, cliente_cpaeg):
    texto = _texto(cliente_cpaeg, ref.P)
    assert "A coleta ainda não começou." in texto
    numeros = k.resumo_em_numeros(k.detalhe(cliente_cpaeg, ref.P))
    assert numeros["Elegíveis atuais"] == "7"
    assert numeros["Participações iniciadas"] == numeros["Participações concluídas"] == "0"
    assert "Iniciadas e não concluídas" in numeros


def test_em_coleta(ref, cliente_cpaeg):
    texto = _texto(cliente_cpaeg, ref.I)
    assert "Em andamento" in texto
    assert "Os números correspondem aos dados no momento da consulta." in texto


def test_periodo_nao_definido(inst, cliente_cpaeg):
    campanha = k.campanha(inst.versao, estado="sem_periodo")
    assert "Período não definido" in _texto(cliente_cpaeg, campanha)


def test_rascunho_para_csaeg_so_instrumento_nao_publicado(ref, cliente_csaeg_vitoria):
    versao = ref.P.versao
    for resposta in (
        cliente_csaeg_vitoria.get("/acompanhamento/"),
        k.detalhe(cliente_csaeg_vitoria, ref.P),
    ):
        html = resposta.content.decode()
        assert "Instrumento ainda não publicado" in html
        assert versao.designacao not in html
        assert versao.pesquisa.nome not in html
        assert f"/editor/versoes/{versao.pk}/" not in html
        assert "Pergunta de teste" not in html


def test_rascunho_para_cpaeg_identificado_com_link(ref, cliente_cpaeg):
    html = k.detalhe(cliente_cpaeg, ref.P).content.decode()
    versao = ref.P.versao
    assert f"{versao.pesquisa.nome} — {versao.designacao}" in html
    assert f'href="/editor/versoes/{versao.pk}/"' in html


def test_publicada_para_csaeg_identificada_com_link(ref, cliente_csaeg_vitoria):
    html = k.detalhe(cliente_csaeg_vitoria, ref.I).content.decode()
    assert f'href="/editor/versoes/{ref.inst.versao.pk}/"' in html


def test_rascunho_de_campanha_nunca_aberta_sem_periodo(cliente_csaeg_vitoria, db):
    campanha = k.campanha(versao_rascunho("Outra"), estado="sem_periodo")
    texto = _texto(cliente_csaeg_vitoria, campanha)
    assert "Instrumento ainda não publicado" in texto and "Período não definido" in texto

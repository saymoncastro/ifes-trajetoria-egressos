"""Detalhe operacional da Campanha (Feature 011; US2; spec FR-030 a FR-039, FR-043 a FR-045;
casos H, I, J, K)."""

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel

_detalhe = k.detalhe
resumo_em_numeros = k.resumo_em_numeros


def _resumo(texto):
    return texto[texto.index("Resumo") : texto.index("Recortes")]


def test_seis_indicadores_com_definicoes(ref, cliente_cpaeg):
    resposta = _detalhe(cliente_cpaeg, ref.I)
    assert resposta.status_code == 200
    assert resumo_em_numeros(resposta) == {
        "Elegíveis atuais": "7",
        "Participações iniciadas": "4",
        "Participações concluídas": "2",
        "Em andamento": "2",
        "Taxa de início": "57,1%",
        "Taxa de conclusão": "28,6%",
    }
    resumo = _resumo(texto_visivel(resposta))
    for definicao in (
        "atendem hoje aos critérios da Campanha (população elegível atual)",
        "inclusive as ainda sem respostas",
        "Participações com conclusão registrada",
        "Participações iniciadas ÷ elegíveis atuais",
        "Participações concluídas ÷ elegíveis atuais",
    ):
        assert definicao in resumo


def test_cabecalho_da_campanha(ref, cliente_cpaeg):
    texto = texto_visivel(_detalhe(cliente_cpaeg, ref.I))
    assert f"{ref.inst.versao.pesquisa.nome} — {ref.inst.versao.designacao}" in texto
    assert "Em coleta" in texto and "Aberta em" in texto
    assert "Números calculados em" in texto


def test_campanha_sem_participacoes_taxas_zero(ref, cliente_cpaeg):
    resumo = _resumo(texto_visivel(_detalhe(cliente_cpaeg, ref.R)))
    assert "0,0%" in resumo
    assert "não se aplica" not in resumo


def test_elegiveis_zero_taxas_nao_se_aplicam(ref, cliente_cpaeg):
    vazia = k.campanha(ref.inst.versao, unidades=["Unidade inexistente"], nome="Campanha Z")
    resposta = _detalhe(cliente_cpaeg, vazia)
    html = resposta.content.decode()
    resumo = _resumo(texto_visivel(resposta))
    numeros = resumo_em_numeros(resposta)
    assert numeros["Taxa de início"] == numeros["Taxa de conclusão"] == "— não se aplica"
    assert '<span aria-hidden="true">—</span>' in html
    for proibido in ("0,0%", "0%", "NaN", "nan", "inf", "∞"):
        assert proibido not in resumo
    assert "nenhuma formação elegível no momento" in texto_visivel(resposta)


def test_contagem_por_formacao_e_linguagem(ref, cliente_cpaeg):
    texto = texto_visivel(_detalhe(cliente_cpaeg, ref.I))
    assert "cada formação concluída conta separadamente" in texto
    assert "Participações concluídas" in texto
    minusculo = texto.lower()
    assert "questionários integralmente respondidos" not in minusculo
    for termo in ("abandon", "desist", "expirad"):
        assert termo not in minusculo

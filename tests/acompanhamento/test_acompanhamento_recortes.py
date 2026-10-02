"""Os seis recortes (Feature 011; US7, US8, US9; spec FR-050 a FR-061; casos A, B, M)."""

import pytest

from tests.acompanhamento import construcao as k
from tests.acompanhamento.conftest import TADS, TI
from tests.editor.construcao_editor import texto_visivel
from trajetoria.acompanhamento.apresentacao import Indicadores
from trajetoria.acompanhamento.consultas import Recorte, campanha_acompanhada
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.participacao.operacoes import responder_texto

INSTITUCIONAL = EscopoDeAcompanhamento(True, frozenset())
VITORIA = EscopoDeAcompanhamento(False, frozenset({"Vitória"}))
SERRA = EscopoDeAcompanhamento(False, frozenset({"Serra"}))
DUAS = EscopoDeAcompanhamento(False, frozenset({"Serra", "Vitória"}))


def _linhas(cliente, campanha, recorte):
    return k.tabela_do_recorte(k.detalhe(cliente, campanha, recorte))["linhas"]


def _consulta(campanha, escopo, recorte):
    return campanha_acompanhada(campanha, escopo, pode_consultar_rascunho=True, recorte=recorte)


# --- Unidade (US7) -----------------------------------------------------------------------------


def test_por_unidade_cpaeg(ref, cliente_cpaeg):
    assert _linhas(cliente_cpaeg, ref.I, "unidade") == [
        ["Cefor", "1", "0", "0", "0,0%"],
        ["Serra", "3", "2", "1", "33,3%"],
        ["Vitória", "2", "1", "1", "50,0%"],
        ["Unidade não informada", "1", "1", "0", "0,0%"],
    ]


def test_unidade_do_criterio_aparece_com_zero(ref, cliente_cpaeg):
    campanha = k.campanha(ref.inst.versao, unidades=["Serra", "Guarapari"])
    assert _linhas(cliente_cpaeg, campanha, "unidade") == [
        ["Guarapari", "0", "0", "0", "— não se aplica"],
        ["Serra", "3", "0", "0", "0,0%"],
    ]


def test_csaeg_de_duas_unidades_em_campanha_sem_criterio_tem_linhas_com_zero(
    ref, cliente_duas_csaeg
):
    sem_vitoria = k.campanha(ref.inst.versao, ano_minimo=2021)  # v1 2019, v2 2020 ficam fora
    assert [linha[:2] for linha in _linhas(cliente_duas_csaeg, sem_vitoria, "unidade")] == [
        ["Serra", "2"],
        ["Vitória", "0"],
    ]


def test_cpaeg_em_campanha_sem_criterio_nao_inventa_unidades(ref, cliente_cpaeg):
    rotulos = [linha[0] for linha in _linhas(cliente_cpaeg, ref.I, "unidade")]
    assert rotulos == ["Cefor", "Serra", "Vitória", "Unidade não informada"]


def test_ordem_nunca_pelo_indicador(ref, cliente_cpaeg):
    """Vitória tem a maior taxa e não sobe; a ordem é a do texto."""
    rotulos = [linha[0] for linha in _linhas(cliente_cpaeg, ref.I, "unidade")]
    assert rotulos.index("Serra") < rotulos.index("Vitória")


def test_unidade_declarada_nao_e_usada(ref, cliente_cpaeg):
    """v1 (Vitória) respondeu "Campus Serra" à pergunta de campus; conta em Vitória."""
    linhas = {linha[0]: linha for linha in _linhas(cliente_cpaeg, ref.I, "unidade")}
    assert linhas["Vitória"][2:4] == ["1", "1"]


# --- Curso (US8) -------------------------------------------------------------------------------


def test_por_curso_cpaeg_desambigua_por_unidade(ref, cliente_cpaeg):
    linhas = _linhas(cliente_cpaeg, ref.I, "curso")
    assert [linha[:2] for linha in linhas] == [
        ["Cefor", "Especialização em Informática na Educação"],
        ["Serra", TI],
        ["Serra", TADS],
        ["Vitória", "Engenharia Civil"],
        ["Vitória", TI],
        ["Unidade não informada", "Curso não informado"],
    ]
    assert linhas[1][2:] == ["2", "2", "1", "50,0%"]


def test_curso_ausente_fica_na_sua_unidade(ref, cliente_cpaeg):
    k.conclusao(unidade="Serra", ano=2024)
    linhas = _linhas(cliente_cpaeg, ref.I, "curso")
    assert ["Serra", "Curso não informado", "1", "0", "0", "0,0%"] in linhas


def test_csaeg_de_uma_unidade_sem_coluna_unidade(ref, cliente_csaeg_serra):
    resposta = k.detalhe(cliente_csaeg_serra, ref.I, "curso")
    tabela = k.tabela_do_recorte(resposta)
    assert "Unidade" not in tabela["cabecalhos"]
    assert tabela["linhas"] == [[TI, "2", "2", "1", "50,0%"], [TADS, "1", "0", "0", "0,0%"]]


def test_csaeg_de_duas_unidades_com_coluna_unidade(ref, cliente_duas_csaeg):
    tabela = k.tabela_do_recorte(k.detalhe(cliente_duas_csaeg, ref.I, "curso"))
    assert tabela["cabecalhos"][:2] == ["Unidade", "Curso"]
    assert {linha[0] for linha in tabela["linhas"]} == {"Serra", "Vitória"}


# --- Nível, modalidade, forma de oferta, ano (US9) ---------------------------------------------


def test_por_nivel_valores_como_registrados(ref, cliente_cpaeg):
    assert [linha[:2] for linha in _linhas(cliente_cpaeg, ref.I, "nivel")] == [
        ["Graduação", "1"],
        ["graduação", "1"],
        ["Pós-graduação", "1"],
        ["Técnico", "3"],
        ["Nível não informado", "1"],
    ]


def test_nivel_declarado_nao_e_usado(ref, cliente_cpaeg):
    """Q14 permanece declarada (ADR 0003): o recorte usa o nível da Conclusão."""
    participacao = k.iniciada(ref.I, ref.s3)
    responder_texto(participacao, ref.inst.texto, "Pós-graduação", agora=None)
    linhas = {linha[0]: linha for linha in _linhas(cliente_cpaeg, ref.I, "nivel")}
    assert linhas["Graduação"][2] == "1"
    assert linhas["Pós-graduação"][2] == "0"


def test_por_modalidade_e_forma_de_oferta(ref, cliente_cpaeg):
    assert [linha[0] for linha in _linhas(cliente_cpaeg, ref.I, "modalidade")] == [
        "A distância", "Presencial", "Modalidade não informada",
    ]  # fmt: skip
    assert [linha[:2] for linha in _linhas(cliente_cpaeg, ref.I, "forma-oferta")] == [
        ["Integrado", "2"], ["Subsequente", "1"], ["Forma de oferta não informada", "4"],
    ]  # fmt: skip


def test_por_ano_crescente_sem_coorte(ref, cliente_cpaeg):
    resposta = k.detalhe(cliente_cpaeg, ref.I, "ano-conclusao")
    assert [linha[0] for linha in k.tabela_do_recorte(resposta)["linhas"]] == [
        "2019", "2020", "2021", "2022", "2023", "Ano de conclusão não informado",
    ]  # fmt: skip
    texto = texto_visivel(resposta)
    assert "Ano de conclusão" in texto
    assert "coorte" not in texto.lower()


def test_recortes_sem_linhas_com_zero_inventadas(ref, cliente_cpaeg):
    for recorte in ("curso", "nivel", "modalidade", "forma-oferta", "ano-conclusao"):
        for linha in _linhas(cliente_cpaeg, ref.I, recorte):
            assert linha[-4:-1] != ["0", "0", "0"], (recorte, linha)


@pytest.mark.parametrize("valor", ["coorte", "", "UNIDADE"])
def test_recorte_desconhecido_e_inexistente(ref, cliente_cpaeg, valor):
    assert k.detalhe(cliente_cpaeg, ref.I, None).status_code == 200
    resposta = cliente_cpaeg.get(f"/acompanhamento/campanhas/{ref.I.pk}/?recorte={valor}")
    assert resposta.status_code == 404


def test_recorte_combinado_e_inexistente(ref, cliente_cpaeg):
    endereco = f"/acompanhamento/campanhas/{ref.I.pk}/?recorte=unidade&recorte=curso"
    assert cliente_cpaeg.get(endereco).status_code == 404


@pytest.mark.parametrize("escopo", [INSTITUCIONAL, VITORIA, DUAS])
@pytest.mark.parametrize("recorte", list(Recorte))
def test_soma_das_linhas_igual_ao_total(ref, escopo, recorte):
    item = _consulta(ref.I, escopo, recorte)
    soma = sum((linha.indicadores for linha in item.linhas), Indicadores())
    assert soma == item.indicadores


def test_linha_de_total_igual_ao_resumo(ref, cliente_cpaeg):
    for recorte in ("unidade", "curso", "ano-conclusao"):
        resposta = k.detalhe(cliente_cpaeg, ref.I, recorte)
        assert k.tabela_do_recorte(resposta)["total"][-4:] == ["7", "4", "2", "28,6%"]


def test_recortes_oferecidos(ref, cliente_cpaeg, cliente_csaeg_vitoria):
    def oferecidos(cliente):
        html = k.detalhe(cliente, ref.I).content.decode()
        nav = html[
            html.index('aria-label="Recortes"') : html.index("</nav>", html.index("Recortes"))
        ]
        return [r.valor for r in Recorte if f'?recorte={r.valor}"' in nav]

    assert oferecidos(cliente_cpaeg) == [r.valor for r in Recorte]
    assert oferecidos(cliente_csaeg_vitoria) == [
        r.valor for r in Recorte if r is not Recorte.UNIDADE
    ]
    assert k.detalhe(cliente_csaeg_vitoria, ref.I, "unidade").status_code == 200

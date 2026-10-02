"""Escopo de unidade nos dois lados do indicador e múltiplos vínculos (Feature 011; US4, US12;
spec FR-012 a FR-015, FR-023, FR-038, FR-071; casos D, F, G)."""

from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.acompanhamento.apresentacao import Indicadores
from trajetoria.acompanhamento.consultas import indicadores_da_campanha, unidades_relevantes
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.operacoes import desativar_vinculo, registrar_vinculo
from trajetoria.governanca.regras import EscopoDeAcompanhamento

INSTITUCIONAL = EscopoDeAcompanhamento(True, frozenset())
VITORIA = EscopoDeAcompanhamento(False, frozenset({"Vitória"}))
SERRA_E_VITORIA = EscopoDeAcompanhamento(False, frozenset({"Serra", "Vitória"}))


def test_csaeg_vitoria_ve_so_vitoria_nos_dois_lados(ref):
    """Serra tem Participações em I (s1 iniciada, s2 concluída) e elas não entram."""
    assert indicadores_da_campanha(ref.I, VITORIA) == Indicadores(2, 1, 1)


def test_conclusao_sem_unidade_fica_fora_de_qualquer_csaeg(ref):
    total = indicadores_da_campanha(ref.I, INSTITUCIONAL)
    soma = indicadores_da_campanha(ref.I, EscopoDeAcompanhamento(
        False, frozenset({"Serra", "Vitória", "Cefor"})
    ))  # fmt: skip
    assert (total.elegiveis - soma.elegiveis, total.iniciadas - soma.iniciadas) == (1, 1)


def test_unidades_relevantes_so_para_apresentacao(ref):
    assert unidades_relevantes(ref.I, INSTITUCIONAL) is None
    assert unidades_relevantes(ref.I, VITORIA) == {"Vitória"}
    assert unidades_relevantes(ref.R, SERRA_E_VITORIA) == {"Serra"}


def test_universo_nao_usa_o_criterio_de_unidades_da_campanha(ref, inst):
    """Simula 005/DP-507 alterando a Conclusão por ORM **só no teste**: a Participação de uma
    Conclusão hoje fora do critério da Campanha, mas na unidade do operador, continua contando
    para a CSAEG como conta para a CPAEG (FR-023, FR-038)."""
    so_serra = k.campanha(inst.versao, unidades=["Serra"])
    x = k.conclusao(unidade="Serra", ano=2022)
    k.concluida(so_serra, x, inst)
    ConclusaoAcademica.objects.filter(pk=x.pk).update(unidade="Vitória")
    assert indicadores_da_campanha(so_serra, SERRA_E_VITORIA).iniciadas == 1
    assert indicadores_da_campanha(so_serra, SERRA_E_VITORIA).concluidas == 1
    assert indicadores_da_campanha(so_serra, INSTITUCIONAL).concluidas == 1
    assert indicadores_da_campanha(so_serra, SERRA_E_VITORIA).elegiveis == 3  # s1, s2, s3


def test_escopo_aplicado_no_sql(ref, cliente_csaeg_vitoria):
    with CaptureQueriesContext(connection) as capturadas:
        k.detalhe(cliente_csaeg_vitoria, ref.I, "curso")
        cliente_csaeg_vitoria.get("/acompanhamento/")
    tabelas = ('"academico_conclusaoacademica"', '"participacao_participacao"')
    relevantes = [q["sql"] for q in capturadas if any(t in q["sql"] for t in tabelas)]
    assert relevantes
    for sql in relevantes:
        assert '"academico_conclusaoacademica"."unidade" IN' in sql, sql


def test_html_da_csaeg_nao_tem_outras_unidades(ref, cliente_csaeg_vitoria):
    for recorte in (None, "curso", "nivel"):
        texto = texto_visivel(k.detalhe(cliente_csaeg_vitoria, ref.I, recorte))
        for outra in ("Serra", "Cefor", "não informada"):
            assert outra not in texto, (recorte, outra)


# --- Múltiplos vínculos (US12) -----------------------------------------------------------------


def test_duas_csaeg_unem_unidades(ref, cliente_duas_csaeg):
    assert indicadores_da_campanha(ref.I, SERRA_E_VITORIA) == Indicadores(5, 3, 2)
    texto = texto_visivel(cliente_duas_csaeg.get("/acompanhamento/"))
    assert "Campanha R" in texto and "Campanha I" in texto


def test_duas_csaeg_em_campanha_restrita_veem_so_a_unidade_da_campanha(ref, cliente_duas_csaeg):
    """Campanha restrita a Serra: só Serra tem linha (Vitória não é unidade do critério)."""
    tabela = k.tabela_do_recorte(k.detalhe(cliente_duas_csaeg, ref.R, "unidade"))
    assert [linha[0] for linha in tabela["linhas"]] == ["Serra"]


def test_participacao_de_outra_unidade_do_escopo_fica_distinguivel(inst, cliente_duas_csaeg):
    """Regressão do code review: com várias unidades no escopo, a coluna Unidade e o recorte
    por unidade dependem do escopo, não do critério da Campanha. Uma Participação de Conclusão
    corrigida para Vitória (simulação de 005/DP-507, por ORM só no teste) aparece na sua
    própria linha, sem se confundir com o mesmo curso em Serra."""
    so_serra = k.campanha(inst.versao, unidades=["Serra"])
    x = k.conclusao(unidade="Serra", curso="Técnico em Informática", ano=2022)
    k.conclusao(unidade="Serra", curso="Técnico em Informática", ano=2023)
    k.concluida(so_serra, x, inst)
    ConclusaoAcademica.objects.filter(pk=x.pk).update(unidade="Vitória")
    resposta = k.detalhe(cliente_duas_csaeg, so_serra, "curso")
    tabela = k.tabela_do_recorte(resposta)
    assert tabela["cabecalhos"][:2] == ["Unidade", "Curso"]
    assert [linha[:5] for linha in tabela["linhas"]] == [
        ["Serra", "Técnico em Informática", "1", "0", "0"],
        ["Vitória", "Técnico em Informática", "0", "1", "1"],
    ]
    assert "?recorte=unidade" in resposta.content.decode()


def test_duas_csaeg_em_campanha_irrestrita_tem_as_duas_unidades(ref, cliente_duas_csaeg):
    tabela = k.tabela_do_recorte(k.detalhe(cliente_duas_csaeg, ref.I, "unidade"))
    assert [linha[0] for linha in tabela["linhas"]] == ["Serra", "Vitória"]


def test_cpaeg_mais_csaeg_e_institucional(ref, cliente_cpaeg_e_csaeg):
    numeros = k.resumo_em_numeros(k.detalhe(cliente_cpaeg_e_csaeg, ref.I))
    assert numeros["Elegíveis atuais"] == "7"
    assert "Unidade não informada" in texto_visivel(k.detalhe(cliente_cpaeg_e_csaeg, ref.I))


def test_desativar_cpaeg_vale_na_requisicao_seguinte(ref, cliente_cpaeg_e_csaeg):
    assert k.resumo_em_numeros(k.detalhe(cliente_cpaeg_e_csaeg, ref.I))["Elegíveis atuais"] == "7"
    cpaeg = VinculoDeGovernanca.objects.get(identificador_operador=k.A, papel=Papel.CPAEG)
    desativar_vinculo(cpaeg)
    assert k.resumo_em_numeros(k.detalhe(cliente_cpaeg_e_csaeg, ref.I))["Elegíveis atuais"] == "3"


def test_sem_seletor_de_atuacao(ref, cliente_cpaeg_e_csaeg):
    html = cliente_cpaeg_e_csaeg.get("/acompanhamento/").content.decode()
    assert "<select" not in html


def test_so_vinculo_inativo_e_recusado(db):
    vinculo = registrar_vinculo(k.B, Papel.CSAEG, "Vitória")
    desativar_vinculo(vinculo)
    resposta = k.atuar_como(Client(), k.B).get("/acompanhamento/")
    assert resposta.status_code == 403

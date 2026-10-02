"""Escape contra fórmula, Unicode e valores não representáveis (US9; spec FR-074 a FR-078,
FR-091; research R10, R12)."""

import pytest

from tests.analitico import construcao as c
from tests.exportacao import apoio, leitura
from tests.participacao.construcao import (
    pergunta_de,
    pergunta_mem,
    preencher_instrumento,
    secao_mem,
    versao_publicada_de,
)
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao.contrato import NOTAS
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.formatos import exportar_csv, exportar_xlsx
from trajetoria.exportacao.regras import ValorNaoRepresentavel
from trajetoria.instrumento.models import Pergunta
from trajetoria.participacao.models import Resposta
from trajetoria.participacao.operacoes import concluir, responder_escala, responder_texto

pytestmark = pytest.mark.django_db

TEXTOS = {
    "=1+1": "'=1+1",
    "+55 27": "'+55 27",
    "-abc": "'-abc",
    "@x": "'@x",
    "\tabc": "'\tabc",
    "\rabc": "'\rabc",
    "'abc": "''abc",
    'ação 😀 "x", y': 'ação 😀 "x", y',
    "abc": "abc",
}
GATILHOS = ("=", "+", "-", "@", "\t", "\r")


@pytest.fixture
def com_textos(inst):
    """Uma Participação concluída por texto declarado; devolve (snapshot, {texto: Conclusão})."""
    campanha = c.campanha_aberta_no_passado(inst.versao, unidades=["Serra"])
    conclusoes = {}
    for texto in TEXTOS:
        conclusao = c.conclusao(unidade="Serra")
        participacao = c.iniciada(campanha, conclusao)
        preencher_instrumento(participacao, inst, agora=c.na_coleta())
        responder_texto(participacao, inst.texto, texto, agora=c.na_coleta())
        concluir(participacao, agora=c.na_coleta())
        conclusoes[texto] = conclusao
    return capturar_snapshot(campanha), conclusoes


def _coluna_texto(inst) -> str:
    return f"pergunta_{inst.texto.pk.hex}"


def test_csv_bruto_escapado(com_textos, inst, chave_ficticia):
    snapshot, conclusoes = com_textos
    bruto = leitura.ler_csv(exportar_csv(snapshot), revertido=False)
    cabecalho = bruto["dados"][0]
    texto, ident = cabecalho.index(_coluna_texto(inst)), cabecalho.index("conclusao_analitica_id")
    por_id = {linha[ident]: linha[texto] for linha in bruto["dados"][1:]}
    for original, esperado in TEXTOS.items():
        assert por_id[apoio.id_de(conclusoes[original], chave_ficticia)] == esperado, original


def test_nenhum_campo_comeca_por_gatilho_nao_escapado(com_textos):
    bruto = leitura.ler_csv(exportar_csv(com_textos[0]), revertido=False)
    for tabela in bruto.values():
        for linha in tabela:
            for campo in linha:
                assert not campo.startswith(GATILHOS), repr(campo[:20])


def test_reversao_universal_devolve_o_dataset_logico(com_textos):
    snapshot = com_textos[0]
    lido = leitura.normalizar_csv(leitura.ler_csv(exportar_csv(snapshot)))
    assert lido == leitura.normalizar_dataset(dataset_exportado(snapshot))


def test_inteiro_negativo_nao_e_escapado(inst):
    versao = versao_publicada_de(secao_mem(pergunta_mem(tipo="ESCALA")))
    pergunta = pergunta_de(versao, 1, 1)
    Pergunta.objects.filter(pk=pergunta.pk).update(escala_inicio=-3)  # instrumento de teste
    campanha = c.campanha_aberta_no_passado(versao)
    participacao = c.iniciada(campanha, c.conclusao(unidade="Serra"))
    pergunta.refresh_from_db()
    responder_escala(participacao, pergunta, -2, agora=c.na_coleta())
    bruto = leitura.ler_csv(exportar_csv(capturar_snapshot(campanha)), revertido=False)
    coluna = bruto["dados"][0].index(f"pergunta_{pergunta.pk.hex}")
    assert [linha[coluna] for linha in bruto["dados"][1:]] == ["-2"]


def test_xlsx_texto_como_texto_sem_formula(com_textos, inst, chave_ficticia):
    snapshot, conclusoes = com_textos
    conteudo = exportar_xlsx(snapshot)
    assert leitura.formulas(conteudo) == []
    cabecalho, linhas = leitura.normalizar_xlsx(leitura.ler_xlsx(conteudo))["dados"]
    texto, ident = cabecalho.index(_coluna_texto(inst)), cabecalho.index("conclusao_analitica_id")
    por_id = {linha[ident]: linha[texto] for linha in linhas}
    for original in TEXTOS:
        assert por_id[apoio.id_de(conclusoes[original], chave_ficticia)] == original


def test_nota_de_escape(snapshot):
    nota = apoio.metadados(snapshot)["nota_escape_csv"]
    assert nota == NOTAS["nota_escape_csv"]
    assert "apóstrofo" in nota and "reverter" in nota.lower() and "XLSX" in nota


@pytest.mark.parametrize(
    "texto",
    ["controle \x01 no meio", "x" * 32768, "padrão _x0041_ literal", "_x005F_x0041_"],
    ids=["controle", "longo", "padrao", "padrao-escapado"],
)
def test_valor_nao_representavel_no_xlsx(snapshot, cenario, texto):
    # gravado por ORM só no teste: a operação da 005 aceitaria, mas o XLSX não representa
    Resposta.objects.filter(participacao=cenario.concluida, pergunta=cenario.inst.texto).update(
        texto=texto
    )
    with pytest.raises(ValorNaoRepresentavel) as erro:
        exportar_xlsx(snapshot)
    assert erro.value.formato == "xlsx"
    assert erro.value.coluna == f"pergunta_{cenario.inst.texto.pk.hex}"
    assert texto[:20] not in str(erro.value)
    lido = leitura.normalizar_csv(leitura.ler_csv(exportar_csv(snapshot)))
    assert texto in {v for linha in lido["dados"][1] for v in linha}

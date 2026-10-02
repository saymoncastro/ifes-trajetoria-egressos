"""Dicionário de dados (US6; spec FR-050 a FR-058; data-model §2)."""

import pytest

from tests.analitico import construcao as c
from tests.participacao.construcao import (
    opcao_de,
    pergunta_de,
    pergunta_mem,
    secao_mem,
    versao_publicada_de,
)
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao.contrato import CABECALHO_DICIONARIO, COLUNAS_BASE
from trajetoria.exportacao.dataset import dataset_exportado

pytestmark = pytest.mark.django_db


def _dicionario(snapshot) -> list[dict]:
    dataset = dataset_exportado(snapshot)
    return [
        dict(zip(CABECALHO_DICIONARIO, linha, strict=True)) for linha in dataset.dicionario.linhas
    ]


def _p(pergunta) -> str:
    return f"pergunta_{pergunta.pk.hex}"


def test_uma_linha_coluna_por_coluna_de_dados_na_mesma_ordem(snapshot):
    dataset = dataset_exportado(snapshot)
    colunas = [linha for linha in _dicionario(snapshot) if linha["elemento"] == "coluna"]
    assert [linha["coluna"] for linha in colunas] == list(dataset.dados.cabecalho)
    assert [linha["ordem"] for linha in colunas] == list(range(1, len(colunas) + 1))


def test_valores_possiveis_da_escolha_unica_apos_a_coluna(snapshot, inst):
    linhas = _dicionario(snapshot)
    nomes = [(linha["elemento"], linha["coluna"]) for linha in linhas]
    i = nomes.index(("coluna", _p(inst.unica_outro)))
    seguintes = linhas[i + 1 : i + 4]
    assert [linha["elemento"] for linha in seguintes] == ["valor_possivel"] * 3
    assert [linha["opcao_texto"] for linha in seguintes] == ["A", "B", "Outro:"]
    assert [linha["opcao_posicao"] for linha in seguintes] == [1, 2, 3]
    for linha in seguintes:
        assert linha["coluna"] == _p(inst.unica_outro)
        assert linha["ordem"] == linhas[i]["ordem"]
        assert (linha["tipo_valor"], linha["proveniencia"]) == ("texto", "declarado")
    assert seguintes[2]["opcao_admite_complemento"] is True
    # escolha múltipla: as Opções são colunas, sem linhas de valor possível
    assert ("valor_possivel", _p(inst.multipla)) not in nomes


def test_regra_finaliza(snapshot, inst):
    nao = next(
        linha
        for linha in _dicionario(snapshot)
        if linha["elemento"] == "valor_possivel"
        and linha["coluna"] == _p(inst.unica)
        and linha["opcao_texto"] == "Não"
    )
    assert nao["opcao_regra_finaliza"] is True
    assert nao["opcao_regra_destino_secao"] is None
    sim = next(
        linha
        for linha in _dicionario(snapshot)
        if linha["elemento"] == "valor_possivel" and linha["opcao_texto"] == "Sim"
    )
    assert sim["opcao_regra_finaliza"] is False


def test_regra_ir_para_secao_e_encaminhamento_por_posicao(inst):
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": 3})),
        secao_mem(pergunta_mem(tipo="TEXTO_CURTO", obrigatoria=False), encaminhamento=4),
        secao_mem(pergunta_mem(tipo="TEXTO_CURTO", obrigatoria=False)),
        secao_mem(pergunta_mem(tipo="TEXTO_CURTO", obrigatoria=False)),
    )
    snapshot = capturar_snapshot(c.campanha_aberta_no_passado(versao))
    linhas = _dicionario(snapshot)
    sim = next(
        linha
        for linha in linhas
        if linha["elemento"] == "valor_possivel"
        and linha["opcao_texto"] == opcao_de(pergunta_de(versao, 1, 1), "Sim").texto
    )
    assert sim["opcao_regra_destino_secao"] == 3
    assert sim["opcao_regra_finaliza"] is False
    da_secao_2 = [
        linha
        for linha in linhas
        if linha["elemento"] == "coluna"
        and linha["coluna"].startswith(_p(pergunta_de(versao, 2, 1)))
    ]
    assert da_secao_2 and all(linha["secao_encaminhamento_destino"] == 4 for linha in da_secao_2)
    sem = [linha for linha in linhas if linha["secao_posicao"] == 3]
    assert all(linha["secao_encaminhamento_destino"] is None for linha in sem)


def test_escala(snapshot, inst):
    escala = next(linha for linha in _dicionario(snapshot) if linha["coluna"] == _p(inst.escala))
    assert (escala["escala_inicio"], escala["escala_fim"]) == (1, 5)
    assert escala["escala_rotulo_fim"] == "Concordo totalmente"
    assert escala["escala_rotulo_inicio"] is None
    assert escala["tipo_valor"] == "inteiro"


def test_proveniencia_de_cada_coluna(snapshot):
    for linha in _dicionario(snapshot):
        if linha["elemento"] != "coluna":
            continue
        nome = linha["coluna"]
        if nome.startswith("pergunta_"):
            esperado = "derivado" if nome.endswith("__aplicavel") else "declarado"
        else:
            esperado = next(b.proveniencia for b in COLUNAS_BASE if b.nome == nome)
        assert linha["proveniencia"] == esperado, nome
    base = {b.nome: b.proveniencia for b in COLUNAS_BASE}
    assert {base[n] for n in ("conclusao_analitica_id", "elegivel_no_snapshot")} == {"derivado"}
    assert base["unidade"] == base["data_conclusao"] == "institucional"
    assert base["possui_participacao"] == base["participacao_concluida_em"] == "coleta"


def test_descricoes_das_colunas_base_sao_as_do_contrato(snapshot):
    descricoes = {
        linha["coluna"]: linha["descricao"]
        for linha in _dicionario(snapshot)
        if linha["elemento"] == "coluna"
    }
    for base in COLUNAS_BASE:
        assert descricoes[base.nome] == base.descricao


def test_campos_da_pergunta_e_versao(snapshot, inst):
    linhas = _dicionario(snapshot)
    assert {linha["versao"] for linha in linhas} == {str(inst.versao.pk)}
    tipos = {linha["pergunta_tipo"] for linha in linhas if linha["pergunta_tipo"]}
    assert tipos == {"escolha_unica", "escolha_multipla", "texto_curto", "escala"}
    texto = next(linha for linha in linhas if linha["coluna"] == _p(inst.texto))
    assert texto["pergunta_texto"] == inst.texto.texto
    assert (texto["secao_posicao"], texto["pergunta_posicao"]) == (1, 4)
    assert texto["pergunta_obrigatoria"] is True


def test_sem_sensibilidade_identidade_global_ou_equivalencia():
    proibidos = ("sensib", "canonic", "global", "linhagem", "equivalen")
    assert not [n for n in CABECALHO_DICIONARIO if any(p in n for p in proibidos)]


def test_esquema_independe_das_respostas(inst):
    vazia = capturar_snapshot(c.campanha_aberta_no_passado(inst.versao))
    assert dataset_exportado(vazia).dados.cabecalho
    linhas = _dicionario(vazia)
    assert {linha["coluna"] for linha in linhas if linha["coluna"].startswith(_p(inst.posterior))}

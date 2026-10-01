"""Fonte simulada: cada linha do catálogo documentado produz o resultado declarado.

O catálogo é lido de contracts/cenarios-simulados.md, para que documentação e dados não
possam divergir (FR-027).
"""

import re
from datetime import date
from pathlib import Path

import pytest

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contrato import (
    ConclusaoEncontrada,
    ConclusaoInexistente,
    FonteAcademicaIndisponivel,
    PessoaEncontrada,
    PessoaInexistente,
    RegistroNaoReconhecidoComoConclusao,
)

CATALOGO = (
    Path(__file__).resolve().parent.parent
    / "specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md"
)
ABREVIACOES = {
    "Téc.": "Técnico", "Grad.": "Graduação", "Pós": "Pós-graduação",
    "Pres.": "Presencial", "EaD": "A distância", "—": None,
}


def _linhas_documentadas() -> list[dict]:
    linhas = []
    for linha in CATALOGO.read_text(encoding="utf-8").splitlines():
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(celulas) != 11 or not celulas[3].startswith("SIM-C-"):
            continue
        _, pessoa, _, registro, situacao, curso, unidade, nivel, modal, oferta, conclusao = celulas
        ano, data = None, None
        if conclusao != "—":
            if m := re.fullmatch(r"(\d{4}) \(só ano\)", conclusao):
                ano = int(m[1])
            else:
                data = date.fromisoformat(conclusao)
                ano = data.year
        linhas.append({
            "id_externo": registro,
            "id_pessoa": pessoa,
            "situacao": None if situacao == "(ausente)" else situacao,
            "curso": curso,
            "unidade": unidade,
            "nivel": ABREVIACOES.get(nivel, nivel),
            "modalidade": ABREVIACOES.get(modal, modal),
            "forma_oferta": ABREVIACOES.get(oferta, oferta),
            "ano_conclusao": ano,
            "data_conclusao": data,
        })
    return linhas


DOCUMENTADAS = _linhas_documentadas()


def test_catalogo_documentado_e_dados_sao_identicos():
    assert len(DOCUMENTADAS) == len(cenarios.REGISTROS) == 19
    assert [vars(r) for r in cenarios.REGISTROS] == DOCUMENTADAS
    assert len(cenarios.PESSOAS) == 11


@pytest.mark.parametrize("linha", DOCUMENTADAS, ids=lambda linha: linha["id_externo"])
def test_cada_registro_produz_o_resultado_declarado(fonte_simulada, linha):
    resposta_conclusao = fonte_simulada.obter_conclusao(linha["id_externo"])
    da_pessoa = fonte_simulada.obter_pessoa(linha["id_pessoa"])
    assert isinstance(da_pessoa, PessoaEncontrada)
    ids_da_pessoa = {c.id_externo for c in da_pessoa.conclusoes}

    if linha["situacao"] == "concluida":
        assert isinstance(resposta_conclusao, ConclusaoEncontrada)
        assert resposta_conclusao.id_externo_pessoa == linha["id_pessoa"]
        assert linha["id_externo"] in ids_da_pessoa
        esperado = {k: v for k, v in linha.items() if k not in ("id_pessoa", "situacao")}
        assert vars(resposta_conclusao.conclusao) == esperado
    else:
        assert isinstance(resposta_conclusao, RegistroNaoReconhecidoComoConclusao)
        assert linha["id_externo"] not in ids_da_pessoa


def test_cenario_g_identificadores_desconhecidos(fonte_simulada):
    assert isinstance(fonte_simulada.obter_pessoa("SIM-P-9999"), PessoaInexistente)
    assert isinstance(fonte_simulada.obter_conclusao("SIM-C-9999"), ConclusaoInexistente)


def test_cenario_h_fonte_indisponivel(fonte_indisponivel):
    with pytest.raises(FonteAcademicaIndisponivel):
        fonte_indisponivel.obter_pessoa("SIM-P-0001")
    with pytest.raises(FonteAcademicaIndisponivel):
        fonte_indisponivel.obter_conclusao("SIM-C-0001")


def test_pessoas_so_com_registros_nao_concluidos_tem_tupla_vazia(fonte_simulada):
    for id_pessoa in ("SIM-P-0006", "SIM-P-0008"):
        assert fonte_simulada.obter_pessoa(id_pessoa).conclusoes == ()


def test_dados_sao_ficticios():
    cpf = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
    for pessoa in cenarios.PESSOAS:
        assert pessoa.id_externo.startswith("SIM-")
        assert pessoa.nome is None or pessoa.nome.endswith(" Exemplo")
    for registro in cenarios.REGISTROS:
        assert registro.id_externo.startswith("SIM-")
        for valor in vars(registro).values():
            if isinstance(valor, str):
                assert not cpf.search(valor)
                assert "@" not in valor
        if registro.data_conclusao is not None:
            assert registro.data_conclusao <= date(2026, 9, 30)

"""Suíte de contrato da fronteira (contracts/fonte-academica.md, regras 1–8).

Toda implementação, simulada ou real, deve passar nesta suíte com os casos que declara.
"""

import ast
from dataclasses import fields
from pathlib import Path

import pytest

from tests.fontes_de_teste import CASOS_DE_CONTRATO, FonteAlternativa
from trajetoria.fonte_academica.contrato import (
    ConclusaoEncontrada,
    ConclusaoInexistente,
    FonteAcademicaIndisponivel,
    PessoaEncontrada,
    PessoaInexistente,
    RegistroNaoReconhecidoComoConclusao,
)
from trajetoria.fonte_academica.simulada import FonteSimulada

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(params=[FonteSimulada, FonteAlternativa], ids=lambda c: c.__name__)
def implementacao(request):
    return request.param


@pytest.fixture
def fonte(implementacao):
    return implementacao()


@pytest.fixture
def casos(implementacao):
    return CASOS_DE_CONTRATO[implementacao]


def test_codigo_nao_vazio(fonte):
    assert isinstance(fonte.codigo, str) and fonte.codigo


def test_pessoa_traz_so_conclusoes_reconhecidas(fonte, casos):
    resposta = fonte.obter_pessoa(casos["pessoa_com_conclusoes"])

    assert isinstance(resposta, PessoaEncontrada)
    assert resposta.conclusoes
    for conclusao in resposta.conclusoes:
        assert isinstance(fonte.obter_conclusao(conclusao.id_externo), ConclusaoEncontrada)


def test_pessoa_sem_conclusao_e_encontrada_com_tupla_vazia(fonte, casos):
    resposta = fonte.obter_pessoa(casos["pessoa_sem_conclusao"])

    assert isinstance(resposta, PessoaEncontrada)
    assert resposta.conclusoes == ()


def test_pessoa_inexistente(fonte, casos):
    assert isinstance(fonte.obter_pessoa(casos["pessoa_inexistente"]), PessoaInexistente)


def test_conclusao_reconhecida_aponta_sua_pessoa(fonte, casos):
    resposta = fonte.obter_conclusao(casos["conclusao_reconhecida"])

    assert isinstance(resposta, ConclusaoEncontrada)
    dona = fonte.obter_pessoa(resposta.id_externo_pessoa)
    assert resposta.conclusao in dona.conclusoes


def test_nao_reconhecido_e_distinto_de_inexistente(fonte, casos):
    assert isinstance(
        fonte.obter_conclusao(casos["registro_nao_reconhecido"]),
        RegistroNaoReconhecidoComoConclusao,
    )
    assert isinstance(fonte.obter_conclusao(casos["conclusao_inexistente"]), ConclusaoInexistente)


def test_ausencia_e_none_e_ano_coerente_com_data(fonte, casos):
    for conclusao in fonte.obter_pessoa(casos["pessoa_com_conclusoes"]).conclusoes:
        for campo in fields(conclusao):
            assert getattr(conclusao, campo.name) != ""
        if conclusao.data_conclusao is not None:
            assert conclusao.ano_conclusao == conclusao.data_conclusao.year


def test_resultado_deterministico(fonte, casos):
    for chave in ("pessoa_com_conclusoes", "pessoa_sem_conclusao", "pessoa_inexistente"):
        assert fonte.obter_pessoa(casos[chave]) == fonte.obter_pessoa(casos[chave])


def test_falha_da_fonte_e_excecao_propria(implementacao, casos):
    fonte = implementacao(indisponivel=True)

    with pytest.raises(FonteAcademicaIndisponivel):
        fonte.obter_pessoa(casos["pessoa_com_conclusoes"])
    with pytest.raises(FonteAcademicaIndisponivel):
        fonte.obter_conclusao(casos["conclusao_reconhecida"])


# --- Fronteira de dependências (FR-021) --------------------------------------------------


def _modulos_importados(caminho: Path) -> set[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            # Inclui `from pacote import modulo` como `pacote.modulo`.
            nomes.add(no.module)
            nomes.update(f"{no.module}.{alias.name}" for alias in no.names)
    return nomes


def test_contrato_nao_importa_django():
    importados = _modulos_importados(RAIZ / "trajetoria/fonte_academica/contrato.py")
    assert not any(nome.split(".")[0] == "django" for nome in importados)


def test_nucleo_nao_conhece_fonte_concreta():
    proibidos = ("trajetoria.fonte_academica.simulada", "trajetoria.fonte_academica.cenarios")
    for caminho in (RAIZ / "trajetoria/academico").rglob("*.py"):
        importados = _modulos_importados(caminho)
        assert not any(nome.startswith(proibidos) for nome in importados), caminho


@pytest.mark.parametrize("cpf", ["123", "123456789012", "000.000.001-91", ""])
def test_cpf_canonico_018(cpf):
    with pytest.raises(ValueError):
        PessoaEncontrada("SIM-P-X", None, (), cpf=cpf)


def test_material_nao_aparece_no_repr_018():
    from datetime import date

    p = PessoaEncontrada("SIM-P-X", None, (), cpf="00000000191", data_nascimento=date(1998, 4, 12))
    assert "00000000191" not in repr(p) and "1998" not in repr(p)
    assert PessoaEncontrada("SIM-P-X", None, ()).cpf is None

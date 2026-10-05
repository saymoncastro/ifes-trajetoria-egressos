"""Contrato serializado da `TrajetoriaNarrativa` (021 FR-012 a FR-014; contracts/narrativa.md)."""

import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import date

import pytest

from trajetoria.narrativa import contrato as ct

PROIBIDAS = {"id", "fonte", "id_externo", "incorporado_em", "cpf", "data_nascimento", "pk"}


def _narrativa():
    return ct.TrajetoriaNarrativa(
        referencia=date(2026, 10, 4),
        nome="Maria Exemplo",
        formacoes=(
            ct.Formacao(curso="TADS", unidade="Serra", nivel="Graduação", ano_conclusao=2022),
            ct.Formacao(
                curso="Especialização",
                unidade="Cefor",
                ano_conclusao=2025,
                data_conclusao=date(2025, 3, 28),
                relacao=ct.Relacao("depois_de", 0),
            ),
        ),
        derivados=(
            ct.Derivado("formacoes_registradas", 2, "contagem das Conclusões Acadêmicas"),
            ct.Derivado("tempo_desde_conclusao", 1, "anos completos", formacao=1),
        ),
        contextos_agregados=(),
        secoes=(
            ct.Secao(
                "o_que_o_ifes_registra",
                "O que o Ifes registra sobre você",
                (ct.Frase("O Ifes registra 2 formações concluídas por você.", "derivado"),),
            ),
        ),
        compartilhavel=ct.Compartilhavel(
            formacoes=(
                ct.FormacaoCompartilhavel(
                    curso="TADS", unidade="Serra", nivel="Graduação", modalidade=None,
                    ano_conclusao=2022, linhas_curso=("TADS",),
                    linhas_detalhe=("Serra · Graduação · 2022",),
                ),
            ),
            formacoes_omitidas=0,
            formacoes_registradas=2,
            contextos_agregados=(),
            nome_disponivel=True,
        ),
    )


def _chaves(valor):
    if isinstance(valor, dict):
        for chave, item in valor.items():
            yield chave
            yield from _chaves(item)
    elif isinstance(valor, list):
        for item in valor:
            yield from _chaves(item)


def _valores(valor):
    if isinstance(valor, dict):
        for item in valor.values():
            yield from _valores(item)
    elif isinstance(valor, list):
        for item in valor:
            yield from _valores(item)
    else:
        yield valor


def test_dataclasses_congeladas():
    for nome in dir(ct):
        classe = getattr(ct, nome)
        if isinstance(classe, type) and is_dataclass(classe):
            assert classe.__dataclass_params__.frozen, nome
    with pytest.raises(FrozenInstanceError):
        _narrativa().nome = "Outro"


def test_versao_e_ordem_das_chaves():
    dados = ct.serializar(_narrativa())
    assert dados["versao_contrato"] == 1
    assert list(dados) == [
        "versao_contrato", "referencia", "identidade", "formacoes", "marcos", "derivados",
        "contextos_agregados", "secoes", "compartilhavel",
    ]
    assert dados["referencia"] == "2026-10-04"
    assert dados["formacoes"][1]["relacao"] == {"tipo": "depois_de", "indice": 0}
    assert dados["formacoes"][1]["data_conclusao"] == "2025-03-28"


def test_ausencia_e_omitida_nunca_null():
    dados = ct.serializar(_narrativa())
    assert None not in list(_valores(dados))
    assert "modalidade" not in dados["formacoes"][0]
    assert "relacao" not in dados["formacoes"][0]


def test_sem_identificadores_tecnicos_nem_dados_pessoais():
    assert not PROIBIDAS & set(_chaves(ct.serializar(_narrativa())))
    for classe in (ct.FatoDaFormacao, ct.Formacao, ct.FormacaoCompartilhavel):
        assert not PROIBIDAS & {f.name for f in fields(classe)}


def test_origem_em_cada_fato():
    dados = ct.serializar(_narrativa())
    assert dados["identidade"]["origem"] == "institucional"
    assert all(f["origem"] == "institucional" for f in dados["formacoes"])
    assert all(d["origem"] == "derivado" for d in dados["derivados"])


def test_sem_nome_a_identidade_fica_vazia():
    narrativa = _narrativa()
    sem_nome = ct.TrajetoriaNarrativa(**{**narrativa.__dict__, "nome": None})
    assert ct.serializar(sem_nome)["identidade"] == {}


def test_serializacao_deterministica():
    um = json.dumps(ct.serializar(_narrativa()), ensure_ascii=False)
    dois = json.dumps(ct.serializar(_narrativa()), ensure_ascii=False)
    assert um == dois


def test_compartilhavel_sem_nome():
    dados = ct.serializar(_narrativa())["compartilhavel"]
    assert "nome" not in dados and dados["nome_disponivel"] is True

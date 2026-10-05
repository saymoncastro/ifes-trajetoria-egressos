"""Catálogo fechado de formulações (021 FR-022 a FR-024, FR-061; contracts/catalogo.md)."""

import re
import string

import pytest

from tests.narrativa import construcao as cn
from trajetoria.narrativa import catalogo as cat
from trajetoria.narrativa.montagem import montar

PERMITIDOS = {"curso", "unidade", "ano", "n", "nome", "apuracao"}


def _placeholders(texto):
    return {campo for _, campo, _, _ in string.Formatter().parse(texto) if campo}


def test_placeholders_do_conjunto_fechado():
    for formulacao in cat.FORMULACOES:
        assert _placeholders(formulacao) <= PERMITIDOS, formulacao


def test_unidade_sem_campus_e_sempre_na_unidade():
    for formulacao in cat.FORMULACOES:
        assert "Campus" not in formulacao, formulacao
        if "{unidade}" in formulacao:
            assert "na unidade {unidade}" in formulacao, formulacao


def test_vedadas_cobrem_o_contrato():
    esperadas = {
        "tudo começou", "turma", "geração", "coorte", "colegas", "se formaram com você",
        "matriculad", "ingressantes", "estudantes", "alunos", "egressos", "%", "taxa",
        "mais que", "melhores", "entre os", "época especial", "viveu", "verticaliza",
    }
    assert esperadas <= set(cat.VEDADAS)


def test_singular_e_plural():
    for par in (cat.REGISTRADAS, cat.HA_ANOS, cat.CARD_MAIS, cat.CARD_REGISTRADAS,
                cat.AGREGADO_CURSO, cat.AGREGADO_UNIDADE):
        assert len(par) == 2
        assert cat.plural(par, 1) == par[0] and cat.plural(par, 2) == par[1]


def test_nenhuma_formulacao_contem_termo_vedado():
    for formulacao in cat.FORMULACOES:
        for termo in cat.VEDADAS:
            assert termo.lower() not in formulacao.lower(), (termo, formulacao)


def test_formulacoes_sem_texto_tecnico():
    for formulacao in cat.FORMULACOES:
        assert not re.search(r"SIM-|simulada|None|null", formulacao), formulacao


# --- Varredura sobre todos os cenários simulados (SC-001; T014) ---------------------------

def _padrao(formulacao):
    partes = re.split(r"(\{[a-z]+\})", formulacao)
    return re.compile(
        "^" + "".join(".+?" if p.startswith("{") else re.escape(p) for p in partes) + "$"
    )


PADROES = [_padrao(f) for f in cat.FORMULACOES]


def _todas_as_frases(narrativa):
    for secao in narrativa.secoes:
        yield from secao.frases


@pytest.mark.parametrize("id_externo", sorted(cn.entradas_dos_cenarios()))
def test_toda_frase_e_do_catalogo(id_externo):
    entrada = cn.entradas_dos_cenarios()[id_externo]
    valores = {
        str(v) for f in entrada.formacoes for v in vars(f).values() if v is not None
    } | ({entrada.nome} if entrada.nome else set())
    for frase in _todas_as_frases(montar(entrada)):
        if frase.tipo == "atributos":
            assert all(parte in valores for parte in frase.texto.split(" · ")), frase.texto
        else:
            assert any(p.match(frase.texto) for p in PADROES), frase.texto


@pytest.mark.parametrize("id_externo", sorted(cn.entradas_dos_cenarios()))
def test_nenhum_termo_vedado(id_externo):
    narrativa = montar(cn.entradas_dos_cenarios()[id_externo])
    textos = [f.texto for f in _todas_as_frases(narrativa)]
    textos += [linha for f in narrativa.compartilhavel.formacoes
               for linha in f.linhas_curso + f.linhas_detalhe]
    for texto in textos:
        for termo in cat.VEDADAS:
            assert termo.lower() not in texto.lower(), (termo, texto)


def test_templates_e_textos_novos_sem_termo_vedado():
    """T054: a varredura cobre também os textos fixos da 021 fora do catálogo."""
    from pathlib import Path

    from trajetoria.interface import mensagens

    fontes = [p.read_text(encoding="utf-8") for p in
              Path("trajetoria/narrativa/templates/narrativa").glob("*.html")]
    fontes += [mensagens.ANTECIPACAO, mensagens.TITULO_TRAJETORIA]
    for texto in fontes:
        texto = re.sub(r"<script>.*?</script>", "", texto, flags=re.S)  # código, não texto
        texto = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", "", texto)  # sintaxe de template
        for termo in cat.VEDADAS:
            assert termo.lower() not in texto.lower(), termo

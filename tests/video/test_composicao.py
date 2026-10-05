"""Composição visual serializada (022; contracts/composicao-visual.md; FR-004 a FR-008,
FR-012, FR-013, FR-019 a FR-023, FR-039)."""

import json
import re
import xml.etree.ElementTree as ET

import pytest

from tests.narrativa import construcao as cn
from tests.video.construcao import CASOS, NOME, composicao, zona
from trajetoria.narrativa import card, catalogo
from trajetoria.narrativa import composicao as modulo

SVG = "{http://www.w3.org/2000/svg}"
CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
DATA = re.compile(r"\d{2}/\d{2}/\d{4}")
CHAVES_VEDADAS = {"id", "cpf", "data_nascimento", "forma_oferta", "ingresso", "data_conclusao",
                  "id_externo", "pessoa", "conclusao", "participacao"}


def _textos_das_partes(c: dict) -> list[str]:
    textos = []
    for z in c["zonas"]:
        for parte in z["partes"]:
            raiz = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{parte}</svg>')
            textos += [t.text for t in raiz.iter(f"{SVG}text") if t.text]
    return textos


def _textos_do_card(caso: str, nome: str | None) -> list[str]:
    raiz = ET.fromstring(card.card_svg(CASOS[caso](), nome=nome))
    return [t.text for t in raiz.iter(f"{SVG}text") if t.text]


def _chaves(valor):
    if isinstance(valor, dict):
        for chave, v in valor.items():
            yield chave
            yield from _chaves(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from _chaves(v)


CASOS_E_NOMES = [(caso, nome) for caso in CASOS for nome in (None, NOME)]


def test_forma():
    c = composicao("maria", NOME)
    assert c["versao_contrato"] == 1
    assert c["template"] == "trajetoria-v1"
    assert (c["largura"], c["altura"]) == (1080, 1920)
    assert c["area_segura"] == [90, 270, 990, 1650]
    traco = zona(c, "traco")
    assert traco["y1"] < traco["y2"]
    assert all(isinstance(p, str) and p for z in c["zonas"] for p in z["partes"])


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_textos_iguais_aos_do_card(caso, nome):
    assert sorted(_textos_das_partes(composicao(caso, nome))) == sorted(
        _textos_do_card(caso, nome)
    )


@pytest.mark.parametrize(("caso", "nome"), CASOS_E_NOMES)
def test_sem_conteudo_vedado(caso, nome):
    c = composicao(caso, nome)
    for texto in _textos_das_partes(c):
        minusculo = texto.lower()
        assert not any(v in minusculo for v in catalogo.VEDADAS), texto
        assert not any(p in minusculo for p in ("certificado", "comprovante", "declaração"))
        assert not CPF.search(texto)
        assert not DATA.search(texto) or texto.startswith("Dados institucionais apurados em")
    assert not CHAVES_VEDADAS & set(_chaves(c))


def test_nome_so_quando_escolhido():
    sem = composicao("maria", None)
    assert zona(sem, "nome") is None
    assert NOME not in json.dumps(sem, ensure_ascii=False)
    com = composicao("maria", NOME)
    assert NOME in _textos_das_partes(com)


def test_texto_escapado():
    nome = 'Ana <b>&amp; "Cia"'
    c = composicao("ana", nome)
    parte = zona(c, "nome")["partes"][0]
    assert "&lt;b&gt;" in parte and "&amp;amp;" in parte and "<b>" not in parte
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{parte}</svg>')
    assert nome in _textos_das_partes(c)


def test_determinismo_e_chave():
    a, b = composicao("maria", NOME), composicao("maria", NOME)
    assert modulo.canonico(a) == modulo.canonico(b)
    assert modulo.chave_da_composicao(a) == modulo.chave_da_composicao(b)
    assert len(modulo.chave_da_composicao(a)) == 64
    assert modulo.chave_da_composicao(a) != modulo.chave_da_composicao(composicao("maria"))


def test_versao_do_template_entra_na_chave(monkeypatch):
    antes = modulo.chave_da_composicao(composicao("ana"))
    monkeypatch.setattr(modulo, "TEMPLATE_DE_VIDEO", "trajetoria-v2")
    assert modulo.chave_da_composicao(composicao("ana")) != antes


def test_modulo_sem_dependencias_de_dominio():
    fonte = open(modulo.__file__, encoding="utf-8").read()
    for proibido in ("trajetoria.academico", "trajetoria.participacao", "trajetoria.video",
                     "subprocess"):
        assert proibido not in fonte


# --- Matriz de casos (US3; T021) ----------------------------------------------------------


@pytest.mark.parametrize(
    ("caso", "nos"),
    [("ana", 1), ("maria", 2), ("diego", 3), ("quatro", 3), ("quatro_curtos", 4)],
)
def test_um_no_por_formacao_exibida(caso, nos):
    c = composicao(caso)
    assert len(zona(c, "nos")["partes"]) == nos
    assert (zona(c, "traco") is not None) == (nos >= 2)


def test_pior_caso_igual_ao_card():
    c = composicao("pior")
    exibidas = card.compor(cn.pior_caso(), None, True).exibidas
    assert len(zona(c, "nos")["partes"]) == exibidas
    mais = _textos_das_partes({"zonas": [zona(c, "mais")]})
    assert mais and mais == [t for t in _textos_do_card("pior", None) if t.startswith("e mais")]


def test_sem_agregado_sem_destaques_nem_numero():
    c = composicao("diego")
    assert zona(c, "destaques") is None and zona(c, "apuracao") is None
    assert 'class="numero"' not in json.dumps(c)


def test_um_destaque():
    c = composicao("sem_imagem")
    assert len(zona(c, "destaques")["partes"]) == 1
    assert "41" in _textos_das_partes({"zonas": [zona(c, "destaques")]})


def test_dois_destaques_iguais_ao_card():
    c = composicao("maria")
    textos = _textos_das_partes({"zonas": [zona(c, "destaques")]})
    assert "27" in textos and "812" in textos
    assert len(zona(c, "destaques")["partes"]) == 2


def test_legenda_sem_imagem_propria_e_sem_unidade():
    sem_imagem = _textos_das_partes({"zonas": [zona(composicao("sem_imagem"), "legenda")]})
    assert sem_imagem == ["Unidade Linhares · ilustração"]
    sem_unidade = _textos_das_partes({"zonas": [zona(composicao("sem_unidade"), "legenda")]})
    assert sem_unidade == ["Ifes · ilustração"]
    for texto in sem_imagem + sem_unidade:
        assert not re.search(r"\d{4}", texto)


def test_acentos_preservados():
    serializado = modulo.canonico(composicao("maria"))
    for trecho in ("Graduação", "Pós-graduação", "A distância", "Análise", "Essa história"):
        assert trecho in serializado


def test_composicao_impossivel_falha_explicitamente(monkeypatch, caplog):
    monkeypatch.setattr(card, "compor", lambda *a, **k: card.Composicao((), 0, False, 0))
    with pytest.raises(modulo.ComposicaoImpossivel):
        composicao("maria")
    assert "Maria" not in caplog.text and "Tecnologia" not in caplog.text


def test_conteudo_que_nao_cabe_nem_no_minimo_falha(monkeypatch):
    # Uma área segura minúscula: nem título, um curso e fecho cabem.
    monkeypatch.setattr(card, "BASE", card.TOPO + 200)
    with pytest.raises(modulo.ComposicaoImpossivel):
        composicao("ana")


@pytest.mark.parametrize("caso", ["maria", "diego", "quatro_curtos"])
def test_paradas_do_traco_sao_os_centros_dos_nos(caso):
    c = composicao(caso)
    traco = zona(c, "traco")
    assert len(traco["paradas"]) == len(zona(c, "nos")["partes"])
    assert traco["paradas"][0] == traco["y1"] and traco["paradas"][-1] == traco["y2"]
    assert traco["paradas"] == sorted(traco["paradas"])


def test_classe_sem_zona_quebra_so_o_video(monkeypatch):
    """Um elemento novo no card sem zona mapeada não pode derrubar o card da 021."""
    monkeypatch.setattr(card, "_ZONA_DA_CLASSE", {})
    assert card.card_svg(cn.caso_maria()).startswith("<svg")
    with pytest.raises(modulo.ComposicaoImpossivel):
        composicao("maria")

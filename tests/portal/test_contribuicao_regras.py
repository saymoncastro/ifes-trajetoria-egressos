"""Regras da contribuição sem banco (026 T002; plan, "Testes": regras)."""

import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao import planilha
from trajetoria.portal.contribuicao.consultas import Descrita
from trajetoria.portal.contribuicao.regras import (
    ManifestacaoRejeitada,
    Motivo,
    Situacao,
    email_da_contribuicao,
    normalizar_mensagem,
    situacao,
    violacoes_da_escolha,
)
from trajetoria.portal.models import MENSAGEM_MAXIMA, Forma

MOMENTO = datetime(2026, 10, 9, 13, 0, tzinfo=UTC)


def _manifestacao(**campos):
    base = {"retirada_em": None, "contato_registrado_em": None, "registrada_em": MOMENTO,
            "unidade": "Vila Velha", "forma": "mentoria", "mensagem": "", "email": "a@b.test"}
    return SimpleNamespace(**{**base, **campos})


# --- Situação derivada (FR-013; D-2601) -----------------------------------------------------

def test_situacao_derivada():
    assert situacao(_manifestacao()) is Situacao.ENVIADA
    assert situacao(_manifestacao(contato_registrado_em=MOMENTO)) is Situacao.CONTATO_REGISTRADO
    assert situacao(_manifestacao(retirada_em=MOMENTO)) is Situacao.RETIRADA
    # A retirada prevalece sobre o contato registrado antes dela.
    assert situacao(
        _manifestacao(contato_registrado_em=MOMENTO, retirada_em=MOMENTO)
    ) is Situacao.RETIRADA


# --- Formas, tamanhos e e-mail (FR-002 a FR-004) --------------------------------------------

def test_lista_fechada_de_formas():
    assert [f.value for f in Forma] == [
        "mentoria", "experiencia", "oportunidade", "pesquisa_extensao", "parceria", "historia",
    ]
    assert set(m.DESCRICOES) == set(Forma)
    for forma in Forma:
        assert violacoes_da_escolha(forma.value, "") == []
    for invalida in ("", "Mentoria", "outra", None):
        assert [v.motivo for v in violacoes_da_escolha(invalida, "")] == [Motivo.FORMA]


def test_mensagem_ate_500_com_quebra_de_linha_como_um_caractere():
    assert MENSAGEM_MAXIMA == 500
    assert violacoes_da_escolha("mentoria", "a" * 500) == []
    assert [v.motivo for v in violacoes_da_escolha("mentoria", "a" * 501)] == [Motivo.MENSAGEM]
    texto = normalizar_mensagem("  " + "a\r\n" * 250 + "  ")
    assert "\r" not in texto and len(texto) == 499
    assert normalizar_mensagem(None) == ""


@pytest.mark.parametrize("valor", ["", "sem-arroba", "a@b", "a b@c.test", "a@b.test\n", None,
                                   "x" * 250 + "@b.test"])
def test_email_invalido(valor):
    with pytest.raises(ManifestacaoRejeitada) as erro:
        email_da_contribuicao(valor)
    assert erro.value.motivos == (Motivo.EMAIL,)


def test_email_normalizado_como_na_020():
    assert email_da_contribuicao(" Nome@Provedor.COM.br ") == "Nome@provedor.com.br"


# --- CSV (FR-010; R8) ------------------------------------------------------------------------

@pytest.mark.parametrize("valor", ["=1+1", "+55", "-2", "@SOMA(A1)", "\tx", "\rx"])
def test_neutraliza_formulas(valor):
    assert planilha.neutralizar(valor) == "'" + valor


def test_texto_comum_fica_como_esta():
    assert planilha.neutralizar("Vila Velha") == "Vila Velha"
    assert planilha.neutralizar(None) == ""


def test_linhas_do_csv_sem_cpf_nem_nascimento():
    descrita = Descrita(
        _manifestacao(mensagem="=HYPERLINK(\"x\")", email="-a@b.test"),
        SimpleNamespace(curso="Licenciatura em Química"), "@Nome",
    )
    cabecalho, linha = planilha.linhas([descrita])
    assert cabecalho == list(m.CSV_CABECALHO)
    assert not {"cpf", "nascimento", "data_nascimento"} & set(cabecalho)
    assert linha == ["2026-10-09", "'@Nome", "Licenciatura em Química", "Vila Velha",
                     "Mentoria", "'=HYPERLINK(\"x\")", "'-a@b.test", m.SEM_CONTATO]


# --- Textos (FR-014; ADR 0009, decisão 7) ----------------------------------------------------

def _textos() -> str:
    constantes = [v for k, v in vars(m).items() if k.isupper()]
    partes = [v for v in constantes if isinstance(v, str)]
    partes += [t for v in constantes if isinstance(v, dict) for t in v.values()]
    partes += m.ciencia("Vila Velha") + m.ciencia("")
    return "\n".join(partes)


PROMESSAS = re.compile(
    r"em até|garant(?:e|imos|ido que)|vamos responder|responderemos|você será contatad|"
    r"vaga garantida|remunera|certificad|pagament|bolsa", re.I,
)
VEDADOS = ("conectad", "comunidade", "%", "turma", "geração", "Olá", "Volte ao Ifes",
           "não perca", "últimas vagas", "selecionado para você")


def test_sem_promessa_de_resposta_prazo_vaga_ou_certificado():
    assert PROMESSAS.findall(_textos()) == []
    assert "Não há prazo garantido." in _textos()


def test_sem_vocabulario_vedado():
    texto = _textos().lower()
    for vedado in VEDADOS:
        assert vedado.lower() not in texto, vedado


def test_ciencia_diz_quem_recebe_finalidade_e_retirada():
    """FR-007: unidade, finalidade do e-mail, sem prazo, marco do contato e retirada."""
    frases = " ".join(m.ciencia("Vila Velha"))
    assert "A unidade Vila Velha recebe" in frases
    assert "só para responder sobre esta contribuição" in frases
    assert "não inclui você em convites de pesquisa" in frases
    assert "Suas contribuições" in frases and "retirar" in frases
    assert "O Ifes recebe" in " ".join(m.ciencia(""))

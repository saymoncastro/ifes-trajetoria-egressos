"""Lista de Campanhas do acompanhamento (Feature 011; US1; spec FR-040 a FR-042; casos C)."""

import re

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel

LISTA = "/acompanhamento/"


def _linha(texto, nome):
    """O trecho da tabela da Campanha `nome` (até a próxima linha)."""
    inicio = texto.index(nome)
    return texto[inicio : inicio + 400]


def test_cpaeg_ve_todas_as_campanhas(ref, cliente_cpaeg):
    expirada = k.campanha(ref.inst.versao, estado="expirada_sem_abertura", nome="Campanha X")
    resposta = cliente_cpaeg.get(LISTA)
    assert resposta.status_code == 200
    texto = texto_visivel(resposta)
    for nome in ("Campanha I", "Campanha R", "Campanha P", "Campanha E", expirada.nome):
        assert nome in texto
    assert "Período encerrado — Campanha nunca aberta" in _linha(texto, expirada.nome)
    html = resposta.content.decode()
    for campanha in (ref.I, ref.R, ref.P, ref.E):
        assert f'href="/acompanhamento/campanhas/{campanha.pk}/"' in html


def test_cada_linha_tem_instrumento_periodo_situacao_e_tres_numeros(ref, cliente_cpaeg):
    texto = texto_visivel(cliente_cpaeg.get(LISTA))
    linha_i = _linha(texto, "Campanha I")
    assert f"{ref.inst.versao.pesquisa.nome} — {ref.inst.versao.designacao}" in linha_i
    assert "Em coleta" in linha_i
    assert re.search(r"\d{2}/\d{2}/\d{4} a \d{2}/\d{2}/\d{4}", linha_i)
    assert re.search(r"\b7\b.*\b4\b.*\b2\b", linha_i, re.S)
    assert "Em preparação" in _linha(texto, "Campanha P")
    assert "Encerrada" in _linha(texto, "Campanha E")


def test_cabecalhos_e_texto_permanente(ref, cliente_cpaeg):
    texto = texto_visivel(cliente_cpaeg.get(LISTA))
    for cabecalho in ("Elegíveis atuais", "Participações iniciadas", "Participações concluídas"):
        assert cabecalho in texto
    assert "população elegível atual" in texto
    assert "cada formação concluída conta separadamente" in texto


def test_sem_taxas_na_lista(ref, cliente_cpaeg):
    assert "%" not in texto_visivel(cliente_cpaeg.get(LISTA))


def test_periodo_nao_definido(ref, cliente_cpaeg):
    k.campanha(ref.inst.versao, estado="sem_periodo", nome="Campanha S")
    assert "Período não definido" in _linha(texto_visivel(cliente_cpaeg.get(LISTA)), "Campanha S")


def test_ordem_nao_depende_dos_numeros(ref, cliente_cpaeg):
    primeira = texto_visivel(cliente_cpaeg.get(LISTA))
    k.concluida(ref.R, k.conclusao(unidade="Serra", ano=2024), ref.inst)
    segunda = texto_visivel(cliente_cpaeg.get(LISTA))
    ordem = [n for n in ("Campanha E", "Campanha I", "Campanha P", "Campanha R")]
    assert sorted(ordem, key=primeira.index) == sorted(ordem, key=segunda.index)


def test_lista_vazia(cliente_cpaeg):
    assert "Nenhuma Campanha no escopo da sua atuação." in texto_visivel(cliente_cpaeg.get(LISTA))

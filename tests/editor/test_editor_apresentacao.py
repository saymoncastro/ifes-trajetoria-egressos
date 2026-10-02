"""Apresentação pura do editor (research R9; FR-032, FR-049, FR-060, FR-070).

Sem `django_db`: as funções só leem `ConteudoVersao` em memória.
"""

from dataclasses import replace

from tests.participacao.construcao import FIM, pergunta_mem, secao_mem, versao_mem
from trajetoria.editor import apresentacao as a
from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import TipoPergunta

TEXTO = TipoPergunta.TEXTO_CURTO


def _conteudo():
    return versao_mem(
        secao_mem(pergunta_mem(regras={"Não": FIM}), titulo="Termos"),
        secao_mem(pergunta_mem(regras={"Sim": 4}), pergunta_mem(tipo=TEXTO), encaminhamento=4),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="Final"),
    )


def test_ordinais_ignoram_lacunas_de_posicao():
    conteudo = _conteudo()
    com_lacunas = replace(
        conteudo,
        secoes=tuple(replace(s, posicao=s.posicao * 10) for s in conteudo.secoes),
    )
    ordinais = a.ordinais(com_lacunas)
    assert [ordinais[s.id] for s in com_lacunas.secoes] == [1, 2, 3, 4]
    segunda = com_lacunas.secoes[1]
    assert [ordinais[p.id] for p in segunda.perguntas] == [1, 2]
    assert [ordinais[o.id] for o in segunda.perguntas[0].opcoes] == [1, 2]


def test_rotulos():
    conteudo = _conteudo()
    termos, segunda = conteudo.secoes[0], conteudo.secoes[1]
    assert a.rotulo_secao(1, termos) == "Seção 1 — Termos"
    assert a.rotulo_secao(2, segunda) == "Seção 2 (sem título)"
    assert a.rotulo_pergunta(2, 1, segunda.perguntas[0]) == "Pergunta 1 da Seção 2: Pergunta 1"
    longa = replace(segunda.perguntas[0], texto="x" * 200)
    rotulo = a.rotulo_pergunta(2, 1, longa)
    assert rotulo.endswith("…") and len(rotulo) < 120
    opcao = segunda.perguntas[0].opcoes[1]
    assert a.rotulo_opcao(2, 1, opcao) == "Opção «Não» da Pergunta 1 da Seção 2"


def test_tipos_sao_exatamente_os_quatro():
    assert set(a.TIPOS) == set(TipoPergunta)
    for nome, descricao in a.TIPOS.values():
        assert nome and descricao


def test_descrever_escala():
    assert a.descrever_escala(Escala(1, 5, "Discordo totalmente", "Concordo totalmente")) == (
        "De 1 a 5 (5 pontos). 1 = «Discordo totalmente»; 5 = «Concordo totalmente». "
        "Pontos intermediários aparecem só com o número."
    )
    sem_inicio = a.descrever_escala(Escala(0, 10, None, "Muito"))
    assert "De 0 a 10 (11 pontos)" in sem_inicio
    assert "0 sem rótulo" in sem_inicio and "10 = «Muito»" in sem_inicio
    assert "intermediários" not in a.descrever_escala(Escala(1, 2))


def test_destinos():
    conteudo = _conteudo()
    termos, segunda, terceira, final = conteudo.secoes
    assert a.destino_da_secao(conteudo, termos) == "segue a ordem (Seção 2 (sem título))"
    assert a.destino_da_secao(conteudo, segunda) == "segue para a Seção 4 — Final"
    assert a.destino_da_secao(conteudo, final) == "finaliza o instrumento"
    nao = termos.perguntas[0].opcoes[1]
    sim = termos.perguntas[0].opcoes[0]
    assert a.destino_da_opcao(conteudo, nao) == "finaliza o instrumento"
    assert a.destino_da_opcao(conteudo, sim) is None
    assert a.destino_da_opcao(conteudo, segunda.perguntas[0].opcoes[0]) == (
        "segue para a Seção 4 — Final"
    )
    assert a.anotacao_previa(conteudo, segunda.perguntas[0].opcoes[0]) == (
        "Se «Sim» for escolhida na aplicação real, a próxima seção será: Seção 4 — Final."
    )
    assert a.anotacao_previa(conteudo, nao) == (
        "Se «Não» for escolhida na aplicação real, o instrumento é finalizado."
    )
    assert a.anotacao_previa(conteudo, sim) is None
    assert terceira.encaminhamento_id is None


def test_localizador():
    conteudo = _conteudo()
    local = a.localizador(conteudo)
    assert local[conteudo.id].endereco == f"/editor/versoes/{conteudo.id}/"
    secao = conteudo.secoes[3]
    assert local[secao.id] == a.Localizacao("Seção 4 — Final", f"/editor/secoes/{secao.id}/")
    pergunta = conteudo.secoes[1].perguntas[1]
    assert local[pergunta.id].rotulo == "Pergunta 2 da Seção 2: Pergunta 2"
    assert local[pergunta.id].endereco == f"/editor/perguntas/{pergunta.id}/"
    opcao = conteudo.secoes[0].perguntas[0].opcoes[0]
    assert local[opcao.id].endereco == f"/editor/opcoes/{opcao.id}/"


def test_referencias_a():
    conteudo = _conteudo()
    final = conteudo.secoes[3]
    assert a.referencias_a(conteudo, final.id) == [
        "o encaminhamento da Seção 2 (sem título)",
        "a Opção «Sim» da Pergunta 1 da Seção 2",
    ]
    assert a.referencias_a(conteudo, conteudo.secoes[2].id) == []

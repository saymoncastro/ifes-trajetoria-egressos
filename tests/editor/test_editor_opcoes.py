"""Opções e complemento (US8; FR-041 a FR-047)."""

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Opcao, TipoPergunta

pytestmark = pytest.mark.django_db
MULTIPLA = TipoPergunta.ESCOLHA_MULTIPLA


@pytest.fixture
def multipla(versao):
    secao = op.adicionar_secao(versao, 1)
    return op.adicionar_pergunta(secao, 1, MULTIPLA, "Quais?", obrigatoria=False)


def _nova(client, pergunta, texto, **extra):
    dados = {"texto": texto, **extra}
    return client.post(f"/editor/perguntas/{pergunta.pk}/opcoes/nova/", dados)


def test_adicionar_ao_final_e_incluir_outra(client, multipla):
    r1 = _nova(client, multipla, "Estágio")
    assert r1["Location"] == f"/editor/perguntas/{multipla.pk}/#opcao-1"
    r2 = _nova(client, multipla, "Monitoria", adicionar_outra="1")
    assert r2["Location"] == f"/editor/perguntas/{multipla.pk}/opcoes/nova/?aviso=opcao-criada"
    assert ce.ordem(multipla.opcoes) == ["Estágio", "Monitoria"]
    assert ce.posicoes(multipla.opcoes) == [1, 2]


def test_texto_gravado_como_digitado(client, multipla):
    _nova(client, multipla, "Outro:", complemento="on")
    opcao = multipla.opcoes.get()
    assert opcao.texto == "Outro:" and opcao.complemento_textual


def test_texto_repetido_recusado_no_campo(client, multipla):
    _nova(client, multipla, "Estágio")
    resposta = _nova(client, multipla, "Estágio")
    assert resposta.status_code == 200
    assert "Já existe uma Opção com este texto nesta Pergunta." in resposta.content.decode()
    assert multipla.opcoes.count() == 1


def test_complemento_unico_com_orientacao(client, multipla):
    _nova(client, multipla, "Outro:", complemento="on")
    _nova(client, multipla, "Nenhum")
    nenhum = multipla.opcoes.get(texto="Nenhum")
    resposta = client.post(f"/editor/opcoes/{nenhum.pk}/", {"texto": "Nenhum", "complemento": "on"})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Desmarque a Opção atual antes de marcar outra." in html
    assert 'id="id_complemento-erro"' in html
    nenhum.refresh_from_db()
    assert not nenhum.complemento_textual
    pagina = ce.texto_visivel(client.get(f"/editor/perguntas/{multipla.pk}/"))
    assert "Outro: — aceita complemento escrito" in pagina
    outro = multipla.opcoes.get(texto="Outro:")
    client.post(f"/editor/opcoes/{outro.pk}/", {"texto": "Outro:"})
    outro.refresh_from_db()
    assert not outro.complemento_textual


def test_editar_texto_mantem_desvio(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(regras={"Não": 2})), secao_mem())
    pergunta = ce.pergunta(versao, 1, 1)
    nao = ce.opcao(pergunta, "Não")
    resposta = client.post(
        f"/editor/opcoes/{nao.pk}/", {"texto": "Não, nunca", "desvio": str(ce.secao(versao, 2).pk)}
    )
    assert resposta["Location"] == f"/editor/perguntas/{pergunta.pk}/?aviso=dados-salvos#opcao-2"
    nao.refresh_from_db()
    assert nao.texto == "Não, nunca" and nao.regra_destino_id == ce.secao(versao, 2).pk


def test_subir_e_descer_opcao(client, multipla):
    for t in ("A", "B", "C"):
        _nova(client, multipla, t)
    a, b, c = multipla.opcoes.order_by("posicao")
    html = client.get(f"/editor/perguntas/{multipla.pk}/").content.decode()
    assert "Subir a Opção «A»" not in html and "Descer a Opção «C»" not in html
    resposta = client.post(f"/editor/opcoes/{c.pk}/mover/", {"direcao": "cima"})
    assert resposta["Location"] == f"/editor/perguntas/{multipla.pk}/#opcao-2"
    assert ce.ordem(multipla.opcoes) == ["A", "C", "B"]
    assert ce.posicoes(multipla.opcoes) == [1, 2, 3]


def test_remover_opcao_com_desvio(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(regras={"Não": 2})), secao_mem())
    nao = ce.opcao(ce.pergunta(versao, 1, 1), "Não")
    url = f"/editor/opcoes/{nao.pk}/remover/"
    assert "desvio" in ce.texto_visivel(client.get(url))
    resposta = client.post(url)
    assert resposta["Location"].endswith("?aviso=opcao-removida")
    assert not Opcao.objects.filter(pk=nao.pk).exists()


def test_texto_curto_e_escala_sem_opcoes(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(
            pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO), pergunta_mem(tipo=TipoPergunta.ESCALA)
        ),
    )
    for n in (1, 2):
        pergunta = ce.pergunta(versao, 1, n)
        html = client.get(f"/editor/perguntas/{pergunta.pk}/").content.decode()
        assert "Adicionar Opção" not in html
        assert client.get(f"/editor/perguntas/{pergunta.pk}/opcoes/nova/").status_code == 404
        assert (
            client.post(f"/editor/perguntas/{pergunta.pk}/opcoes/nova/", {"texto": "X"}).status_code
            == 404
        )


def test_sem_limite_de_opcoes(client, multipla):
    for n in range(1, 31):
        op.adicionar_opcao(multipla, n, f"Opção {n}")
    assert _nova(client, multipla, "Mais uma").status_code == 302
    assert multipla.opcoes.count() == 31

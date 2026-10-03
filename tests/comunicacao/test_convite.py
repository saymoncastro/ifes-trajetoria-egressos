import pytest

from trajetoria.comunicacao.convite import renderizar_convite

URL = "http://127.0.0.1:8000/demonstracao/"


@pytest.mark.parametrize(
    "nome,saudacao", [(None, "Olá!"), ("Ana", "Olá, Ana!"), ("<nome>", "Olá, &lt;nome&gt;!")]
)
def test_renderer(nome, saudacao):
    c = renderizar_convite(nome, "Campanha <teste>", URL)
    assert saudacao in c.html
    assert "Campanha &lt;teste&gt;" in c.html
    assert URL in c.texto and URL in c.html
    assert "Abrir a demonstração" in c.texto
    assert "fictícios" in c.texto and "fictícios" in c.html
    assert "Convite para a pesquisa" in c.assunto
    assert not any(tag in c.html for tag in ("<script", "<img", "http://externo", "tracking"))


@pytest.mark.parametrize("campanha", ["bad\r\nBcc: external", "bad\nheader"])
def test_cabecalho_invalido(campanha):
    with pytest.raises(ValueError):
        renderizar_convite(None, campanha, URL)

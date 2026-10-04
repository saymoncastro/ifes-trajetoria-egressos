import re

from tests.acompanhamento import construcao as k
from tests.acompanhamento.test_gestao_abrir_encerrar import url
from tests.acompanhamento.test_gestao_criar_editar import NOVA, dados, editar_url


def test_shell_e_titulos(inst, cliente_cpaeg):
    pronta = k.campanha(inst.versao, estado="pronta")
    aberta = k.campanha(inst.versao)
    titulos = []
    for endereco in (NOVA, editar_url(pronta), url(pronta), url(aberta, "encerrar")):
        html = cliente_cpaeg.get(endereco).content.decode()
        assert '<html lang="pt-BR">' in html and html.count("<h1>") == 1
        assert 'aria-current="page"' in html
        assert 'href="#conteudo"' in html and 'id="conteudo" tabindex="-1"' in html
        assert "<script" not in html
        assert '<button type="submit">' in html
        titulos.append(re.search(r"<title>(.*?)</title>", html).group(1))
    assert len(set(titulos)) == 4


def test_rotulos_erros_e_foco(inst, cliente_cpaeg):
    r = cliente_cpaeg.post(NOVA, dados(inst, nome="  "))
    html = r.content.decode()
    for campo in ("nome", "versao", "inicio", "fim"):
        assert f'<label for="id_{campo}">' in html
        assert f'id="id_{campo}"' in html
    assert 'aria-invalid="true"' in html
    assert 'aria-describedby="id_nome-erro"' in html
    assert 'id="id_nome-erro"' in html
    assert 'role="alert"' in html and 'tabindex="-1" id="erros"' in html
    assert "autofocus" in html

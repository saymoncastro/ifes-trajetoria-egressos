import pytest

from tests.acompanhamento.construcao import A, atuar_como
from tests.declaracao.construcao import declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.declaracao.models import ValidacaoDaFormacao
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

pytestmark = pytest.mark.django_db


def test_formulario_vazio_e_validacao(client):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    registrar_vinculo(A, Papel.CPAEG)
    atuar_como(client, A)
    url = f"/validacoes-formacao/{f.pk}/"
    html = client.get(url).content.decode()
    assert 'value="Informática"' not in html and 'value="2004"' not in html
    dados = {
        "acervo-unidade": "Serra",
        "acervo-referencia": "Livro 3",
        "acervo-nivel": "Técnico",
        "acervo-curso": "Edificações",
        "acervo-ano_conclusao": "2005",
        "resultado": "confirmada",
        "origem": "acervo",
        "confirmar": "1",
    }
    r = client.post(url + "registrar/", dados)
    assert r.status_code == 303
    assert ValidacaoDaFormacao.objects.get().conclusao.fonte == "acervo_historico"
    assert "confirmada com dados diferentes" in client.get(url).content.decode()


def test_acervo_nao_bloqueia_outras_origens_no_navegador():
    from trajetoria.declaracao.formularios import AcervoForm

    assert "required" not in AcervoForm(prefix="acervo").as_p()

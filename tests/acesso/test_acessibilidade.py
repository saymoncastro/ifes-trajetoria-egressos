import pytest

from tests.interface.test_interface_acessibilidade import verificar

pytestmark = pytest.mark.django_db


def test_rotulos_erros_foco_e_vocabulario(preparado, client):
    respostas = [
        client.get("/acesso/"),
        client.post("/acesso/", {"cpf": "123", "data_nascimento": "31/02/2000"}),
        client.post("/acesso/", {"cpf": "000.000.009-49", "data_nascimento": "12/04/1998"}),
    ]
    for r in respostas:
        assert verificar(r) == []
        html = r.content.decode()
        assert 'for="cpf"' in html and 'for="data_nascimento"' in html
        assert 'id="cpf"' in html and 'id="data_nascimento"' in html
        assert html.count('inputmode="numeric"') == 2
        assert 'autocomplete="bday"' in html and 'autocomplete="off"' in html
        assert 'aria-describedby="dica-cpf' in html
        assert "<script" not in html and 'type="date"' not in html
        for palavra in ("login", "senha", "autenticação segura", "acesso seguro"):
            assert palavra not in html.lower()
    assert 'aria-invalid="true"' in respostas[1].content.decode()
    assert 'class="resumo-erros"' in respostas[1].content.decode()
    assert 'tabindex="-1" autofocus' in respostas[2].content.decode()

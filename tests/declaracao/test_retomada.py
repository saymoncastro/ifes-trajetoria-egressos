from datetime import date

import pytest

from tests.declaracao.construcao import CPF, DATA, declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.declaracao.operacoes import declaracoes_do_par
from trajetoria.declaracao.selo import selar_transito

pytestmark = pytest.mark.django_db


def test_mesmo_par_outra_data_e_lista(client):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    assert declaracoes_do_par(CPF, DATA) == (f.pk,)
    assert declaracoes_do_par(CPF, date(1999, 1, 1)) == ()
    r = client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    assert r.status_code == 200 and "Resposta registrada" in r.content.decode()
    assert "Informar outra formação" in r.content.decode()
    html = client.get("/declaracao/").content.decode()
    assert 'name="selo"' not in html and "verificação" not in html.lower()

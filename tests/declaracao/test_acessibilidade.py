import pytest

from tests.acompanhamento.construcao import A, atuar_como
from tests.declaracao.construcao import CPF, DADOS, DATA, declaracao_concluida
from tests.declaracao.test_rotas_egresso import preparar
from tests.interface.test_interface_acessibilidade import verificar
from trajetoria.campanha.models import Campanha
from trajetoria.declaracao.selo import selar_transito
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

pytestmark = pytest.mark.django_db


def test_telas_rotulos_foco(client):
    preparar()
    selo = selar_transito(CPF, DATA)
    telas = [
        client.post("/declaracao/", {"selo": selo}),
        client.post("/declaracao/nova/", {"selo": selo, "nome": ""}),
        client.post("/declaracao/nova/", {"selo": selo, **DADOS}),
    ]
    f = declaracao_concluida(Campanha.objects.get())
    telas.append(client.post("/declaracao/", {"selo": selo}))
    registrar_vinculo(A, Papel.CPAEG)
    atuar_como(client, A)
    telas.extend([client.get("/validacoes-formacao/"), client.get(f"/validacoes-formacao/{f.pk}/")])
    telas.append(client.post(f"/validacoes-formacao/{f.pk}/revelar/"))
    for r in telas:
        assert verificar(r) == []
    assert 'inputmode="numeric"' in telas[0].content.decode()
    assert 'tabindex="-1" autofocus' in telas[1].content.decode()

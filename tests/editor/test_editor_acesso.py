"""Editor disponível só no modo não produtivo (FR-001 a FR-006; SC-013).

O bloqueio é central (`ModoDemonstracaoMiddleware`): um único teste percorre todas as rotas
do editor, sem multiplicar testes por rota.
"""

import re
import uuid

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.editor import mensagens, urls


def _caminhos():
    for padrao in urls.urlpatterns:
        rota = str(padrao.pattern)
        rota = re.sub(r"<uuid:\w+>", lambda _: str(uuid.uuid4()), rota)
        yield "/editor/" + re.sub(r"<int:\w+>", "1", rota)


def test_modo_desligado_nenhuma_rota_responde(client, settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    caminhos = list(_caminhos())
    assert len(caminhos) == len(urls.urlpatterns) > 20
    for caminho in caminhos:
        assert client.get(caminho).status_code == 404, caminho
        assert client.post(caminho, {"texto": "X"}).status_code == 404, caminho


@pytest.mark.django_db
def test_modo_ligado_uma_rota_por_familia(client, copia):
    secao, pergunta = ce.secao(copia, 1), ce.pergunta(copia, 1, 1)
    opcao = pergunta.opcoes.first()
    for caminho in (
        "/editor/",
        f"/editor/pesquisas/{copia.pesquisa_id}/",
        f"/editor/versoes/{copia.pk}/",
        f"/editor/secoes/{secao.pk}/",
        f"/editor/perguntas/{pergunta.pk}/",
        f"/editor/opcoes/{opcao.pk}/",
        f"/editor/versoes/{copia.pk}/diagnostico/",
        f"/editor/versoes/{copia.pk}/previa/",
    ):
        assert client.get(caminho).status_code == 200, caminho


@pytest.mark.django_db
def test_banner_e_sem_pessoa_de_demonstracao(client, copia):
    client.cookies["trajetoria_demonstracao_pessoa"] = "qualquer"
    resposta = client.get(f"/editor/versoes/{copia.pk}/")
    texto = ce.texto_visivel(resposta)
    assert mensagens.BANNER in texto
    assert "Pessoa fictícia" not in texto and "Trocar de pessoa" not in texto

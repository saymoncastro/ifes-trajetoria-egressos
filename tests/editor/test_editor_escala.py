"""Configuração de escala (US9; FR-048 a FR-050)."""

import re

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import TipoPergunta

pytestmark = pytest.mark.django_db
EXPLICACAO = (
    "De 1 a 5 (5 pontos). 1 = «Discordo totalmente»; 5 = «Concordo totalmente». "
    "Pontos intermediários aparecem só com o número."
)


@pytest.fixture
def escala(versao):
    secao = op.adicionar_secao(versao, 1)
    return op.adicionar_pergunta(
        secao, 1, TipoPergunta.ESCALA, "Satisfação", obrigatoria=True,
        escala=Escala(1, 5, "Discordo totalmente", "Concordo totalmente"),
    )  # fmt: skip


def _editar(client, pergunta, **escala):
    dados = {"texto": "Satisfação", "texto_explicativo": "", "obrigatoria": "sim"}
    dados |= {"inicio": "1", "fim": "5", "rotulo_inicio": "", "rotulo_fim": "", **escala}
    return client.post(f"/editor/perguntas/{pergunta.pk}/editar/", dados)


def test_explicacao_na_consulta_e_na_edicao(client, escala):
    assert EXPLICACAO in ce.texto_visivel(client.get(f"/editor/perguntas/{escala.pk}/"))
    assert EXPLICACAO in ce.texto_visivel(client.get(f"/editor/perguntas/{escala.pk}/editar/"))


def test_alterar_limites_e_rotulos(client, escala):
    resposta = _editar(client, escala, inicio="0", fim="10", rotulo_fim="Muito")
    assert resposta.status_code == 302
    escala.refresh_from_db()
    assert (escala.escala_inicio, escala.escala_fim) == (0, 10)
    assert escala.escala_rotulo_inicio is None and escala.escala_rotulo_fim == "Muito"
    texto = ce.texto_visivel(client.get(f"/editor/perguntas/{escala.pk}/"))
    assert "0 sem rótulo" in texto


@pytest.mark.parametrize(("inicio", "fim"), [("5", "1"), ("3", "3"), ("", "5")])
def test_limites_invalidos_recusados_pela_002(client, escala, inicio, fim):
    antes = ce.retrato(escala.secao.versao)
    resposta = _editar(client, escala, inicio=inicio, fim=fim)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "O limite inicial precisa ser um número inteiro menor que o limite final." in html
    assert 'id="id_inicio-erro"' in html and f'name="fim" value="{fim}"' in html
    assert ce.retrato(escala.secao.versao) == antes


def test_limite_nao_inteiro(client, escala):
    resposta = _editar(client, escala, inicio="1.5")
    assert resposta.status_code == 200
    assert "Informe um número inteiro." in resposta.content.decode()


def test_limites_negativos_aceitos(client, escala):
    assert _editar(client, escala, inicio="-2", fim="2").status_code == 302


def test_sem_campos_alem_dos_da_002(client, escala):
    html = client.get(f"/editor/perguntas/{escala.pk}/editar/").content.decode()
    nomes = set(re.findall(r'name="([^"]+)"', html)) - {"viewport", "csrfmiddlewaretoken"}
    assert nomes == {"texto", "texto_explicativo", "obrigatoria", "inicio", "fim",
                     "rotulo_inicio", "rotulo_fim"}  # fmt: skip

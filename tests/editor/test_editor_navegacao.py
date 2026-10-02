"""Navegação já suportada (US10; FR-051 a FR-060; 006 FR-010 a FR-016)."""

import re

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada, Violacao

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


@pytest.fixture
def abc(pesquisa):
    """Seções A, B, C; em A, escolha única Sim/Não sem desvio."""
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(), titulo="A"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="B"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="C"),
    )
    pergunta = ce.pergunta(versao, 1, 1)
    return versao, pergunta, ce.opcao(pergunta, "Sim"), ce.opcao(pergunta, "Não")


def _salvar_opcao(client, opcao, desvio, texto=None):
    return client.post(
        f"/editor/opcoes/{opcao.pk}/", {"texto": texto or opcao.texto, "desvio": desvio}
    )


def _regra(opcao):
    opcao.refresh_from_db()
    return opcao.regra_destino_id, opcao.regra_finaliza


def test_destinos_oferecidos_sem_filtro_de_posicao(client, abc):
    versao, _, _, nao = abc
    html = client.get(f"/editor/opcoes/{nao.pk}/").content.decode()
    valores = re.findall(r'<option value="([^"]*)"', html)
    secoes = [str(s.pk) for s in versao.secoes.order_by("posicao")]
    assert valores == ["", "finalizar", *secoes]
    texto = ce.texto_visivel(client.get(f"/editor/opcoes/{nao.pk}/"))
    assert "Ir para a Seção 1 — A" in texto and "Finalizar o instrumento" in texto


def test_definir_trocar_e_remover_desvio(client, abc):
    versao, pergunta, sim, nao = abc
    c = ce.secao(versao, 3)
    assert _salvar_opcao(client, nao, str(c.pk)).status_code == 302
    assert _regra(nao) == (c.pk, False)
    estrutura = ce.texto_visivel(client.get(f"/editor/secoes/{ce.secao(versao, 1).pk}/"))
    assert "«Não» → segue para a Seção 3 — C" in estrutura
    _salvar_opcao(client, nao, "finalizar")
    assert _regra(nao) == (None, True)
    _salvar_opcao(client, nao, "")
    assert _regra(nao) == (None, False)
    assert _regra(sim) == (None, False)


def test_troca_atomica_pela_view(client, abc, monkeypatch):
    versao, _, _, nao = abc
    c = ce.secao(versao, 3)
    _salvar_opcao(client, nao, str(c.pk))
    antes = ce.retrato(versao)

    def falha(*args):
        raise OperacaoRejeitada((Violacao(Motivo.REGRA_EM_TIPO_INCOMPATIVEL, None, "injetada"),))

    monkeypatch.setattr(op, "definir_regra", falha)
    with pytest.raises(OperacaoRejeitada):
        _salvar_opcao(client, nao, "finalizar", texto="Não, obrigado")
    assert ce.retrato(versao) == antes


def test_tipos_sem_desvio(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(tipo=TipoPergunta.ESCOLHA_MULTIPLA), pergunta_mem(tipo=TEXTO)),
    )
    multipla = ce.pergunta(versao, 1, 1)
    opcao = multipla.opcoes.first()
    assert 'name="desvio"' not in client.get(f"/editor/opcoes/{opcao.pk}/").content.decode()
    pagina = ce.texto_visivel(client.get(f"/editor/perguntas/{multipla.pk}/"))
    assert "Somente Perguntas de escolha única podem ter desvio" in pagina
    resposta = client.post(
        f"/editor/opcoes/{opcao.pk}/", {"texto": opcao.texto, "desvio": "finalizar"}
    )
    assert resposta.status_code == 302
    opcao.refresh_from_db()
    assert not opcao.tem_regra


def test_encaminhamento(client, abc):
    versao, *_ = abc
    a, b, c = (ce.secao(versao, n) for n in (1, 2, 3))
    url = f"/editor/secoes/{b.pk}/editar/"
    html = client.get(url).content.decode()
    valores = re.findall(r'<option value="([^"]*)"', html)
    assert valores == ["", str(a.pk), str(c.pk)]  # a própria Seção não é listada
    client.post(url, {"titulo": "B", "texto": "", "encaminhamento": str(c.pk)})
    b.refresh_from_db()
    assert b.encaminhamento_id == c.pk
    estrutura = ce.texto_visivel(client.get(f"/editor/versoes/{versao.pk}/"))
    assert "depois desta Seção: segue para a Seção 3 — C" in estrutura
    client.post(url, {"titulo": "B", "texto": "", "encaminhamento": ""})
    b.refresh_from_db()
    assert b.encaminhamento_id is None


def test_nova_secao_com_encaminhamento(client, abc):
    versao, *_ = abc
    c = ce.secao(versao, 3)
    client.post(
        f"/editor/versoes/{versao.pk}/secoes/nova/",
        {"titulo": "D", "texto": "", "encaminhamento": str(c.pk)},
    )
    assert versao.secoes.get(titulo="D").encaminhamento_id == c.pk


def test_semantica_atual_explicada(client, abc):
    versao, _, _, nao = abc
    for url in (f"/editor/opcoes/{nao.pk}/", f"/editor/secoes/{ce.secao(versao, 1).pk}/editar/"):
        texto = ce.texto_visivel(client.get(url))
        assert "o desvio é aplicado quando o respondente conclui a Seção" in texto
        assert "semântica atual da jornada, não uma regra permanente" in texto


def test_segunda_pergunta_com_desvio_e_destino_anterior_sao_gravados(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": 3}), pergunta_mem(), titulo="A"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="B"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="C"),
    )
    segunda = ce.pergunta(versao, 1, 2)
    sim = ce.opcao(segunda, "Sim")
    assert _salvar_opcao(client, sim, str(ce.secao(versao, 2).pk)).status_code == 302
    assert _regra(sim) == (ce.secao(versao, 2).pk, False)
    # Encaminhamento para Seção anterior: aceito em rascunho, como na 002.
    b = ce.secao(versao, 2)
    client.post(
        f"/editor/secoes/{b.pk}/editar/",
        {"titulo": "B", "texto": "", "encaminhamento": str(ce.secao(versao, 1).pk)},
    )
    b.refresh_from_db()
    assert b.encaminhamento_id == ce.secao(versao, 1).pk


def test_sem_editor_de_condicoes(client, abc):
    _, _, _, nao = abc
    html = client.get(f"/editor/opcoes/{nao.pk}/").content.decode()
    nomes = set(re.findall(r'name="([^"]+)"', html)) - {"viewport", "csrfmiddlewaretoken"}
    assert nomes == {"texto", "complemento", "desvio"}

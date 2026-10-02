"""Perguntas dos quatro tipos (US7; FR-031 a FR-040, FR-062 da 002)."""

import re

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Opcao, Pergunta, TipoPergunta

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


@pytest.fixture
def secao(versao):
    return op.adicionar_secao(versao, 1, titulo="A")


def _nova(client, secao, tipo, **dados):
    dados.setdefault("texto", "Qual é sua situação profissional?")
    dados.setdefault("texto_explicativo", "")
    dados.setdefault("obrigatoria", "sim")
    return client.post(f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo={tipo}", dados)


def test_passo_do_tipo_lista_exatamente_os_quatro(client, secao):
    resposta = client.get(f"/editor/secoes/{secao.pk}/perguntas/nova/")
    html = resposta.content.decode()
    assert set(re.findall(r'name="tipo" value="([^"]+)"', html)) == set(TipoPergunta.values)
    texto = ce.texto_visivel(resposta)
    for nome in ("Escolha única", "Escolha múltipla", "Texto curto", "Escala"):
        assert nome in texto
    assert "o respondente marca uma Opção" in texto


@pytest.mark.parametrize("tipo", ["DATA", "MATRIZ", ""])
def test_tipo_invalido_volta_ao_passo_do_tipo(client, secao, tipo):
    resposta = _nova(client, secao, tipo)
    assert resposta.status_code == 200 and 'name="tipo"' in resposta.content.decode()
    assert secao.perguntas.count() == 0


def test_cria_os_quatro_tipos_ao_final(client, secao):
    r1 = _nova(client, secao, "ESCOLHA_UNICA")
    p1 = secao.perguntas.get(posicao=1)
    assert r1["Location"] == f"/editor/perguntas/{p1.pk}/?aviso=adicione-opcoes"
    r2 = _nova(client, secao, "ESCOLHA_MULTIPLA", texto="Múltipla")
    assert (
        r2["Location"]
        == f"/editor/perguntas/{secao.perguntas.get(posicao=2).pk}/?aviso=adicione-opcoes"
    )
    r3 = _nova(client, secao, "TEXTO_CURTO", texto="Texto", obrigatoria="nao")
    assert r3["Location"] == f"/editor/secoes/{secao.pk}/?aviso=pergunta-criada#pergunta-3"
    _nova(
        client,
        secao,
        "ESCALA",
        texto="Escala",
        inicio="1",
        fim="5",
        rotulo_inicio="",
        rotulo_fim="",
    )
    tipos = [p.tipo for p in secao.perguntas.order_by("posicao")]
    assert tipos == ["ESCOLHA_UNICA", "ESCOLHA_MULTIPLA", "TEXTO_CURTO", "ESCALA"]
    texto = secao.perguntas.get(posicao=3)
    assert texto.obrigatoria is False and texto.texto_explicativo is None
    escala = secao.perguntas.get(posicao=4)
    assert (escala.escala_inicio, escala.escala_fim) == (1, 5)


def test_campos_de_escala_so_no_tipo_escala(client, secao):
    url = f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo="
    assert 'name="inicio"' in client.get(url + "ESCALA").content.decode()
    for tipo in ("ESCOLHA_UNICA", "ESCOLHA_MULTIPLA", "TEXTO_CURTO"):
        assert 'name="inicio"' not in client.get(url + tipo).content.decode()


def test_obrigatoriedade_e_escolhida_explicitamente(client, secao):
    html = client.get(
        f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=TEXTO_CURTO"
    ).content.decode()
    assert "<legend>Obrigatoriedade</legend>" in html and " checked" not in html
    resposta = client.post(
        f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=TEXTO_CURTO", {"texto": "Sem escolha"}
    )
    assert resposta.status_code == 200
    assert "Indique se a Pergunta é obrigatória ou opcional." in resposta.content.decode()
    assert secao.perguntas.count() == 0


def test_texto_vazio_recusado_pela_002(client, secao):
    resposta = _nova(client, secao, "TEXTO_CURTO", texto="  ")
    assert resposta.status_code == 200
    assert 'id="id_texto-erro"' in resposta.content.decode()
    assert secao.perguntas.count() == 0


def test_edicao_sem_campo_de_tipo(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TEXTO)))
    pergunta = ce.pergunta(versao, 1, 1)
    url = f"/editor/perguntas/{pergunta.pk}/editar/"
    pagina = client.get(url)
    assert 'name="tipo"' not in pagina.content.decode()
    assert "O tipo não pode ser trocado" in ce.texto_visivel(pagina)
    resposta = client.post(
        url, {"texto": "Novo texto", "texto_explicativo": "Ajuda", "obrigatoria": "nao"}
    )
    assert resposta["Location"] == f"/editor/perguntas/{pergunta.pk}/?aviso=dados-salvos"
    pergunta.refresh_from_db()
    assert (pergunta.texto, pergunta.texto_explicativo, pergunta.obrigatoria) == (
        "Novo texto",
        "Ajuda",
        False,
    )
    assert "Opcional" in ce.texto_visivel(client.get(f"/editor/perguntas/{pergunta.pk}/"))
    client.post(url, {"texto": "Novo texto", "texto_explicativo": "", "obrigatoria": "sim"})
    pergunta.refresh_from_db()
    assert pergunta.texto_explicativo is None and pergunta.obrigatoria is True
    assert pergunta.tipo == TEXTO


def test_subir_e_descer_pergunta(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(tipo=TEXTO), pergunta_mem(tipo=TEXTO), pergunta_mem(tipo=TEXTO)),
    )
    p1, p2, p3 = (ce.pergunta(versao, 1, n) for n in (1, 2, 3))
    secao = ce.secao(versao, 1)
    html = client.get(f"/editor/secoes/{secao.pk}/").content.decode()
    assert (
        "Subir a Pergunta 1 da Seção 1" not in html and "Descer a Pergunta 3 da Seção 1" not in html
    )
    resposta = client.post(f"/editor/perguntas/{p1.pk}/mover/", {"direcao": "baixo"})
    assert resposta["Location"] == f"/editor/secoes/{secao.pk}/#pergunta-2"
    assert [p.pk for p in secao.perguntas.order_by("posicao")] == [p2.pk, p1.pk, p3.pk]
    assert ce.posicoes(secao.perguntas) == [1, 2, 3]


def test_mover_para_outra_secao(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": 3}), pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    pergunta = ce.pergunta(versao, 1, 1)
    origem, destino = ce.secao(versao, 1), ce.secao(versao, 2)
    url = f"/editor/perguntas/{pergunta.pk}/trocar-secao/"
    html = client.get(url).content.decode()
    valores = set(re.findall(r'<option value="([^"]+)"', html)) - {""}
    assert valores == {str(destino.pk), str(ce.secao(versao, 3).pk)}
    resposta = client.post(url, {"secao": str(destino.pk)})
    assert resposta["Location"] == f"/editor/perguntas/{pergunta.pk}/?aviso=pergunta-movida"
    pergunta.refresh_from_db()
    assert pergunta.secao_id == destino.pk and pergunta.posicao == 2
    assert origem.perguntas.count() == 1
    nao = pergunta.opcoes.get(texto="Não")
    assert nao.regra_destino_id == ce.secao(versao, 3).pk and pergunta.opcoes.count() == 2


def test_remover_pergunta_com_cascata(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(regras={"Não": 2})), secao_mem())
    pergunta = ce.pergunta(versao, 1, 1)
    url = f"/editor/perguntas/{pergunta.pk}/remover/"
    confirmacao = ce.texto_visivel(client.get(url))
    assert "Opções" in confirmacao and "desvios" in confirmacao
    resposta = client.post(url)
    assert (
        resposta["Location"] == f"/editor/secoes/{ce.secao(versao, 1).pk}/?aviso=pergunta-removida"
    )
    assert not Pergunta.objects.filter(pk=pergunta.pk).exists()
    assert not Opcao.objects.filter(pergunta_id=pergunta.pk).exists()


def test_sem_rota_de_troca_de_tipo(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TEXTO)))
    pergunta = ce.pergunta(versao, 1, 1)
    for sufixo in ("tipo/", "trocar-tipo/", "converter/"):
        assert client.get(f"/editor/perguntas/{pergunta.pk}/{sufixo}").status_code == 404

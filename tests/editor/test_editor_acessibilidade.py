"""Acessibilidade estrutural de todas as telas do editor (US15; FR-110 a FR-112; SC-012).

Reutiliza, sem alterá-la, a verificação estrutural da 008 (`verificar`): lang, título,
`role="alert"` só com "Erro:", um h1, hierarquia, foco inicial, ids únicos, rótulos,
fieldset/legend em grupos, `aria-describedby` válido, sem script nem largura fixa.
"""

import re

import pytest

from tests.editor import construcao_editor as ce
from tests.interface.test_interface_acessibilidade import verificar
from tests.participacao.construcao import FIM, pergunta_mem, secao_mem
from trajetoria.instrumento.models import TipoPergunta

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO


def _paginas(versao, *, editavel=True):
    secao, pergunta = ce.secao(versao, 1), ce.pergunta(versao, 1, 1)
    opcao = pergunta.opcoes.order_by("posicao").first()
    paginas = [
        "/editor/",
        f"/editor/pesquisas/{versao.pesquisa_id}/",
        f"/editor/versoes/{versao.pk}/",
        f"/editor/versoes/{versao.pk}/nova-a-partir/",
        f"/editor/secoes/{secao.pk}/",
        f"/editor/perguntas/{pergunta.pk}/",
        f"/editor/versoes/{versao.pk}/previa/",
        f"/editor/versoes/{versao.pk}/previa/secoes/1/",
        f"/editor/versoes/{versao.pk}/previa/secoes/2/",
    ]
    if editavel:
        paginas += [
            "/editor/pesquisas/nova/",
            f"/editor/pesquisas/{versao.pesquisa_id}/versoes/nova/",
            f"/editor/versoes/{versao.pk}/dados/",
            f"/editor/versoes/{versao.pk}/diagnostico/",
            f"/editor/versoes/{versao.pk}/secoes/nova/",
            f"/editor/secoes/{secao.pk}/editar/",
            f"/editor/secoes/{secao.pk}/remover/",
            f"/editor/secoes/{secao.pk}/perguntas/nova/",
            f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=ESCALA",
            f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=ESCOLHA_UNICA",
            f"/editor/perguntas/{pergunta.pk}/editar/",
            f"/editor/perguntas/{pergunta.pk}/trocar-secao/",
            f"/editor/perguntas/{pergunta.pk}/remover/",
            f"/editor/perguntas/{pergunta.pk}/opcoes/nova/",
            f"/editor/opcoes/{opcao.pk}/",
            f"/editor/opcoes/{opcao.pk}/remover/",
        ]
    return paginas


@pytest.fixture
def rascunho(pesquisa):
    return ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Não": FIM}), pergunta_mem(tipo=TEXTO), titulo="A"),
        secao_mem(pergunta_mem(tipo=TipoPergunta.ESCALA), pergunta_mem(outro=True)),
    )


def test_todas_as_telas_do_rascunho(client, rascunho):
    for url in _paginas(rascunho):
        resposta = client.get(url)
        assert resposta.status_code == 200, url
        assert verificar(resposta) == [], url


def test_telas_da_publicada(client, publicada):
    for url in _paginas(publicada, editavel=False):
        resposta = client.get(url)
        assert verificar(resposta) == [], url


def test_telas_com_erro_e_avisos(client, rascunho, publicada):
    pergunta = ce.pergunta(rascunho, 1, 1)
    respostas = [
        client.post(f"/editor/perguntas/{pergunta.pk}/opcoes/nova/", {"texto": "Sim"}),
        client.post(f"/editor/perguntas/{pergunta.pk}/editar/", {"texto": "X"}),
        client.post(
            f"/editor/secoes/{ce.secao(rascunho, 1).pk}/perguntas/nova/?tipo=ESCALA",
            {"texto": "X", "obrigatoria": "sim", "inicio": "5", "fim": "1"},
        ),
        client.post(
            f"/editor/pesquisas/{rascunho.pesquisa_id}/versoes/nova/", {"designacao": "Montada"}
        ),
        client.post(f"/editor/versoes/{publicada.pk}/dados/", {"designacao": "X"}),
        client.post(f"/editor/secoes/{ce.secao(rascunho, 1).pk}/remover/"),
    ]
    for resposta in respostas:
        assert verificar(resposta) == [], resposta.content.decode()[:200]


def test_diagnostico_nas_tres_situacoes(client, pesquisa, rascunho):
    incompativel = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Sim": 2}), pergunta_mem(regras={"Não": FIM})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
        designacao="Incompatível",
    )
    problemas = ce.versao_de(pesquisa, secao_mem(), designacao="Com problemas")
    for versao in (rascunho, incompativel, problemas):
        for url in (f"/editor/versoes/{versao.pk}/diagnostico/", f"/editor/versoes/{versao.pk}/"):
            assert verificar(client.get(url)) == [], url


def test_nomes_acessiveis_e_estados_em_texto(client, rascunho):
    secao = ce.secao(rascunho, 1)
    html = client.get(f"/editor/secoes/{secao.pk}/").content.decode()
    rotulos = re.findall(r'<button[^>]*aria-label="([^"]+)"', html)
    assert rotulos == [
        "Descer a Pergunta 1 da Seção 1: Pergunta 1",
        "Subir a Pergunta 2 da Seção 1: Pergunta 2",
    ]
    assert 'aria-label="Remover a Pergunta 1 da Seção 1: Pergunta 1"' in html
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{rascunho.pk}/"))
    assert "Rascunho" in texto and "Obrigatória" in texto
    assert 'nav class="trilha" aria-label="Você está em"' in html
    assert html.count("<h1") == 1


def test_recusas_de_acesso(cliente_sem_vinculo, cliente_csaeg, rascunho):
    # 010: sem atuação; vínculo que não permite (leitura de rascunho e elaboração).
    for resposta in (
        cliente_sem_vinculo.get("/editor/"),
        cliente_csaeg.get(f"/editor/versoes/{rascunho.pk}/"),
        cliente_csaeg.get("/editor/pesquisas/nova/"),
    ):
        assert resposta.status_code == 403
        assert verificar(resposta) == [], resposta.content.decode()[:200]

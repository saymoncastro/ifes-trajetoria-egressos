"""Refinamento visual da conclusão e da confirmação (Feature 034; spec FR-001 a FR-011).

Por requisição, sem navegador: ordem, presença e marcação. Medidas, refluxo, teclado e
leitor de tela ficam na validação (`specs/034-refinamento-conclusao-confirmacao/`).
"""

import re

import pytest

from tests.declaracao import construcao as cd
from tests.interface import construcao_interface as ci
from tests.narrativa.test_declarada import _como_declarante
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from tests.participacao.construcao import pergunta_mem, secao_mem
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.interface import mensagens
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

ANA, MARIA = "SIM-P-0001", "SIM-P-0003"
_ESCOLHAS = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim"}
PERCURSO = c.secoes_esperadas("Sim", "Graduação", "Sim", "Sim")
CURSO = "Tecnologia em Análise e Desenvolvimento de Sistemas"
# Frases de finalidade, uso, contato ou periodicidade (014 FR-039; DP-504).
FINALIDADE = ("ajuda o ifes", "aprimor", "melhorar", "entraremos em contato", "próxima pesquisa",
              "periodic", "anualmente")  # fmt: skip


def _url(pk, sufixo=""):
    return f"/participacoes/{pk}/{sufixo}"


def _principal(resposta) -> str:
    return resposta.content.decode().split('<main id="conteudo"')[1].split("</main>")[0]


@pytest.fixture
def ana(client, cenario):
    """Ana na conclusão, pelo percurso "trabalha e estuda" (9 partes)."""
    participacao = Participacao.objects.get(
        pk=ci.participacao_de(ci.iniciar(client, cenario.pessoa(ANA)))
    )
    ci.percorrer_pela_interface(
        client, participacao.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, _ESCOLHAS)
    )
    return participacao


def _confirmacao(client, participacao):
    return client.get(client.post(_url(participacao.pk, "concluir/"))["Location"])


# --- US1: conclusão ----------------------------------------------------------------------------


def test_ordem_da_conclusao(client, cenario, ana):
    html = _principal(client.get(_url(ana.pk, "concluir/")))
    marcos = [
        f'<p class="parte">{mensagens.ULTIMA_ETAPA}</p>',
        "<h1>Concluir a pesquisa</h1>",
        mensagens.FIM_DA_PESQUISA,
        f"Você está respondendo sobre:</strong> {CURSO} · Serra · 2022",
        f"{mensagens.REVISAR} <span class=\"quantas\">· 9 partes</span>",
        mensagens.IRREVERSIVEL,
        "Concluir pesquisa</button>",
    ]
    posicoes = [html.index(m) for m in marcos]
    assert posicoes == sorted(posicoes)
    assert "Sobre a sua formação" not in html and "<dl>" not in html  # FR-001: sem a ficha


def test_revisao_sempre_recolhida(client, cenario, ana):
    """FR-002 (B4): fechada também na volta de uma revisão, com "Parte salva." visível."""
    for consulta in ("", "?aviso=revisada&secao=2"):
        html = _principal(client.get(_url(ana.pk, f"concluir/{consulta}")))
        assert '<details class="revisao">' in html and "<details open" not in html
    voltou = client.get(_url(ana.pk, "concluir/?aviso=revisada&secao=2"))
    assert mensagens.AVISOS["revisada"] in ci.texto_visivel(voltou)


def test_lista_numerada_fora_do_link_e_em_ordem(client, cenario, ana):
    html = _principal(client.get(_url(ana.pk, "concluir/")))
    lista = re.search(r'<ol class="lista-revisao">(.*?)</ol>', html, re.S).group(1)
    itens = re.findall(r"<li>(.*?)</li>", lista, re.S)
    assert len(itens) == 9
    # FR-003: "Parte N" fora do link; o link diz só o título.
    assert itens[0] == (
        '<span class="numero">Parte 1</span>'
        f'<a href="{_url(ana.pk, "secoes/1/?revisao=1")}">Termos e condições</a>'
    )
    # Seção sem título: o link diz "Parte 9" e não há número repetido (023 FR-015).
    assert itens[-1] == f'<a href="{_url(ana.pk, "secoes/13/?revisao=1")}">Parte 9</a>'
    # FR-004: a ordem do documento é a do percurso (as colunas a seguem).
    posicoes = [ci.posicao_da_url(u) for u in re.findall(r'href="([^"]+)"', lista)]
    assert posicoes == PERCURSO


def test_uma_parte_no_singular(client, cenario):
    pk = ci.participacao_de(ci.iniciar(client, cenario.pessoa(ANA)))
    client.post(_url(pk, "secoes/1/"), {"p1": "2"})  # Termos "Não" → finalização
    assert '<span class="quantas">· 1 parte</span>' in _principal(client.get(_url(pk, "concluir/")))


def test_css_da_revisao(client, cenario, ana):
    html = client.get(_url(ana.pk, "concluir/")).content.decode()
    regras = {r.seletor: r.declaracoes for r in ci.regras(html) if not r.media}
    assert regras["details.revisao summary"]["display"] == "list-item"  # marcador nativo
    assert regras["details.revisao summary"]["min-height"] == "var(--alvo)"
    assert regras[".lista-revisao"]["columns"] == "2 15rem"  # multicoluna, ordem do documento
    assert regras[".lista-revisao li"]["break-inside"] == "avoid"
    assert regras[".lista-revisao a"]["min-height"] == "var(--alvo)"


# --- US2: confirmação -------------------------------------------------------------------------


def test_confirmacao_ordem_identificacao_e_acao_principal(client, cenario, ana):
    tela = _confirmacao(client, ana)
    html = _principal(tela)
    marcos = [
        "<h1>Pesquisa concluída</h1>",
        f"Suas respostas sobre {CURSO} foram registradas.",
        f'<p class="formacao-concluida">Formação: {CURSO} · Serra · 2022</p>',
        "Este formulário chegou ao fim!",
        "<h2>No Portal do Egresso</h2>",
        '<p class="acao-principal"><a href="/minha-trajetoria/">Ver minha trajetória no Ifes</a>',
        "Quer manter seu e-mail atualizado com o Ifes?",
    ]
    posicoes = [html.index(m) for m in marcos]
    assert posicoes == sorted(posicoes)
    assert "Sobre a sua formação" not in html and "<dl>" not in html  # FR-005: sem a ficha
    assert "Você está respondendo" not in html  # B1


def test_textos_protegidos_e_nenhuma_finalidade(client, cenario, ana):
    texto = ci.texto_visivel(_confirmacao(client, ana))
    assert "Pesquisa concluída" in texto
    assert "Agradecemos imensamente a atenção dispensada e a participação na pesquisa." in texto
    assert not [f for f in FINALIDADE if f in texto.lower()]


def test_identificacao_parcial_e_ausente(client, cenario, ana):
    ConclusaoAcademica.objects.filter(pk=ana.conclusao_id).update(curso=None)
    html = _principal(_confirmacao(client, ana))
    assert '<p class="formacao-concluida">Formação: Serra · 2022</p>' in html
    ConclusaoAcademica.objects.filter(pk=ana.conclusao_id).update(
        unidade=None, ano_conclusao=None, data_conclusao=None
    )
    html = _principal(client.get(_url(ana.pk, "concluida/")))
    # Nada informado: a linha não aparece; a frase de registro cobre o caso (014 FR-038).
    assert "formacao-concluida" not in html and "Formação:" not in html
    assert "Suas respostas foram registradas." in html


def test_com_proxima_formacao_a_trajetoria_volta_a_ser_link(client, cenario):
    maria = cenario.pessoa(MARIA)
    primeira, _segunda = maria.conclusoes.order_by("ano_conclusao", "id")
    pk = ci.participacao_de(ci.iniciar(client, maria, primeira))
    client.post(_url(pk, "secoes/1/"), {"p1": "2"})
    html = _principal(client.get(client.post(_url(pk, "concluir/"))["Location"]))
    assert html.count('class="primario"') == 1  # FR-006: uma única ação principal
    assert "acao-principal" not in html
    assert html.index("Responder sobre esta formação") < html.index("Ver minha trajetória")


def test_portal_desligado_sem_titulo_do_bloco(client, cenario, ana, settings):
    settings.TRAJETORIA_PORTAL = False
    html = _principal(_confirmacao(client, ana))
    assert "<h2>" not in html.split('<div class="continuidade">')[1]
    assert '<p class="acao-principal"><a href="/minha-trajetoria/">' in html


def test_declarada_inalterada(client, cenario):
    formacao = cd.declaracao_concluida(cenario.campanha)
    _como_declarante(client, formacao)
    participacao = Participacao.objects.get(formacao_declarada=formacao)
    html = _principal(client.get(_url(participacao.pk, "concluida/")))
    assert '<a href="/declaracao/">Ver suas formações informadas</a>' in html
    assert '<section class="contexto"' in html  # a ficha continua (FR-007)
    for novo in ("formacao-concluida", "continuidade", "acao-principal", "/minha-trajetoria/"):
        assert novo not in html


# --- B6: aviso neutro da 033 (FR-011) ---------------------------------------------------------


def test_aviso_neutro_na_parte_nova(client, cenario, ana):
    dados = ci.dados_validos(
        ci.secao_do_conteudo(cenario.base.versao, 8),
        ci.escolhas_por_id(cenario.base, {**_ESCOLHAS, "Q33": "Não"}),
    )
    destino = client.post(_url(ana.pk, "secoes/8/"), {**dados, "revisao": "1"})["Location"]
    assert destino == _url(ana.pk, "secoes/10/?revisao=1&aviso=caminho")
    texto = ci.texto_visivel(client.get(destino))
    assert mensagens.AVISOS["caminho"] in texto and "mudou o caminho" not in texto


def test_aviso_neutro_na_parte_opcional_ja_vista_em_branco(client, db):
    ce.incorporar(FonteSimulada(), ANA)
    versao = c.versao_publicada_de(
        secao_mem(pergunta_mem()),
        secao_mem(pergunta_mem(obrigatoria=False)),  # só opcional
        secao_mem(pergunta_mem()),
    )
    c.campanha_aberta(versao)
    pk = ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte(ANA)))
    client.post(_url(pk, "secoes/1/"), {"p1": "1"})
    client.post(_url(pk, "secoes/2/"), {})  # vista e deixada em branco
    assert client.post(_url(pk, "secoes/3/"), {"p1": "1"})["Location"] == _url(pk, "concluir/")
    # Revisão da Parte 1 sem mudar nada: o caminho é o mesmo, mas a Parte 2 é reapresentada.
    destino = client.post(_url(pk, "secoes/1/"), {"p1": "1", "revisao": "1"})["Location"]
    assert destino == _url(pk, "secoes/2/?revisao=1&aviso=caminho")
    texto = ci.texto_visivel(client.get(destino))
    assert mensagens.AVISOS["caminho"] in texto and "mudou o caminho" not in texto

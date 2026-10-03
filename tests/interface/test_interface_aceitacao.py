"""Cenários ponta a ponta da spec (008 E2E-1, E2E-2, E2E-3; SC-002, SC-003).

Tudo por requisições HTTP comuns, sem JavaScript, sobre as Features reais 001–007 — o
cenário vem do próprio comando `preparar_demonstracao`, sem dublês de domínio.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.participacao.consultas import respostas_atuais, situacao_da_jornada
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.percurso import perguntas_do_percurso

pytestmark = pytest.mark.django_db


@pytest.fixture
def demonstracao(db):
    call_command("preparar_demonstracao", stdout=StringIO())


def _chaves(participacao):
    return c.chaves_baseline(conteudo_da_versao(participacao.campanha.versao))


def _url(participacao, sufixo=""):
    return f"/participacoes/{participacao.pk}/{sufixo}"


def _enviar(client, participacao, posicao, escolhas, **trocas):
    chaves = _chaves(participacao)
    secao = ci.secao_do_conteudo(participacao.campanha.versao, posicao)
    dados = ci.dados_validos(secao, {chaves[k]: v for k, v in escolhas.items()})
    dados.update(trocas)
    dados = {k: v for k, v in dados.items() if v is not None}
    return client.post(_url(participacao, f"secoes/{posicao}/"), dados)


def test_e2e_1_jornada_principal_com_retomada_e_conclusao(client, demonstracao):
    escolhas = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim"}
    ana = ce.pessoa_da_fonte("SIM-P-0001")
    # 2–3. Entrada de demonstração e escolha da Pessoa fictícia.
    assert "Ambiente de demonstração." in ci.texto_visivel(client.get("/demonstracao/"))
    ci.entrar_como(client, ana)
    # 4. A formação com pesquisa é encontrada, sem escolha artificial.
    formacoes = ci.texto_visivel(client.get("/formacoes/"))
    assert "Você concluiu " in formacoes  # 014 FR-031
    assert "Iniciar a pesquisa" in formacoes
    # 5. Iniciar: Participação pela 007/005, S1 com o texto de abertura.
    entrada = client.post("/formacoes/entrar/")
    participacao = Participacao.objects.get(pk=ci.participacao_de(entrada))
    assert client.get(_url(participacao))["Location"] == _url(participacao, "secoes/1/")
    assert "É com muita satisfação" in ci.texto_visivel(client.get(_url(participacao, "secoes/1/")))
    # 6. Q1 = Sim.
    assert _enviar(client, participacao, 1, escolhas)["Location"] == _url(participacao, "secoes/2/")
    # 7. Ramos reais; uma pendência; "Outro:" com complemento em S8.
    pendente = _enviar(client, participacao, 2, escolhas, p2=None)
    assert pendente["Location"] == _url(participacao, "secoes/2/?pendencias=1")
    assert "Esta pergunta é obrigatória." in ci.texto_visivel(client.get(pendente["Location"]))
    for posicao, destino in ((2, 3), (3, 6), (6, 8)):
        resposta = _enviar(client, participacao, posicao, escolhas)
        assert resposta["Location"] == _url(participacao, f"secoes/{destino}/")
    secao8 = ci.secao_do_conteudo(participacao.campanha.versao, 8)
    q26 = next(p for p in secao8.perguntas if p.id == _chaves(participacao)["Q26"])
    outro = next(o for o in q26.opcoes if o.complemento_textual)
    resposta = _enviar(
        client,
        participacao,
        8,
        escolhas,
        **{f"p{q26.posicao}": ["1", str(outro.posicao)], f"p{q26.posicao}-complemento": "Zine"},
    )
    assert resposta["Location"] == _url(participacao, "secoes/9/")
    # 8. Respostas salvas.
    assert respostas_atuais(participacao)[q26.id].complemento == "Zine"
    # 9. No meio de S9: parte das respostas, depois abandona a demonstração.
    _enviar(client, participacao, 9, escolhas, p1=None)
    client.post("/demonstracao/encerrar/")
    # 10–11. Retorna e retoma exatamente o rascunho.
    ci.entrar_como(client, ana)
    assert "Continuar a pesquisa" in ci.texto_visivel(client.get("/formacoes/"))
    assert client.post("/formacoes/entrar/")["Location"] == _url(participacao)
    assert client.get(_url(participacao))["Location"] == _url(participacao, "secoes/9/")
    s8 = client.get(_url(participacao, "secoes/8/")).content.decode()
    assert 'value="Zine"' in s8
    # 12. Continua até o fim.
    for posicao, destino in ((9, 11), (11, 12), (12, 13)):
        resposta = _enviar(client, participacao, posicao, escolhas)
        assert resposta["Location"] == _url(participacao, f"secoes/{destino}/")
    fim = _enviar(client, participacao, 13, escolhas)
    assert fim["Location"] == _url(participacao, "concluir/")
    # 13–14. Conclui e vê a confirmação.
    confirmacao = client.get(client.post(_url(participacao, "concluir/"))["Location"])
    assert "Pesquisa concluída" in ci.texto_visivel(confirmacao)
    # 15–16. Tenta acessar de novo.
    assert "Pesquisa já respondida." in ci.texto_visivel(client.get("/formacoes/"))
    de_novo = ci.texto_visivel(client.get(_url(participacao, "secoes/2/")))
    assert "Esta pesquisa já foi respondida." in de_novo
    # A Participação concluída contém exatamente Respostas do percurso final.
    jornada = situacao_da_jornada(participacao)
    assert jornada.concluida_em is not None and jornada.finalizada
    assert set(jornada.respostas) <= perguntas_do_percurso(jornada.passagens)
    obrigatorias = {
        p.id for passagem in jornada.passagens for p in passagem.secao.perguntas if p.obrigatoria
    }
    assert obrigatorias <= set(jornada.respostas)


def test_e2e_2_q1_nao(client, demonstracao):
    carla = ce.pessoa_da_fonte("SIM-P-0011")
    participacao = Participacao.objects.get(pk=ci.participacao_de(ci.iniciar(client, carla)))
    assert _enviar(client, participacao, 1, {"Q1": "Não"})["Location"] == _url(
        participacao, "concluir/"
    )
    confirmacao = client.get(client.post(_url(participacao, "concluir/"))["Location"])
    assert "Pesquisa concluída" in ci.texto_visivel(confirmacao)
    assert len(respostas_atuais(participacao)) == 1


def test_e2e_2_variante_sim_depois_nao(client, demonstracao):
    elisa = ce.pessoa_da_fonte("SIM-P-0005")
    participacao = Participacao.objects.get(pk=ci.participacao_de(ci.iniciar(client, elisa)))
    _enviar(client, participacao, 1, {"Q1": "Sim"})
    _enviar(client, participacao, 2, {}, p2=None)  # parte de S2, com pendência
    assert len(respostas_atuais(participacao)) > 1
    html = client.get(_url(participacao, "secoes/2/")).content.decode()
    assert "Voltar à seção anterior" in html
    resposta = _enviar(client, participacao, 1, {"Q1": "Não"})
    assert resposta["Location"] == _url(participacao, "concluir/")
    client.post(_url(participacao, "concluir/"))
    assert len(respostas_atuais(participacao)) == 1


def test_e2e_3_selecao_entre_formacoes(client, demonstracao):
    maria = ce.pessoa_da_fonte("SIM-P-0003")
    ci.entrar_como(client, maria)
    tela = client.get("/formacoes/")
    assert "Cada formação tem sua própria pesquisa." in ci.texto_visivel(tela)  # 014 FR-033
    primeira, segunda = maria.conclusoes.all()
    resposta = client.post("/formacoes/entrar/", {"formacao": str(primeira.pk)})
    p1 = Participacao.objects.get(pk=ci.participacao_de(resposta))
    _enviar(client, p1, 1, {"Q1": "Sim"})
    texto = ci.texto_visivel(client.get("/formacoes/"))
    assert "Cada formação tem sua própria pesquisa." in texto
    assert "Continuar a pesquisa desta formação" in texto
    assert "Iniciar a pesquisa desta formação" in texto
    resposta = client.post("/formacoes/entrar/", {"formacao": str(segunda.pk)})
    p2 = Participacao.objects.get(pk=ci.participacao_de(resposta))
    assert p1.pk != p2.pk and {p1.conclusao_id, p2.conclusao_id} == {primeira.pk, segunda.pk}
    assert len(respostas_atuais(p2)) == 0

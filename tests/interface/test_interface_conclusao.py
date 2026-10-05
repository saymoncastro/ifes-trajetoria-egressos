"""Conclusão, confirmação e Participação concluída (008 US8, US9, US10; FR-056 a FR-064).

Concluir é só a operação da 006; a interface não grava momento, não remove respostas e não
valida percurso por conta própria.
"""

import re

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from tests.participacao.construcao import FIM, pergunta_mem, secao_mem
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.participacao import operacoes as op
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db

COMPLETO = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Não"}
PALAVRAS_DE_CONSENTIMENTO = ("consentimento", "recusa", "opt-out", "consentiu", "recusou")


@pytest.fixture
def ana(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


def _url(participacao, sufixo):
    return f"/participacoes/{participacao.pk}/{sufixo}"


def _percorrer(client, cenario, participacao, escolhas=COMPLETO):
    return ci.percorrer_pela_interface(
        client, participacao.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, escolhas)
    )


def test_conclusao_so_com_jornada_finalizada(client, cenario, ana):
    resposta = client.get(_url(ana, "concluir/"))
    assert resposta["Location"] == _url(ana, "secoes/1/")


def test_tela_de_conclusao(client, cenario, ana):
    _percorrer(client, cenario, ana)
    resposta = client.get(_url(ana, "concluir/"))
    assert resposta.status_code == 200
    html, texto = resposta.content.decode(), ci.texto_visivel(resposta)
    assert "Você chegou ao fim da pesquisa." in texto
    assert "Depois de concluída, ela não poderá ser alterada." in texto
    assert "Concluir pesquisa" in texto and "Sobre a sua formação" in texto
    assert f'href="{_url(ana, "secoes/1/")}"' in html and "Termos e condições" in texto
    assert "Seção 13" in texto  # Seção sem título: o número do próprio instrumento
    assert ci.TEXTO_FICTICIO not in texto  # nenhum valor declarado
    assert "no-store" in resposta["Cache-Control"]


def test_concluir_pela_006_e_repetir(client, cenario, ana):
    b = cenario.base
    _percorrer(client, cenario, ana)
    op.responder_texto(ana, b.q(10), "fora do percurso?")  # S3: dentro do percurso
    op.responder_escolha_unica(ana, b.q(45), b.q(45).opcoes.first())  # S10: fora do percurso
    resposta = client.post(_url(ana, "concluir/"))
    assert resposta["Location"] == _url(ana, "concluida/")
    ana.refresh_from_db()
    concluida_em = ana.concluida_em
    assert concluida_em is not None
    assert not Resposta.objects.filter(participacao=ana, pergunta=b.q(45)).exists()
    assert client.post(_url(ana, "concluir/"))["Location"] == _url(ana, "concluida/")
    ana.refresh_from_db()
    assert ana.concluida_em == concluida_em


def test_pendencia_criada_entre_a_tela_e_a_acao(client, cenario, ana):
    b = cenario.base
    _percorrer(client, cenario, ana)
    client.get(_url(ana, "concluir/"))
    op.remover_resposta(ana, b.q(54))
    resposta = client.post(_url(ana, "concluir/"))
    assert resposta["Location"] == _url(ana, "secoes/13/?pendencias=1")
    ana.refresh_from_db()
    assert ana.concluida_em is None


def test_estrutura_nao_suportada_vira_pesquisa_indisponivel(client):
    ce.incorporar(FonteSimulada(), "SIM-P-0001")
    versao = c.versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": FIM}), pergunta_mem(regras={"Não": FIM})),
        secao_mem(pergunta_mem(tipo=TipoPergunta.TEXTO_CURTO)),
    )
    c.campanha_aberta(versao)
    participacao = ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte("SIM-P-0001")))
    for metodo, sufixo in (
        ("get", ""),
        ("get", "secoes/1/"),
        ("get", "concluir/"),
        ("post", "concluir/"),
    ):
        resposta = getattr(client, metodo)(f"/participacoes/{participacao}/{sufixo}")
        assert resposta.status_code == 200, sufixo
        texto = ci.texto_visivel(resposta)
        assert "Esta pesquisa não está disponível no momento." in texto
        assert ci.tecnicos_em(texto) == []


def test_q1_nao_conclui_com_uma_resposta_sem_falar_em_consentimento(client, cenario, ana):
    apresentadas, fim = _percorrer(client, cenario, ana, {"Q1": "Não"})
    assert apresentadas == [1] and fim == _url(ana, "concluir/")
    telas = [client.get(fim)]
    telas.append(client.get(client.post(fim)["Location"]))
    assert Resposta.objects.filter(participacao=ana).count() == 1
    for tela in telas:
        texto = ci.texto_visivel(tela).lower()
        assert not [p for p in PALAVRAS_DE_CONSENTIMENTO if p in texto]


# --- Confirmação (US9) ---------------------------------------------------------------------

PROIBIDAS_NA_CONFIRMACAO = (
    "comprovante", "certificado", "protocolo", "download", "editar", "reabrir", "pdf",
)  # fmt: skip


def test_confirmacao_simples_sem_respostas(client, cenario, ana):
    _percorrer(client, cenario, ana)
    resposta = client.get(client.post(_url(ana, "concluir/"))["Location"])
    assert resposta.status_code == 200
    texto = ci.texto_visivel(resposta)
    assert "Pesquisa concluída" in texto
    # 014 FR-040: a Versão tem texto de encerramento, que é o agradecimento; o fixo não aparece.
    assert "Obrigado pela sua participação." not in texto
    assert "Sobre a sua formação" in texto and "Serra" in texto
    assert "Este formulário chegou ao fim!" in texto  # texto de encerramento da Versão
    assert ci.TEXTO_FICTICIO not in texto
    ana.refresh_from_db()
    assert ana.concluida_em.strftime("%d/%m/%Y") not in texto
    assert not [p for p in PROIBIDAS_NA_CONFIRMACAO if p in texto.lower()]
    html = resposta.content.decode()
    # 021 FR-003 (revisa 014 FR-041): a ação única leva à Minha trajetória.
    assert 'href="/minha-trajetoria/">Ver minha trajetória no Ifes' in html
    assert "<img" not in html and "download" not in html  # 021 FR-004
    assert "<form" not in html.split('<main id="conteudo"')[1]


def test_confirmacao_de_rascunho_volta_a_participacao(client, cenario, ana):
    resposta = client.get(_url(ana, "concluida/"))
    assert resposta["Location"] == _url(ana, "")


# --- Participação já concluída (US10) -------------------------------------------------------


def test_concluida_nunca_reabre_por_nenhuma_rota(client, cenario, ana):
    _percorrer(client, cenario, ana)
    formulario_antigo = ci.dados_validos(ci.secao_do_conteudo(cenario.base.versao, 2))
    client.post(_url(ana, "concluir/"))
    antes = c.retrato(ana)
    formacoes = ci.texto_visivel(client.get("/formacoes/"))
    assert "Pesquisa já respondida." in formacoes
    assert "Iniciar a pesquisa" not in formacoes and "Continuar a pesquisa" not in formacoes
    for posicao in (1, 2, 8, 13):
        resposta = client.get(_url(ana, f"secoes/{posicao}/"))
        html = resposta.content.decode()
        assert "Esta pesquisa já foi respondida." in ci.texto_visivel(resposta)
        assert 'action="/participacoes/' not in html and ci.TEXTO_FICTICIO not in html
    resposta = client.post(_url(ana, "secoes/2/"), formulario_antigo)
    assert "Esta pesquisa já foi respondida." in ci.texto_visivel(resposta)
    assert client.get(_url(ana, "concluir/"))["Location"] == _url(ana, "concluida/")
    entrada = client.post("/formacoes/entrar/", {"formacao": str(ana.conclusao_id)})
    assert "Esta pesquisa já foi respondida." in ci.texto_visivel(entrada)
    assert Participacao.objects.count() == 1 and c.retrato(ana) == antes
    for tela in (client.get("/formacoes/"), client.get(_url(ana, "concluida/"))):
        texto = ci.texto_visivel(tela).lower()
        assert "reabrir" not in texto and "editar" not in texto


def test_motivo_que_nao_e_pendencia_vira_pesquisa_indisponivel(client, cenario, ana, monkeypatch):
    # Só a tradução: qualquer motivo além de coleta e pendência (estrutura, incoerência ou
    # um motivo futuro) é "pesquisa indisponível", sem reler a jornada.
    from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada, Violacao

    _percorrer(client, cenario, ana, {"Q1": "Não"})

    def rejeita(participacao):
        raise ParticipacaoRejeitada((Violacao(Motivo.PARTICIPACAO_INEXISTENTE, None, "x"),))

    monkeypatch.setattr("trajetoria.interface.views.concluir", rejeita)
    resposta = client.post(_url(ana, "concluir/"))
    assert resposta.status_code == 200
    assert "Esta pesquisa não está disponível no momento." in ci.texto_visivel(resposta)


def test_pendencia_vinda_da_conclusao_segue_a_regra_de_verdade(client, cenario, ana):
    _percorrer(client, cenario, ana)
    op.remover_resposta(ana, cenario.base.q(54))
    destino = client.post(_url(ana, "concluir/"))["Location"]
    texto = ci.texto_visivel(client.get(destino))
    assert "Esta pergunta é obrigatória." in texto
    # 014 FR-008: a frase depende só do que está gravado na Seção, não de onde se veio.
    secao = situacao_da_jornada(ana).passagens[-1].secao
    gravada = any(p.id in situacao_da_jornada(ana).respostas for p in secao.perguntas)
    assert ("O que você respondeu nesta seção está salvo." in texto) == gravada


def test_titulo_principal_da_conclusao(client, cenario, ana):
    """014 FR-023: o título principal é a etapa, não o título da pesquisa."""
    _percorrer(client, cenario, ana)
    html = client.get(_url(ana, "concluir/")).content.decode()
    assert re.findall(r"<h1>\s*(.*?)\s*</h1>", html) == ["Concluir a pesquisa"]
    assert not re.search(r"<h2[^>]*>\s*Concluir a pesquisa", html)
    assert re.search(r"<h2[^>]*>\s*Sobre a sua formação", html)  # contexto completo mantido


# --- 014 US8: encerramento que fecha a conversa (FR-038 a FR-041) ---------------------------


def _confirmacao(client, participacao):
    return client.get(client.post(_url(participacao, "concluir/"))["Location"])


def test_confirmacao_diz_o_que_foi_registrado(client, cenario, ana):
    _percorrer(client, cenario, ana)
    texto = ci.texto_visivel(_confirmacao(client, ana))
    assert (
        "Suas respostas sobre Tecnologia em Análise e Desenvolvimento de Sistemas foram "
        "registradas." in texto
    )
    assert texto.count("Obrigado") == 0 and "Este formulário chegou ao fim!" in texto
    for proibida in ("entrar em contato", "próxima pesquisa", "daqui a", "anos", "finalidade"):
        assert proibida not in texto.lower(), proibida


def test_confirmacao_sem_curso_nao_fabrica_texto(client, cenario, ana):
    from trajetoria.academico.models import ConclusaoAcademica

    _percorrer(client, cenario, ana)
    ConclusaoAcademica.objects.filter(pk=ana.conclusao_id).update(curso=None)
    texto = ci.texto_visivel(_confirmacao(client, ana))
    assert "Suas respostas foram registradas." in texto
    assert "Suas respostas sobre" not in texto


def test_sem_texto_de_encerramento_agradece_uma_vez(client, db):
    ce.incorporar(FonteSimulada(), "SIM-P-0001")
    inst = c.instrumento()  # Versão sem texto de encerramento
    c.campanha_aberta(inst.versao)
    pk = ci.participacao_de(ci.iniciar(client, ce.pessoa_da_fonte("SIM-P-0001")))
    participacao = Participacao.objects.get(pk=pk)
    c.preencher_instrumento(participacao, inst)
    resposta = _confirmacao(client, participacao)
    texto = ci.texto_visivel(resposta)
    assert texto.count("Obrigado pela sua participação.") == 1
    principal = resposta.content.decode().split('<main id="conteudo"')[1].split("</main>")[0]
    # 020 E7: a ação principal continua a primeira; o convite de e-mail vem depois.
    assert re.findall(r"<a [^>]*>([^<]+)</a>", principal) == [
        "Ver minha trajetória no Ifes", "Quer manter seu e-mail atualizado com o Ifes?",
    ]


def test_ligacoes_da_conclusao_em_lista_com_alvo_de_toque(client, cenario, ana):
    """014 FR-026 (MF-13): as ligações para revisar Seções ficam numa lista com alvo de 44 px
    (medido no quickstart §2.4); aqui, a marcação que recebe esse estilo."""
    _percorrer(client, cenario, ana)
    html = client.get(_url(ana, "concluir/")).content.decode()
    lista = re.search(r'<ul class="lista-secoes">(.*?)</ul>', html, re.S)
    assert lista and f'href="{_url(ana, "secoes/1/")}"' in lista.group(1)

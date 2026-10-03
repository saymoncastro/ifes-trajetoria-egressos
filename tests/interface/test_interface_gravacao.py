"""Gravação da Seção pela 005 (008 US5; FR-040 a FR-049; contracts/formulario-secao.md).

Uma operação da 005 por Pergunta alterada, numa transação: qualquer erro desfaz a
submissão inteira, e todos os erros aparecem de uma vez.
"""

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.interface.formularios import Valor
from trajetoria.interface.gravacao import salvar_secao
from trajetoria.participacao import operacoes as op
from trajetoria.participacao.consultas import respostas_atuais, situacao_da_jornada
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db

OPERACOES = (
    "responder_escolha_unica",
    "responder_escolha_multipla",
    "responder_texto",
    "responder_escala",
    "remover_resposta",
)


@pytest.fixture
def ana(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


@pytest.fixture
def chamadas(monkeypatch):
    """Conta as chamadas às operações da 005 feitas pela interface, repassando-as."""
    contagem = []
    for nome in OPERACOES:
        original = getattr(op, nome)

        def espia(*args, _original=original, _nome=nome, **kwargs):
            contagem.append(_nome)
            return _original(*args, **kwargs)

        monkeypatch.setattr(f"trajetoria.interface.gravacao.{nome}", espia)
    return contagem


def _post(client, participacao, posicao, dados):
    return client.post(f"/participacoes/{participacao.pk}/secoes/{posicao}/", dados)


def _resposta(participacao, pergunta):
    return Resposta.objects.filter(participacao=participacao, pergunta=pergunta).first()


def _ate(participacao, base, secoes, **escolhas):
    c.preencher(participacao, base, secoes, {"Q1": "Sim", "Q14": "Graduação", **escolhas})


def _dados_s2(**trocas):
    """S2 completa e válida (Q2–Q9), com trocas por campo."""
    dados = {"p1": "1", "p2": "27", "p3": "1", "p4": "2", "p6": "1", "p7": "1", "p8": "1"}
    dados.update(trocas)
    return {k: v for k, v in dados.items() if v is not None}


def test_registrar_nos_quatro_tipos_e_complemento(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1])
    assert _post(client, ana, 2, _dados_s2(p2="  27 anos ")).status_code == 302
    assert _resposta(ana, b.q(2)).opcao == b.opcao(2, b.q(2).opcoes.get(posicao=1).texto)
    assert _resposta(ana, b.q(3)).texto == "  27 anos "  # exatamente como digitado
    _ate(ana, b, [2, 3, 6])
    dados = ci.dados_validos(ci.secao_do_conteudo(b.versao, 8))
    dados.update({"p1": "4", "p7": ["1", "6"], "p7-complemento": " Relatório técnico "})
    assert _post(client, ana, 8, dados).status_code == 302
    assert _resposta(ana, b.q(20)).escala == 4
    q26 = _resposta(ana, b.q(26))
    assert {o.posicao for o in q26.opcoes.all()} == {1, 6}
    assert q26.complemento == " Relatório técnico "


def test_substituir_e_remover(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1, 2])
    _post(client, ana, 2, _dados_s2(p1="3", p2="30", p5="2"))
    assert _resposta(ana, b.q(2)).opcao.posicao == 3 and _resposta(ana, b.q(3)).texto == "30"
    assert _resposta(ana, b.q(6)).opcao.posicao == 2
    _post(client, ana, 2, _dados_s2(p2="   ", **{"p5-remover": "1", "p5": "2"}))
    assert _resposta(ana, b.q(3)) is None  # só espaços = sem resposta
    assert _resposta(ana, b.q(6)) is None  # "Deixar esta pergunta sem resposta" prevalece


def test_sem_resposta_desfaz_marcacao_ainda_nao_gravada(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1])
    resposta = _post(client, ana, 2, _dados_s2(**{"p5": "2", "p5-remover": "1"}))
    assert resposta.status_code == 302
    assert _resposta(ana, b.q(6)) is None  # nada gravado para a opcional
    assert _resposta(ana, b.q(2)) is not None  # as demais seguem gravadas


def test_sem_resposta_nao_existe_em_obrigatoria(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1, 2])
    _post(client, ana, 2, _dados_s2(**{"p1-remover": "1"}))
    assert _resposta(ana, b.q(2)) is not None  # campo inexistente: ignorado


def test_multipla_sem_opcao_remove(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1, 2, 3, 6, 8])
    dados = ci.dados_validos(ci.secao_do_conteudo(b.versao, 8))
    del dados["p7"]
    _post(client, ana, 8, dados)
    assert _resposta(ana, b.q(26)) is None


def test_reenviar_sem_mudanca_nao_chama_a_005(client, cenario, ana, chamadas):
    b = cenario.base
    _ate(ana, b, [1, 2])
    antes = c.retrato(ana)
    respostas = respostas_atuais(ana)
    dados = _dados_s2(
        p1=str(respostas[b.q(2).id].opcao.posicao),
        p2=respostas[b.q(3).id].texto,
        p3=str(respostas[b.q(4).id].opcao.posicao),
        p4=str(respostas[b.q(5).id].opcao.posicao),
        p6=str(respostas[b.q(7).id].opcao.posicao),
        p7=str(respostas[b.q(8).id].opcao.posicao),
        p8=str(respostas[b.q(9).id].opcao.posicao),
    )
    assert _post(client, ana, 2, dados).status_code == 302
    assert chamadas == [] and c.retrato(ana) == antes


def test_atomicidade_pela_005(cenario, ana):
    b = cenario.base
    _ate(ana, b, [1, 2, 3, 6])
    secao = ci.secao_do_conteudo(b.versao, 8)
    antes = c.retrato(ana)
    # Valores forjados (o formulário não os deixaria passar): o segundo a 005 rejeita.
    limpos = {1: Valor(escala=3), 2: Valor(escala=99)}
    resultado = salvar_secao(ana, secao, limpos, respostas_atuais(ana))
    assert list(resultado.erros_por_pergunta) == [2] and resultado.operacoes == 0
    assert c.retrato(ana) == antes  # a primeira também foi desfeita


def test_todos_os_erros_de_uma_vez_e_nada_gravado(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1])
    antes = c.retrato(ana)
    resposta = _post(client, ana, 2, _dados_s2(p1="99", p7="99", p2="valor digitado"))
    assert resposta.status_code == 200
    html, texto = resposta.content.decode(), ci.texto_visivel(resposta)
    assert "<title>Erro: " in html
    assert "Há problemas nesta seção" in texto
    # Erro de forma continua erro (014 FR-004): nunca a apresentação de pendência.
    assert "Ainda faltam" not in texto and "Falta responder" not in texto
    assert "Erro: Selecione uma das opções apresentadas." in texto
    assert texto.count("Selecione uma das opções apresentadas.") >= 2
    assert 'href="#p1"' in html and 'href="#p7"' in html
    assert 'value="valor digitado"' in html  # valores reapresentados
    assert 'aria-invalid="true"' in html
    assert c.retrato(ana) == antes


@pytest.mark.parametrize("com_opcao", [True, False])
def test_complemento_sem_a_opcao(client, cenario, ana, com_opcao):
    b = cenario.base
    _ate(ana, b, [1, 2, 3, 6])
    antes = c.retrato(ana)
    dados = ci.dados_validos(ci.secao_do_conteudo(b.versao, 8))
    dados["p7"] = ["1"] if com_opcao else []
    dados["p7-complemento"] = "Texto fictício"
    resposta = _post(client, ana, 8, dados)
    assert resposta.status_code == 200
    assert "Para descrever, marque a opção «Outro»." in ci.texto_visivel(resposta)
    assert c.retrato(ana) == antes


def test_campos_alheios_sao_ignorados(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1])
    dados = _dados_s2(p99="1", **{"p1-x": "1", "formacao": "qualquer"})
    assert _post(client, ana, 2, dados).status_code == 302
    perguntas_da_s2 = {p.id for p in b.s(2).perguntas.all()}
    gravadas = set(respostas_atuais(ana)) - {b.q(1).id}
    assert gravadas <= perguntas_da_s2


def test_post_de_secao_fora_do_percurso(client, cenario, ana):
    b = cenario.base
    _ate(ana, b, [1, 2, 3, 6, 8], Q33="Não")
    antes = c.retrato(ana)
    secao9 = ci.secao_do_conteudo(b.versao, 9)
    resposta = _post(client, ana, 9, ci.dados_validos(secao9))
    assert resposta["Location"] == f"/participacoes/{ana.pk}/secoes/10/?aviso=percurso"
    assert c.retrato(ana) == antes


def test_concluida_entre_get_e_post(client, cenario, ana):
    b = cenario.base
    client.get(f"/participacoes/{ana.pk}/secoes/1/")
    op.responder_escolha_unica(ana, b.q(1), b.opcao(1, "Não"))
    op.concluir(ana)
    antes = c.retrato(ana)
    resposta = _post(client, ana, 1, {"p1": "1"})
    assert resposta.status_code == 200
    assert "Esta pesquisa já foi respondida." in ci.texto_visivel(resposta)
    assert c.retrato(ana) == antes


def test_tipos_da_baseline_estao_todos_exercitados(cenario):
    tipos = {p.tipo for p in cenario.base.perguntas.values()}
    assert tipos == set(TipoPergunta)


def test_jornada_consultada_depois_de_gravar(client, cenario, ana):
    _ate(ana, cenario.base, [1])
    _post(client, ana, 2, _dados_s2())
    assert situacao_da_jornada(ana).secao_atual.posicao == 3


def test_posicao_de_opcao_desconhecida_e_erro_sem_chamar_a_005(cenario, ana, chamadas):
    b = cenario.base
    _ate(ana, b, [1])
    secao = ci.secao_do_conteudo(b.versao, 2)
    antes = c.retrato(ana)
    resultado = salvar_secao(
        ana, secao, {1: Valor(opcao=99), 2: Valor(texto="27")}, respostas_atuais(ana)
    )
    assert resultado.erros_por_pergunta == {1: ["Selecione uma das opções apresentadas."]}
    assert "responder_escolha_unica" not in chamadas
    assert c.retrato(ana) == antes  # a resposta válida (texto) também foi desfeita

"""Tela de formações (008 US2, US11, US12) e contexto da formação (FR-025, FR-026)."""

import re
from datetime import date

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.interface.apresentacao import contexto_da_formacao, resumo_da_formacao
from trajetoria.participacao.entrada import situacao_de_entrada

# --- Contexto da formação: puro, sem banco -------------------------------------------------


def test_contexto_com_todos_os_atributos_na_ordem():
    conclusao = ConclusaoAcademica(
        curso="Técnico em Química",
        unidade="Vila Velha",
        ano_conclusao=2012,
        nivel="Técnico",
        modalidade="Presencial",
        forma_oferta="Integrado",
    )
    assert contexto_da_formacao(conclusao) == [
        ("Curso", "Técnico em Química"),
        ("Unidade", "Vila Velha"),
        ("Ano de conclusão", "2012"),
        ("Nível", "Técnico"),
        ("Modalidade", "Presencial"),
        ("Forma de oferta", "Integrado"),
    ]


def test_contexto_sem_atributos_e_vazio():
    assert contexto_da_formacao(ConclusaoAcademica()) == []
    assert resumo_da_formacao(ConclusaoAcademica()) == ""


def test_resumo_usa_o_ano_da_data_quando_so_ha_data():
    conclusao = ConclusaoAcademica(curso="Curso", data_conclusao=date(2020, 7, 10))
    assert resumo_da_formacao(conclusao) == "Curso · 2020"


def test_contexto_omite_o_que_nao_foi_informado():
    conclusao = ConclusaoAcademica(curso="Licenciatura em Pedagogia")
    assert contexto_da_formacao(conclusao) == [("Curso", "Licenciatura em Pedagogia")]


def test_data_prevalece_sobre_o_ano_e_nada_e_inventado():
    conclusao = ConclusaoAcademica(
        unidade="Serra", ano_conclusao=2022, data_conclusao=date(2022, 12, 16)
    )
    assert contexto_da_formacao(conclusao) == [
        ("Unidade", "Serra"),
        ("Data de conclusão", "16/12/2022"),
    ]
    assert resumo_da_formacao(conclusao) == "Serra · 2022"


# --- Tela de formações: consumo da 007 (US2) ------------------------------------------------


@pytest.fixture
def inst(db):
    ce.incorporar(FonteSimulada())
    return c.instrumento()


def _tela(client, id_externo):
    ci.entrar_como(client, ce.pessoa_da_fonte(id_externo))
    resposta = client.get("/formacoes/")
    assert resposta.status_code == 200
    return resposta, ci.texto_visivel(resposta)


def _formacoes_nos_botoes(resposta) -> list[str]:
    return re.findall(r'name="formacao" value="([^"]+)"', resposta.content.decode())


def _botoes(resposta) -> list[str]:
    return re.findall(r"<button[^>]*>([^<]+)</button>", resposta.content.decode())


def _conclusao(id_externo, curso):
    return ce.pessoa_da_fonte(id_externo).conclusoes.get(curso=curso)


def test_entrada_resolvida_um_unico_botao_sem_escolha(client, inst):
    campanha = c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0001")
    assert "Esta pesquisa refere-se à sua formação:" in texto
    assert "você pode parar e continuar depois" in texto  # como o salvamento funciona
    assert "Tecnologia em Análise e Desenvolvimento de Sistemas" in texto and "Serra" in texto
    assert "Forma de oferta" not in texto  # não informada pela fonte: omitida
    assert [b for b in _botoes(resposta) if "pesquisa" in b] == ["Iniciar a pesquisa"]
    assert _formacoes_nos_botoes(resposta) == []
    assert campanha.nome not in texto and ci.tecnicos_em(texto) == []


def test_entrada_resolvida_com_rascunho_continua(client, inst):
    campanha = c.campanha_aberta(inst.versao)
    ce.participacao_em_rascunho(campanha, ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get())
    resposta, _ = _tela(client, "SIM-P-0001")
    assert [b for b in _botoes(resposta) if "pesquisa" in b] == ["Continuar a pesquisa"]


def test_selecao_necessaria_uma_acao_por_formacao_sem_ranking(client, inst):
    campanha = c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0003")
    assert "Sobre qual formação do Ifes você responderá esta pesquisa?" in texto
    assert "respondida separadamente para cada formação" in texto
    pessoa = ce.pessoa_da_fonte("SIM-P-0003")
    esperadas = [str(f.conclusao.pk) for f in situacao_de_entrada(pessoa).pendentes]
    assert _formacoes_nos_botoes(resposta) == esperadas and len(esperadas) == 2
    for palavra in ("sugerida", "principal", "recomendada", "mais recente"):
        assert palavra not in texto.lower()
    assert campanha.nome not in texto


def test_sem_pesquisa_disponivel(client, inst):
    resposta, texto = _tela(client, "SIM-P-0002")
    assert "No momento, não há pesquisa disponível para as suas formações." in texto
    assert "Técnico em Edificações" in texto and "Bacharelado em Engenharia Civil" in texto
    assert "Iniciar a pesquisa" not in texto and _formacoes_nos_botoes(resposta) == []


def test_sem_entrada_pendente_com_formacao_concluida(client, inst):
    campanha = c.campanha_aberta(inst.versao)
    conclusao = ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get()
    ce.participacao_concluida(campanha, conclusao, inst)
    resposta, texto = _tela(client, "SIM-P-0001")
    assert "Não há pesquisa pendente para você neste momento." in texto
    assert "Pesquisa já respondida." in texto
    assert "Iniciar a pesquisa" not in texto and "Continuar a pesquisa" not in texto


def test_outras_formacoes_informadas_com_sua_situacao(client, inst):
    c.campanha_aberta(inst.versao, niveis=["Pós-graduação"])
    resposta, texto = _tela(client, "SIM-P-0004")
    assert "Mestrado Profissional em Química" in texto
    assert "Suas outras formações" in texto
    assert texto.count("Sem pesquisa disponível no momento.") == 2


def test_sem_formacao(client, inst):
    pessoa = Pessoa.objects.create(fonte="simulada", id_externo="SIM-P-T", nome="Teste Exemplo")
    ci.entrar_como(client, pessoa)
    texto = ci.texto_visivel(client.get("/formacoes/"))
    assert "Não encontramos formações concluídas no Ifes associadas a você." in texto


def test_consulta_nao_grava(client, inst):
    c.campanha_aberta(inst.versao)
    ci.entrar_como(client, ce.pessoa_da_fonte("SIM-P-0003"))
    antes = ce.linhas()
    client.get("/formacoes/")
    assert ce.linhas() == antes


def test_avisos_e_metodos(client, inst):
    ci.entrar_como(client, ce.pessoa_da_fonte("SIM-P-0001"))
    assert "A situação da pesquisa mudou." in ci.texto_visivel(
        client.get("/formacoes/?aviso=situacao")
    )
    assert "mudou" not in ci.texto_visivel(client.get("/formacoes/?aviso=x"))
    assert client.post("/formacoes/").status_code == 405
    assert "no-store" in client.get("/formacoes/")["Cache-Control"]


def test_sem_pessoa_vai_para_a_entrada(client, inst):
    resposta = client.get("/formacoes/")
    assert resposta.status_code == 302 and resposta["Location"] == "/demonstracao/"


def test_consultas_limitadas(client, inst, django_assert_max_num_queries):
    c.campanha_aberta(inst.versao)
    ci.entrar_como(client, ce.pessoa_da_fonte("SIM-P-0004"))
    with django_assert_max_num_queries(8):  # medido: 2 + 1 por formação; 3 formações
        client.get("/formacoes/")


# --- Ausência de pesquisa (US11) e ambiguidade (US12) ----------------------------------------


def test_inelegivel_tem_a_mesma_mensagem_sem_criterios(client, inst):
    campanha = c.campanha_aberta(inst.versao, unidades=["Vitória"])
    resposta, texto = _tela(client, "SIM-P-0001")
    assert "No momento, não há pesquisa disponível para as suas formações." in texto
    assert "Vitória" not in texto and campanha.nome not in texto
    assert "critério" not in texto.lower() and "elegív" not in texto.lower()


def test_rascunho_de_campanha_encerrada_nao_e_oferecido(client, inst, relogio):
    campanha = c.campanha_aberta(inst.versao)
    ce.participacao_em_rascunho(campanha, ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get())
    relogio.agora = c.DEPOIS_DO_FIM
    resposta, texto = _tela(client, "SIM-P-0001")
    assert "Sem pesquisa disponível no momento." in texto
    assert "Continuar a pesquisa" not in texto


def _ambigua_e_outra(inst):
    maria = ce.pessoa_da_fonte("SIM-P-0003")
    ambigua = maria.conclusoes.get(unidade="Cefor")
    outra = maria.conclusoes.get(unidade="Serra")
    c.campanha_aberta(inst.versao, unidades=["Cefor"])
    c.campanha_aberta(inst.versao, unidades=["Cefor", "Serra"])
    return maria, ambigua, outra


def test_ambiguidade_e_local_e_neutra(client, inst):
    _, ambigua, outra = _ambigua_e_outra(inst)
    resposta, texto = _tela(client, "SIM-P-0003")
    assert "Esta pesquisa refere-se à sua formação:" in texto  # a outra, sem escolha
    assert _formacoes_nos_botoes(resposta) == []
    assert [b for b in _botoes(resposta) if "pesquisa" in b] == ["Iniciar a pesquisa"]
    assert (
        "A pesquisa referente a esta formação não está disponível neste momento." in texto
    )
    assert "Campanha" not in texto  # nem nome, nem quantidade, nem período de Campanha
    assert "30/06/2027" not in texto and "01/04/2027" not in texto


def test_so_ambigua_e_sem_entrada_pendente(client, inst):
    c.campanha_aberta(inst.versao)
    c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0001")
    assert "Não há pesquisa pendente para você neste momento." in texto
    assert "não está disponível neste momento" in texto


def test_entrada_pela_ambigua_nao_cria_nada(client, inst):
    maria, ambigua, _ = _ambigua_e_outra(inst)
    ci.entrar_como(client, maria)
    antes = ce.linhas()
    resposta = client.post("/formacoes/entrar/", {"formacao": str(ambigua.pk)})
    assert resposta["Location"] == "/formacoes/?aviso=situacao"
    assert ce.linhas() == antes

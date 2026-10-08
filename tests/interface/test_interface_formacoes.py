"""Tela de formações (008 US2, US11, US12) e contexto da formação (FR-025, FR-026)."""

import re
from datetime import date

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.interface import mensagens
from trajetoria.interface.apresentacao import (
    complemento_da_formacao,
    contexto_da_formacao,
    resumo_da_formacao,
)
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


def test_complemento_da_formacao_so_com_o_informado():
    """014 FR-034: nível · modalidade · forma de oferta, só os informados (007/DP-702)."""
    from types import SimpleNamespace as Conclusao

    todos = Conclusao(nivel="Técnico", modalidade="Presencial", forma_oferta="Integrado")
    assert complemento_da_formacao(todos) == "Técnico · Presencial · Integrado"
    parte = Conclusao(nivel="Graduação", modalidade=None, forma_oferta=None)
    assert complemento_da_formacao(parte) == "Graduação"
    assert complemento_da_formacao(Conclusao(nivel=None, modalidade=None, forma_oferta=None)) == ""


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
    assert (
        "Você concluiu Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022." in texto
    )  # 014 FR-031
    assert "mesmo sem terminar a seção, e continuar depois" in texto  # 014 FR-002
    assert "Tecnologia em Análise e Desenvolvimento de Sistemas" in texto and "Serra" in texto
    assert "Forma de oferta" not in texto and "Curso" not in texto  # sem a ficha (014 FR-034)
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
    assert "Cada formação tem sua própria pesquisa." in texto  # 014 FR-033
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
    # 014 FR-036: "sem pesquisa" não se repete por formação; as formações continuam listadas.
    assert "Sem pesquisa disponível no momento." not in texto
    assert "Técnico em Química" in texto and "Licenciatura em Química" in texto


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
    assert resposta.status_code == 302 and resposta["Location"] == "/acesso/"


def test_consultas_limitadas(client, inst, django_assert_max_num_queries):
    c.campanha_aberta(inst.versao)
    ci.entrar_como(client, ce.pessoa_da_fonte("SIM-P-0004"))
    # 018: inclui leitura da sessão; 3 formações. 024: +5 da Versão da Campanha e do seu
    # conteúdo, lidos uma vez por Versão para "no máximo N partes" (FR-014). O item "Minha
    # trajetória" da navegação reaproveita a consulta da página (`elegivel` memorizado).
    with django_assert_max_num_queries(14):
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
    assert "No momento, não há pesquisa disponível para as suas formações." in texto
    assert "Sem pesquisa disponível no momento." not in texto  # 014 FR-036
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
    assert "Você concluiu " in texto  # a outra, sem escolha (014 FR-031)
    assert _formacoes_nos_botoes(resposta) == []
    assert [b for b in _botoes(resposta) if "pesquisa" in b] == ["Iniciar a pesquisa"]
    assert "A pesquisa referente a esta formação não está disponível neste momento." in texto
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


# --- 014 US1: a entrada diz que se pode salvar a Seção incompleta (FR-002) ----------------

FRASE_SALVAR = (
    "Você responde uma seção de cada vez. Pode salvar a qualquer momento, mesmo sem terminar "
    "a seção, e continuar depois."
)


@pytest.mark.parametrize("id_externo", ["SIM-P-0001", "SIM-P-0003"])
def test_entrada_diz_que_se_pode_salvar_secao_incompleta(client, inst, id_externo):
    c.campanha_aberta(inst.versao)
    _, texto = _tela(client, id_externo)
    assert FRASE_SALVAR in texto


# --- 014 US2: avisos de saída por "Salvar e sair" (FR-012), lista fechada ------------------


def _aviso(client, consulta):
    ci.entrar_como(client, ce.pessoa_da_fonte("SIM-P-0001"))
    resposta = client.get(f"/formacoes/{consulta}")
    m = re.search(r'<p class="aviso[^"]*" role="status">(.*?)</p>', resposta.content.decode(), re.S)
    return m and m.group(1).strip()


def test_aviso_de_saida_com_respostas_salvas(client, inst):
    c.campanha_aberta(inst.versao)
    assert _aviso(client, "?aviso=salvo") == (
        "O que você respondeu nesta seção está salvo. Você pode continuar a pesquisa quando quiser."
    )


def test_aviso_de_saida_sem_respostas_e_neutro(client, inst):
    c.campanha_aberta(inst.versao)
    aviso = _aviso(client, "?aviso=saida")
    assert aviso == "Você pode continuar a pesquisa quando quiser." and "salvo" not in aviso


def test_avisos_fora_da_lista_sao_ignorados(client, inst):
    c.campanha_aberta(inst.versao)
    assert _aviso(client, "?aviso=situacao") == (
        "A situação da pesquisa mudou. Veja abaixo a situação atual."
    )
    assert _aviso(client, "?aviso=qualquer") is None
    assert _aviso(client, "?aviso=percurso") is None


# --- 014 US6: "Suas formações no Ifes" (FR-030 a FR-037; título revisado pela 021 FR-006) -----


def _h1(resposta):
    return re.findall(r"<h1>\s*(.*?)\s*</h1>", resposta.content.decode())


def test_titulo_trajetoria_em_todas_as_situacoes(client, inst):
    campanha = c.campanha_aberta(inst.versao)
    for id_externo in ("SIM-P-0001", "SIM-P-0003", "SIM-P-0002"):  # resolvida, seleção, sem pesq.
        assert _h1(_tela(client, id_externo)[0]) == ["Suas formações no Ifes"], id_externo
    ce.participacao_concluida(campanha, ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get(), inst)
    assert _h1(_tela(client, "SIM-P-0001")[0]) == ["Suas formações no Ifes"]  # sem pendente
    pessoa = Pessoa.objects.create(fonte="simulada", id_externo="SIM-P-T", nome="Teste Exemplo")
    ci.entrar_como(client, pessoa)
    assert _h1(client.get("/formacoes/")) == ["Suas formações no Ifes"]  # sem formação


def test_entrada_resolvida_parte_do_fato_e_da_continuacao(client, inst):
    c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0001")
    conclusao = ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get()
    assert f"Você concluiu {resumo_da_formacao(conclusao)}." in texto
    assert "O Ifes quer saber como sua trajetória seguiu depois disso." in texto
    assert "campus" not in texto.lower()  # 014 FR-032: nenhuma qualificação fixa da unidade


def test_entrada_sem_atributos_usa_texto_neutro(client, inst, monkeypatch):
    c.campanha_aberta(inst.versao)
    monkeypatch.setattr("trajetoria.interface.views.resumo_da_formacao", lambda conclusao: "")
    _, texto = _tela(client, "SIM-P-0001")
    assert "Encontramos uma formação sua no Ifes." in texto
    assert "Você concluiu" not in texto


def test_selecao_sem_contagem_e_na_ordem_da_007(client, inst):
    c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0003")
    assert "Cada formação tem sua própria pesquisa." in texto
    assert not re.search(r"\b(duas|três|\d+) formações\b", texto)
    pessoa = ce.pessoa_da_fonte("SIM-P-0003")
    esperadas = [str(f.conclusao.pk) for f in situacao_de_entrada(pessoa).pendentes]
    assert _formacoes_nos_botoes(resposta) == esperadas
    for palavra in ("cronológ", "mais recente", "principal", "atual"):
        assert palavra not in texto.lower(), palavra


def test_formacao_compacta_com_ano_e_complemento(client, inst):
    c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0003")
    assert "Data de conclusão" not in texto and "Ano de conclusão" not in texto  # 014 FR-034
    for formacao in ce.pessoa_da_fonte("SIM-P-0003").conclusoes.all():
        assert resumo_da_formacao(formacao) in texto
        if complemento_da_formacao(formacao):
            assert complemento_da_formacao(formacao) in texto
    assert "2025" in texto  # o ano da data de conclusão da Especialização


def test_ordem_das_outras_formacoes_e_a_da_007(client, inst):
    c.campanha_aberta(inst.versao, niveis=["Pós-graduação"])
    resposta, texto = _tela(client, "SIM-P-0004")
    pessoa = ce.pessoa_da_fonte("SIM-P-0004")
    linhas = [resumo_da_formacao(f.conclusao) for f in situacao_de_entrada(pessoa).formacoes]
    outras = [linha for linha in linhas if f"Você concluiu {linha}." not in texto]
    posicoes = [texto.index(linha) for linha in outras]
    assert posicoes == sorted(posicoes) and len(outras) == 2


# --- 021 FR-005, revista pela 024 (FR-009, FR-013, FR-014; reauditoria R-02) -----------------


def test_ligacao_para_a_narrativa_antes_de_participar(client, inst):
    c.campanha_aberta(inst.versao)
    resposta, texto = _tela(client, "SIM-P-0001")
    assert 'href="/minha-trajetoria/">Ver minha trajetória no Ifes' in resposta.content.decode()


def test_sem_antecipacao_e_com_tamanho_ao_iniciar(client, inst):
    from trajetoria.instrumento.conteudo import conteudo_da_versao
    from trajetoria.participacao.percurso import maximo_restante

    campanha = c.campanha_aberta(inst.versao)
    conteudo = conteudo_da_versao(inst.versao)
    n = 1 + maximo_restante(conteudo, conteudo.secoes[0].id)
    tamanho = mensagens.TAMANHO_DA_PESQUISA.format(n=n)
    _, texto = _tela(client, "SIM-P-0001")
    assert "Ao final, você poderá ver" not in texto
    assert tamanho in texto
    ana = ce.pessoa_da_fonte("SIM-P-0001").conclusoes.get()
    ce.participacao_em_rascunho(campanha, ana)
    _, texto = _tela(client, "SIM-P-0001")
    assert tamanho not in texto  # retomar: vale o "onde parou" da 023


def test_tamanho_em_cada_formacao_da_selecao(client, inst):
    c.campanha_aberta(inst.versao)
    _, texto = _tela(client, "SIM-P-0003")
    assert texto.count("A pesquisa tem no máximo") == 2


def test_aviso_liga_as_formacoes():
    """021 FR-006 (R16): as telas de estado ligam a "Suas formações no Ifes"."""
    html = open("trajetoria/interface/templates/interface/aviso.html").read()
    assert '<a href="/formacoes/">Ver suas formações no Ifes</a>' in html
    assert "Ver sua trajetória no Ifes" not in html

"""Apresentação da Seção (008 US4; FR-032 a FR-039) e retomada (US6; SC-008).

A renderização deriva só do instrumento: os testes conhecem Q1…Q54 (pela `Baseline`), a
interface não.
"""

import re
from html.parser import HTMLParser

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.participacao import operacoes as op
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

ESCOLHAS_ATE_S11 = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Não", "Q46": "Não"}


@pytest.fixture
def ana(client, cenario):
    """Ana com a Participação iniciada pela interface."""
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    return Participacao.objects.get(pk=ci.participacao_de(resposta))


def _preencher(participacao, base, secoes, escolhas=ESCOLHAS_ATE_S11):
    c.preencher(participacao, base, secoes, escolhas)


def _get(client, participacao, posicao, consulta=""):
    return client.get(f"/participacoes/{participacao.pk}/secoes/{posicao}/{consulta}")


def _html(resposta) -> str:
    return resposta.content.decode()


def _formulario(html: str) -> str:
    """O formulário da Seção (o cabeçalho também tem formulários: trocar e encerrar)."""
    return html[html.index('<form method="post" action="/participacoes/') :]


def _bloco(html: str, n: int) -> str:
    """O HTML da Pergunta de posição `n` (elemento com id="p<n>")."""
    inicio = html.index(f'id="p{n}"')
    fim = html.find('class="pergunta', inicio + 1)
    return html[inicio : fim if fim != -1 else len(html)]


def test_primeira_secao_com_titulo_abertura_e_q1(client, cenario, ana):
    resposta = _get(client, ana, 1)
    assert resposta.status_code == 200
    html, texto = _html(resposta), ci.texto_visivel(resposta)
    assert re.findall(r"<h1>\s*(.*?)\s*</h1>", html) == ["Termos e condições"]  # 014 FR-023
    assert "É com muita satisfação" in texto  # texto de abertura da Versão
    assert "Termos e condições" in texto
    q1 = _bloco(html, 1)
    assert re.search(r'<fieldset[^>]*id="p1"', html) and "<legend" in q1
    assert "Você concorda com os termos acima?" in q1 and "(obrigatória)" in q1
    assert q1.count('type="radio"') == 2
    assert not re.search(r"\bQ\d{1,2}\b", texto)
    assert ci.tecnicos_em(texto) == []


def test_abertura_so_na_primeira_secao(client, cenario, ana):
    _preencher(ana, cenario.base, [1])
    assert "É com muita satisfação" not in ci.texto_visivel(_get(client, ana, 2))


def test_quatro_tipos_complemento_escala_e_explicativo(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6])
    html = _html(_get(client, ana, 8))
    q20 = _bloco(html, 1)  # escala
    assert q20.count('type="radio"') == 5
    assert "5 = Concordo totalmente" in q20
    assert not re.search(r"\b1 = ", q20)  # rótulo inicial ausente não é inventado
    q26 = _bloco(html, 7)  # escolha múltipla com "Outro:"
    assert q26.count('type="checkbox"') == 6
    assert 'name="p7-complemento"' in q26 and "Descreva: «Outro»" in q26
    q32 = _bloco(html, 13)  # explicativo
    assert "Não considerar auxilio estudantil como bolsa." in q32
    descrito = re.search(r'aria-describedby="([^"]+)"', q32).group(1).split()
    assert all(f'id="{i}"' in html for i in descrito)
    html3 = _html(_get(client, ana, 3))
    q10 = _bloco(html3, 1)  # texto curto
    assert re.search(r'<label[^>]*for="p1-campo"', q10) and 'type="text"' in q10


def test_lista_suspensa_acima_de_dez_opcoes(client, cenario, ana):
    _preencher(ana, cenario.base, [1])
    html = _html(_get(client, ana, 2))
    q8 = _bloco(html, 7)  # 17 Opções
    assert "<select" in q8 and "Selecione…" in q8 and 'type="radio"' not in q8
    q2 = _bloco(html, 1)  # 6 Opções
    assert "<select" not in q2 and q2.count('type="radio"') == 6


def test_s11_apresenta_q46_q47_q48_juntas(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6, 8, 10])
    op.responder_escolha_unica(ana, cenario.base.q(46), cenario.base.opcao(46, "Não"))
    texto = ci.texto_visivel(_get(client, ana, 11))
    posicoes = [texto.index(t) for t in ("Atualmente você estuda?", "Após o curso, você:")]
    assert posicoes == sorted(posicoes)
    assert "Caso não tenha estudado mais deixe essa resposta em branco." in texto


def test_s3_sem_pre_preenchimento_pela_conclusao(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2])
    resposta = _get(client, ana, 3)
    html = _html(resposta)
    formulario = _formulario(html)
    assert "checked" not in formulario and "selected" not in formulario.replace(
        '<option value="" selected', ""
    )
    assert 'value="2022"' not in formulario
    assert "Você está respondendo sobre:" in ci.texto_visivel(resposta)
    assert html.index("Você está respondendo sobre:") < html.index(_formulario(html)[:40])


def test_contexto_compacto_e_resumo_de_erros_no_topo(client, cenario, ana):
    resposta = client.post(f"/participacoes/{ana.pk}/secoes/1/", {"p1": "99"})
    html, texto = _html(resposta), ci.texto_visivel(resposta)
    assert (
        "Você está respondendo sobre: Tecnologia em Análise e Desenvolvimento de Sistemas" in texto
    )
    assert "Unidade" not in texto and "Modalidade" not in texto  # sem a lista completa
    resumo = html.index('class="resumo-erros"')
    assert html.index("<h1>") < resumo < html.index("Você está respondendo sobre:")
    assert resumo < html.index("É com muita satisfação")  # antes do texto de abertura
    assert "Você concorda com os termos acima? — Selecione uma das opções" in texto


def test_secao_sem_titulo_nao_ganha_h2_inventado(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6, 8, 10, 11])
    html = _html(_get(client, ana, 13))
    principal = _formulario(html)
    assert "<h2" not in principal
    # 014 FR-023: sem título na Versão, o título principal é o da pesquisa — nada inventado —
    # e o título da aba mantém a regra atual, único por tela.
    assert re.findall(r"<h1>\s*(.*?)\s*</h1>", html) == ["Egresso Ifes"]
    assert re.search(r"<title>Seção 13 — ", html)


def test_sem_resposta_so_para_radio_e_escala_nao_obrigatorios(client, cenario, ana):
    _preencher(ana, cenario.base, [1])
    html = _html(_get(client, ana, 1))
    assert "-remover" not in html  # Q1 obrigatória, mesmo respondida
    html2 = _html(_get(client, ana, 2))
    q6 = _bloco(html2, 5)  # Q6, rádio não obrigatória, ainda sem resposta
    assert 'name="p5-remover"' in q6 and "Deixar esta pergunta sem resposta" in q6
    assert re.findall(r'name="(p\d+)-remover"', html2) == ["p5"]  # demais: obrigatórias


def test_secao_fora_do_percurso_vai_para_a_atual(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6, 8])  # Q33 = "Não": S9 fora do percurso
    for posicao in (9, 99):
        resposta = _get(client, ana, posicao)
        assert resposta.status_code == 302
        assert resposta["Location"] == f"/participacoes/{ana.pk}/secoes/10/?aviso=percurso"
    texto = ci.texto_visivel(client.get(f"/participacoes/{ana.pk}/secoes/10/?aviso=percurso"))
    assert "mudaram o caminho da pesquisa" in texto


def test_formulario_salvar_primeiro_csrf_e_cache(client, cenario, ana):
    resposta = _get(client, ana, 1)
    html = _html(resposta)
    formulario = _formulario(html)
    # O primeiro botão de envio é o bloqueador oculto do envio implícito (014 FR-016); o
    # primeiro **visível** continua sendo "Salvar e continuar".
    visiveis = [
        texto
        for atributos, texto in re.findall(r"<button([^>]*)>([^<]+)</button>", formulario)
        if "hidden" not in atributos
    ]
    assert visiveis[0].strip() == "Salvar e continuar"
    assert 'method="post"' in formulario and "csrfmiddlewaretoken" in formulario
    assert "no-store" in resposta["Cache-Control"]


def test_participacao_alheia_e_404(client, cenario, ana):
    ci.entrar_como(client, cenario.pessoa("SIM-P-0011"))
    assert _get(client, ana, 1).status_code == 404


# --- Retomada (US6; SC-008) -----------------------------------------------------------------


def _marcado(html: str, n: int, valor: str) -> bool:
    return bool(re.search(rf'id="p{n}-o{valor}"[^>]*checked', html))


def test_valores_gravados_restaurados_nos_quatro_tipos(client, cenario, ana):
    b = cenario.base
    _preencher(ana, b, [1])
    op.responder_escolha_unica(ana, b.q(2), b.q(2).opcoes.get(posicao=3))
    op.responder_texto(ana, b.q(3), "  27 anos ")
    op.responder_escolha_unica(ana, b.q(8), b.q(8).opcoes.get(posicao=5))
    html = _html(_get(client, ana, 2))
    assert _marcado(html, 1, "3")
    assert 'value="  27 anos "' in _bloco(html, 2)
    assert re.search(r'<option value="5" selected>', _bloco(html, 7))
    _preencher(ana, b, [2, 3, 6])
    op.responder_escala(ana, b.q(20), 4)
    outro = b.q(26).opcoes.get(complemento_textual=True)
    op.responder_escolha_multipla(
        ana, b.q(26), [b.q(26).opcoes.get(posicao=1), outro], complemento="Relatório fictício"
    )
    html = _html(_get(client, ana, 8))
    assert _marcado(html, 1, "4") and not _marcado(html, 1, "3")
    assert _marcado(html, 7, "1") and _marcado(html, 7, str(outro.posicao))
    assert 'value="Relatório fictício"' in _bloco(html, 7)


def test_sair_e_voltar_retoma_a_secao_atual_com_as_respostas(client, cenario, ana):
    b = cenario.base
    pessoa = cenario.pessoa("SIM-P-0001")
    _preencher(ana, b, [1, 2, 3, 6, 8], {**ESCOLHAS_ATE_S11, "Q33": "Sim"})
    op.responder_escolha_unica(ana, b.q(34), b.q(34).opcoes.get(posicao=2))  # S9 parcial
    client.post("/demonstracao/encerrar/")
    ci.entrar_como(client, pessoa)
    assert "Continuar a pesquisa" in ci.texto_visivel(client.get("/formacoes/"))
    antes = ce.linhas()
    resposta = client.post("/formacoes/entrar/")
    secao = client.get(resposta["Location"])["Location"]
    assert secao == f"/participacoes/{ana.pk}/secoes/9/"
    assert _marcado(_html(client.get(secao)), 1, "2")
    assert ce.linhas() == antes


def test_trocar_de_ramo_e_voltar_recupera_as_respostas(client, cenario, ana):
    b = cenario.base
    _preencher(ana, b, [1, 2, 3, 6, 8], {**ESCOLHAS_ATE_S11, "Q33": "Sim"})
    op.responder_escolha_unica(ana, b.q(34), b.q(34).opcoes.get(posicao=2))
    q33 = next(p for p in ci.secao_do_conteudo(b.versao, 8).perguntas if p.id == b.q(33).id)
    posicao = {o.texto: str(o.posicao) for o in q33.opcoes}
    nao, sim = posicao["Não"], posicao["Sim"]
    dados = ci.dados_validos(ci.secao_do_conteudo(b.versao, 8))
    for valor in (nao, sim):
        dados[f"p{q33.posicao}"] = valor
        client.post(f"/participacoes/{ana.pk}/secoes/8/", dados)
    assert _marcado(_html(_get(client, ana, 9)), 1, "2")


def test_valores_nao_salvos_nao_existem_depois(client, cenario, ana):
    b = cenario.base
    _preencher(ana, b, [1])
    client.post(f"/participacoes/{ana.pk}/secoes/2/", {"p1": "99", "p2": "digitado e perdido"})
    assert "digitado e perdido" not in _html(_get(client, ana, 2))


def test_consultas_da_secao_nao_crescem_com_as_respostas(client, cenario, ana):
    escolhas = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim"}
    _preencher(ana, cenario.base, [1, 2, 3, 6], escolhas)
    contagens = []
    for secoes in ([], [8, 9, 11, 12, 13]):
        _preencher(ana, cenario.base, secoes, escolhas)
        with CaptureQueriesContext(connection) as consultas:
            assert _get(client, ana, 8).status_code == 200
        contagens.append(len(consultas))
    assert contagens[0] == contagens[1] <= 11  # medido: 11 (sem reler o conteúdo da Versão)


# --- 014 US1: Seção incompleta, pendência × erro (FR-001 a FR-008) -------------------------


def _envio_parcial_s2(client, cenario, ana, quantas=3):
    """Envia a Seção 2 com só as `quantas` primeiras Perguntas obrigatórias respondidas."""
    _preencher(ana, cenario.base, [1])
    dados = ci.dados_validos(ci.secao_do_conteudo(cenario.base.versao, 2))
    primeiras = sorted(dados, key=lambda campo: int(campo[1:]))[:quantas]
    return client.post(f"/participacoes/{ana.pk}/secoes/2/", {k: dados[k] for k in primeiras})


def _pendentes_s2(cenario, ana) -> list[int]:
    from trajetoria.participacao.consultas import situacao_da_jornada

    pendentes = situacao_da_jornada(ana).passagens[-1].pendentes
    secao = ci.secao_do_conteudo(cenario.base.versao, 2)
    return [p.posicao for p in secao.perguntas if p.id in pendentes]


def test_secao_incompleta_e_gravada_e_volta_como_pendencia(client, cenario, ana):
    from trajetoria.participacao.models import Resposta

    _preencher(ana, cenario.base, [1])
    antes = Resposta.objects.filter(participacao=ana).count()
    resposta = _envio_parcial_s2(client, cenario, ana)
    assert resposta.status_code == 302
    assert resposta["Location"] == f"/participacoes/{ana.pk}/secoes/2/?pendencias=1"
    assert Resposta.objects.filter(participacao=ana).count() == antes + 3


def test_pendencia_nao_e_apresentada_como_erro(client, cenario, ana):
    _envio_parcial_s2(client, cenario, ana)
    tela = _get(client, ana, 2, "?pendencias=1")
    html, texto = _html(tela), ci.texto_visivel(tela)
    assert "Ainda faltam estas perguntas:" in texto
    assert "O que você respondeu nesta seção está salvo." in texto
    assert "Há problemas" not in texto and "Erro" not in texto
    assert re.search(r"<title>Faltam respostas: ", html)
    pendentes = _pendentes_s2(cenario, ana)
    assert pendentes
    for n in pendentes:
        bloco = _bloco(html, n)
        assert "Falta responder: Esta pergunta é obrigatória." in bloco
        assert 'aria-invalid="true"' in bloco and f'id="p{n}-erro"' in bloco


def test_secao_vazia_nao_afirma_salvamento(client, cenario, ana):
    resposta = client.post(f"/participacoes/{ana.pk}/secoes/1/", {})
    assert resposta["Location"] == f"/participacoes/{ana.pk}/secoes/1/?pendencias=1"
    texto = ci.texto_visivel(client.get(resposta["Location"]))
    assert "Ainda faltam estas perguntas:" in texto
    assert "nesta seção está salvo" not in texto and "nesta seção foi salvo" not in texto


def test_indicador_salvo_no_endereco_e_ignorado(client, cenario, ana):
    texto = ci.texto_visivel(_get(client, ana, 1, "?pendencias=1&salvo=1"))
    assert "Ainda faltam estas perguntas:" in texto
    assert "nesta seção está salvo" not in texto and "nesta seção foi salvo" not in texto


# --- Auditoria de identidade visual, IV-03: a cor da pendência não é a do erro --------------
# Sem navegador: a cor resulta da cascata das folhas incluídas na própria página, aplicada às
# classes que a página dá aos ancestrais (leitor em `construcao_interface`).


def _cor(html: str, ancestrais: set[str], classe: str, tag: str = "") -> str:
    """`color` efetivo de `tag.classe` sob ancestrais com as classes `ancestrais`."""
    cor = ci.valor(html, ancestrais, classe, tag)
    assert cor, (ancestrais, classe, tag)
    return cor


def _classes_da_pergunta(html: str, n: int) -> set[str]:
    return set(re.search(rf'class="([^"]*)" id="p{n}"', html)[1].split())


def _classes_do_resumo(html: str) -> set[str]:
    return set(re.search(r'<div class="(resumo-erros[^"]*)"', html)[1].split())


def _secao_2_com_erro_de_forma(client, cenario, ana) -> str:
    _preencher(ana, cenario.base, [1])
    dados = ci.dados_validos(ci.secao_do_conteudo(cenario.base.versao, 2))
    dados["p1"] = "99"  # posição de Opção inexistente: erro de forma, nada gravado
    resposta = client.post(f"/participacoes/{ana.pk}/secoes/2/", dados)
    assert resposta.status_code == 200
    return _html(resposta)


def test_pergunta_pendente_nao_usa_a_cor_de_erro(client, cenario, ana):
    _envio_parcial_s2(client, cenario, ana)
    html = _html(_get(client, ana, 2, "?pendencias=1"))
    pendentes = _pendentes_s2(cenario, ana)
    assert pendentes
    cor_do_erro = _cor(html, set(), "erro")
    cor_da_pendencia = _cor(html, _classes_do_resumo(html), "", "h2")
    assert cor_da_pendencia != cor_do_erro
    for n in pendentes:
        classes = _classes_da_pergunta(html, n)
        assert "com-pendencia" in classes
        assert _cor(html, classes, "erro") == cor_da_pendencia


def test_pergunta_com_erro_de_forma_continua_com_a_cor_de_erro(client, cenario, ana):
    html = _secao_2_com_erro_de_forma(client, cenario, ana)
    classes = _classes_da_pergunta(html, 1)
    assert "com-erro" in classes and "com-pendencia" not in classes
    assert _cor(html, classes, "erro") == _cor(html, set(), "erro")


def test_resumos_de_pendencia_e_de_erro_continuam_distintos(client, cenario, ana):
    _envio_parcial_s2(client, cenario, ana)
    pendencia = _html(_get(client, ana, 2, "?pendencias=1"))
    erro = _secao_2_com_erro_de_forma(client, cenario, ana)
    classes_p, classes_e = _classes_do_resumo(pendencia), _classes_do_resumo(erro)
    assert classes_p == {"resumo-erros", "resumo-pendencias"} and classes_e == {"resumo-erros"}
    assert "Ainda faltam estas perguntas:" in pendencia and "Há problemas nesta seção" in erro
    assert _cor(pendencia, classes_p, "", "h2") != _cor(erro, classes_e, "", "h2")
    assert _cor(erro, classes_e, "", "h2") == _cor(erro, set(), "erro")


# --- 014 US4: grupo de rádios só com as Opções (UX-19; FR-018, FR-022) ---------------------


class _Arvore(HTMLParser):
    """Para cada `input`, os atributos dos ancestrais (do mais externo ao mais interno)."""

    VAZIOS = ("input", "br", "meta", "link", "img", "hr")

    def __init__(self):
        super().__init__()
        self.pilha, self.inputs, self.elementos = [], [], []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        self.elementos.append((tag, atributos))
        if tag == "input":
            self.inputs.append((atributos, [dict(a, _tag=t) for t, a in self.pilha]))
        if tag not in self.VAZIOS:
            self.pilha.append((tag, atributos))

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break


def _estrutura(html):
    arvore = _Arvore()
    arvore.feed(html)
    return arvore


def _verificar_grupo_exclusivo(html, nome, *, obrigatoria):
    arvore = _estrutura(html)
    fieldset = next(a for t, a in arvore.elementos if t == "fieldset" and a.get("id") == nome)
    assert "role" not in fieldset and "aria-required" not in fieldset
    assert ("legend", {"id": f"{nome}-enunciado"}) in arvore.elementos
    radios = [(a, anc) for a, anc in arvore.inputs if a.get("name") == nome]
    assert radios
    for _, ancestrais in radios:
        grupo = [a for a in ancestrais if a.get("role") == "radiogroup"]
        assert len(grupo) == 1 and grupo[0]["aria-labelledby"] == f"{nome}-enunciado"
        assert (grupo[0].get("aria-required") == "true") == obrigatoria
        assert any(a.get("id") == nome and a["_tag"] == "fieldset" for a in ancestrais)
    return arvore


def test_escala_obrigatoria_tem_radiogroup_so_com_os_pontos(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6])
    html = _html(_get(client, ana, 8))
    arvore = _verificar_grupo_exclusivo(html, "p1", obrigatoria=True)
    grupo = next(a for t, a in arvore.elementos if a.get("aria-labelledby") == "p1-enunciado")
    assert grupo.get("class") == "escala"


def test_remover_fica_na_pergunta_mas_fora_do_grupo(client, cenario, ana):
    _preencher(ana, cenario.base, [1, 2, 3, 6, 8, 10])
    html = _html(_get(client, ana, 11))  # p3 = escala opcional (Q48), com a caixa de remoção
    arvore = _verificar_grupo_exclusivo(html, "p3", obrigatoria=False)
    remover = [anc for a, anc in arvore.inputs if a.get("name") == "p3-remover"]
    assert len(remover) == 1
    ancestrais = remover[0]
    assert any(a.get("id") == "p3" and a["_tag"] == "fieldset" for a in ancestrais)
    assert not any(a.get("role") == "radiogroup" for a in ancestrais)
    fieldset = next(a for t, a in arvore.elementos if t == "fieldset" and a.get("id") == "p3")
    assert "aria-describedby" in fieldset  # descrição da escala continua ligada


def test_radio_opcional_tem_grupo_e_remover_fora_dele(client, cenario, ana):
    _preencher(ana, cenario.base, [1])
    html = _html(_get(client, ana, 2))  # p5 = escolha única opcional em rádios
    arvore = _verificar_grupo_exclusivo(html, "p5", obrigatoria=False)
    remover = [anc for a, anc in arvore.inputs if a.get("name") == "p5-remover"]
    assert remover and not any(a.get("role") == "radiogroup" for a in remover[0])


def test_escolha_multipla_e_lista_sem_radiogroup(client, cenario, ana):
    _preencher(ana, cenario.base, [1])
    html = _html(_get(client, ana, 2))
    assert 'id="p7-enunciado"' not in html  # p7 = lista suspensa: sem mudança
    _preencher(ana, cenario.base, [2, 3, 6])
    arvore = _estrutura(_html(_get(client, ana, 8)))
    caixas = [anc for a, anc in arvore.inputs if a.get("name") == "p7"]  # múltipla
    assert caixas and not any(a.get("role") == "radiogroup" for anc in caixas for a in anc)


# --- 014 US5: título principal da Seção e "Você está respondendo sobre:" (FR-023 a FR-025) --


def test_titulo_principal_e_o_da_secao_em_todo_o_percurso(client, cenario, ana):
    titulos = {
        1: "Termos e condições", 2: "Informações Pessoais", 3: "Informações do curso",
        6: "Graduação", 8: "Avaliação", 10: "Egresso que não trabalha", 11: "Estudo",
    }  # fmt: skip
    feitas = []
    for posicao, titulo in titulos.items():
        _preencher(ana, cenario.base, feitas)
        html = _html(_get(client, ana, posicao))
        assert re.findall(r"<h1>\s*(.*?)\s*</h1>", html) == [titulo], posicao
        assert not re.search(rf"<h2[^>]*>\s*{re.escape(titulo)}\s*</h2>", html)
        assert "<h1>Egresso Ifes</h1>" not in html
        feitas.append(posicao)


def test_contexto_diz_sobre_qual_formacao_se_responde(client, cenario, ana):
    texto = ci.texto_visivel(_get(client, ana, 1))
    assert "Você está respondendo sobre: Tecnologia em Análise e Desenvolvimento de Sistemas" in (
        texto
    )
    assert "Sobre a sua formação" not in texto

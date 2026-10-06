"""Jornada com menos esforço (Feature 023; spec FR-001 a FR-036).

Por requisição, sem navegador. Os testes conhecem Q1…Q54 pela `Baseline`; a interface não.
Ordem: envio pendente (US1), próxima formação (US2), parte e retomada (US3), complemento
(US4), não confirmação (US5), densidade (US6), conclusão (US7), entrada e declaração (US8),
fronteiras.
"""

import re
from datetime import timedelta

import pytest
from django.contrib.sessions.models import Session
from django.test import Client

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.acesso import mensagens as mensagens_acesso
from trajetoria.acesso import pendente
from trajetoria.interface import mensagens
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

ANA, MARIA, CARLA = "SIM-P-0001", "SIM-P-0003", "SIM-P-0010"
_ESCOLHAS = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Sim"}


def _url(pk, posicao, consulta=""):
    return f"/participacoes/{pk}/secoes/{posicao}/{consulta}"


def _na_secao(client, cenario, posicao, pessoa=ANA, formacao=None):
    """A Pessoa entra, inicia e tem as Seções anteriores do percurso respondidas."""
    resposta = ci.iniciar(client, cenario.pessoa(pessoa), formacao)
    participacao = Participacao.objects.get(pk=ci.participacao_de(resposta))
    percurso = c.secoes_esperadas("Sim", "Graduação", "Sim", "Sim")
    anteriores = [p for p in percurso if p < posicao]
    if anteriores:
        c.preencher(participacao, cenario.base, anteriores, _ESCOLHAS)
    return participacao


def _completa(cenario, posicao):
    return ci.dados_validos(
        ci.secao_do_conteudo(cenario.base.versao, posicao),
        ci.escolhas_por_id(cenario.base, _ESCOLHAS),
    )


def _expirar(settings, relogio):
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=1)
    relogio.agora += timedelta(seconds=61)


def _respostas(participacao):
    return len(c.retrato(participacao)["respostas"])


# --- US1: envio pendente (FR-001 a FR-009) -----------------------------------------------------


def test_tela_com_sessao_expirada_vai_a_entrada_com_aviso(client, cenario, settings, relogio):
    ci.entrar_como(client, cenario.pessoa(ANA))
    _expirar(settings, relogio)
    assert client.get("/formacoes/")["Location"] == "/acesso/?aviso=sessao"
    texto = ci.texto_visivel(client.get("/acesso/?aviso=sessao"))
    assert mensagens_acesso.SESSAO_ENCERRADA in texto
    assert mensagens_acesso.ENVIO_GUARDADO not in texto


def test_sem_sessao_anterior_a_entrada_fica_como_antes(cenario):
    anonimo = Client()
    assert anonimo.get("/formacoes/")["Location"] == "/acesso/"
    assert anonimo.get("/minha-trajetoria/")["Location"] == "/acesso/"
    assert anonimo.get("/meu-email/")["Location"] == "/acesso/"
    assert anonimo.get("/declaracao/")["Location"] == "/acesso/"
    assert mensagens_acesso.SESSAO_ENCERRADA not in ci.texto_visivel(anonimo.get("/acesso/"))


def test_aviso_de_lista_fechada(cenario):
    texto = ci.texto_visivel(Client().get("/acesso/?aviso=qualquer"))
    assert mensagens_acesso.SESSAO_ENCERRADA not in texto
    assert mensagens_acesso.SELO_VENCIDO not in texto


def test_envio_expirado_e_guardado_e_restaurado_sem_gravar(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    antes = _respostas(ana)
    _expirar(settings, relogio)
    enviado = {"p1": "2", "p2": "25", "p3": "3", "depois": "sair"}
    resposta = client.post(_url(ana.pk, 2), enviado)
    assert resposta["Location"] == "/acesso/?aviso=sessao"
    assert _respostas(ana) == antes
    texto = ci.texto_visivel(client.get(resposta["Location"]))
    assert mensagens_acesso.SESSAO_ENCERRADA in texto
    assert mensagens_acesso.ENVIO_GUARDADO in texto
    # Nova confirmação da mesma Pessoa: formações → Participação → a Seção, restaurada.
    ci.entrar_como(client, cenario.pessoa(ANA))
    assert client.get("/formacoes/")["Location"] == f"/participacoes/{ana.pk}/"
    assert client.get(f"/participacoes/{ana.pk}/")["Location"] == _url(ana.pk, 2)
    tela = client.get(_url(ana.pk, 2))
    html = tela.content.decode()
    assert tela.status_code == 200 and mensagens.RECUPERADO in ci.texto_visivel(tela)
    assert re.search(r'id="p1-o2"[^>]*checked', html)
    assert 'value="25"' in html
    assert 'class="pergunta com-erro' not in html and '<div class="resumo-erros' not in html
    assert _respostas(ana) == antes  # nada gravado, nem a intenção de sair foi executada
    # Já apresentado: as outras telas não prendem a pessoa num laço.
    assert client.get("/formacoes/").status_code == 200
    # O envio de verdade grava pela 005 e encerra o envio pendente.
    assert client.post(_url(ana.pk, 2), _completa(cenario, 2)).status_code == 302
    assert _respostas(ana) > antes
    assert pendente.CHAVE not in client.session


def test_confirmacao_de_outra_pessoa_descarta(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    client.post(_url(ana.pk, 2), {"p1": "2"})
    chave = client.session[pendente.CHAVE]
    ci.entrar_como(client, cenario.pessoa(CARLA))
    assert client.get("/formacoes/").status_code == 200
    assert pendente.CHAVE not in client.session
    assert not Session.objects.filter(session_key=chave).exists()


def test_secao_fora_do_percurso_descarta(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    client.post(_url(ana.pk, 9), {"p1": "1"})  # Seção ainda não alcançada
    ci.entrar_como(client, cenario.pessoa(ANA))
    assert client.get(f"/participacoes/{ana.pk}/")["Location"] == _url(ana.pk, 9)
    assert client.get(_url(ana.pk, 9))["Location"] == _url(ana.pk, 2, "?aviso=percurso")
    assert pendente.CHAVE not in client.session


def test_envio_pendente_vencido_nao_e_usado(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    client.post(_url(ana.pk, 2), {"p1": "2"})
    relogio.agora += pendente.VALIDADE
    texto = ci.texto_visivel(client.get("/acesso/?aviso=sessao"))
    assert mensagens_acesso.ENVIO_GUARDADO not in texto
    ci.entrar_como(client, cenario.pessoa(ANA))
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=30)
    assert client.get("/formacoes/").status_code == 200
    assert mensagens.RECUPERADO not in ci.texto_visivel(client.get(_url(ana.pk, 2)))


def test_sair_descarta(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    client.post(_url(ana.pk, 2), {"p1": "2"})
    chave = client.session[pendente.CHAVE]
    client.post("/acesso/sair/")
    assert not Session.objects.filter(session_key=chave).exists()


def test_declarante_descarta_envio_de_outro_sujeito(client, cenario, settings, relogio):
    from tests.declaracao.construcao import CPF, DATA
    from trajetoria.declaracao.selo import selar_transito

    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    client.post(_url(ana.pk, 2), {"p1": "2"})
    assert pendente.CHAVE in client.session
    client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    assert pendente.CHAVE not in client.session


def test_declarante_recupera_pela_lista(client, settings, relogio):
    from tests.declaracao.construcao import CPF, DADOS, DATA
    from trajetoria.declaracao.selo import selar_transito

    c.campanha_aberta(c.instrumento().versao)
    x = c.conclusao()
    x.nivel = "Técnico"
    x.save()
    transito = selar_transito(CPF, DATA)
    client.post("/declaracao/", {"selo": transito})
    confirmacao = client.post("/declaracao/nova/", {"selo": transito, **DADOS}).content.decode()
    inicio = re.search(r'action="/declaracao/comecar/">.*?name="selo" value="([^"]+)"',
                       confirmacao, re.S)[1]  # fmt: skip
    participacao = client.post("/declaracao/comecar/", {"selo": inicio})["Location"]
    _expirar(settings, relogio)
    assert client.post(participacao + "secoes/1/", {"p1": "1", "p4": "40"})["Location"] == (
        "/acesso/?aviso=sessao"
    )
    client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    assert pendente.CHAVE in client.session  # do próprio par: preservado
    assert client.get(participacao)["Location"] == participacao + "secoes/1/"
    tela = client.get(participacao + "secoes/1/")
    assert mensagens.RECUPERADO in ci.texto_visivel(tela)
    assert 'value="40"' in tela.content.decode()


def test_envio_acima_dos_limites_nao_e_guardado(client, cenario, settings, relogio):
    ana = _na_secao(client, cenario, 2)
    _expirar(settings, relogio)
    enorme = {f"p{n}": "x" * pendente.LIMITE_VALOR for n in range(1, 30)}
    assert client.post(_url(ana.pk, 2), enorme)["Location"] == "/acesso/?aviso=sessao"
    assert pendente.CHAVE not in client.session
    texto = ci.texto_visivel(client.get("/acesso/?aviso=sessao"))
    assert mensagens_acesso.ENVIO_GUARDADO not in texto


# --- US2: próxima formação (FR-011, FR-012, FR-028) ------------------------------------------


def _concluir_por_q1_nao(client, participacao):
    client.post(_url(participacao.pk, 1), {"p1": "2"})  # Q1 = "Não" → finalização
    resposta = client.post(f"/participacoes/{participacao.pk}/concluir/")
    return client.get(resposta["Location"])


def test_proxima_formacao_na_confirmacao(client, cenario):
    maria = cenario.pessoa(MARIA)
    primeira, segunda = maria.conclusoes.order_by("ano_conclusao", "id")
    p = _na_secao(client, cenario, 1, pessoa=MARIA, formacao=primeira)
    tela = _concluir_por_q1_nao(client, p)
    html = tela.content.decode()
    texto = ci.texto_visivel(tela)
    assert mensagens.PROXIMA_FORMACAO in texto
    assert "Responder sobre esta formação" in texto
    assert f'name="formacao" value="{segunda.pk}"' in html
    assert html.index("Responder sobre esta formação") < html.index("Ver minha trajetória")
    assert "Ver todas as suas formações" not in texto
    # Um toque: a entrada da 007 abre a segunda formação.
    entrada = client.post("/formacoes/entrar/", {"formacao": str(segunda.pk)})
    assert entrada.status_code == 302
    assert Participacao.objects.get(pk=ci.participacao_de(entrada)).conclusao == segunda


def test_sem_outra_formacao_a_confirmacao_fica_como_antes(client, cenario):
    p = _na_secao(client, cenario, 1)
    texto = ci.texto_visivel(_concluir_por_q1_nao(client, p))
    assert mensagens.PROXIMA_FORMACAO not in texto and "Ver minha trajetória" in texto


# --- US3: parte, máximo e retomada (FR-013 a FR-017) -----------------------------------------


def test_parte_e_maximo_nas_secoes(client, cenario):
    ana = _na_secao(client, cenario, 1)
    assert "Parte 1 · faltam no máximo 8 partes" in ci.texto_visivel(client.get(_url(ana.pk, 1)))
    ana13 = _na_secao(client, cenario, 13)
    tela = client.get(_url(ana13.pk, 13))
    texto = ci.texto_visivel(tela)
    assert "Parte 9 · última parte" in texto
    assert re.search(r"<title>Parte 9 — ", tela.content.decode())
    assert "Seção 13" not in texto


def test_parte_anterior_salva_so_com_resposta(client, cenario):
    ana = _na_secao(client, cenario, 2)
    seguinte = client.post(_url(ana.pk, 2), _completa(cenario, 2))
    assert seguinte["Location"] == _url(ana.pk, 3, "?aviso=anterior")
    assert "Parte anterior salva." in ci.texto_visivel(client.get(seguinte["Location"]))
    # Aviso fora da lista fechada é ignorado.
    assert "Parte anterior salva." not in ci.texto_visivel(
        client.get(_url(ana.pk, 3, "?aviso=outro"))
    )


def test_formacoes_dizem_onde_parou(client, cenario):
    ana = _na_secao(client, cenario, 2)
    client.post(_url(ana.pk, 2), {**_completa(cenario, 2), "depois": "sair"})
    texto = ci.texto_visivel(client.get("/formacoes/"))
    assert "Você parou em «Informações do curso» · faltam no máximo 6 partes." in texto
    c.preencher(ana, cenario.base, c.secoes_esperadas("Sim", "Graduação", "Sim", "Sim"),
                _ESCOLHAS)  # fmt: skip
    assert "Falta só concluir." in ci.texto_visivel(client.get("/formacoes/"))


def test_revisao_da_conclusao_usa_parte(client, cenario):
    ana = _na_secao(client, cenario, 14)  # todas as Seções do percurso respondidas
    texto = ci.texto_visivel(client.get(f"/participacoes/{ana.pk}/concluir/"))
    assert "Parte 9" in texto and "Seção 13" not in texto


# --- US4: complemento (FR-018 a FR-020) --------------------------------------------------------


def test_complemento_marcado_e_rotulo(client, cenario):
    ana = _na_secao(client, cenario, 8)
    html = client.get(_url(ana.pk, 8)).content.decode()
    q26 = html[html.index('id="p7"'): html.index('id="p8"')]
    assert 'class="opcao opcao-com-complemento"' in q26
    assert 'class="complemento"' in q26  # sem texto: pode ser ocultado
    assert "Descreva o que se encaixa em «Outro»" in q26
    assert "@supports selector(:has(*))" in html


def test_complemento_sem_opcao_recusa_com_campo_visivel(client, cenario):
    ana = _na_secao(client, cenario, 8)
    antes = _respostas(ana)
    dados = {**_completa(cenario, 8), "p7-complemento": "Pôster"}
    tela = client.post(_url(ana.pk, 8), dados)
    html = tela.content.decode()
    assert tela.status_code == 200 and _respostas(ana) == antes
    assert "complemento sempre-visivel" in html and 'value="Pôster"' in html
    assert mensagens.COMPLEMENTO_SEM_OPCAO.format(opcao="Outro") in ci.texto_visivel(tela)


def test_regra_de_ocultacao_so_na_jornada():
    from pathlib import Path

    pasta = Path(__file__).resolve().parents[2] / "trajetoria" / "interface" / "templates"
    assert ":has(*)" in (pasta / "interface" / "jornada.css").read_text()
    # A prévia do editor inclui só estilo.css: lá o complemento continua sempre visível.
    estilo = (pasta / "interface" / "estilo.css").read_text()
    assert ".complemento:not(.sempre-visivel)" not in estilo


# --- US5: não confirmação em dois passos (FR-021, FR-022) --------------------------------------


def _nao_confirmada(client, cpf, data):
    resposta = client.post("/acesso/", {"cpf": cpf, "data_nascimento": data})
    assert resposta.status_code == 200
    return resposta


def _sem_tokens(html):
    return re.sub(r'value="[^"]{20,}"', "", html)


def test_nao_confirmada_em_dois_passos_igual_entre_causas(client, cenario):
    from tests.acesso.construcao import ANA, preparar_material

    preparar_material("SIM-P-0001")
    inexistente = _nao_confirmada(Client(), "000.000.009-49", "12/04/1998")
    divergente = _nao_confirmada(Client(), ANA.cpf, "12/04/1999")
    html = inexistente.content.decode()
    assert '<ol class="passos">' in html
    assert html.index("Conferir os dados") < html.index("Informar minha formação")
    texto = ci.texto_visivel(inexistente)
    assert mensagens_acesso.PASSO_CONFERIR in texto and mensagens_acesso.PASSO_INFORMAR in texto

    def aviso(resposta):
        bloco = re.search(r'<div class="aviso" role="status".*?</ol></div>', resposta.content
                          .decode(), re.S)[0]  # fmt: skip
        return re.sub(r'value="[^"]*"', "", bloco)

    # Mesmo conteúdo para causas diferentes (018 FR-032), a menos do selo cifrado.
    assert aviso(inexistente) == aviso(divergente)


def test_falha_nao_oferece_continuar_de_sessao_anterior(client, cenario):
    ci.entrar_como(client, cenario.pessoa(ANA))
    assert "Continuar para suas formações" in ci.texto_visivel(client.get("/acesso/"))
    falha = client.post("/acesso/", {"cpf": "000.000.009-49", "data_nascimento": "12/04/1998"})
    assert "Continuar para suas formações" not in ci.texto_visivel(falha)


# --- US6: densidade (FR-010, FR-023 a FR-026) ----------------------------------------------------


def test_opcional_e_obrigatoria(client, cenario):
    ana = _na_secao(client, cenario, 2)
    html = client.get(_url(ana.pk, 2)).content.decode()
    assert html.count('<span class="visualmente-oculto"> (obrigatória)</span>') == 7
    assert html.count('<span class="opcional">(opcional)</span>') == 1  # Q6
    assert "(obrigatória)</span>" not in html.replace(
        '<span class="visualmente-oculto"> (obrigatória)</span>', ""
    )


def test_duas_opcoes_curtas_lado_a_lado(client, cenario):
    ana = _na_secao(client, cenario, 2)
    html = client.get(_url(ana.pk, 2)).content.decode()
    q5 = html[html.index('id="p4"'): html.index('id="p5"')]  # Sim/Não
    q2 = html[html.index('id="p1"'): html.index('id="p2"')]  # seis Opções
    assert "opcoes-lado-a-lado" in q5 and "opcoes-lado-a-lado" not in q2


def test_abertura_recolhida_e_termos_visiveis(client, cenario):
    ana = _na_secao(client, cenario, 1)
    html = client.get(_url(ana.pk, 1)).content.decode()
    inicio = html.index('<details class="abertura"><summary>Sobre esta pesquisa</summary>')
    fim = html.index("</details>")
    assert inicio < html.index("Prezado(a) egresso(a)") < fim
    assert html.index("Para participar deste estudo") > fim


def test_ponto_do_meio_so_em_secoes_longas(client, cenario):
    ana8 = _na_secao(client, cenario, 8)
    html = client.get(_url(ana8.pk, 8)).content.decode()
    meio = html.index('class="ponto-do-meio"')
    assert html.index('id="p7"') < meio < html.index('id="p8"')  # 14 Perguntas → depois da 7ª
    assert html.index('<button type="submit" disabled hidden>') < meio
    assert '<button type="submit" name="depois" value="sair" class="secundario">' in html[meio:]
    ana2 = _na_secao(client, cenario, 2)
    assert 'class="ponto-do-meio"' not in client.get(_url(ana2.pk, 2)).content.decode()


def test_sair_sem_salvar_so_com_erro_de_forma(client, cenario):
    ana = _na_secao(client, cenario, 8)
    assert "Sair sem salvar esta seção" not in client.get(_url(ana.pk, 8)).content.decode()
    erro = client.post(_url(ana.pk, 8), {**_completa(cenario, 8), "p7-complemento": "Pôster"})
    assert "Sair sem salvar esta seção" in erro.content.decode()
    pendencia = client.post(_url(ana.pk, 8), {"p1": "1"})
    assert "Sair sem salvar esta seção" not in client.get(pendencia["Location"]).content.decode()


# --- US7: conclusão (FR-027) -----------------------------------------------------------------


def test_ordem_da_tela_de_conclusao(client, cenario):
    ana = _na_secao(client, cenario, 14)
    html = client.get(f"/participacoes/{ana.pk}/concluir/").content.decode()
    ordem = [
        html.index("não poderá ser alterada"),
        html.index("Concluir pesquisa</button>"),
        html.index("volte a uma das partes"),
        html.index("Sobre a sua formação"),
    ]
    assert ordem == sorted(ordem)


# --- US8: entrada e declaração (FR-029 a FR-032) -----------------------------------------------


def test_dica_da_data(cenario):
    assert "Só os números, por exemplo 05031994" in ci.texto_visivel(Client().get("/acesso/"))


def test_selo_invalido_volta_com_aviso(cenario):
    anonimo = Client()
    for rota in ("/declaracao/", "/declaracao/nova/", "/declaracao/comecar/"):
        assert anonimo.post(rota, {"selo": "adulterado"})["Location"] == "/acesso/?aviso=selo"
    texto = ci.texto_visivel(anonimo.get("/acesso/?aviso=selo"))
    assert mensagens_acesso.SELO_VENCIDO in texto


def test_declaracao_nome_niveis_confirmacao_e_corrigir(client):
    from tests.declaracao.construcao import CPF, DADOS, DATA
    from trajetoria.declaracao.selo import selar_transito

    c.campanha_aberta(c.instrumento().versao)
    x = c.conclusao()
    x.nivel = "Técnico"
    x.save()
    transito = selar_transito(CPF, DATA)
    formulario = client.post("/declaracao/", {"selo": transito}).content.decode()
    assert 'autocomplete="name"' in formulario
    assert '<fieldset class="campo campo-opcoes" id="nivel"' in formulario
    assert 'type="radio" name="nivel"' in formulario
    confirmacao = client.post("/declaracao/nova/", {"selo": transito, **DADOS})
    html = confirmacao.content.decode()
    linha = f"{DADOS['curso']} · {DADOS['unidade']} · {DADOS['nivel']} · {DADOS['ano_conclusao']}"
    assert linha in html
    assert '<button type="submit" class="primario">Começar</button>' in html
    corrigir = re.search(r'name="selo" value="([^"]+)"><input type="hidden" name="corrigir"', html)
    assert corrigir and corrigir[1] == transito
    volta = client.post(
        "/declaracao/nova/", {"selo": transito, "corrigir": "1", **DADOS}
    ).content.decode()
    assert f'value="{DADOS["curso"]}"' in volta and "Confira os campos informados" not in volta


# --- Fronteiras (FR-033 a FR-035) -------------------------------------------------------------


def test_sem_javascript_nem_armazenamento_local():
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2] / "trajetoria"
    for pasta in ("interface", "acesso", "declaracao"):
        for arquivo in (raiz / pasta / "templates").rglob("*"):
            if arquivo.is_file():
                texto = arquivo.read_text()
                assert "<script" not in texto, arquivo
                assert "localStorage" not in texto and "sessionStorage" not in texto, arquivo

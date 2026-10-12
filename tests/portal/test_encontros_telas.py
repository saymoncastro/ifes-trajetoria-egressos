"""Telas dos encontros (031, incremento 1; T014, T016, T018–T021, T023, T029).

O foco é a autorização: quem vê o conteúdo, quem vê o link (fora do HTML de quem não pode;
SC-002) e quem modera. Os textos vêm de `encontros/mensagens.py`.
"""

from datetime import timedelta

import pytest
from django.test import Client

from tests.editor.construcao_editor import atuar_como
from tests.participacao import construcao as c
from tests.portal import construcao as cp
from tests.portal import construcao_encontros as ce
from tests.portal import construcao_oportunidades as co
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo
from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros import operacoes
from trajetoria.portal.encontros.mensagens import VERSAO_DA_CIENCIA, VERSAO_DO_TERMO
from trajetoria.portal.models import Confirmacao, Encontro

pytestmark = pytest.mark.django_db

LICENCIATURA = "Licenciatura em Química"


@pytest.fixture
def pessoas(cenario):
    return {k: cenario.pessoa(v) for k, v in (
        ("ana", "SIM-P-0001"), ("bruno", "SIM-P-0002"), ("maria", "SIM-P-0003"),
        ("diego", "SIM-P-0004"),
    )}


@pytest.fixture
def encontro(pessoas):
    """Publicado pela CPAEG, para quem concluiu a Licenciatura em Química (Diego)."""
    return ce.publicado(pessoas["maria"], publico_cursos=[LICENCIATURA])


def _como(pessoa) -> Client:
    cliente = Client()
    cp.entrar(cliente, pessoa)
    return cliente


def _html(cliente, url) -> tuple[int, str]:
    resposta = cliente.get(url)
    return resposta.status_code, resposta.content.decode()


def _pagina(encontro) -> str:
    return f"/encontros/{encontro.pk}/"


# --- Descoberta (FR-011 a FR-014) -----------------------------------------------------------------

def test_lista_por_formacao_com_explicacao_e_rotulos(pessoas, encontro):
    aberto = ce.publicado(pessoas["bruno"], titulo="Aberto a todos")
    outro = ce.publicado(pessoas["bruno"], titulo="Só para a Serra", publico_unidades=["Serra"])
    co.publicada("Semana da Química", categoria="eventos")
    status, html = _html(_como(pessoas["diego"]), "/encontros/")
    assert status == 200 and html.count("<h1") == 1
    assert ce.TITULO in html and "Aberto a todos" in html and "Só para a Serra" not in html
    assert "Aparece porque você concluiu Licenciatura em Química" in html
    assert m.ABERTO_A_TODOS in html
    assert m.SELO_F in html and m.SELO_A in html and "Semana da Química" in html
    assert ce.LINK not in html  # FR-021: a lista nunca traz o link
    assert str(outro.pk) not in html and str(aberto.pk) in html


def test_lista_vazia(pessoas):
    status, html = _html(_como(pessoas["diego"]), "/encontros/")
    assert m.VAZIO_F in html and m.VAZIO_A in html and m.PROPOR in html


def test_sem_conclusao_nao_ha_encontros(pessoas, encontro):
    sem = _como(cp.pessoa_sem_conclusao())
    assert sem.get("/encontros/").status_code == 404
    assert sem.get("/encontros/propor/").status_code == 404
    status, html = _html(sem, _pagina(encontro))
    assert status == 200 and m.SO_PARA_EGRESSOS in html and ce.TITULO not in html


def test_sem_sessao_lista_vai_a_entrada_e_pagina_e_neutra(encontro):
    assert Client().get("/encontros/")["Location"] == "/entrar/"
    status, html = _html(Client(), _pagina(encontro))
    assert status == 200 and m.NEUTRA_ACAO in html
    for privado in (ce.TITULO, "Maria E.", ce.LINK, "Cefor"):
        assert privado not in html  # FR-022


# --- Página, confirmação e link (FR-020 a FR-024a; SC-002) ---------------------------------------

def test_participante_confirma_ve_o_link_e_cancela(pessoas, encontro):
    diego = _como(pessoas["diego"])
    status, html = _html(diego, _pagina(encontro))
    assert status == 200 and ce.LINK not in html  # antes de confirmar
    for frase in m.CIENCIA:
        assert frase in html
    resposta = diego.post(f"{_pagina(encontro)}participar/", {"versao": VERSAO_DA_CIENCIA})
    assert resposta.status_code == 303
    status, html = _html(diego, resposta["Location"])
    assert ce.LINK in html and m.VOCE_VAI in html and m.AVISOS["confirmado"] in html
    assert diego.post(f"{_pagina(encontro)}cancelar-participacao/").status_code == 303
    status, html = _html(diego, _pagina(encontro))
    assert ce.LINK not in html and m.VOU_PARTICIPAR in html


def test_fora_do_publico_abre_pelo_endereco_e_pode_confirmar(pessoas, encontro):
    ana = _como(pessoas["ana"])
    status, html = _html(ana, _pagina(encontro))
    assert status == 200 and m.VOCE_RECEBEU in html  # H-3108
    assert ana.post(f"{_pagina(encontro)}participar/",
                    {"versao": VERSAO_DA_CIENCIA}).status_code == 303
    assert ce.LINK in _html(ana, _pagina(encontro))[1]


def test_organizador_ve_contagem_sem_nomes_e_o_link(pessoas, encontro):
    ce.confirmar(pessoas["diego"], encontro)
    ce.confirmar(pessoas["ana"], encontro)
    for url in (_pagina(encontro), "/encontros/seus/"):
        status, html = _html(_como(pessoas["maria"]), url)
        assert "2 pessoas confirmaram" in html
        assert "Diego" not in html and "Ana Exemplo" not in html
    assert ce.LINK in _html(_como(pessoas["maria"]), _pagina(encontro))[1]


@pytest.mark.parametrize("acao", ["recusar", "retirar", "cancelar", "encerrar", "analise"])
def test_link_ausente_fora_de_publicado(pessoas, acao, relogio):
    maria, diego = pessoas["maria"], pessoas["diego"]
    if acao in ("recusar", "analise"):
        encontro = ce.propor(maria, publico_cursos=[LICENCIATURA])
    else:
        encontro = ce.publicado(maria, publico_cursos=[LICENCIATURA])
        ce.confirmar(diego, encontro)
    depois = c.NO_PERIODO + timedelta(hours=1)
    if acao == "recusar":
        operacoes.recusar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG,
                          motivo="comercial", complemento="", agora=depois)
    elif acao == "retirar":
        operacoes.retirar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG,
                          motivo="link", complemento="", agora=depois)
    elif acao == "cancelar":
        operacoes.cancelar(maria, encontro.pk, agora=depois)
    elif acao == "encerrar":
        relogio.agora = encontro.termino
    for pessoa in (maria, diego, pessoas["ana"]):
        status, html = _html(_como(pessoa), _pagina(encontro))
        assert ce.LINK not in html, (acao, pessoa)


@pytest.mark.parametrize("acao", ["analise", "retirar"])
def test_conteudo_so_para_organizador_fora_de_publicado(pessoas, acao):
    maria = pessoas["maria"]
    if acao == "analise":
        encontro = ce.propor(maria, publico_cursos=[LICENCIATURA])
    else:
        encontro = ce.publicado(maria, publico_cursos=[LICENCIATURA])
        ce.confirmar(pessoas["diego"], encontro)
        operacoes.retirar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG,
                          motivo="link", complemento="", agora=c.NO_PERIODO)
    assert ce.TITULO in _html(_como(maria), _pagina(encontro))[1]
    status, html = _html(_como(pessoas["diego"]), _pagina(encontro))
    assert ce.TITULO not in html and "Maria E." not in html
    assert status == (404 if acao == "analise" else 200)
    if acao == "retirar":
        assert m.RETIRADO in html


def test_encerrado_ou_cancelado_mostra_conteudo_so_a_quem_tinha_confirmado(pessoas, relogio):
    maria = pessoas["maria"]
    encontro = ce.publicado(maria, publico_cursos=[LICENCIATURA])
    ce.confirmar(pessoas["diego"], encontro)
    relogio.agora = encontro.termino
    assert ce.TITULO in _html(_como(pessoas["diego"]), _pagina(encontro))[1]
    html = _html(_como(pessoas["ana"]), _pagina(encontro))[1]
    assert ce.TITULO not in html and m.ENCERRADO in html


def test_confirmar_em_encontro_retirado_e_conflito(pessoas, encontro):
    diego = _como(pessoas["diego"])
    operacoes.retirar(encontro.pk, operador=ce.OPERADOR_A, escopo=ce.CPAEG, motivo="link",
                      complemento="", agora=c.NO_PERIODO)
    resposta = diego.post(f"{_pagina(encontro)}participar/", {"versao": VERSAO_DA_CIENCIA})
    assert resposta.status_code == 409 and not Confirmacao.objects.exists()


# --- Propor (FR-002 a FR-007) ---------------------------------------------------------------------

def test_propor_confira_e_envie(pessoas):
    maria = pessoas["maria"]
    origem = maria.conclusoes.first()
    cliente = _como(maria)
    dados = ce.formulario(origem, publico="formacoes", curso=[LICENCIATURA])
    status, html = _html(cliente, "/encontros/propor/")
    assert status == 200 and m.LEGENDA_PUBLICO in html and m.QUEM_ANALISA in html
    resposta = cliente.post("/encontros/propor/", dados)
    html = resposta.content.decode()
    assert resposta.status_code == 200 and m.CONFIRA in html and VERSAO_DO_TERMO in html
    assert m.QUEM_ANALISA_CPAEG in html and not Encontro.objects.exists()
    resposta = cliente.post("/encontros/propor/enviar/", {**dados, "versao": VERSAO_DO_TERMO})
    assert resposta.status_code == 303
    encontro = Encontro.objects.get()
    assert encontro.publico_cursos == [LICENCIATURA] and encontro.publicado_em is None
    html = cliente.get(resposta["Location"]).content.decode()
    assert m.ENVIADO in html and "Em análise pela CPAEG" in html


def test_publico_de_uma_unidade_vai_a_csaeg(pessoas):
    bruno = pessoas["bruno"]
    dados = ce.formulario(bruno.conclusoes.first(), publico="formacoes", unidade=["Vitória"])
    html = _como(bruno).post("/encontros/propor/", dados).content.decode()
    assert m.QUEM_ANALISA_UNIDADE.format(unidade="Vitória") in html


def test_erros_voltam_com_o_que_foi_digitado_sem_gravar(pessoas):
    maria = pessoas["maria"]
    dados = ce.formulario(maria.conclusoes.first(), titulo="", link="meet sem https",
                          publico="formacoes")
    resposta = _como(maria).post("/encontros/propor/", dados)
    html = resposta.content.decode()
    assert resposta.status_code == 422 and m.ERROS["resumo"] in html
    for chave in ("titulo", "link", "publico"):
        assert m.ERROS[chave] in html
    assert 'value="meet sem https"' in html and not Encontro.objects.exists()


def test_valor_de_publico_fora_dos_registrados_e_recusado(pessoas):
    maria = pessoas["maria"]
    dados = ce.formulario(maria.conclusoes.first(), publico="formacoes", curso=["Inventado"])
    assert _como(maria).post("/encontros/propor/", dados).status_code == 422


def test_limite_no_formulario(pessoas):
    maria = pessoas["maria"]
    for _ in range(3):
        ce.propor(maria)
    cliente = _como(maria)
    assert m.ERROS["limite"] in cliente.get("/encontros/propor/").content.decode()
    dados = ce.formulario(maria.conclusoes.first())
    resposta = cliente.post("/encontros/propor/enviar/", {**dados, "versao": VERSAO_DO_TERMO})
    assert resposta.status_code == 409 and Encontro.objects.count() == 3


def test_organizador_cancela(pessoas, encontro):
    maria = _como(pessoas["maria"])
    assert m.CANCELAR_ENCONTRO in maria.get(f"{_pagina(encontro)}cancelar/").content.decode()
    assert _como(pessoas["diego"]).get(f"{_pagina(encontro)}cancelar/").status_code == 404
    assert maria.post(f"{_pagina(encontro)}cancelar/").status_code == 303
    encontro.refresh_from_db()
    assert encontro.cancelado_em is not None


def test_seus_encontros_vazio(pessoas):
    assert m.SEUS_VAZIO in _como(pessoas["diego"]).get("/encontros/seus/").content.decode()


# --- Moderação (FR-015 a FR-019) ------------------------------------------------------------------

@pytest.fixture
def vinculos(cenario):
    registrar_vinculo(ce.OPERADOR_A, Papel.CPAEG)
    registrar_vinculo(ce.OPERADOR_B, Papel.CSAEG, "Vitória")


def _operador(identificador) -> Client:
    return atuar_como(Client(), identificador)


def test_sem_operador_vai_para_a_escolha(client, vinculos):
    assert client.get("/curadoria/encontros/")["Location"] == (
        "/demonstracao/operador/?destino=encontros")


def test_operador_sem_competencia_e_recusado(vinculos):
    resposta = _operador(ce.OPERADOR_C).get("/curadoria/encontros/")
    assert resposta.status_code == 403 and m.MODERACAO_RECUSA in resposta.content.decode()


def test_escopo_da_moderacao(pessoas, vinculos):
    vitoria = ce.propor(pessoas["bruno"], titulo="Só Vitória", publico_unidades=["Vitória"])
    geral = ce.propor(pessoas["maria"], titulo="Para todos")
    html_b = _operador(ce.OPERADOR_B).get("/curadoria/encontros/").content.decode()
    assert "Só Vitória" in html_b and "Para todos" not in html_b
    assert _operador(ce.OPERADOR_B).get(f"/curadoria/encontros/{geral.pk}/").status_code == 404
    html_a = _operador(ce.OPERADOR_A).get("/curadoria/encontros/").content.decode()
    assert "Só Vitória" in html_a and "Para todos" in html_a
    analise = _operador(ce.OPERADOR_B).get(f"/curadoria/encontros/{vitoria.pk}/")
    html = analise.content.decode()
    assert ce.LINK in html and "000.000" not in html and "Bruno Exemplo" not in html


def test_publicar_e_recusar_pelas_telas(pessoas, vinculos):
    publicar = ce.propor(pessoas["maria"], titulo="Para publicar")
    recusar = ce.propor(pessoas["maria"], titulo="Para recusar")
    cpaeg = _operador(ce.OPERADOR_A)
    assert cpaeg.post(f"/curadoria/encontros/{publicar.pk}/").status_code == 302
    sem_complemento = cpaeg.post(f"/curadoria/encontros/{recusar.pk}/recusar/",
                                 {"motivo": "outro", "complemento": ""})
    assert sem_complemento.status_code == 422
    assert cpaeg.post(f"/curadoria/encontros/{recusar.pk}/recusar/",
                      {"motivo": "comercial", "complemento": ""}).status_code == 302
    publicar.refresh_from_db()
    recusar.refresh_from_db()
    assert publicar.publicado_por == ce.OPERADOR_A and recusar.motivo == "comercial"
    # Já decidido: a mesma ação vira conflito, sem gravar.
    assert cpaeg.post(f"/curadoria/encontros/{publicar.pk}/").status_code == 409


def test_pagina_diz_quem_moderou(pessoas, vinculos):
    encontro = ce.propor(pessoas["bruno"], publico_unidades=["Vitória"])
    _operador(ce.OPERADOR_B).post(f"/curadoria/encontros/{encontro.pk}/")
    html = _html(_como(pessoas["bruno"]), _pagina(encontro))[1]
    assert "CSAEG Vitória" in html


# --- Navegação (H-3105) ---------------------------------------------------------------------------

def test_item_encontros_na_navegacao(pessoas, encontro):
    html = _html(_como(pessoas["diego"]), _pagina(encontro))[1]
    assert 'href="/encontros/" data-rotulo="Encontros" aria-current="page"' in html
    sem = _html(_como(cp.pessoa_sem_conclusao()), "/inicio/")[1]
    assert 'href="/encontros/"' not in sem

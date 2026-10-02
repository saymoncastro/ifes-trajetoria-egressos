"""Autorização institucional do editor (Feature 010; spec US3–US12; contracts/acesso-editor.md).

Segurança exaustiva sem produto cartesiano:

1. um teste **estrutural** garante que cada uma das 25 rotas declara uma das três regras e
   que toda escrita exige elaborar;
2. um POST (e GET) **não autorizado em cada uma das 17 escritas**, com o perfil mais próximo
   de autorizado (CSAEG), prova que nada é validado, chamado ou gravado;
3. os demais perfis são verificados numa rota representativa: o decorador é o mesmo em
   todas, garantido pelo item 1.

Operadores fictícios: A (CPAEG, a fixture `client`), B (CSAEG Vitória), C (sem vínculo).
"""

import inspect
import re
import uuid

import pytest
from django import forms
from django.test import Client

from tests.editor import construcao_editor as ce
from tests.editor.construcao_editor import A, B, C, atuar_como
from trajetoria.editor import mensagens, urls
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import desativar_vinculo, registrar_vinculo
from trajetoria.governanca.regras import (
    pode_consultar_publicado,
    pode_consultar_rascunho,
    pode_elaborar_instrumento,
)
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import EstadoVersao, Pesquisa

pytestmark = pytest.mark.django_db

LEITURAS = {
    "pesquisas", "pesquisa", "versao", "diagnostico", "previa", "previa_secao", "secao", "pergunta",
}  # fmt: skip
POR_ESTADO = ("versao", "previa", "previa_secao", "secao", "pergunta")
ESCOLHA = "/demonstracao/operador/"
CPAEG_ROTULO = "Comissão Própria de Acompanhamento do Egresso (CPAEG) — atuação institucional"
CSAEG_ROTULO = "Comissão Setorial de Acompanhamento de Egressos (CSAEG) — unidade Vitória"


def _nome(padrao) -> str:
    return padrao.callback.__name__


ESCRITAS = [p for p in urls.urlpatterns if _nome(p) not in LEITURAS]


def _caminho(padrao, versao) -> str:
    """O endereço da rota com os elementos da `versao` (Seção 1, Pergunta 1.1, sua 1ª Opção)."""
    pergunta = ce.pergunta(versao, 1, 1)
    ids = {
        "pesquisa": versao.pesquisa_id,
        "versao": versao.pk,
        "secao": ce.secao(versao, 1).pk,
        "pergunta": pergunta.pk,
        "opcao": pergunta.opcoes.first().pk,
    }
    rota = re.sub(r"<uuid:(\w+)>", lambda m: str(ids[m.group(1)]), str(padrao.pattern))
    return "/editor/" + re.sub(r"<int:\w+>", "1", rota)


def _rota(nome):
    return next(p for p in urls.urlpatterns if _nome(p) == nome)


def _recusa(resposta, texto):
    assert resposta.status_code == 403, resposta.status_code
    visivel = ce.texto_visivel(resposta)
    assert mensagens.RECUSA_TITULO in visivel and texto in visivel
    assert 'role="alert"' not in resposta.content.decode()


# --- 1. Estrutural (SC-001; FR-042) ---------------------------------------------------------


def test_toda_rota_declara_uma_das_tres_regras():
    assert len(urls.urlpatterns) == 25
    regras = (pode_consultar_publicado, pode_consultar_rascunho, pode_elaborar_instrumento)
    for padrao in urls.urlpatterns:
        assert getattr(padrao.callback, "exige", None) in regras, _nome(padrao)


def test_leituras_declaradas_e_escritas_exigem_elaborar():
    assert len(ESCRITAS) == 17
    # Toda leitura por `pode_consultar_publicado` é uma lista ou uma leitura por estado coberta
    # por `test_csaeg_nao_abre_rascunho_por_endereco_direto`: uma leitura nova força revisão.
    publicadas = {
        _nome(p) for p in urls.urlpatterns if p.callback.exige is pode_consultar_publicado
    }
    assert publicadas == {"pesquisas", "pesquisa", *POR_ESTADO}
    for padrao in urls.urlpatterns:
        exige = padrao.callback.exige
        if _nome(padrao) == "diagnostico":
            assert exige is pode_consultar_rascunho
        elif _nome(padrao) in LEITURAS:
            assert exige is pode_consultar_publicado, _nome(padrao)
        else:
            assert exige is pode_elaborar_instrumento, _nome(padrao)


# --- 2. Nenhuma escrita sem elaborar (SC-002; FR-039, FR-040) -------------------------------


@pytest.fixture
def proibido(copia, cliente_csaeg, monkeypatch):
    """Depois do arranjo: qualquer operação da 002 ou validação de formulário falha."""

    def falha(*args, **kwargs):
        raise AssertionError("uma recusa de acesso chamou operação ou validou formulário")

    for nome, objeto in vars(op).items():
        if inspect.isfunction(objeto) and objeto.__module__ == op.__name__:
            monkeypatch.setattr(op, nome, falha)
    monkeypatch.setattr(forms.BaseForm, "is_valid", falha)


INVALIDOS = {"nome": "", "designacao": "", "texto": "", "tipo": "x", "direcao": "x"}


@pytest.mark.parametrize("padrao", ESCRITAS, ids=_nome)
def test_csaeg_recusado_em_toda_escrita(padrao, copia, cliente_csaeg, proibido):
    caminho = _caminho(padrao, copia)
    antes = ce.retrato(copia), ce.contagens()
    for metodo in (cliente_csaeg.get, cliente_csaeg.post):
        _recusa(metodo(caminho, INVALIDOS), mensagens.RECUSA_ELABORACAO)
    assert (ce.retrato(copia), ce.contagens()) == antes


# --- 3. Perfis representativos (US4; FR-037, FR-045) ----------------------------------------


def test_sem_operador_leva_a_escolha_sem_ler_nem_gravar(
    cliente_nao_identificado, vinculo_cpaeg, copia
):
    # Com o modo ligado, só o cookie assinado identifica: parâmetro, cabeçalho e campo com o
    # identificador de um operador CPAEG ativo não identificam ninguém.
    c, cabecalho = cliente_nao_identificado, {"HTTP_X_OPERADOR": A}
    for resposta in (
        c.get(f"/editor/versoes/{copia.pk}/"),
        c.get(f"/editor/versoes/{copia.pk}/", {"operador": A}, **cabecalho),
        c.post("/editor/pesquisas/nova/", {"nome": "Indevida"}),
        c.post("/editor/pesquisas/nova/", {"nome": "Indevida", "operador": A}, **cabecalho),
    ):
        assert resposta.status_code == 302 and resposta["Location"] == ESCOLHA
    assert not Pesquisa.objects.filter(nome="Indevida").exists()


@pytest.mark.parametrize("perfil", ["cliente_sem_vinculo", "cliente_inativo"])
def test_sem_vinculo_ativo_e_recusado(perfil, request, copia):
    cliente = request.getfixturevalue(perfil)
    antes = ce.contagens()
    _recusa(cliente.get(f"/editor/versoes/{copia.pk}/"), mensagens.RECUSA_SEM_ATUACAO)
    _recusa(cliente.get("/editor/"), mensagens.RECUSA_SEM_ATUACAO)
    _recusa(cliente.post("/editor/pesquisas/nova/", {"nome": "X"}), mensagens.RECUSA_SEM_ATUACAO)
    assert ce.contagens() == antes


def test_recusa_precede_a_busca_do_elemento(cliente_sem_vinculo, client):
    caminho = f"/editor/versoes/{uuid.uuid4()}/"
    _recusa(cliente_sem_vinculo.get(caminho), mensagens.RECUSA_SEM_ATUACAO)
    assert client.get(caminho).status_code == 404


# --- CPAEG (US3) ----------------------------------------------------------------------------


def test_cpaeg_consulta_rascunho_e_publicada(client, copia, publicada):
    for versao in (copia, publicada):
        for nome in (*POR_ESTADO, "pesquisa"):
            assert client.get(_caminho(_rota(nome), versao)).status_code == 200, nome
    assert client.get(f"/editor/versoes/{copia.pk}/diagnostico/").status_code == 200
    texto = ce.texto_visivel(client.get("/editor/"))
    assert f"Atuação: {CPAEG_ROTULO}" in texto and "Trocar operador fictício" in texto
    assert mensagens.BANNER in texto and "Criar Pesquisa" in texto


def test_cpaeg_elabora(client, copia, publicada):
    assert client.post("/editor/pesquisas/nova/", {"nome": "Fictícia 010"}).status_code == 302
    resposta = client.post(
        f"/editor/versoes/{publicada.pk}/nova-a-partir/", {"designacao": "Nova 010"}
    )
    assert resposta.status_code == 302
    antes = copia.secoes.count()
    assert client.post(f"/editor/versoes/{copia.pk}/secoes/nova/", {}).status_code == 302
    assert copia.secoes.count() == antes + 1


# --- CSAEG (US6) ----------------------------------------------------------------------------


def test_csaeg_ve_listas_so_com_publicadas(cliente_csaeg, baseline, copia, publicada):
    texto = ce.texto_visivel(cliente_csaeg.get("/editor/"))
    assert "1 Versão" in texto and mensagens.SOMENTE_PUBLICADAS in texto
    assert "Criar Pesquisa" not in texto and f"Atuação: {CSAEG_ROTULO}" in texto
    resposta = cliente_csaeg.get(f"/editor/pesquisas/{publicada.pesquisa_id}/")
    texto, html = ce.texto_visivel(resposta), resposta.content.decode()
    assert publicada.designacao in texto and mensagens.SOMENTE_PUBLICADAS in texto
    assert "Rascunho" not in texto  # nenhum rascunho listado
    # A origem da publicada é só um dado dela (texto), nunca um rascunho listado ou ligado.
    assert (
        f"/editor/versoes/{copia.pk}/" not in html and f"/editor/versoes/{baseline.pk}/" not in html
    )
    assert "Criar Versão em rascunho" not in texto and "Criar nova Versão" not in texto


def test_csaeg_pesquisa_sem_publicada(cliente_csaeg, versao):
    texto = ce.texto_visivel(cliente_csaeg.get(f"/editor/pesquisas/{versao.pesquisa_id}/"))
    assert "nenhuma Versão publicada" in texto and versao.designacao not in texto
    assert "nenhuma Versão publicada" in ce.texto_visivel(cliente_csaeg.get("/editor/"))


def test_csaeg_consulta_publicada_sem_acoes(cliente_csaeg, publicada):
    for nome in POR_ESTADO:
        resposta = cliente_csaeg.get(_caminho(_rota(nome), publicada))
        assert resposta.status_code == 200, nome
        texto = ce.texto_visivel(resposta)
        assert "Criar nova Versão" not in texto and "Editar" not in texto, nome


def test_csaeg_nao_abre_rascunho_por_endereco_direto(cliente_csaeg, copia):
    for nome in (*POR_ESTADO, "diagnostico"):
        _recusa(cliente_csaeg.get(_caminho(_rota(nome), copia)), mensagens.RECUSA_RASCUNHO)


def test_unidade_nao_muda_o_que_se_consulta(cliente_csaeg, publicada):
    registrar_vinculo(C, Papel.CSAEG, "Serra")
    serra = atuar_como(Client(), C)
    caminho = f"/editor/versoes/{publicada.pk}/"
    assert serra.get(caminho).status_code == cliente_csaeg.get(caminho).status_code == 200


# --- Publicada (US7) ------------------------------------------------------------------------


def test_publicada_imutavel_para_as_duas_atuacoes(client, cliente_csaeg, publicada):
    caminho = f"/editor/versoes/{publicada.pk}/"
    assert "Criar nova Versão a partir desta" in ce.texto_visivel(client.get(caminho))
    assert "Criar nova Versão a partir desta" not in ce.texto_visivel(cliente_csaeg.get(caminho))
    antes = ce.retrato(publicada)
    dados = {"designacao": "Outra"}
    assert client.post(caminho + "dados/", dados).status_code == 409
    _recusa(cliente_csaeg.post(caminho + "dados/", dados), mensagens.RECUSA_ELABORACAO)
    assert ce.retrato(publicada) == antes


# --- Vários vínculos (US8) e desativação (US9; SC-005) --------------------------------------


def test_cpaeg_e_csaeg_somam_capacidades(client, vinculo_cpaeg, copia, publicada):
    registrar_vinculo(A, Papel.CSAEG, "Vitória")
    texto = ce.texto_visivel(client.get("/editor/"))
    assert CPAEG_ROTULO in texto and CSAEG_ROTULO in texto
    assert client.get(f"/editor/versoes/{copia.pk}/").status_code == 200
    desativar_vinculo(vinculo_cpaeg)
    _recusa(client.get(f"/editor/versoes/{copia.pk}/"), mensagens.RECUSA_RASCUNHO)
    assert client.get(f"/editor/versoes/{publicada.pk}/").status_code == 200


def test_duas_csaeg_nao_somam_poder_institucional(cliente_csaeg, copia):
    registrar_vinculo(B, Papel.CSAEG, "Serra")
    _recusa(cliente_csaeg.get(f"/editor/versoes/{copia.pk}/"), mensagens.RECUSA_RASCUNHO)
    _recusa(
        cliente_csaeg.post("/editor/pesquisas/nova/", {"nome": "X"}), mensagens.RECUSA_ELABORACAO
    )


def test_desativacao_vale_na_requisicao_seguinte_e_reativacao_tambem(client, vinculo_cpaeg):
    assert client.get("/editor/").status_code == 200
    desativar_vinculo(vinculo_cpaeg)
    _recusa(client.get("/editor/"), mensagens.RECUSA_SEM_ATUACAO)
    assert registrar_vinculo(A, Papel.CPAEG).pk == vinculo_cpaeg.pk
    assert client.get("/editor/").status_code == 200


def test_desativacao_entre_formulario_e_envio(client, vinculo_cpaeg, copia):
    caminho = f"/editor/versoes/{copia.pk}/dados/"
    assert client.get(caminho).status_code == 200
    antes = ce.retrato(copia)
    desativar_vinculo(vinculo_cpaeg)
    _recusa(client.post(caminho, {"designacao": "Alterada"}), mensagens.RECUSA_SEM_ATUACAO)
    assert ce.retrato(copia) == antes


# --- Modo de demonstração não autoriza (US10, caso H) ---------------------------------------


def test_modo_ligado_nao_autoriza_sem_vinculo(settings, cliente_sem_vinculo):
    assert settings.TRAJETORIA_DEMONSTRACAO is True
    _recusa(cliente_sem_vinculo.get("/editor/"), mensagens.RECUSA_SEM_ATUACAO)
    _recusa(
        cliente_sem_vinculo.post("/editor/pesquisas/nova/", {"nome": "X"}),
        mensagens.RECUSA_SEM_ATUACAO,
    )


# --- Publicação ausente (US11, caso K) ------------------------------------------------------


def test_nenhuma_superficie_de_publicacao(client, copia):
    for caminho in (
        "/editor/",
        f"/editor/pesquisas/{copia.pesquisa_id}/",
        f"/editor/versoes/{copia.pk}/",
        f"/editor/versoes/{copia.pk}/diagnostico/",
    ):
        html = client.get(caminho).content.decode()
        assert not re.search(r'(href|action)="[^"]*(publicar|aprov|homolog)', html), caminho
        assert not re.search(r"<button[^>]*>[^<]*(Publicar|Aprovar|Homologar)", html), caminho
    assert client.post(f"/editor/versoes/{copia.pk}/publicar/").status_code == 404
    copia.refresh_from_db()
    assert copia.estado == EstadoVersao.RASCUNHO


# --- Textos das recusas (US12; SC-010, SC-011) ----------------------------------------------


def test_textos_das_recusas(cliente_sem_vinculo, cliente_csaeg, copia):
    respostas = {
        mensagens.RECUSA_SEM_ATUACAO: cliente_sem_vinculo.get("/editor/"),
        mensagens.RECUSA_RASCUNHO: cliente_csaeg.get(f"/editor/versoes/{copia.pk}/"),
        mensagens.RECUSA_ELABORACAO: cliente_csaeg.get("/editor/pesquisas/nova/"),
    }
    for texto, resposta in respostas.items():
        _recusa(resposta, texto)
        visivel = ce.texto_visivel(resposta)
        assert ce.padroes_tecnicos(resposta) == []
        assert not re.search(r"\bArt\.|\b(role|permission|ACL|policy|scope)\b|pode_", visivel)
        assert "demonstracao:operador" not in resposta.content.decode()
        assert not re.search(r"\b(CPAEG|CSAEG)\b(?!\))", visivel)  # só a sigla entre parênteses
    sem = ce.texto_visivel(respostas[mensagens.RECUSA_SEM_ATUACAO])
    assert "Trocar operador fictício" in sem and "Voltar às Pesquisas" not in sem
    assert "Voltar às Pesquisas" in ce.texto_visivel(respostas[mensagens.RECUSA_RASCUNHO])


# --- Origem de Versão (010, revisão final) --------------------------------------------------


def test_origem_rascunho_so_para_quem_consulta_rascunhos(
    client, cliente_csaeg, baseline, publicada
):
    # `publicada` foi criada a partir da baseline, que é RASCUNHO.
    origem = f"criada a partir de «{baseline.designacao}»"
    for caminho in (
        f"/editor/pesquisas/{publicada.pesquisa_id}/",
        f"/editor/versoes/{publicada.pk}/",
    ):
        assert origem in ce.texto_visivel(client.get(caminho)), caminho
        resposta = cliente_csaeg.get(caminho)
        texto = ce.texto_visivel(resposta)
        assert resposta.status_code == 200 and publicada.designacao in texto, caminho
        assert baseline.designacao not in texto and "criada a partir de" not in texto, caminho


def test_origem_publicada_continua_visivel_para_a_csaeg(cliente_csaeg, publicada):
    derivada = op.criar_versao_a_partir_de(publicada, "Derivada publicada de teste")
    op.publicar(derivada)
    texto = ce.texto_visivel(cliente_csaeg.get(f"/editor/versoes/{derivada.pk}/"))
    assert f"criada a partir de «{publicada.designacao}»" in texto

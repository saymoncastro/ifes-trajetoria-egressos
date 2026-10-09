"""Curadoria de oportunidades (025 FR-025 a FR-035; contracts/curadoria.md; T036, T038, T039)."""

import re
from datetime import timedelta

import pytest
from django.test import Client

from tests.editor.construcao_editor import atuar_como
from tests.portal import construcao as cp
from tests.portal import construcao_oportunidades as co
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo
from trajetoria.portal.models import Oportunidade
from trajetoria.portal.oportunidades import mensagens as m
from trajetoria.portal.oportunidades import operacoes
from trajetoria.portal.oportunidades.regras import Estado, estado

pytestmark = pytest.mark.django_db

LISTA = "/curadoria/oportunidades/"
OPERADOR_C = "demonstracao:operador-c"


@pytest.fixture
def vinculos(cenario):
    registrar_vinculo(co.OPERADOR_A, Papel.CPAEG)
    registrar_vinculo(co.OPERADOR_B, Papel.CSAEG, "Vitória")


@pytest.fixture
def operador_b(client, vinculos):
    return atuar_como(client, co.OPERADOR_B)


@pytest.fixture
def operador_a(client, vinculos):
    return atuar_como(client, co.OPERADOR_A)


def _formulario(**extra) -> dict:
    base = {
        "titulo": "Especialização em Gestão Pública", "resumo": "Inscrições abertas.",
        "categoria": "cursos", "unidade_responsavel": "Vitória",
        "endereco": "https://oportunidades.example/gestao",
        "inicio": co.HOJE.isoformat(), "fim": (co.HOJE + timedelta(days=30)).isoformat(),
    }
    return {**base, **extra}


def _linha(o) -> tuple:
    return tuple(Oportunidade.objects.filter(pk=o.pk).values_list().get())


# --- Acesso (FR-025, FR-035) ----------------------------------------------------------------


def test_sem_operador_vai_para_a_escolha_e_volta(client, vinculos):
    resposta = client.get(LISTA)
    assert resposta.status_code == 302
    assert resposta["Location"] == "/demonstracao/operador/?destino=curadoria"
    escolha = client.post("/demonstracao/operador/escolher/",
                          {"operador": co.OPERADOR_B, "destino": "curadoria"})
    assert escolha["Location"] == LISTA


def test_operador_sem_vinculo_e_recusado(client, vinculos):
    atuar_como(client, OPERADOR_C)
    resposta = client.get(LISTA)
    assert resposta.status_code == 403 and m.RECUSA in resposta.content.decode()


def test_csaeg_ve_so_a_propria_unidade(operador_b):
    co.publicada("De Vitória", escopo=co.ESCOPO_B, operador=co.OPERADOR_B,
                 unidade_responsavel="Vitória")
    co.publicada("Da Serra", unidade_responsavel="Serra")
    co.publicada("Do Ifes")
    html = operador_b.get(LISTA).content.decode()
    assert "De Vitória" in html and "Da Serra" not in html and "Do Ifes" not in html


# --- Cadastro, edição e publicação (FR-028 a FR-030, FR-033; T036) -------------------------


def test_cadastrar_cria_rascunho_invisivel(operador_b, cenario):
    resposta = operador_b.post(f"{LISTA}nova/", _formulario())
    assert resposta.status_code == 302 and resposta["Location"] == f"{LISTA}?aviso=cadastrada"
    oportunidade = Oportunidade.objects.get()
    assert estado(oportunidade, co.HOJE) is Estado.RASCUNHO
    assert oportunidade.publicada_por is None
    egresso = Client()
    cp.entrar(egresso, cenario.pessoa("SIM-P-0002"))
    assert "Gestão Pública" not in egresso.get("/oportunidades/").content.decode()


def test_editar_e_publicar(operador_b, cenario):
    operador_b.post(f"{LISTA}nova/", _formulario())
    pk = Oportunidade.objects.get().pk
    assert operador_b.post(f"{LISTA}{pk}/editar/", _formulario(resumo="Novo resumo."))[
        "Location"] == f"{LISTA}?aviso=editada"
    previa = operador_b.get(f"{LISTA}{pk}/publicar/").content.decode()
    assert "Endereço: oportunidades.example" in previa
    assert m.AVISO_EXTERNO in previa
    assert m.PUBLICO_TODOS in previa
    assert operador_b.post(f"{LISTA}{pk}/publicar/")["Location"] == f"{LISTA}?aviso=publicada"
    oportunidade = Oportunidade.objects.get()
    assert oportunidade.resumo == "Novo resumo."
    assert oportunidade.publicada_por == co.OPERADOR_B
    assert co.OPERADOR_B not in operador_b.get(LISTA).content.decode()


def test_publico_livre_para_a_csaeg(operador_b, cenario):
    """FR-026 (DP-2502): a unidade administra o que é dela e dirige a qualquer público."""
    operador_b.post(f"{LISTA}nova/", _formulario(publico_unidades=["Serra"]))
    pk = Oportunidade.objects.get().pk
    operador_b.post(f"{LISTA}{pk}/publicar/")
    egresso = Client()
    cp.entrar(egresso, cenario.pessoa("SIM-P-0001"))
    pagina = egresso.get("/oportunidades/").content.decode()
    assert "Gestão Pública" in pagina and "Oferecida pela unidade Vitória" in pagina


@pytest.mark.parametrize("unidade", ["Serra", ""])
def test_csaeg_nao_cadastra_para_outra_unidade(operador_b, unidade):
    resposta = operador_b.post(f"{LISTA}nova/", _formulario(unidade_responsavel=unidade))
    assert resposta.status_code == 422
    assert m.ERROS["unidade_responsavel"] in resposta.content.decode()
    assert not Oportunidade.objects.exists()


@pytest.mark.parametrize(
    "endereco",
    ["http://x.example/", "https://user:pw@x.example/", "https://10.0.0.1/",
     "https://[::1]/", "https://x.example/a b", "https://x.example/" + "a" * 490],
)
def test_endereco_recusado_no_campo(operador_b, endereco):
    resposta = operador_b.post(f"{LISTA}nova/", _formulario(endereco=endereco))
    html = resposta.content.decode()
    assert resposta.status_code == 422 and m.ERROS["endereco"] in html
    assert 'id="id_endereco-erro"' in html and 'aria-invalid="true"' in html
    assert not Oportunidade.objects.exists()


@pytest.mark.parametrize(
    "extra, erro",
    [
        ({"titulo": ""}, "titulo"),
        ({"titulo": "   "}, "titulo"),
        ({"titulo": "x" * 121}, "titulo"),
        ({"resumo": "y" * 301}, "resumo"),
        ({"fim": (co.HOJE - timedelta(days=2)).isoformat()}, "periodo_invertido"),
    ],
)
def test_validacoes_no_campo(operador_b, extra, erro):
    resposta = operador_b.post(f"{LISTA}nova/", _formulario(**extra))
    assert resposta.status_code == 422 and m.ERROS[erro] in resposta.content.decode()
    assert not Oportunidade.objects.exists()


def test_foco_no_primeiro_erro_e_resumo(operador_b):
    html = operador_b.post(f"{LISTA}nova/", _formulario(titulo="", endereco="x")).content.decode()
    assert re.search(r'<input[^>]*name="titulo"[^>]*autofocus', html)
    assert "Erro: corrija os itens abaixo" in html


def test_publicacao_com_fim_vencido_recusada(operador_b, relogio):
    operador_b.post(f"{LISTA}nova/", _formulario())
    pk = Oportunidade.objects.get().pk
    relogio.agora += timedelta(days=40)
    atuar_como(operador_b, co.OPERADOR_B)
    resposta = operador_b.post(f"{LISTA}{pk}/publicar/")
    assert resposta.status_code == 422
    assert m.ERROS["publicacao_vencida"] in resposta.content.decode()
    assert Oportunidade.objects.get().publicada_em is None


def test_sc007_quatro_telas(operador_b):
    """Lista → formulário → confirmação → lista, seguindo links e botões (SC-007)."""
    telas = [operador_b.get(LISTA)]
    assert f'href="{LISTA}nova/"' in telas[0].content.decode()
    telas.append(operador_b.get(f"{LISTA}nova/"))
    telas.append(operador_b.post(f"{LISTA}nova/", _formulario(), follow=True))
    pk = Oportunidade.objects.get().pk
    assert f'href="{LISTA}{pk}/publicar/"' in telas[-1].content.decode()
    telas[-1] = operador_b.get(f"{LISTA}{pk}/publicar/")
    telas.append(operador_b.post(f"{LISTA}{pk}/publicar/", follow=True))
    assert [t.status_code for t in telas] == [200, 200, 200, 200]
    assert m.AVISOS["publicada"] in telas[-1].content.decode()


def test_escape_na_lista_e_na_previa(operador_b):
    operador_b.post(f"{LISTA}nova/", _formulario(titulo="<b>x</b>", resumo="<script>y</script>"))
    pk = Oportunidade.objects.get().pk
    for url in (LISTA, f"{LISTA}{pk}/publicar/"):
        html = operador_b.get(url).content.decode()
        main = html[html.index("<main"):html.index("</main>")]
        assert "<b>x" not in main and "<script>y" not in main and "&lt;b&gt;x" in main


def test_sem_exclusao(operador_b):
    """FR-010."""
    rascunho = co.rascunho(escopo=co.ESCOPO_B, operador=co.OPERADOR_B,
                           unidade_responsavel="Vitória")
    assert operador_b.post(f"{LISTA}{rascunho.pk}/excluir/").status_code == 404
    assert operador_b.delete(f"{LISTA}{rascunho.pk}/editar/").status_code == 405
    assert "Excluir" not in operador_b.get(LISTA).content.decode()
    assert Oportunidade.objects.filter(pk=rascunho.pk).exists()


def test_csrf_exigido(vinculos):
    cliente = atuar_como(Client(enforce_csrf_checks=True), co.OPERADOR_B)
    assert cliente.post(f"{LISTA}nova/", _formulario()).status_code == 403


# --- Ciclo de vida (FR-029 a FR-034; T038) -------------------------------------------------


def test_retirada_imediata_e_registrada(operador_b, cenario):
    o = co.publicada("Encontro", escopo=co.ESCOPO_B, operador=co.OPERADOR_B,
                     unidade_responsavel="Vitória", publico_unidades=["Vitória"])
    egresso = Client()
    cp.entrar(egresso, cenario.pessoa("SIM-P-0002"))
    assert "Encontro" in egresso.get("/oportunidades/").content.decode()
    assert m.RETIRAR_TEXTO in operador_b.get(f"{LISTA}{o.pk}/retirar/").content.decode()
    assert operador_b.post(f"{LISTA}{o.pk}/retirar/")["Location"] == f"{LISTA}?aviso=retirada"
    o.refresh_from_db()
    assert o.retirada_por == co.OPERADOR_B and o.retirada_em is not None
    assert "Encontro" not in egresso.get("/oportunidades/").content.decode()


def test_rascunho_retirado_nunca_publica(operador_b):
    o = co.rascunho(escopo=co.ESCOPO_B, operador=co.OPERADOR_B, unidade_responsavel="Vitória")
    operador_b.post(f"{LISTA}{o.pk}/retirar/")
    assert operador_b.post(f"{LISTA}{o.pk}/publicar/").status_code == 409
    assert Oportunidade.objects.get(pk=o.pk).publicada_em is None


def test_fim_antes_de_hoje_em_publicada_recusado(operador_b):
    o = co.publicada(escopo=co.ESCOPO_B, operador=co.OPERADOR_B, unidade_responsavel="Vitória")
    resposta = operador_b.post(f"{LISTA}{o.pk}/editar/", _formulario(
        inicio=(co.HOJE - timedelta(days=5)).isoformat(),
        fim=(co.HOJE - timedelta(days=1)).isoformat()))
    assert resposta.status_code == 422
    assert m.ERROS["fim_antes_de_hoje"] in resposta.content.decode()


def test_encerrada_e_retirada_sem_acoes(operador_a, relogio):
    o = co.publicada("Antiga", fim=co.HOJE + timedelta(days=1))
    relogio.agora += timedelta(days=3)
    atuar_como(operador_a, co.OPERADOR_A)
    html = operador_a.get(LISTA).content.decode()
    linha = re.search(r"<tr>\s*<th scope=\"row\">Antiga</th>.*?</tr>", html, re.S).group(0)
    assert "Encerrada" in linha and "<a " not in linha
    for acao in ("editar", "publicar", "retirar"):
        assert operador_a.get(f"{LISTA}{o.pk}/{acao}/").status_code == 409


def test_conflito_nada_gravado(vinculos):
    o = co.publicada(escopo=co.ESCOPO_B, operador=co.OPERADOR_B, unidade_responsavel="Vitória")
    um, outro = atuar_como(Client(), co.OPERADOR_A), atuar_como(Client(), co.OPERADOR_B)
    assert outro.get(f"{LISTA}{o.pk}/editar/").status_code == 200  # abriu a página
    um.post(f"{LISTA}{o.pk}/retirar/")
    antes = _linha(o)
    resposta = outro.post(f"{LISTA}{o.pk}/editar/", _formulario(titulo="Outro título"))
    assert resposta.status_code == 409 and m.CONFLITO in resposta.content.decode()
    assert _linha(o) == antes


@pytest.mark.parametrize("acao", ["editar", "publicar", "retirar"])
def test_sc006_registro_alheio_e_404(operador_b, acao):
    """SC-006: editar, publicar e retirar oportunidade de outra unidade (O2, Serra) ou
    institucional (O1) respondem 404 e nada muda. A CPAEG pode."""
    da_serra = co.rascunho("Da Serra", unidade_responsavel="Serra")
    do_ifes = co.rascunho("Do Ifes")
    for o in (da_serra, do_ifes):
        antes = _linha(o)
        assert operador_b.get(f"{LISTA}{o.pk}/{acao}/").status_code == 404
        dados = _formulario(unidade_responsavel="Vitória") if acao == "editar" else {}
        assert operador_b.post(f"{LISTA}{o.pk}/{acao}/", dados).status_code == 404
        assert _linha(o) == antes
    atuar_como(operador_b, co.OPERADOR_A)
    assert operador_b.get(f"{LISTA}{da_serra.pk}/{acao}/").status_code == 200


# --- Institucional (FR-025, FR-026; US4; T039) ---------------------------------------------


def test_cpaeg_ve_tudo_e_usa_o_ifes(operador_a, cenario):
    co.publicada("De Vitória", escopo=co.ESCOPO_B, operador=co.OPERADOR_B,
                 unidade_responsavel="Vitória")
    assert "De Vitória" in operador_a.get(LISTA).content.decode()
    resposta = operador_a.post(f"{LISTA}nova/", _formulario(unidade_responsavel="",
                                                            publico_niveis=["Pós-graduação"]))
    assert resposta.status_code == 302
    nova = Oportunidade.objects.get(unidade_responsavel="")
    operador_a.post(f"{LISTA}{nova.pk}/publicar/")
    vistos = {}
    for id_externo in ("SIM-P-0001", "SIM-P-0002", "SIM-P-0003", "SIM-P-0004"):
        egresso = Client()
        cp.entrar(egresso, cenario.pessoa(id_externo))
        vistos[id_externo] = "Gestão Pública" in egresso.get("/oportunidades/").content.decode()
    assert vistos == {"SIM-P-0001": False, "SIM-P-0002": False,
                      "SIM-P-0003": True, "SIM-P-0004": True}


def test_cpaeg_retira_oportunidade_de_unidade(operador_a):
    o = co.publicada(escopo=co.ESCOPO_B, operador=co.OPERADOR_B, unidade_responsavel="Vitória")
    operador_a.post(f"{LISTA}{o.pk}/retirar/")
    o.refresh_from_db()
    assert o.retirada_por == co.OPERADOR_A


def test_operacoes_recusam_operador_vazio():
    with pytest.raises(TypeError):
        operacoes.cadastrar(co.dados(), operador="", escopo=co.ESCOPO_A, hoje=co.HOJE)

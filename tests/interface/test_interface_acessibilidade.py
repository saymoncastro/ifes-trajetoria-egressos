"""Verificação estrutural de acessibilidade de todas as telas (008 US14; FR-071 a FR-078;
SC-014). Sem navegador: regras sobre o HTML, com o `html.parser` da biblioteca padrão. O
roteiro manual (teclado, leitor de tela, 320 px, zoom 200%) está no quickstart."""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

import pytest
from django.test import Client

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.participacao import operacoes as op
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

FOCAVEIS = ("a", "button", "input", "select", "textarea")
VAZIOS = ("input", "meta", "br", "link", "img", "hr")


@dataclass
class Elemento:
    tag: str
    attrs: dict
    pais: list  # tags ancestrais
    texto: str = ""
    ancestrais: list = field(default_factory=list)  # Elementos ancestrais


class _Arvore(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elementos: list[Elemento] = []
        self.pilha: list[Elemento] = []

    def handle_starttag(self, tag, attrs):
        elemento = Elemento(tag, dict(attrs), [e.tag for e in self.pilha], "", list(self.pilha))
        self.elementos.append(elemento)
        if tag not in VAZIOS:
            self.pilha.append(elemento)

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i].tag == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        for elemento in self.pilha:
            elemento.texto += data


def verificar(resposta) -> list[str]:
    """Lista de violações; vazia quando a tela passa."""
    html = resposta.content.decode()
    arvore = _Arvore()
    arvore.feed(html)
    els = arvore.elementos
    falhas = []
    tag = lambda t: [e for e in els if e.tag == t]  # noqa: E731

    if not re.search(r'<html lang="pt-BR">', html):
        falhas.append("html sem lang=pt-BR")
    titulos = tag("title")
    titulo = titulos[0].texto.strip() if len(titulos) == 1 else ""
    if not titulo:
        falhas.append("title ausente ou repetido")
    tem_erros = any(e.attrs.get("role") == "alert" for e in els)
    if tem_erros != titulo.startswith("Erro:"):
        falhas.append(f"título e erros incoerentes: {titulo!r}")
    if len(tag("h1")) != 1:
        falhas.append(f"{len(tag('h1'))} h1")
    niveis = [int(e.tag[1]) for e in els if re.fullmatch(r"h[1-6]", e.tag)]
    if any(b > a + 1 for a, b in zip(niveis, niveis[1:], strict=False)):
        falhas.append(f"salto de títulos {niveis}")
    focaveis = [e for e in els if e.tag in FOCAVEIS and e.attrs.get("type") != "hidden"]
    if not focaveis or focaveis[0].attrs.get("href") != "#conteudo":
        falhas.append("primeiro focável não é 'Pular para o conteúdo'")
    if not [e for e in tag("main") if e.attrs.get("id") == "conteudo"]:
        falhas.append("main#conteudo ausente")
    ids = [e.attrs["id"] for e in els if "id" in e.attrs]
    if len(ids) != len(set(ids)):
        falhas.append("ids repetidos")
    rotulados = {e.attrs.get("for") for e in tag("label")}
    for e in els:
        if e.tag in ("input", "select", "textarea") and e.attrs.get("type") not in (
            "hidden",
            "submit",
        ):
            if e.attrs.get("id") not in rotulados and "label" not in e.pais:
                falhas.append(f"controle sem rótulo: {e.attrs.get('name')}")
            remover = e.attrs.get("name", "").endswith("-remover")
            if e.attrs.get("type") in ("radio", "checkbox") and not remover:
                grupo = [a for a in e.ancestrais if a.tag == "fieldset"]
                legendas = [
                    x for x in tag("legend") if grupo and grupo[-1] in x.ancestrais
                ]
                if not grupo or not legendas or not legendas[0].texto.strip():
                    falhas.append(f"grupo sem fieldset/legend: {e.attrs.get('name')}")
        for alvo in e.attrs.get("aria-describedby", "").split():
            if alvo not in ids:
                falhas.append(f"aria-describedby aponta para {alvo} inexistente")
    for erro in [i for i in ids if i.endswith("-erro")]:
        base = erro.removesuffix("-erro")
        invalidos = [
            e
            for e in els
            if e.attrs.get("aria-invalid") == "true" and e.attrs.get("id", "").startswith(base)
        ]
        if not invalidos:
            falhas.append(f"{base} com erro sem aria-invalid")
    for a in tag("a"):
        href = a.attrs.get("href", "")
        if href.startswith("#") and href != "#conteudo" and href[1:] not in ids:
            falhas.append(f"ligação para {href} inexistente")
    if tag("script"):
        falhas.append("<script> presente")
    if re.search(r'style="[^"]*width:\s*\d+px', html):
        falhas.append("largura fixa em style=")
    for e in els:
        recurso = e.attrs.get("src") or (e.attrs.get("href") if e.tag == "link" else None)
        if recurso and re.match(r"https?://", recurso):
            falhas.append(f"recurso externo {recurso}")
    for b in tag("button"):
        if not b.texto.strip():
            falhas.append("botão sem texto")
    return falhas


# --- Telas --------------------------------------------------------------------------------


@pytest.fixture
def telas(client, cenario, relogio):
    """Todas as telas da jornada, com os estados relevantes."""
    b = cenario.base
    ce.incorporar(FonteSimulada(), "SIM-P-0002")
    resultado = {"entrada": client.get("/demonstracao/")}
    resultado["operador"] = client.get("/demonstracao/operador/")  # 010
    resultado["formacoes-sem-pesquisa"] = _como(client, "SIM-P-0002", "/formacoes/")
    resultado["formacoes-selecao"] = _como(client, "SIM-P-0003", "/formacoes/")
    resultado["formacoes-resolvida"] = _como(client, "SIM-P-0001", "/formacoes/")
    pk = ci.participacao_de(client.post("/formacoes/entrar/"))
    ana = Participacao.objects.get(pk=pk)
    url = f"/participacoes/{pk}/"
    resultado["s1"] = client.get(url + "secoes/1/")
    resultado["s1-erros"] = client.post(url + "secoes/1/", {"p1": "99"})
    c.preencher(ana, b, [1], {"Q1": "Sim"})
    client.post(url + "secoes/2/", {"p1": "1"})
    resultado["s2-pendencias"] = client.get(url + "secoes/2/?pendencias=1")
    escolhas = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Não", "Q46": "Não"}
    c.preencher(ana, b, [2], escolhas)
    resultado["s3"] = client.get(url + "secoes/3/")
    c.preencher(ana, b, [3, 6], escolhas)
    resultado["s8"] = client.get(url + "secoes/8/")
    resultado["s8-complemento"] = client.post(
        url + "secoes/8/", {"p7-complemento": "x", "p1": "9"}
    )
    c.preencher(ana, b, [8], escolhas)
    resultado["s10"] = client.get(url + "secoes/10/")
    c.preencher(ana, b, [10], escolhas)
    op.responder_escala(ana, b.q(48), 3)
    resultado["s11"] = client.get(url + "secoes/11/")
    c.preencher(ana, b, [11], escolhas)
    resultado["s13"] = client.get(url + "secoes/13/")
    c.preencher(ana, b, [13], escolhas)
    resultado["conclusao"] = client.get(url + "concluir/")
    client.post(url + "concluir/")
    resultado["concluida"] = client.get(url + "concluida/")
    resultado["aviso-ja-respondida"] = client.get(url + "secoes/1/")
    resultado["404"] = client.get("/nao-existe/")
    resultado["403"] = Client(enforce_csrf_checks=True).post("/demonstracao/encerrar/")
    return resultado


def _como(client, id_externo, url):
    ci.entrar_como(client, ce.pessoa_da_fonte(id_externo))
    return client.get(url)


def test_todas_as_telas_passam_no_verificador(telas):
    falhas = {nome: verificar(r) for nome, r in telas.items()}
    assert {nome: f for nome, f in falhas.items() if f} == {}


def test_telas_com_erros_tem_resumo_e_titulo_de_erro(telas):
    for nome in ("s1-erros", "s2-pendencias", "s8-complemento"):
        html = telas[nome].content.decode()
        assert "<title>Erro: " in html and 'role="alert"' in html, nome


def test_titulos_distintos_por_tela(telas):
    nomes = ("entrada", "formacoes-resolvida", "s1", "s3", "conclusao", "concluida", "404", "403")
    titulos = [re.search(r"<title>(.*?)</title>", telas[n].content.decode())[1] for n in nomes]
    assert len(set(titulos)) == len(titulos)


def test_obrigatoriedade_e_estado_nao_dependem_de_cor(client, telas):
    assert "(obrigatória)" in ci.texto_visivel(telas["s1"])
    assert "Erro: " in ci.texto_visivel(telas["s1-erros"])
    # Depois da conclusão (feita em `telas`), o estado da formação é texto, não cor.
    assert "Pesquisa já respondida." in ci.texto_visivel(client.get("/formacoes/"))


class _Falsa:
    def __init__(self, html):
        self.content = html.encode()


def test_o_verificador_detecta_violacoes():
    ruim = (
        "<html><head><title>X</title></head><body><main><h1>A</h1><h3>B</h3>"
        '<input type="text" name="sem-rotulo"><input type="radio" name="solto" id="r">'
        '<label for="r">r</label><p id="p1-erro">erro</p><a href="#nada">x</a>'
        '<button></button><script></script><img src="https://externo/x.png">'
        '<div role="alert"></div></main></body></html>'
    )
    falhas = " | ".join(verificar(_Falsa(ruim)))
    for esperado in (
        "lang", "título e erros", "salto de títulos", "Pular", "main#conteudo",
        "sem rótulo", "fieldset/legend", "aria-invalid", "#nada", "<script>",
        "recurso externo", "botão sem texto",
    ):  # fmt: skip
        assert esperado in falhas, esperado

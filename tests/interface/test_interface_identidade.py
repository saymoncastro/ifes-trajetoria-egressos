"""Identidade visual da jornada do egresso (Feature 015; spec FR-001 a FR-046).

Sem navegador: as regras visuais são verificadas nas folhas incluídas nas próprias páginas
(leitor de cascata em `construcao_interface`). Alturas, contraste renderizado, reflow e
capturas são do gate (quickstart; `validacao.md`), não destes testes.
"""

import re
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import Client

from tests.editor.construcao_editor import A, atuar_como
from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from trajetoria.formulario_2024 import materializar
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db

RAIZ = Path(__file__).resolve().parents[2] / "trajetoria"
DIR_INTERFACE = RAIZ / "interface" / "templates" / "interface"
ESTILO = DIR_INTERFACE / "estilo.css"
MARCA_DA_CAMADA = "Camada da jornada do egresso (015)"

COMPLETO = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Sim", "Q46": "Não"}

# contracts/tokens.md — valores fixos (os "a calibrar" só precisam existir).
TOKENS_FIXOS = {
    "--cor-marca": "#2f9e41",
    "--cor-acao": "#1351b4",  # Direção B, valor provisório mergeado (FR-014)
    "--cor-acao-forte": "#0c326f",
    "--cor-sucesso": "#195128",
    "--cor-texto": "#1b1b1b",
    "--cor-texto-suave": "#565c65",
    "--cor-fundo": "#ffffff",
    "--cor-borda-forte": "#565c65",
    "--cor-info": "#1a4480",
    "--cor-erro": "#b50909",
    "--cor-foco": "#1b1b1b",
    "--cor-foco-halo": "#ffdd00",
    "--cor-demonstracao": "#fff1d2",
}
TOKENS_CALIBRAVEIS = ("--cor-institucional", "--cor-selecao", "--cor-borda-suave")
TOKENS_DE_FORMA = (
    *(f"--fonte-{n}" for n in range(1, 6)),
    "--fonte",
    "--peso-normal",
    "--peso-medio",
    "--peso-forte",
    "--entrelinha-titulo",
    "--entrelinha-enunciado",
    "--entrelinha-corpo",
    *(f"--espaco-{n}" for n in range(1, 8)),
    "--raio",
    "--borda-fina",
    "--borda-controle",
    "--borda-acento",
    "--coluna",
    "--alvo",
)
# Valores das duas Direções e do sucesso: só nas linhas que definem esses tokens.
HEX_DE_ACAO = ("#1351b4", "#0c326f", "#195128", "#00420c")
LINHAS_DE_ACAO = ("--cor-acao:", "--cor-acao-forte:", "--cor-sucesso:")

# Seletores usados também pelo editor/acompanhamento (research R1): em `estilo.css`, nunca
# com token. Uma regra é exclusiva da jornada só se o seletor tiver uma destas classes.
EXCLUSIVAS_DA_JORNADA = (".pergunta", ".escala", ".opcoes", ".com-pendencia", ".resumo-pendencias")


def _css(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def _folhas_da_interface() -> dict[Path, str]:
    return {p: _css(p) for p in sorted(DIR_INTERFACE.glob("*.css"))}


def _regras_do_arquivo(caminho: Path) -> list[ci.Regra]:
    return ci.regras(f"<style>{_css(caminho)}</style>")


def _html(resposta) -> str:
    return resposta.content.decode()


# --- Tokens (FR-001, FR-002, FR-011, FR-014; contracts/tokens.md) --------------------------


def test_tokens_do_contrato_definidos_uma_vez_no_root_de_estilo():
    texto = _css(ESTILO)
    raiz = [r for r in _regras_do_arquivo(ESTILO) if r.seletor == ":root"]
    assert len(raiz) == 1
    definidos = raiz[0].declaracoes
    for nome in (*TOKENS_FIXOS, *TOKENS_CALIBRAVEIS, *TOKENS_DE_FORMA):
        assert nome in definidos, nome
        assert len(re.findall(rf"(?m)^\s*{re.escape(nome)}\s*:", texto)) == 1, nome
    for nome, esperado in TOKENS_FIXOS.items():
        assert definidos[nome].lower() == esperado, nome


def test_cada_token_de_cor_documenta_o_contraste():
    for linha in _css(ESTILO).splitlines():
        if re.match(r"\s*--cor-[\w-]+\s*:", linha):
            assert "/*" in linha and "*/" in linha, linha


def test_direcao_a_b_so_nos_dois_tokens_de_acao():
    """A troca A ↔ B altera exclusivamente `--cor-acao` e `--cor-acao-forte` (FR-011)."""
    for caminho, texto in _folhas_da_interface().items():
        for linha in texto.splitlines():
            if any(h in linha.lower() for h in HEX_DE_ACAO):
                assert linha.strip().startswith(LINHAS_DE_ACAO), (caminho.name, linha)


def test_nenhum_mecanismo_de_alternancia_em_execucao():
    """Sem flag, configuração, variável, preferência, parâmetro ou condicional (FR-012)."""
    for caminho in RAIZ.rglob("*"):
        if caminho.suffix not in (".py", ".html") or "migrations" in caminho.parts:
            continue
        texto = caminho.read_text(encoding="utf-8").lower()
        assert "cor-acao" not in texto, caminho
        assert not any(h in texto for h in HEX_DE_ACAO), caminho


# --- Fronteiras de cor e de camada (FR-003, FR-040; research R1) ----------------------------


def test_verde_da_marca_nunca_e_cor_de_texto_nem_de_fundo():
    for caminho in _folhas_da_interface():
        for regra in _regras_do_arquivo(caminho):
            for nome, valor in regra.declaracoes.items():
                if nome in ("color", "background", "background-color"):
                    assert "--cor-marca" not in valor, (caminho.name, regra.seletor)


def test_seletores_compartilhados_com_a_administracao_nao_usam_tokens():
    for regra in _regras_do_arquivo(ESTILO):
        if regra.seletor == ":root" or any(c in regra.seletor for c in EXCLUSIVAS_DA_JORNADA):
            continue
        for nome, valor in regra.declaracoes.items():
            assert "var(--" not in valor, (regra.seletor, nome, valor)


# --- Matriz de inclusão das folhas (FR-020, FR-040; contracts/telas.md; research R5) --------


@pytest.fixture
def telas_da_jornada(client, cenario):
    """HTML de cada tela da jornada e da demonstração que estende o template base."""
    telas = {
        "entrada da demonstração": _html(client.get("/acesso/")),
        "operador da demonstração": _html(client.get("/demonstracao/operador/")),
    }
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    telas["trajetória"] = _html(client.get("/formacoes/"))
    telas["Seção"] = _html(client.get(f"/participacoes/{ana.pk}/secoes/1/"))
    ci.percorrer_pela_interface(
        client, ana.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, COMPLETO)
    )
    telas["conclusão"] = _html(client.get(f"/participacoes/{ana.pk}/concluir/"))
    client.post(f"/participacoes/{ana.pk}/concluir/")
    telas["confirmação"] = _html(client.get(f"/participacoes/{ana.pk}/concluida/"))
    telas["tela de estado"] = _html(client.get(f"/participacoes/{ana.pk}/secoes/1/"))
    return telas


@pytest.fixture
def telas_fora_da_jornada(db):
    registrar_vinculo(A, Papel.CPAEG)
    operador = atuar_como(Client(), A)
    versao = materializar().versao
    return {
        "lista de Pesquisas (009)": _html(operador.get("/editor/")),
        "prévia de Seção (009)": _html(
            operador.get(f"/editor/versoes/{versao.pk}/previa/secoes/8/")
        ),
        "acompanhamento (011)": _html(operador.get("/acompanhamento/")),
        "404": render_to_string("404.html"),
        "500": render_to_string("500.html"),
        "403 (CSRF)": render_to_string("403_csrf.html"),
    }


def test_camada_da_jornada_em_toda_tela_da_jornada(telas_da_jornada):
    assert "já foi respondida" in telas_da_jornada["tela de estado"]
    for nome, html in telas_da_jornada.items():
        assert MARCA_DA_CAMADA in html, nome


def test_camada_da_jornada_ausente_fora_da_jornada(telas_fora_da_jornada):
    for nome, html in telas_fora_da_jornada.items():
        assert "<style>" in html, nome
        assert MARCA_DA_CAMADA not in html, nome


# --- US2: ritmo, tipografia e estados das Perguntas (FR-022 a FR-025) -----------------------

ESCOLHAS_ATE_S11 = {"Q1": "Sim", "Q14": "Graduação", "Q33": "Não", "Q46": "Não"}


@pytest.fixture
def secao_8(client, cenario):
    """HTML da Seção 8 ("Avaliação": escalas, rádios, caixas, "Outro") de Ana."""
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    c.preencher(ana, cenario.base, [1, 2, 3, 6], ESCOLHAS_ATE_S11)
    resposta = client.get(f"/participacoes/{ana.pk}/secoes/8/")
    assert resposta.status_code == 200
    return _html(resposta)


def _margem_inferior(valor_css: str | None) -> str | None:
    """Componente inferior de `margin` (atalho de 1 a 4 valores) ou o próprio longhand."""
    if valor_css is None:
        return None
    partes = valor_css.split()
    return {1: partes[0], 2: partes[0], 3: partes[2], 4: partes[2]}[len(partes)]


def test_ritmo_entre_perguntas_e_ate_a_resposta(secao_8):
    assert "escala" in secao_8 and "<fieldset" in secao_8
    margem = ci.valor(secao_8, set(), "pergunta", "fieldset", ("margin", "margin-bottom"))
    assert _margem_inferior(margem) == "3rem"  # 48 px entre Perguntas
    enunciado = ci.valor(
        secao_8, {"pergunta", "fieldset"}, "", "legend", ("margin", "margin-bottom")
    )
    assert _margem_inferior(enunciado) == "0.5rem"  # 8 px até a resposta


def test_tipografia_do_enunciado_e_dos_auxiliares(secao_8):
    for ancestrais, classe, tag in (
        ({"pergunta", "fieldset"}, "", "legend"),
        ({"pergunta"}, "enunciado", "label"),
    ):
        assert ci.valor(secao_8, ancestrais, classe, tag, "font-size") == "1.125rem", tag
        assert ci.valor(secao_8, ancestrais, classe, tag, "font-weight") == "600", tag
        assert ci.valor(secao_8, ancestrais, classe, tag, "line-height") == "1.4", tag
    auxiliares = (
        ({"pergunta"}, "explicacao", "p"),
        ({"pergunta"}, "descricao-escala", "p"),
        ({"pergunta", "legend"}, "obrigatoria", "span"),
        ({"pergunta", "legend"}, "nota", "span"),
    )
    for ancestrais, classe, tag in auxiliares:
        assert ci.valor(secao_8, ancestrais, classe, tag, "font-size") == "0.9375rem", classe
        assert ci.valor(secao_8, ancestrais, classe, tag, "color") == "#565c65", classe


def test_controles_marcados_e_estado_selecionado(secao_8):
    acao = ci.tokens(secao_8)["--cor-acao"]
    assert ci.valor(secao_8, {"pergunta", "opcao"}, "", "input", "accent-color") == acao
    selecionado = [
        r
        for r in ci.regras(secao_8)
        if r.seletor.startswith(".pergunta") and ".opcao:has(input:checked)" in r.seletor
    ]
    assert selecionado, "estado selecionado da linha/célula"
    marcas = " ".join(
        ci.resolver(v, ci.tokens(secao_8)) for r in selecionado for v in r.declaracoes.values()
    )
    assert acao in marcas and "4px" in marcas


def test_celulas_da_escala_delimitadas(secao_8):
    borda = ci.valor(secao_8, {"pergunta", "escala"}, "opcao", "div", ("border", "border-color"))
    assert borda == "1px solid #565c65"  # contorno forte, 6,7:1 (≥ 3:1)
    assert (
        ci.valor(secao_8, {"pergunta", "escala"}, "opcao", "div", "border-radius")
        == ci.tokens(secao_8)["--raio"]
    )


def test_pergunta_sem_card_nem_sombra(secao_8):
    for propriedade in ("background", "background-color", "box-shadow"):
        assert ci.valor(secao_8, set(), "pergunta", "fieldset", propriedade) is None, propriedade
    for regra in ci.regras(secao_8):
        sombra = regra.declaracoes.get("box-shadow", "none")
        if ".pergunta" in regra.seletor and sombra != "none":
            assert "inset" in sombra, (regra.seletor, sombra)  # marca de acento, não elevação


# --- US3: avisos, pendência × erro, foco do resumo, confirmação (FR-026 a FR-029) -----------


def _borda_esquerda(html: str, classe: str, tag: str = "div") -> str | None:
    return ci.valor(html, set(), classe, tag, ("border-left",))


def _aviso(html: str) -> tuple[str, str]:
    m = re.search(r'<p class="(aviso[^"]*)" role="status">(.*?)</p>', html, re.S)
    assert m, "aviso"
    return m[1], m[2].strip()


def test_variante_fixa_para_cada_codigo_de_aviso():
    from trajetoria.interface import mensagens

    assert set(mensagens.VARIANTE_DO_AVISO) == set(mensagens.AVISOS)
    assert mensagens.VARIANTE_DO_AVISO == {
        "salvo": "sucesso",
        "saida": "informacao",
        "situacao": "informacao",
        "percurso": "informacao",
    }


@pytest.mark.parametrize(
    ("codigo", "variante", "token"),
    [
        ("salvo", "sucesso", "--cor-sucesso"),
        ("saida", "informacao", "--cor-info"),
        ("situacao", "informacao", "--cor-info"),
    ],
)
def test_aviso_da_trajetoria_com_variante(client, cenario, codigo, variante, token):
    from trajetoria.interface import mensagens

    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get(f"/formacoes/?aviso={codigo}"))
    classes, texto = _aviso(html)
    assert classes == f"aviso aviso-{variante}"
    assert texto == mensagens.AVISOS[codigo]
    acento = _borda_esquerda(html, classes, "p")
    assert acento == f"4px solid {ci.tokens(html)[token]}"


def test_aviso_de_percurso_na_secao_e_informativo(client, cenario):
    from trajetoria.interface import mensagens

    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    html = _html(client.get(f"/participacoes/{ana.pk}/secoes/1/?aviso=percurso"))
    classes, texto = _aviso(html)
    assert classes == "aviso aviso-informacao" and texto == mensagens.AVISOS["percurso"]


def _secao_2(client, cenario, *, erro: bool) -> str:
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    c.preencher(ana, cenario.base, [1], ESCOLHAS_ATE_S11)
    dados = ci.dados_validos(ci.secao_do_conteudo(cenario.base.versao, 2))
    if erro:
        dados["p1"] = "99"  # Opção inexistente: erro de forma
        resposta = client.post(f"/participacoes/{ana.pk}/secoes/2/", dados)
        assert resposta.status_code == 200
        return _html(resposta)
    primeiras = sorted(dados, key=lambda campo: int(campo[1:]))[:3]
    client.post(f"/participacoes/{ana.pk}/secoes/2/", {k: dados[k] for k in primeiras})
    return _html(client.get(f"/participacoes/{ana.pk}/secoes/2/?pendencias=1"))


@pytest.mark.parametrize(("erro", "token"), [(False, "--cor-info"), (True, "--cor-erro")])
def test_cores_de_pendencia_e_de_erro(client, cenario, erro, token):
    html = _secao_2(client, cenario, erro=erro)
    cor = ci.tokens(html)[token]
    resumo = re.search(r'<div class="(resumo-erros[^"]*)"', html)[1]
    assert ci.valor(html, {*resumo.split()}, "", "h2") == cor
    assert _borda_esquerda(html, resumo) == f"4px solid {cor}"
    pergunta = re.search(r'class="(pergunta com-erro[^"]*)" id="p\d+"', html)[1]
    assert cor in ci.valor(
        html, set(), pergunta, "fieldset", ("border-left", "border-left-color")
    ) or cor in (ci.valor(html, set(), pergunta, "div", ("border-left", "border-left-color")) or "")
    assert ci.valor(html, set(pergunta.split()), "erro", "p") == cor
    campo = [
        r
        for r in ci.regras(html)
        if r.seletor
        == ('.com-pendencia input[type="text"]' if not erro else '.com-erro input[type="text"]')
    ]
    assert campo and cor in ci.resolver(campo[-1].declaracoes["border-color"], ci.tokens(html))


def test_resumo_focado_ao_carregar_tem_foco_visivel(client, cenario):
    html = _secao_2(client, cenario, erro=False)
    regras = ci.regras(html)
    foco = next(r for r in regras if r.seletor == ":focus-visible").declaracoes
    resumo = [r for r in regras if r.seletor == ".resumo-erros:focus"]
    assert resumo, ".resumo-erros:focus"
    mapa = ci.tokens(html)
    for nome in ("outline", "outline-offset", "box-shadow"):
        assert ci.resolver(resumo[-1].declaracoes[nome], mapa) == ci.resolver(foco[nome], mapa), (
            nome
        )


def test_topo_da_confirmacao_com_acento_de_sucesso(client, cenario):
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    ci.percorrer_pela_interface(
        client, ana.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, COMPLETO)
    )
    client.post(f"/participacoes/{ana.pk}/concluir/")
    html = _html(client.get(f"/participacoes/{ana.pk}/concluida/"))
    topo = re.search(r'<div class="confirmacao">\s*<h1>Pesquisa concluída</h1>', html)
    assert topo, "bloco do topo da confirmação"
    assert _borda_esquerda(html, "confirmacao") == f"4px solid {ci.tokens(html)['--cor-sucesso']}"


def test_confirmacao_separada_da_ficha_sem_mudar_a_ficha(client, cenario):
    """Gate, rodada 3: com a ficha logo abaixo, os fios de sucesso e da marca pareciam uma
    linha só. Só o bloco de sucesso ganha 48 px abaixo, e só quando a ficha vem em seguida;
    a ficha (fio, fundo, espaçamento) não muda."""
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    ci.percorrer_pela_interface(
        client, ana.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, COMPLETO)
    )
    client.post(f"/participacoes/{ana.pk}/concluir/")
    html = _html(client.get(f"/participacoes/{ana.pk}/concluida/"))
    mapa, regras = ci.tokens(html), ci.regras(html)

    separacao = [r for r in regras if r.seletor == ".confirmacao:has(+ .contexto)"]
    assert len(separacao) == 1 and not separacao[0].media
    assert separacao[0].declaracoes == {"margin-bottom": "var(--espaco-7)"}
    assert mapa["--espaco-7"] == "3rem"  # 48 px
    # Fora dessa vizinhança (ex.: agradecimento entre os dois), o bloco mantém 24 px.
    assert ci.valor(html, set(), "confirmacao", "div", "margin") == f"0 0 {mapa['--espaco-5']}"
    # A ficha continua a mesma.
    ficha = [r for r in regras if "contexto" in r.seletor]
    assert all(r.seletor.startswith((".contexto", ".confirmacao:has")) for r in ficha)
    assert ci.valor(html, set(), "contexto", "section", "margin") == f"0 0 {mapa['--espaco-5']}"
    assert ci.valor(html, set(), "contexto", "section", "border-left") == (
        f"4px solid {mapa['--cor-marca']}"
    )
    assert ci.valor(html, set(), "contexto", "section", "background") == mapa["--cor-institucional"]
    # A vizinhança existe quando não há agradecimento entre os blocos.
    assert re.search(r'</div>\s*(<p>[^<]*</p>\s*)?<section class="contexto"', html)


# --- US4: trajetória, contexto, ação principal e divisores (FR-031 a FR-035) ----------------


def test_frase_de_entrada_destaca_a_linha_sem_mudar_o_texto(client, cenario):
    from trajetoria.interface import mensagens
    from trajetoria.interface.apresentacao import resumo_da_formacao

    pessoa = cenario.pessoa("SIM-P-0001")
    ci.entrar_como(client, pessoa)
    html = _html(client.get("/formacoes/"))
    linha = resumo_da_formacao(pessoa.conclusoes.get())
    destaque = mensagens.ENTRADA_FATO.split("{linha}")
    assert f"{destaque[0]}<strong>{linha}{destaque[1]}</strong>" in html
    sem_tags = re.sub(r"<[^>]+>", "", html)
    assert (
        f"{mensagens.ENTRADA_FATO.format(linha=linha)} {mensagens.ENTRADA_CONTINUACAO}" in sem_tags
    )


def test_frase_de_entrada_sem_atributos_continua_neutra(client, cenario, monkeypatch):
    from trajetoria.interface import mensagens

    monkeypatch.setattr("trajetoria.interface.views.resumo_da_formacao", lambda conclusao: "")
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get("/formacoes/"))
    assert mensagens.ENTRADA_SEM_ATRIBUTOS in html and "<strong></strong>" not in html


@pytest.fixture
def trajetoria_com_outras(client, cenario):
    """Trajetória de Ana depois de concluir: a formação aparece em "outras", com situação."""
    resposta = ci.iniciar(client, cenario.pessoa("SIM-P-0001"))
    ana = Participacao.objects.get(pk=ci.participacao_de(resposta))
    ci.percorrer_pela_interface(
        client, ana.pk, cenario.base.versao, ci.escolhas_por_id(cenario.base, COMPLETO)
    )
    client.post(f"/participacoes/{ana.pk}/concluir/")
    return _html(client.get("/formacoes/"))


def test_item_de_formacao_com_hierarquia(trajetoria_com_outras):
    from trajetoria.interface import mensagens
    from trajetoria.participacao.entrada import SituacaoDaFormacao

    html = trajetoria_com_outras
    situacao = mensagens.SITUACAO_DA_FORMACAO[SituacaoDaFormacao.JA_CONCLUIDA]
    assert f'<span class="situacao">{situacao}</span>' in html
    assert f"<strong>{situacao}</strong>" not in html
    assert ci.valor(html, {"formacao"}, "", "strong", "font-weight") == "600"
    assert ci.valor(html, set(), "situacao", "span", "font-weight") == "400"
    assert ci.valor(html, {"formacao"}, "nota", "span", "font-size") == "0.9375rem"
    assert ci.valor(html, {"formacao"}, "nota", "span", "color") == "#565c65"
    divisor = ci.valor(html, {"lista-simples"}, "", "li", ("border-top",))
    assert divisor == f"1px solid {ci.tokens(html)['--cor-borda-suave']}"


def test_contexto_com_voz_institucional(secao_8):
    mapa = ci.tokens(secao_8)
    classes = "contexto contexto-compacto"
    assert (
        ci.valor(secao_8, set(), classes, "section", ("border-left",))
        == f"4px solid {mapa['--cor-marca']}"
    )
    assert (
        ci.valor(secao_8, set(), classes, "section", ("background", "background-color"))
        == mapa["--cor-institucional"]
    )


def test_ficha_empilhada_e_acao_principal_em_largura_total_no_celular(secao_8):
    estreitas = [r for r in ci.regras(secao_8) if "30em" in r.media]
    ficha = [r for r in estreitas if r.seletor == ".contexto dl"]
    assert ficha and ficha[-1].declaracoes.get("grid-template-columns") == "1fr"
    acao = [r for r in estreitas if r.seletor == "main form button.primario"]
    assert acao and acao[-1].declaracoes.get("width") == "100%"


# --- US1: shell institucional da jornada, sem a assinatura (FR-015 a FR-021) ----------------
# A assinatura oficial está bloqueada por D-03 (sem SVG oficial; research R3): nenhum teste
# aqui a exige nem a substitui; T015 acrescenta os testes dela quando o ativo existir.


def _parte(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.S)
    assert m, tag
    return m[1]


def _faixa(html: str) -> str:
    m = re.search(r'<div class="faixa-demonstracao" role="note">(.*?)\n</div>', html, re.S)
    assert m, "faixa"
    return m[1]


def test_cabecalho_com_nome_do_produto_em_texto(telas_da_jornada):
    for nome, html in telas_da_jornada.items():
        cabecalho = _parte(html, "header")
        texto = re.sub(r"<[^>]+>", " ", cabecalho)
        assert "Trajetória Ifes" in texto and "Acompanhamento de egressos" in texto, nome
        assert "<h1" not in cabecalho and "<a " not in cabecalho, nome
        assert "<form" not in cabecalho and "Pessoa fictícia" not in cabecalho, nome


def test_controles_de_demonstracao_na_faixa(client, cenario):
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get("/formacoes/"))
    faixa = _faixa(html)
    assert "Pessoa fictícia: Ana Exemplo" in faixa
    assert "Trocar de pessoa" not in faixa
    assert "Encerrar demonstração" not in faixa
    assert 'action="/acesso/sair/"' in faixa
    assert ">Sair</button>" in faixa
    assert "Ambiente de demonstração." in faixa


def test_rodape_minimo(telas_da_jornada):
    for nome, html in telas_da_jornada.items():
        rodape = re.sub(r"<[^>]+>", " ", _parte(html, "footer"))
        assert "Instituto Federal do Espírito Santo" in rodape, nome
        assert "demonstração local com dados fictícios" in rodape, nome


def test_nenhum_recurso_externo_nem_script(telas_da_jornada):
    for nome, html in telas_da_jornada.items():
        assert "<script" not in html and "<link" not in html, nome
        assert not re.search(r'(src|href)="https?://', html), nome
        assert "@import" not in html and not re.search(r"url\(\s*['\"]?https?:", html), nome


def test_cores_do_shell_e_das_acoes_da_jornada(client, cenario):
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get("/formacoes/"))
    t = ci.tokens(html)
    assert (
        ci.valor(html, set(), "produto", "header", ("border-top",))
        == f"4px solid {t['--cor-marca']}"
    )
    assert (
        ci.valor(html, set(), "produto", "header", ("border-bottom",))
        == f"1px solid {t['--cor-borda-suave']}"
    )
    assert (
        ci.valor(html, set(), "rodape", "footer", ("border-top",))
        == f"1px solid {t['--cor-borda-suave']}"
    )
    assert ci.valor(html, {"coluna"}, "", "a") == t["--cor-acao"]
    assert (
        ci.valor(html, set(), "primario", "button", ("background", "background-color"))
        == t["--cor-acao"]
    )
    assert t["--cor-acao"] in ci.valor(
        html, set(), "secundario", "button", ("border", "border-color")
    )
    assert ci.valor(html, set(), "secundario", "button") == t["--cor-acao"]
    forte = {
        r.seletor for r in ci.regras(html) if "--cor-acao-forte" in " ".join(r.declaracoes.values())
    }
    assert {"button.primario:hover", "button.secundario:hover", "a:hover"} <= forte
    # A faixa de demonstração não usa marca nem ação (FR-021).
    assert (
        ci.valor(html, set(), "faixa-demonstracao", "div", ("background", "background-color"))
        == t["--cor-demonstracao"]
    )
    assert ci.valor(html, {"faixa-demonstracao"}, "", "a") == t["--cor-texto"]
    for regra in ci.regras(html):
        if "faixa-demonstracao" in regra.seletor:
            valores = " ".join(regra.declaracoes.values())
            assert "--cor-marca" not in valores and "--cor-acao" not in valores, regra.seletor


def test_titulos_quebram_palavras_longas_sem_rolagem_horizontal(secao_8):
    """Gate, rodada 1: "Informações Pessoais" a 320 px com fonte a 200% transbordava (SC-005)."""
    for tag in ("h1", "h2"):
        assert ci.valor(secao_8, set(), "", tag, "overflow-wrap") == "break-word", tag


def test_raio_unico_nos_controles(secao_8):
    """Gate, rodada 1 (FR-008, FR-044): raio de 4 px escolhido; o mesmo token em campos,
    listas, células da escala (`.pergunta`, também na prévia) e botões da jornada."""
    raio = ci.tokens(secao_8)["--raio"]
    assert raio == "4px"
    por_seletor = {r.seletor: r.declaracoes for r in ci.regras(secao_8)}
    for seletor in (
        '.pergunta input[type="text"]',
        ".pergunta select",
        ".pergunta .escala .opcao",
        "button.primario",
        "button.secundario",
    ):
        assert ci.resolver(por_seletor[seletor]["border-radius"], ci.tokens(secao_8)) == raio, (
            seletor
        )


# --- T015: assinatura do Ifes (FR-017, FR-018; research R3) ----------------------------------
# Ativo derivado do EPS oficial, aceito pelo solicitante; usado byte a byte (SHA-256).

ASSINATURA = DIR_INTERFACE / "assinatura.svg"
SHA256_DA_ASSINATURA = "bb35783718560dca4ce1a6a20a8fca283881b9371fceb1b4a72f57ce7f387fc7"
NOME_ACESSIVEL = "Instituto Federal do Espírito Santo"


def test_ativo_da_assinatura_e_o_recebido_sem_alteracao():
    import hashlib

    assert hashlib.sha256(ASSINATURA.read_bytes()).hexdigest() == SHA256_DA_ASSINATURA


def test_assinatura_antes_do_nome_em_toda_tela_da_jornada(telas_da_jornada):
    svg = ASSINATURA.read_text(encoding="utf-8").strip()
    for nome, html in telas_da_jornada.items():
        cabecalho = _parte(html, "header")
        m = re.search(
            rf'<span class="assinatura" role="img" aria-label="{NOME_ACESSIVEL}">'
            r"\s*(.*?)\s*</span>",
            cabecalho,
            re.S,
        )
        assert m, nome
        assert m[1] == svg, nome  # incluída inline, sem alteração
        assert cabecalho.index('class="assinatura"') < cabecalho.index("Trajetória Ifes"), nome


def test_assinatura_ausente_fora_da_jornada(telas_fora_da_jornada):
    for nome, html in telas_fora_da_jornada.items():
        assert 'class="assinatura"' not in html and "<svg" not in html, nome


def test_dimensao_da_assinatura_garante_simbolo_minimo(client, cenario):
    """Altura fixa em px: símbolo ≥ 30 px (Manual da Marca); a área de proteção é a margem
    do próprio ativo, sem recorte (research R3)."""
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get("/formacoes/"))
    altura = ci.valor(html, {"assinatura"}, "", "svg", "height")
    assert altura and altura.endswith("px")
    assert float(altura[:-2]) * (219.234375 - 56.375) / 284 >= 30  # símbolo no viewBox 709×284
    assert ci.valor(html, {"assinatura"}, "", "svg", "width") == "auto"


def test_assinatura_maior_onde_cabe_ao_lado_do_nome(client, cenario):
    """Gate, rodada 3: a partir de 22em (352 px), símbolo de 36 px (63 px de altura) e
    cabeçalho de até 68 px (FR-016). Abaixo disso, 54 px (símbolo de 31 px): com 63 px o nome
    passaria para baixo da assinatura a 320 px."""
    ci.entrar_como(client, cenario.pessoa("SIM-P-0001"))
    html = _html(client.get("/formacoes/"))
    simbolo = (219.234375 - 56.375) / 284  # fração do viewBox 709×284 ocupada pelo símbolo
    base = ci.valor(html, {"assinatura"}, "", "svg", "height")
    maior = ci.valor(html, {"assinatura"}, "", "svg", "height", media="min-width: 22em")
    assert base == "54px" and maior == "63px"
    assert 36 <= 63 * simbolo < 37
    fios = 4 + 1  # fio de marca no topo + divisa inferior; sem respiro vertical próprio
    assert 63 + fios <= 68
    medias = [r.media for r in ci.regras(html) if r.seletor == ".assinatura svg"]
    assert medias == ["", "(min-width: 22em)"]

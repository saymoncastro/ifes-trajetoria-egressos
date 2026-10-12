# ruff: noqa: E501 — HTML e CSS embutidos em linhas longas (protótipo).
"""Protótipo estático da Feature 031 (Encontros propostos por egressos). Conceitual.

Cada tela parte do HTML **realmente servido** pela demonstração, na identidade C (032): faixa
de demonstração, cabeçalho, navegação, CSS da 015 e da camada do Portal, fontes locais. Só o
conteúdo principal é trocado, com uma folha própria (`.pe-*`) feita só de tokens existentes.
Toda tela ganha a faixa "Protótipo: não existe no Portal". Os textos são provisórios
(DP-801) e os dados, fictícios. Nada aqui é importado pela aplicação, e as telas servidas não
mudam: não é implementação.

Uso, na raiz do repositório, com o `.env` da demonstração e o banco preparado:

    source .env && uv run python specs/031-encontros-propostos-egressos/prototipo/gerar.py

Depois de gerar, mede e captura cada tela com o arnês dos protótipos da ADR 0009
(`docs/prototipos/2026-10-09-portal/medir.py`, pela variante da 029) e escreve
`medidas.json` e `index.html`. `--sem-capturas` só gera o HTML.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from html import escape
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
CAPTURAS = PASTA / "capturas"
FONTES = "../../../trajetoria/portal/fontes/"
VERSAO = "2026-10-11.1 (provisória)"
ENDERECO = "http://127.0.0.1:8000/encontros/7f3c2a9e-5b1d-4c8e-9a0f-3d2e1c0b9a31/"
LINK = "https://meet.exemplo.org/tecnologia-sala-de-aula"
PESSOAS = {  # personas fictícias da demonstração (fonte simulada, 001)
    "diego": ("000.000.003-53", "08/02/1994"),
    "maria": ("000.000.002-72", "25/11/1997"),
    "bruno": ("111.444.777-35", "03/09/1990"),
    "fernanda": ("000.000.005-15", "21/08/1999"),
}


def e(t) -> str:
    return escape(str(t), quote=True)


# --- Folha do protótipo ---------------------------------------------------------------------

CSS = """
/* 031 — protótipo conceitual. Só tokens da 015 e da camada do Portal (ADR 0009, revisão C):
   verde profundo, creme, verde-claro, verde-médio e verde de rótulo. O vermelho fica só no
   "Hoje" da linha, como na 032. Nada é comunicado só por cor: cada selo tem texto. */
.prototipo { background: #1b1b1b; color: #fff; padding: .5rem 1rem; margin: 0; font-size: .875rem;
  line-height: 1.4; text-align: center; }
.prototipo strong { color: #ffdd00; }
main:has(.pe) { padding: 0; background: var(--portal-creme); }
main:has(.pe) > .coluna { max-width: none; padding: 0; }
.pe h1, .pe h2, .pe h3 { color: var(--portal-profundo); margin: 0; }
.pe h2 { font-size: clamp(1.5rem, 6.5vw, 1.875rem); line-height: 1.05; margin-bottom: .75rem; }
.pe h3 { font-family: var(--portal-fonte-titulo); font-size: 1.375rem; line-height: 1.1; letter-spacing: -0.02em; }
.pe p, .pe li, .pe dd, .pe dt { color: var(--portal-profundo); }
.pe-pagina { padding-block: 1.5rem 3rem; }
.pe-pagina > h1, .pe-abertura h1 { margin-bottom: 1rem; }
.pe-lead { font-size: 1.25rem; line-height: 1.45; }
.pe-nota { color: #3f5b47; font-size: var(--fonte-5); }
.pe-porque { font-weight: 700; }
.pe .ligacao-isolada a, .pe-acoes a { font-weight: 700; color: var(--portal-profundo); }
.pe-acoes { display: flex; flex-wrap: wrap; gap: .75rem 1.25rem; align-items: center; margin: 1.25rem 0 0; }
.pe-acoes a { display: inline-flex; align-items: center; min-height: 44px; }
.pe .pe-botao, .pe button.pe-botao { display: inline-flex; align-items: center; min-height: 48px;
  padding: .625rem 1.5rem; background: var(--portal-profundo); border: 2px solid var(--portal-profundo);
  color: var(--portal-creme); border-radius: 6px; font-weight: 700; font-size: 1.0625rem; text-decoration: none; }
.pe .pe-botao:hover { background: var(--cor-acao); color: #fff; }
.pe .pe-contorno { display: inline-flex; align-items: center; min-height: 48px; padding: .5rem 1.25rem;
  border: 2px solid var(--portal-profundo); border-radius: 6px; text-decoration: none; background: transparent;
  color: var(--portal-profundo); font-weight: 700; }

/* Selos: texto sempre; o círculo vazado é o egresso, o cheio é o Ifes. */
.pe-selo { display: inline-flex; align-items: center; gap: .5rem; margin: 0 0 .75rem; padding: .25rem .75rem;
  border-radius: 999px; font-size: var(--fonte-5); font-weight: 700; line-height: 1.3; }
.pe-selo::before { content: ""; flex: none; width: .75rem; height: .75rem; border-radius: 50%; }
.pe .pe-selo.pe-selo-f { background: var(--portal-verde-claro); color: var(--portal-profundo); border: 2px solid var(--portal-profundo); }
.pe-selo-f::before { border: 2px solid currentColor; }
.pe .pe-selo.pe-selo-a { background: var(--portal-profundo); color: #fff; border: 2px solid var(--portal-profundo); }
.pe-selo-a::before { background: var(--portal-verde-medio); }

/* Página do encontro: faixa com título e data, corpo editorial e a área de participação. */
.pe-hero { background: var(--portal-profundo); padding-block: 1.75rem 2rem; }
.pe .pe-hero h1 { color: var(--portal-creme); font-size: clamp(2rem, 9.5vw, 2.5rem); line-height: 1;
  letter-spacing: -0.035em; margin-bottom: 1.25rem; max-width: 18ch; }
.pe .pe-hero p { color: var(--portal-suave); }
.pe-hero-grade { display: grid; gap: 1.25rem; }
.pe-data { display: grid; grid-template-columns: auto minmax(0, 1fr); column-gap: 1rem; align-items: center;
  margin: 0; padding-top: 1rem; border-top: 1px solid rgba(207, 230, 214, .35); max-width: none; }
.pe-data-dia { grid-row: span 3; font-family: var(--portal-fonte-titulo); font-size: 4.25rem; font-weight: 700;
  line-height: .85; color: var(--portal-verde-medio); }
.pe-data span:not(.pe-data-dia) { display: block; }
.pe .pe-hero .pe-data-mes, .pe .pe-hero .pe-data-hora { color: #fff; font-weight: 700; }
.pe-onde { margin: .75rem 0 0; }
.pe-corpo { display: grid; gap: 2rem; padding-block: 2rem 1rem; }
.pe-bloco + .pe-bloco { margin-top: 2rem; }
.pe-pessoa { display: flex; gap: 1rem; align-items: center; background: #fff; border: 1px solid #e2ddd0;
  border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: .75rem; }
.pe-pessoa p { margin: 0; }
.pe-inicial { flex: none; width: 3.5rem; height: 3.5rem; border-radius: 50%; background: var(--portal-verde-claro);
  color: var(--portal-profundo); display: grid; place-items: center; font-family: var(--portal-fonte-titulo);
  font-size: 1.75rem; font-weight: 700; }
.pe .pe-nome { font-family: var(--portal-fonte-titulo); font-size: 1.375rem; font-weight: 700; line-height: 1.1; }
.pe-participar { background: var(--portal-verde-claro); border-radius: 12px; padding: 1.5rem min(1.5rem, 5vw);
  align-self: start; }
.pe-participar > :last-child { margin-bottom: 0; }
.pe-ciencia { margin: 0 0 1.25rem; padding-left: 1.25rem; }
.pe-ciencia li { margin-bottom: .375rem; }
.pe-versao { font-size: var(--fonte-5); margin: 1rem 0 0; }
.pe-participar form { margin: 0; }
.pe-confirmado { display: flex; gap: .75rem; align-items: center; font-weight: 700; font-size: 1.125rem; }
.pe-confirmado::before { content: ""; flex: none; width: 1.25rem; height: .625rem; margin-top: -.25rem;
  border-left: 3px solid var(--portal-profundo); border-bottom: 3px solid var(--portal-profundo); transform: rotate(-45deg); }
.pe-cartao { background: #fff; border-radius: 10px; padding: 1rem 1.25rem; margin: 1rem 0; }
.pe-cartao > :last-child { margin-bottom: 0; }
.pe-rotulo { font-size: var(--fonte-5); font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  margin: 0 0 .25rem; }
.pe .pe-cartao .pe-rotulo { color: var(--portal-verde-rotulo); }
.pe-cartao a { font-weight: 700; color: var(--portal-profundo); overflow-wrap: anywhere; }
/* Alvos de 44 px nas ligações isoladas do protótipo (como em visual.css). */
.pe-cartao p > a:only-child, .pe-item h3 a, .pe-estados h2 a, .inicio-encontro .oportunidade-titulo a {
  display: inline-flex; align-items: center; min-height: 44px; }
.pe-aviso { border-left: 4px solid var(--portal-profundo); padding: .5rem .75rem; background: rgba(255, 255, 255, .65); }
.pe-endereco { display: block; background: #fff; border: 2px dashed var(--portal-verde-rotulo); padding: .5rem .75rem;
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: .875rem; overflow-wrap: anywhere;
  color: var(--portal-profundo); user-select: all; }
.pe .pe-contagem { font-family: var(--portal-fonte-titulo); font-size: 1.25rem; font-weight: 700; margin: 0 0 .5rem; }
.pe-contagem strong { display: block; font-size: 3.5rem; line-height: 1; }
.pe-situacao { display: inline-block; font-weight: 700; padding: .25rem .75rem; border-radius: 6px;
  background: #fff; border: 2px solid var(--portal-profundo); }
.pe-alterado { background: #fff1d2; border-left: 4px solid var(--portal-profundo); padding: .75rem 1rem; }
.pe .pe-hero .pe-alterado, .pe .pe-hero .pe-alterado strong { color: #1b1b1b; }
.pe-fim { padding-block: 0 2.5rem; }

/* Listas de encontros. F: cartão branco com a data; A: contorno, sem data (025 FR-001). */
.pe-abertura { padding-block: 1.5rem 1rem; }
.pe-grupo { padding-block: 1.75rem; }
.pe-grupo + .pe-grupo { border-top: 1px solid #e2ddd0; }
.pe-lista { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
.pe-lista > li, .pe-estados > li { min-width: 0; }
.pe-item > div { flex: 1 1 12rem; min-width: 0; }
.pe-item-data { flex: none; }
/* Flex que quebra: sem largura para a data e o texto lado a lado (320 px com fonte a 200%), a
   data sobe e o texto ocupa a linha inteira. */
.pe-item { display: flex; flex-wrap: wrap; gap: 1rem; background: #fff;
  border: 1px solid #e2ddd0; border-radius: 10px; padding: 1.25rem min(1.25rem, 4vw); }
.pe-item p { margin: 0 0 .25rem; }
.pe-item .pe-selo { margin-bottom: .5rem; }
.pe-item h3 { margin: 0 0 .5rem; }
.pe-item h3 a { color: var(--portal-profundo); }
.pe-item-data { margin: 0; text-align: center; border-right: 3px solid var(--portal-verde-claro); padding-right: .75rem; }
.pe-item-dia { display: block; font-family: var(--portal-fonte-titulo); font-size: 2.5rem; font-weight: 700;
  line-height: .9; color: var(--portal-profundo); }
.pe-item-mes { display: block; font-size: var(--fonte-5); font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: var(--portal-verde-rotulo); }
.pe-item-a { background: transparent; border: 2px solid var(--portal-profundo); }
.pe-vazio { border: 2px dashed var(--portal-verde-rotulo); border-radius: 10px; padding: 1.25rem; background: rgba(255, 255, 255, .55); }
.pe-vazio > :last-child { margin-bottom: 0; }
.pe-estados { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
.pe-estados > li { background: #fff; border: 1px solid #e2ddd0; border-radius: 10px; padding: 1.25rem min(1.25rem, 4vw); }
.pe-estados h2 { font-family: var(--portal-fonte-titulo); font-size: 1.375rem; margin: 0 0 .5rem; }
.pe-estados h2 a { color: var(--portal-profundo); }
.pe-estados p { margin: 0 0 .25rem; }

/* Início: a seção "Ninguém se forma sozinho." com F e A lado a lado. */
.pe-inicio-par { display: grid; gap: 1rem; }
.pe-inicio-par .inicio-encontro { margin-top: 0; }
.inicio-encontros .pe-acoes a { color: #fff; }
.inicio-encontros .inicio-encontro p.pe-quem-linha { font-size: var(--fonte-5); }

/* Formulários (padrão da 015 e da contribuição da 026). */
.pe input[type=text], .pe input[type=date], .pe input[type=time], .pe input[type=url], .pe textarea {
  display: block; width: 100%; max-width: 36rem; font: inherit; padding: .5rem; min-height: 2.75rem;
  border: 2px solid #565c65; border-radius: 0; background: #fff; color: #1b1b1b; box-sizing: border-box; }
.pe textarea { min-height: 7rem; }
.pe .com-erro input, .pe .com-erro textarea { border-color: #b50909; }
.pe .campo label { display: block; font-weight: 700; margin-bottom: .25rem; }
.pe .pergunta { margin-bottom: 2rem; }
.pe details.pe-escolha { margin: .25rem 0 .75rem; border: 1px solid var(--cor-borda-forte); background: #fff;
  border-radius: var(--raio); padding: 0 1rem; max-width: 36rem; }
.pe details.pe-escolha summary { min-height: 44px; display: flex; align-items: center; font-weight: 700; cursor: pointer;
  color: var(--portal-profundo); }
.pe details.pe-escolha[open] summary { border-bottom: 1px solid #e2ddd0; margin-bottom: .5rem; }
.pe-campos-data { display: grid; gap: 0 1rem; }
.pe .contribuicao-resumo dd { white-space: normal; }
.pe .resumo-erros { background: #fff; }
.pe .resumo-erros li a { color: #b50909; font-weight: 700; }
.pe-previa { border: 2px dashed #c6cace; border-radius: 10px; padding: 1rem; margin: 0 0 1.5rem; background: #fff; }
.pe-previa .pe-item { border: 0; padding: 0; }

@media (min-width: 768px) {
  .pe-pagina { padding-block: 2.5rem 4rem; }
  .pe .pe-hero h1 { font-size: clamp(2.75rem, 5.5vw, 3.75rem); }
  .pe-campos-data { grid-template-columns: repeat(3, minmax(0, 12rem)); }
  .pe-item-data { min-width: 4.5rem; }
}
@media (min-width: 1024px) {
  .pe-hero { padding-block: 3rem 3.5rem; }
  .pe-hero-grade { grid-template-columns: minmax(0, 8fr) minmax(0, 4fr); gap: 3rem; align-items: end; }
  .pe-data { border-top: 0; border-left: 1px solid rgba(207, 230, 214, .35); padding: 0 0 0 2rem; }
  .pe-data-dia { font-size: 6rem; }
  .pe-corpo { grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 3rem; padding-block: 3rem 1.5rem; }
  .pe-lista { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pe-inicio-par { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pe-pagina-estreita { max-width: 52rem; }
}
"""

CSS_OPERADOR = """
/* 031 — protótipo da moderação, no padrão das telas de operação (017, 025). */
.prototipo { background: #1b1b1b; color: #fff; padding: .5rem 1rem; margin: 0; font-size: .875rem;
  line-height: 1.4; text-align: center; }
.prototipo strong { color: #ffdd00; }
#conteudo .rolagem .pe-tabela th, #conteudo .rolagem .pe-tabela td { white-space: normal; vertical-align: top; }
.pe-tabela td:first-of-type { min-width: 7rem; }
.pe-dl { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: .5rem 1rem; }
.pe-dl dt { font-weight: 700; }
.pe-dl dd { margin: 0; overflow-wrap: anywhere; }
.pe-previa { border: 2px dashed #565c65; padding: 1rem; margin: 0 0 1.5rem; }
.pe-previa p { margin: 0 0 .25rem; }
.pe-acoes { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
/* Alvos de 44 px nas ligações isoladas da moderação (células, trilha, ações). */
.pe-tabela td a, .trilha a, .pe-acoes a { display: inline-flex; align-items: center; min-height: 44px; }
textarea { font: inherit; width: 100%; max-width: 36rem; min-height: 6rem; padding: .5rem; border: 2px solid #565c65; }
@media (max-width: 30em) { .pe-dl { grid-template-columns: 1fr; gap: 0; } .pe-dl dd { margin-bottom: .5rem; } }
"""

FAIXA = ('<p class="prototipo" role="note"><strong>Protótipo: não existe no Portal.</strong> '
         'Encontros propostos por egressos (Feature 031), conceitual, com dados fictícios.</p>')


# --- Conteúdo: encontros fictícios ---------------------------------------------------------

TEC = {
    "titulo": "Tecnologia na sala de aula: o que funciona de verdade",
    "descricao": "Conversa entre egressos que dão aula ou trabalham com formação. Cada pessoa traz uma experiência com tecnologia em sala, que deu certo ou não. Sem apresentação de slides.",
    "semana": "quinta-feira", "dia": "29", "mes": "outubro de 2026", "mes_curto": "out",
    "hora": "19h às 20h30", "data": "29/10/2026",
    "nome": "Maria E.", "inicial": "M",
    "origem": "Especialização em Informática na Educação · Cefor · 2025",
    "origem_curta": "Especialização em Informática na Educação (Cefor, 2025)",
    "publico": "Proposto para egressos da Especialização em Informática na Educação (Cefor) e da Licenciatura em Química (Vila Velha). Quem receber o endereço também pode participar.",
    "moderacao": "CPAEG",
}
VOLTAR = {
    "titulo": "Voltar a estudar depois de anos longe da sala de aula",
    "semana": "quinta-feira", "dia": "05", "mes_curto": "nov", "hora": "18h30 às 19h30",
    "nome": "Bruno E.", "origem_curta": "Bacharelado em Engenharia Civil (Vitória, 2020)",
}
PORQUE_DIEGO = "Aparece para você porque você concluiu Licenciatura em Química (Vila Velha, 2017)."

CIENCIA = [
    "Quem propôs vê só quantas pessoas confirmaram. Ninguém vê o seu nome.",
    "O link da reunião aparece aqui depois que você confirmar.",
    "Confirmar não é inscrição e não registra presença.",
    "Você pode cancelar até o início do encontro.",
    "Você não recebe e-mail nem notificação. As mudanças aparecem nesta página.",
    "O encontro acontece fora do Portal, na plataforma do link.",
]
TERMO = [
    "Você propõe e conduz o encontro. O Ifes analisa antes de publicar, mas não organiza.",
    "Na página aparecem o título, a descrição, a data, o público, o nome que você escolheu e a sua formação de origem. Só egressos que entraram no Portal veem a página.",
    "O link da reunião aparece só para quem confirmar. Quem confirmou pode repassá-lo; o Portal não impede.",
    "Você vê quantas pessoas confirmaram, nunca quem são.",
    "A análise não tem prazo garantido. Se não for analisado até a data, o encontro não é publicado.",
    "O Ifes pode recusar ou retirar o encontro, sempre com o motivo. Você pode cancelar até o início.",
    "Depois de publicado, data, horário e uma nova sala na mesma plataforma mudam na hora. Outras mudanças passam por nova análise, e o encontro sai das listas até a decisão.",
    "Ninguém recebe e-mail nem notificação: as mudanças aparecem só na página do encontro.",
]
AVISO_ICS = ("Se a data mudar ou o encontro for cancelado, o calendário que você baixou não muda "
             "sozinho. Confira esta página antes do encontro.")
MOTIVOS = [
    ("finalidade", "Fora da finalidade dos encontros entre egressos"),
    ("comercial", "Divulgação comercial ou venda"),
    ("link", "Link da reunião inadequado"),
    ("confusao", "Informação incompleta ou que pode ser confundida com evento oficial do Ifes"),
    ("respeito", "Desrespeito a pessoas ou à lei"),
    ("outro", "Outro motivo (descreva no complemento)"),
]
MOTIVOS_DENUNCIA = [
    ("link", "Link suspeito ou que não funciona"),
    ("comercial", "Divulgação comercial"),
    ("respeito", "Desrespeito a pessoas"),
    ("oficial", "Parece evento oficial do Ifes"),
    ("outro", "Outro motivo"),
]


def lista_ul(itens, classe="pe-ciencia") -> str:
    return f'<ul class="{classe}">' + "".join(f"<li>{e(i)}</li>" for i in itens) + "</ul>"


def radios(nome, itens, marcado=None) -> str:
    return "".join(
        f'<div class="opcao"><input type="radio" id="{nome}-{v}" name="{nome}" value="{v}"'
        f'{" checked" if v == marcado else ""}><label for="{nome}-{v}">{rotulo}</label></div>'
        for v, rotulo in itens)


def caixas(nome, itens, marcados=()) -> str:
    return "".join(
        f'<div class="opcao"><input type="checkbox" id="{nome}-{i}" name="{nome}" value="{e(v)}"'
        f'{" checked" if v in marcados else ""}><label for="{nome}-{i}">{e(v)}</label></div>'
        for i, v in enumerate(itens))


def hero(enc=TEC, extra="") -> str:
    return f"""<section class="pe-hero" aria-labelledby="pe-titulo">
<div class="portal-container pe-hero-grade">
<div>
<p class="pe-selo pe-selo-f">Encontro proposto por egresso</p>
<h1 id="pe-titulo">{e(enc["titulo"])}</h1>
<p class="pe-onde">Virtual · o link aparece para quem confirmar</p>
</div>
<p class="pe-data"><span class="pe-data-dia" aria-hidden="true">{enc["dia"]}</span><span class="pe-data-semana">{e(enc["semana"])},</span><span class="pe-data-mes">{e(enc["dia"])} de {e(enc["mes"])}</span><span class="pe-data-hora">{e(enc["hora"])} (horário de Brasília)</span></p>
{extra}
</div>
</section>"""


def sobre(enc=TEC, porque=PORQUE_DIEGO, para_quem=None) -> str:
    para_quem = para_quem or f'<p>{e(enc["publico"])}</p><p class="pe-porque">{e(porque)}</p>'
    return f"""<div class="pe-texto">
<section class="pe-bloco" aria-labelledby="pe-sobre"><h2 id="pe-sobre">Sobre o encontro</h2><p>{e(enc["descricao"])}</p></section>
<section class="pe-bloco" aria-labelledby="pe-quem"><h2 id="pe-quem">Quem propõe</h2>
<div class="pe-pessoa"><span class="pe-inicial" aria-hidden="true">{enc["inicial"]}</span><div><p class="pe-nome">{e(enc["nome"])}</p><p class="pe-nota">Nome escolhido por quem propõe</p><p>{e(enc["origem"])} <span class="inicio-origem">· Registro do Ifes</span></p></div></div>
<p class="pe-nota">Publicado depois da análise da {e(enc["moderacao"])}. O Ifes revisou a proposta, mas não organiza este encontro: quem conduz é a pessoa que propôs.</p></section>
<section class="pe-bloco" aria-labelledby="pe-para-quem"><h2 id="pe-para-quem">Para quem foi proposto</h2>{para_quem}</section>
</div>"""


def participar() -> str:
    return f"""<section class="pe-participar" aria-labelledby="pe-participar">
<h2 id="pe-participar">Vou participar?</h2>
{lista_ul(CIENCIA)}
<form method="post" action="p4-confirmado.html"><button type="submit" class="pe-botao pe-acao-principal">Vou participar</button></form>
<p class="pe-versao">Ciência da participação, versão {e(VERSAO)}.</p>
</section>"""


def confirmado() -> str:
    return f"""<section class="pe-participar" aria-labelledby="pe-participar">
<h2 id="pe-participar" class="pe-confirmado">Você vai participar</h2>
<p>Confirmado em 14/10/2026. Quem propôs vê só que há mais uma pessoa, sem o seu nome.</p>
<div class="pe-cartao"><p class="pe-rotulo">Link da reunião</p>
<p><a href="{e(LINK)}" rel="noreferrer">{e(LINK.removeprefix("https://"))}</a></p>
<p class="pe-nota">site externo: meet.exemplo.org · sala criada por quem propôs, fora do Portal</p></div>
<div class="pe-cartao"><p class="pe-rotulo">Calendário</p>
<p><a href="exemplo.ics" download="encontro.ics">Adicionar ao calendário (.ics)</a></p>
<p class="pe-nota">{e(AVISO_ICS)}</p></div>
<p class="pe-acoes"><a class="pe-contorno" href="p5-cancelar-participacao.html">Cancelar minha participação</a></p>
<p class="pe-nota">Para indicar o encontro a alguém, envie o endereço desta página. A pessoa precisa confirmar os dados no Portal para ver.</p>
<span class="pe-endereco">{e(ENDERECO)}</span>
</section>"""


def rodape_encontro(denunciado=False) -> str:
    denuncia = ('<p class="pe-nota">Você denunciou este encontro em 15/10/2026.</p>' if denunciado
                else '<p class="ligacao-isolada"><a href="p12-denunciar.html">Denunciar este encontro</a></p>')
    return f"""<div class="portal-container pe-fim">{denuncia}
<p class="ligacao-isolada"><a href="p2-encontros.html">Ver todos os encontros</a></p></div>"""


def pagina_encontro(lateral, enc=TEC, extra_hero="", para_quem=None, aviso="", denunciado=False) -> str:
    return f"""<div class="pe">{aviso}{hero(enc, extra_hero)}
<div class="portal-container pe-corpo">{sobre(enc, para_quem=para_quem)}{lateral}</div>
{rodape_encontro(denunciado)}</div>"""


# --- Telas do participante ------------------------------------------------------------------

def item_f(enc, porque, destino="p3-encontro.html") -> str:
    return f"""<li class="pe-item"><p class="pe-item-data" aria-hidden="true"><span class="pe-item-dia">{enc["dia"]}</span><span class="pe-item-mes">{enc["mes_curto"]}</span></p>
<div><p class="pe-selo pe-selo-f">Proposto por egresso</p>
<h3><a href="{destino}">{e(enc["titulo"])}</a></h3>
<p>{e(enc["semana"]).capitalize()}, {enc["dia"]}/{"10" if enc["mes_curto"] == "out" else "11"} · {e(enc["hora"])} · virtual</p>
<p>Proposto por {e(enc["nome"])} · {e(enc["origem_curta"])}</p>
<p class="oportunidade-por-que">{e(porque)}</p></div></li>"""


ITEM_A = """<li class="pe-item pe-item-a" id="evento-ifes"><div><p class="pe-selo pe-selo-a">Evento do Ifes</p>
<h3><a href="p2-encontros.html#evento-ifes" rel="noreferrer">Semana da Química: mesa com egressos<span class="visualmente-oculto"> — site do Ifes: vilavelha.ifes.edu.br</span></a></h3>
<p>Mesa de conversa com egressos da Química durante a semana acadêmica, no campus.</p>
<p class="oportunidade-por-que">Aparece porque você concluiu Licenciatura em Química (Vila Velha, 2017).</p>
<p class="oportunidade-origem">Divulgado pela unidade Vila Velha · site do Ifes: vilavelha.ifes.edu.br</p></div></li>"""


def encontros() -> str:
    return f"""<div class="pe">
<section class="pe-abertura" aria-labelledby="pe-titulo"><div class="portal-container">
<h1 id="pe-titulo">Encontros</h1>
<p class="pe-lead">Encontros da comunidade de egressos do Ifes. Alguns são propostos por egressos; outros são eventos divulgados pelo Ifes.</p>
<p class="pe-acoes"><a class="pe-botao" href="o1-propor.html">Propor um encontro</a> <a href="o10-seus-vazio.html">Seus encontros</a></p>
</div></section>
<section class="pe-grupo" aria-labelledby="pe-g-f"><div class="portal-container">
<h2 id="pe-g-f">Propostos por egressos</h2>
<p class="pe-nota">Cada um foi analisado pelo Ifes antes de aparecer aqui. Quem propõe é quem conduz.</p>
<ol class="pe-lista">{item_f(TEC, "Aparece porque você concluiu Licenciatura em Química (Vila Velha, 2017).")}{item_f(VOLTAR, "Aberto a todos os egressos do Ifes.", "p3-encontro.html")}</ol>
</div></section>
<section class="pe-grupo" aria-labelledby="pe-g-a"><div class="portal-container">
<h2 id="pe-g-a">Eventos do Ifes</h2>
<p class="pe-nota">Divulgados pelas unidades. Data, local e inscrição estão na página oficial.</p>
<ul class="pe-lista">{ITEM_A}</ul>
</div></section></div>"""


def secao_inicio() -> str:
    return f"""<section class="inicio-encontros portal-faixa" aria-labelledby="inicio-encontros">
  <div class="portal-container inicio-duas">
    <div>
      <h2 id="inicio-encontros">Ninguém se forma sozinho.</h2>
      <p>Encontros da comunidade de egressos: alguns propostos por egressos, outros divulgados pelo Ifes.</p>
      <p class="pe-acoes"><a href="p2-encontros.html">Ver todos os encontros</a> <a href="o1-propor.html">Propor um encontro</a></p>
    </div>
    <div class="pe-inicio-par pe">
      <div class="inicio-encontro"><p class="pe-selo pe-selo-f">Proposto por egresso</p>
        <p class="oportunidade-titulo"><a href="p3-encontro.html">{e(TEC["titulo"])}</a></p>
        <p>Quinta-feira, 29/10 · {e(TEC["hora"])} · virtual</p>
        <p class="pe-quem-linha">Proposto por {e(TEC["nome"])} · {e(TEC["origem_curta"])}</p></div>
      <div class="inicio-encontro"><p class="pe-selo pe-selo-a">Evento do Ifes</p>
        <p class="oportunidade-titulo"><a href="p2-encontros.html#evento-ifes">Semana da Química: mesa com egressos</a></p>
        <p>Data e local na página oficial</p>
        <p class="pe-quem-linha">Divulgado pela unidade Vila Velha · site do Ifes</p></div>
    </div>
  </div>
</section>
"""


def encontro() -> str:
    return pagina_encontro(participar())


def encontro_confirmado() -> str:
    return pagina_encontro(confirmado())


def cancelar_participacao() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Cancelar sua participação</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<p>Quinta-feira, 29/10/2026, {e(TEC["hora"])}.</p>
<ul class="pe-ciencia"><li>O link da reunião deixa de aparecer para você.</li><li>Quem propôs passa a ver uma confirmação a menos, sem saber quem cancelou.</li><li>Você pode confirmar de novo até o início do encontro.</li></ul>
<form method="post" action="p3-encontro.html"><p class="pe-acoes"><button type="submit" class="pe-botao">Cancelar participação</button> <a href="p4-confirmado.html">Voltar sem cancelar</a></p></form>
</div></div>"""


def sem_sessao() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<p class="pe-selo pe-selo-f">Encontro entre egressos</p>
<h1>Encontro no Portal do Egresso</h1>
<p class="pe-lead">Este endereço leva a um encontro entre egressos do Ifes. Para ver a data, a descrição e quem propõe, confirme seus dados.</p>
<p class="pe-acoes"><a class="pe-botao pe-acao-principal" href="p3-encontro.html">Confirme seus dados para ver</a></p>
<p class="pe-nota">São pedidos o CPF e a data de nascimento registrados no Ifes. Depois, você volta a este encontro.</p>
<p class="pe-nota">Os encontros são para quem tem formação concluída registrada no Ifes.</p>
</div></div>"""


def fora_do_publico() -> str:
    para_quem = ('<p>Proposto para egressos da Especialização em Informática na Educação (Cefor) e da Licenciatura em Química (Vila Velha).</p>'
                 '<p class="pe-aviso"><strong>Você recebeu este endereço.</strong> '
                 'O encontro não aparece na sua lista porque foi pensado para essas formações, mas você também pode participar.</p>')
    return pagina_encontro(participar(), para_quem=para_quem)


def data_alterada() -> str:
    enc = {**TEC, "semana": "terça-feira", "dia": "03", "mes": "novembro de 2026"}
    extra = ('<p class="pe-alterado" role="note"><strong>Data alterada em 20/10/2026.</strong> Era 29/10. '
             'Se você baixou o calendário antes, baixe de novo: o arquivo antigo não muda sozinho.</p>')
    return pagina_encontro(confirmado(), enc=enc, extra_hero=extra)


def cancelado() -> str:
    return f"""<div class="pe">{hero(TEC, '<p class="pe-alterado" role="note"><strong>Cancelado por quem propôs em 22/10/2026.</strong> O encontro não vai acontecer, e o link não está mais disponível.</p>')}
<div class="portal-container pe-corpo">{sobre()}<section class="pe-participar" aria-labelledby="pe-situacao"><h2 id="pe-situacao">Encontro cancelado</h2>
<p>Se você tinha baixado o calendário, apague o compromisso: o arquivo não muda sozinho.</p>
<p class="pe-acoes"><a class="pe-botao" href="p2-encontros.html">Ver outros encontros</a></p></section></div></div>"""


def encerrado() -> str:
    return f"""<div class="pe">{hero(TEC)}
<div class="portal-container pe-corpo">{sobre()}<section class="pe-participar" aria-labelledby="pe-situacao"><h2 id="pe-situacao">Encontro encerrado</h2>
<p>Terminou em 29/10/2026, às 20h30. O link da reunião não aparece mais.</p>
<p class="pe-acoes"><a class="pe-botao" href="p2-encontros.html">Ver outros encontros</a> <a href="o1-propor.html">Propor um encontro</a></p></section></div>
{rodape_encontro()}</div>"""


def vazio() -> str:
    return """<div class="pe">
<section class="pe-abertura" aria-labelledby="pe-titulo"><div class="portal-container">
<h1 id="pe-titulo">Encontros</h1>
<p class="pe-lead">Encontros da comunidade de egressos do Ifes. Alguns são propostos por egressos; outros são eventos divulgados pelo Ifes.</p>
</div></section>
<section class="pe-grupo" aria-labelledby="pe-g-f"><div class="portal-container">
<h2 id="pe-g-f">Propostos por egressos</h2>
<div class="pe-vazio"><p><strong>Nenhum encontro proposto para a sua formação agora.</strong></p>
<p>Você pode propor o primeiro: um tema da sua área, uma conversa sobre carreira ou sobre voltar a estudar.</p>
<p class="pe-acoes"><a class="pe-botao" href="o1-propor.html">Propor um encontro</a></p></div>
</div></section>
<section class="pe-grupo" aria-labelledby="pe-g-a"><div class="portal-container">
<h2 id="pe-g-a">Eventos do Ifes</h2>
<p>Nenhum evento divulgado pelo Ifes para a sua formação agora.</p>
</div></section></div>"""


def denunciar() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Denunciar este encontro</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<p>A CPAEG, responsável por este encontro, recebe a denúncia. Quem propôs não vê a denúncia, e a moderação não vê quem denunciou.</p>
<form method="post" action="p13-denuncia-enviada.html" novalidate>
<fieldset class="pergunta"><legend>Qual é o problema?</legend>{radios("motivo", MOTIVOS_DENUNCIA, "link")}</fieldset>
<div class="campo"><label for="complemento">Conte o que aconteceu <span class="opcional">(opcional)</span></label>
<p class="dica" id="complemento-dica">Até 300 caracteres. Não inclua CPF, telefone, endereço ou outros dados pessoais.</p>
<textarea id="complemento" name="complemento" maxlength="300" aria-describedby="complemento-dica">O link pede para instalar um programa antes de entrar.</textarea></div>
<p class="pe-acoes"><button type="submit" class="pe-botao">Enviar denúncia</button> <a href="p4-confirmado.html">Voltar ao encontro</a></p>
</form></div></div>"""


def denuncia_enviada() -> str:
    aviso = ('<div class="portal-container"><p role="status" class="aviso aviso-sucesso" style="margin:1rem 0 0;background:#fff">'
             'Denúncia enviada à CPAEG. Não há prazo garantido de análise, e você não recebe resposta automática.</p></div>')
    return pagina_encontro(confirmado(), aviso=aviso, denunciado=True)


def conflito() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Não foi possível confirmar</h1>
<p class="pe-lead">Este encontro foi retirado pela moderação do Ifes enquanto você confirmava. Nada foi registrado.</p>
<p class="pe-acoes"><a class="pe-botao" href="p2-encontros.html">Ver outros encontros</a></p>
</div></div>"""


# --- Telas do organizador -------------------------------------------------------------------

UNIDADES = ["Alegre", "Cachoeiro de Itapemirim", "Cariacica", "Cefor", "Colatina", "Serra", "Viana", "Vila Velha", "Vitória"]
NIVEIS = ["Técnico", "Graduação", "Pós-graduação"]
CURSOS = ["Bacharelado em Engenharia Civil", "Especialização em Informática na Educação",
          "Licenciatura em Química", "Mestrado Profissional em Química", "Técnico em Agropecuária",
          "Técnico em Edificações", "Técnico em Informática", "Técnico em Mecânica", "Técnico em Química",
          "Tecnologia em Análise e Desenvolvimento de Sistemas"]
ESCOLHIDOS = ("Especialização em Informática na Educação", "Licenciatura em Química")


def campo(id_, rotulo, controle, dica="", erro="") -> str:
    desc = " ".join(x for x in (f"{id_}-dica" if dica else "", f"{id_}-erro" if erro else "") if x)
    controle = controle.replace("{desc}", f' aria-describedby="{desc}"' if desc else "")
    if erro:
        controle = controle.replace(" id=", ' aria-invalid="true" id=', 1)
    return (f'<div class="campo{" com-erro" if erro else ""}" id="campo-{id_}"><label for="{id_}">{rotulo}</label>'
            + (f'<p class="dica" id="{id_}-dica">{dica}</p>' if dica else "")
            + (f'<p class="erro" id="{id_}-erro">{e(erro)}</p>' if erro else "")
            + controle + "</div>")


def formulario(erros=None) -> str:
    erros = erros or {}
    v = {"titulo": "" if "titulo" in erros else TEC["titulo"], "data": "2026-10-29", "inicio": "19:00",
         "termino": "18:30" if "termino" in erros else "20:30",
         "link": "meet.exemplo.org/tecnologia sala" if "link" in erros else LINK}
    resumo = ""
    if erros:
        resumo = ('<div class="resumo-erros" role="alert" tabindex="-1" autofocus><h2>Corrija para continuar</h2><ul>'
                  + "".join(f'<li><a href="#campo-{k}">{e(m)}</a></li>' for k, m in erros.items()) + "</ul></div>")
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Propor um encontro</h1>
{resumo}
<p class="pe-lead">Um encontro virtual entre egressos, conduzido por você. O Ifes analisa antes de publicar.</p>
<form method="post" action="o3-confira.html" novalidate>
{campo("titulo", "Título", f'<input type="text" id="titulo" name="titulo" maxlength="90" value="{e(v["titulo"])}"{{desc}}>', "Até 90 caracteres.", erros.get("titulo", ""))}
{campo("descricao", "Do que vocês vão conversar", f'<textarea id="descricao" name="descricao" maxlength="400"{{desc}}>{e(TEC["descricao"])}</textarea>', "Até 400 caracteres. Não inclua telefone, e-mail ou outros contatos.")}
<div class="pe-campos-data">
{campo("data", "Data", f'<input type="date" id="data" name="data" min="2026-10-13" max="2027-01-09" value="{v["data"]}"{{desc}}>', "Entre 13/10/2026 e 09/01/2027.", erros.get("data", ""))}
{campo("inicio", "Início", f'<input type="time" id="inicio" name="inicio" value="{v["inicio"]}"{{desc}}>', "Horário de Brasília.")}
{campo("termino", "Término", f'<input type="time" id="termino" name="termino" value="{v["termino"]}"{{desc}}>', "Até 3 horas depois do início.", erros.get("termino", ""))}
</div>
<fieldset class="pergunta" id="campo-publico"><legend>Para quem o encontro aparece? <span class="nota">Ele aparece na lista de quem tem essas formações. Quem receber o endereço também pode participar. Não precisa incluir a sua formação: um tema pode reunir egressos de cursos e unidades diferentes.</span></legend>
{radios("publico", [("todos", "Todos os egressos do Ifes"), ("formacoes", "Egressos de certas unidades, níveis ou cursos")], "formacoes")}
<details class="pe-escolha"><summary>Unidades (nenhuma escolhida)</summary>{caixas("unidade", UNIDADES)}</details>
<details class="pe-escolha"><summary>Níveis (nenhum escolhido)</summary>{caixas("nivel", NIVEIS)}</details>
<details class="pe-escolha" open><summary>Cursos (2 escolhidos)</summary>{caixas("curso", CURSOS, ESCOLHIDOS)}</details>
<p class="pe-nota">Quem analisa na demonstração: a CSAEG da unidade, se você escolher uma só unidade; a CPAEG, nos demais casos.</p>
</fieldset>
{campo("link", "Link da reunião", f'<input type="url" id="link" name="link" maxlength="500" value="{e(v["link"])}"{{desc}}>', "Crie a sala na plataforma que preferir e cole o endereço, começando com https://. Ele só aparece para quem confirmar.", erros.get("link", ""))}
{campo("nome", "Como você quer se apresentar", '<input type="text" id="nome" name="nome" maxlength="40" value="Maria E."{desc}>', "Aparece na página do encontro. Pode ser só o primeiro nome.")}
<fieldset class="pergunta"><legend>Sua formação de origem <span class="nota">Aparece como registro do Ifes. Não limita quem pode participar.</span></legend>
{radios("origem", [("c4", "Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022"), ("c5", "Especialização em Informática na Educação · Cefor · 2025")], "c5")}
</fieldset>
<p class="pe-acoes"><button type="submit" class="pe-botao">Continuar</button> <a href="p2-encontros.html">Voltar aos encontros</a></p>
</form></div></div>"""


def propor() -> str:
    return formulario()


def propor_erros() -> str:
    return formulario({
        "titulo": "Informe o título.",
        "termino": "O término precisa ser depois do início, no mesmo dia, com até 3 horas.",
        "link": "O link precisa começar com https:// e não pode ter espaços.",
    })


def previa() -> str:
    return f"""<div class="pe-previa" aria-labelledby="pe-previa-titulo"><p class="pe-rotulo" id="pe-previa-titulo">Como os egressos verão na lista</p>
<ul class="pe-lista">{item_f(TEC, "Aparece porque você concluiu … (cada pessoa vê a própria formação).", "#")}</ul></div>"""


def confira() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Confira e envie</h1>
{previa()}
<dl class="contribuicao-resumo">
<dt>Descrição</dt><dd>{e(TEC["descricao"])}</dd>
<dt>Quando</dt><dd>Quinta-feira, 29/10/2026, {e(TEC["hora"])} (horário de Brasília)</dd>
<dt>Onde aparece</dt><dd>{e(TEC["publico"])}</dd>
<dt>Quem analisa</dt><dd>CPAEG, porque o público inclui mais de uma unidade.</dd>
<dt>Link da reunião</dt><dd>{e(LINK)} · site externo</dd>
<dt>Como você aparece</dt><dd>Maria E. · {e(TEC["origem"])} (registro do Ifes)</dd>
</dl>
<section class="contribuicao-ciencia" aria-labelledby="pe-termo"><h2 id="pe-termo">Antes de enviar</h2>
<ul>{"".join(f"<li>{e(t)}</li>" for t in TERMO)}</ul>
<p class="contribuicao-versao">Termo do organizador, versão {e(VERSAO)}.</p></section>
<form method="post" action="o4-em-analise.html"><p class="pe-acoes"><button type="submit" class="pe-botao">Enviar para análise</button> <a href="o1-propor.html">Voltar e alterar</a></p></form>
</div></div>"""


def em_analise() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<p role="status" class="aviso aviso-sucesso" style="background:#fff">Encontro enviado para análise.</p>
<h1>{e(TEC["titulo"])}</h1>
<p><span class="pe-situacao">Em análise pela CPAEG desde 11/10/2026</span></p>
<ul class="pe-ciencia">
<li>Ainda não aparece para ninguém.</li>
<li>Quando a CPAEG decidir, a situação muda aqui e em Seus encontros. Você não recebe e-mail.</li>
<li>Se não for analisado até 29/10/2026, às 19h, o encontro não é publicado.</li>
<li>Enquanto estiver em análise, você pode editar tudo ou cancelar.</li>
</ul>
<p class="pe-acoes"><a class="pe-contorno" href="o1-propor.html">Editar</a> <a href="o8-cancelar.html">Cancelar este encontro</a> <a href="o5-seus-encontros.html">Seus encontros</a></p>
</div></div>"""


def seus_encontros() -> str:
    itens = [
        ("o6-publicado.html", TEC["titulo"], "Quinta-feira, 29/10/2026 · 19h às 20h30", "Publicado em 13/10/2026 pela CPAEG", "12 pessoas confirmaram"),
        ("", "Café virtual: primeiro emprego em TI", "Terça-feira, 10/11/2026 · 19h às 20h", "Em análise pela CSAEG Serra desde 11/10/2026", "O público é só a unidade Serra."),
        ("o9-recusado.html", "Mentoria para concursos públicos", "Sábado, 17/10/2026 · 10h às 11h", "Recusado em 08/10/2026 pela CPAEG", "Motivo: divulgação comercial ou venda."),
        ("", "Roda de conversa: primeiros anos de docência", "Sexta-feira, 02/10/2026 · 19h às 20h", "Encerrado", "7 pessoas confirmaram"),
        ("", "Leituras sobre educação a distância", "Quarta-feira, 07/10/2026 · 20h às 21h", "Cancelado por você em 01/10/2026", ""),
        ("", "Mestrado depois da especialização: vale a pena?", "Domingo, 20/09/2026 · 18h às 19h", "Não analisado a tempo", "Não foi publicado."),
    ]
    lis = "".join(
        f'<li><h2>{f"<a href=\"{d}\">{e(t)}</a>" if d else e(t)}</h2><p>{e(q)}</p><p><span class="pe-situacao">{e(s)}</span></p>'
        + (f"<p>{e(x)}</p>" if x else "") + "</li>" for d, t, q, s, x in itens)
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Seus encontros</h1>
<p class="pe-lead">Os encontros que você propôs. Você vê quantas pessoas confirmaram, nunca quem são.</p>
<p class="pe-acoes"><a class="pe-botao" href="o1-propor.html">Propor um encontro</a></p>
<ol class="pe-estados">{lis}</ol>
<p class="ligacao-isolada"><a href="p2-encontros.html">Voltar aos encontros</a></p>
</div></div>"""


def seus_vazio() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Seus encontros</h1>
<div class="pe-vazio"><p><strong>Você ainda não propôs nenhum encontro.</strong></p>
<p>Um encontro pode ser uma conversa sobre a sua área, sobre carreira ou sobre voltar a estudar, com egressos de qualquer curso ou unidade.</p>
<p class="pe-acoes"><a class="pe-botao" href="o1-propor.html">Propor um encontro</a></p></div>
<p class="ligacao-isolada"><a href="p2-encontros.html">Voltar aos encontros</a></p>
</div></div>"""


def organizador_lateral() -> str:
    return f"""<section class="pe-participar" aria-labelledby="pe-participar">
<h2 id="pe-participar">Você propôs este encontro</h2>
<p><span class="pe-situacao">Publicado em 13/10/2026, depois da análise da CPAEG</span></p>
<p class="pe-contagem"><strong>12</strong> pessoas confirmaram</p>
<p class="pe-nota">Você vê só o número. Ninguém, nem você, vê quem confirmou.</p>
<div class="pe-cartao"><p class="pe-rotulo">Link da reunião</p><p><a href="{e(LINK)}" rel="noreferrer">{e(LINK.removeprefix("https://"))}</a></p>
<p class="pe-nota">Aparece para quem confirmou. Uma nova sala na mesma plataforma vale na hora; outra plataforma passa por nova análise.</p></div>
<div class="pe-cartao"><p class="pe-rotulo">Para compartilhar</p><p>Envie o endereço desta página. Quem receber precisa confirmar os dados no Portal para ver.</p>
<span class="pe-endereco">{e(ENDERECO)}</span>
<p><a href="exemplo.ics" download="encontro.ics">Adicionar ao calendário (.ics)</a></p></div>
<p class="pe-acoes"><a class="pe-contorno" href="o7-alterar-data.html">Alterar data e horário</a> <a class="pe-contorno" href="o11-corrigir-link.html">Corrigir o link</a></p>
<p class="pe-acoes"><a href="o12-alterar-encontro.html">Alterar título, descrição ou público</a> <a href="o8-cancelar.html">Cancelar este encontro</a></p>
</section>"""


def publicado() -> str:
    return pagina_encontro(organizador_lateral(), para_quem=f'<p>{e(TEC["publico"])}</p>')


def alterar_data() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Alterar data e horário</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<p class="pe-aviso">As 12 confirmações continuam. Ninguém é avisado: a página passa a mostrar "Data alterada em …", e quem baixou o calendário continua com a data antiga no arquivo.</p>
<form method="post" action="p8-data-alterada.html" novalidate>
<div class="pe-campos-data">
{campo("data", "Nova data", '<input type="date" id="data" name="data" value="2026-11-03"{desc}>', "Antes do início, até 09/01/2027.")}
{campo("inicio", "Início", '<input type="time" id="inicio" name="inicio" value="19:00"{desc}>', "Horário de Brasília.")}
{campo("termino", "Término", '<input type="time" id="termino" name="termino" value="20:30"{desc}>', "Até 3 horas depois do início.")}
</div>
<p class="pe-nota">Data e horário são correção operacional: não passam por nova análise. Para mudar título, descrição, público ou nome, use "Alterar título, descrição ou público": a mudança passa por nova análise.</p>
<p class="pe-acoes"><button type="submit" class="pe-botao">Salvar nova data</button> <a href="o6-publicado.html">Voltar sem alterar</a></p>
</form></div></div>"""


def cancelar() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Cancelar este encontro</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<ul class="pe-ciencia">
<li>O encontro sai das listas, e a página passa a dizer "Cancelado por quem propôs".</li>
<li>O link deixa de aparecer.</li>
<li>As 12 pessoas que confirmaram não são avisadas automaticamente: elas verão o cancelamento na página.</li>
<li>O cancelamento não pode ser desfeito. Para fazer o encontro em outra data, altere a data em vez de cancelar.</li>
</ul>
<form method="post" action="p9-cancelado.html"><p class="pe-acoes"><button type="submit" class="pe-botao">Cancelar o encontro</button> <a href="o6-publicado.html">Voltar sem cancelar</a></p></form>
</div></div>"""


def recusado() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Mentoria para concursos públicos</h1>
<p><span class="pe-situacao">Recusado pela CPAEG em 08/10/2026</span></p>
<div class="pe-cartao"><p class="pe-rotulo">Motivo</p><p><strong>Divulgação comercial ou venda.</strong></p>
<p>"A descrição oferece um curso pago. Encontros entre egressos não divulgam venda de produtos ou serviços."</p></div>
<p>A recusa é definitiva e o encontro não aparece para ninguém. Você pode propor outro encontro a partir destes dados.</p>
<p class="pe-acoes"><a class="pe-botao" href="o1-propor.html">Propor de novo com estes dados</a> <a href="o5-seus-encontros.html">Seus encontros</a></p>
</div></div>"""


def corrigir_link() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Corrigir o link da reunião</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<form method="post" action="o6-publicado.html" novalidate>
{campo("link", "Novo link", '<input type="url" id="link" name="link" maxlength="500" value="https://meet.exemplo.org/tecnologia-sala-2"{desc}>', "Link analisado: meet.exemplo.org/tecnologia-sala-de-aula.")}
<ul class="pe-ciencia">
<li><strong>Na mesma plataforma</strong> (meet.exemplo.org): o novo link vale na hora, para quem confirmou, e a página mostra "Link atualizado em …".</li>
<li><strong>Em outra plataforma</strong>: a mudança passa por nova análise da CPAEG. Até a decisão, o encontro sai das listas e o link não aparece. As 12 confirmações continuam.</li>
<li>Ninguém é avisado automaticamente. O calendário baixado não tem o link, então não muda.</li>
</ul>
<p class="pe-acoes"><button type="submit" class="pe-botao">Salvar novo link</button> <a href="o6-publicado.html">Voltar sem alterar</a></p>
</form></div></div>"""


def alterar_encontro() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Confira a alteração</h1>
<p class="pe-lead">{e(TEC["titulo"])}</p>
<dl class="contribuicao-resumo">
<dt>Campos alterados</dt><dd>Descrição; para quem aparece (acrescentado: Mestrado Profissional em Química)</dd>
<dt>Quem analisa</dt><dd>CPAEG</dd>
</dl>
<section class="contribuicao-ciencia" aria-labelledby="pe-efeito"><h2 id="pe-efeito">O que acontece até a decisão</h2>
<ul>
<li>O encontro sai das listas, e a página passa a dizer "Em revisão depois de uma alteração".</li>
<li>O link deixa de aparecer, inclusive para quem confirmou.</li>
<li>As 12 confirmações continuam.</li>
<li>Se for publicado de novo, o encontro volta às listas com "Alterado em …".</li>
<li>Se a alteração for recusada, o encontro é retirado, com o motivo. A versão anterior não é guardada.</li>
<li>Se não houver decisão até o início, o encontro não acontece pelo Portal.</li>
</ul></section>
<form method="post" action="o5-seus-encontros.html"><p class="pe-acoes"><button type="submit" class="pe-botao">Enviar alteração para análise</button> <a href="o6-publicado.html">Voltar sem alterar</a></p></form>
</div></div>"""


def em_revisao() -> str:
    """FR-024a: em revisão, o conteúdo alterado ainda não foi moderado. Quem confirmou vê só a
    situação, a data e o horário."""
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<p class="pe-selo pe-selo-f">Encontro proposto por egresso</p>
<h1>Encontro em revisão</h1>
<p class="pe-lead">Quem propôs alterou este encontro em 20/10/2026, e a moderação do Ifes está analisando a alteração. O conteúdo volta a aparecer se ele for publicado de novo.</p>
<div class="pe-participar"><p class="pe-confirmado">Você vai participar</p>
<p>Quinta-feira, 29/10/2026, {e(TEC["hora"])} (horário de Brasília).</p>
<p>Sua confirmação continua. O link da reunião não aparece enquanto o encontro estiver em revisão. Confira esta página antes do encontro: você não recebe aviso.</p>
<p class="pe-acoes"><a class="pe-contorno" href="p5-cancelar-participacao.html">Cancelar minha participação</a></p></div>
<p class="ligacao-isolada"><a href="p2-encontros.html">Ver outros encontros</a></p>
</div></div>"""


def reanalisar() -> str:
    return f"""{trilha(("m1-fila.html", "Moderação de encontros"), ("", "Nova análise"))}
<h1>Nova análise depois de alteração</h1>
<p role="note" class="aviso">Publicado em 13/10/2026. Alterado por quem propôs em 20/10/2026. Campos alterados: <strong>descrição; público</strong>. O encontro está fora das listas e sem link até a sua decisão. 12 confirmações continuam.</p>
<section class="pe-previa" aria-labelledby="pe-como"><h2 id="pe-como">Como os egressos verão</h2>
<p><strong>Encontro proposto por egresso</strong></p><p><strong>{e(TEC["titulo"])}</strong></p><p>{e(TEC["descricao"])} Também quem fez mestrado na área é bem-vindo.</p>
<p>Proposto por {e(TEC["nome"])} · {e(TEC["origem"])} (registro do Ifes)</p></section>
<dl class="pe-dl">
<dt>Público</dt><dd>Quem concluiu Especialização em Informática na Educação, Licenciatura em Química ou Mestrado Profissional em Química.</dd>
<dt>Link da reunião</dt><dd><strong>{e(LINK)}</strong> (sem alteração)</dd>
</dl>
<form method="post" action="m1-fila.html"><p class="pe-acoes"><button type="submit">Publicar de novo</button> <a href="m3-recusar.html">Recusar a alteração</a> <a href="m1-fila.html">Voltar</a></p></form>
<p>Recusar a alteração retira o encontro, com o motivo: não há versão anterior para restaurar.</p>"""


# --- Moderação (operador fictício CPAEG) ----------------------------------------------------

def trilha(*passos) -> str:
    itens = "".join(f'<li><a href="{d}">{e(r)}</a></li>' for d, r in passos[:-1])
    return (f'<nav class="trilha" aria-label="Você está em"><ol>{itens}'
            f'<li><span aria-current="page">{e(passos[-1][1])}</span></li></ol></nav>')


def fila() -> str:
    return f"""{trilha(("", "Moderação de encontros"))}
<h1>Encontros propostos por egressos</h1>
<p>Encontros no escopo da sua atuação. Nenhum aparece aos egressos sem a sua publicação. Você não vê CPF, data de nascimento nem contato de quem propõe, nem quem confirmou ou denunciou.</p>
<div class="rolagem" role="region" aria-label="Para análise" tabindex="0">
<table class="pe-tabela"><caption>Para análise (3)</caption>
<thead><tr><th scope="col">Data do encontro</th><th scope="col">Título</th><th scope="col">Público</th><th scope="col">Responsável</th><th scope="col">Enviado em</th><th scope="col">Ações</th></tr></thead>
<tbody>
<tr><td>29/10/2026</td><th scope="row">{e(TEC["titulo"])}</th><td>Cursos: Especialização em Informática na Educação; Licenciatura em Química</td><td>CPAEG (mais de uma unidade)</td><td>11/10/2026</td><td><a href="m2-analisar.html" aria-label="Analisar: {e(TEC["titulo"])}">Analisar</a></td></tr>
<tr><td>10/11/2026</td><th scope="row">Café virtual: primeiro emprego em TI</th><td>Unidade: Serra</td><td>CSAEG Serra</td><td>11/10/2026</td><td><a href="m2-analisar.html" aria-label="Analisar: Café virtual: primeiro emprego em TI">Analisar</a></td></tr>
<tr><td>29/10/2026</td><th scope="row">{e(TEC["titulo"])} <small>(alterado depois da publicação: descrição; público)</small></th><td>Cursos: três</td><td>CPAEG</td><td>20/10/2026</td><td><a href="m6-reanalisar.html" aria-label="Nova análise: {e(TEC["titulo"])}">Nova análise</a></td></tr>
</tbody></table></div>
<div class="rolagem" role="region" aria-label="Publicados" tabindex="0">
<table class="pe-tabela"><caption>Publicados (1)</caption>
<thead><tr><th scope="col">Data do encontro</th><th scope="col">Título</th><th scope="col">Confirmações</th><th scope="col">Denúncias</th><th scope="col">Ações</th></tr></thead>
<tbody><tr><td>05/11/2026</td><th scope="row">{e(VOLTAR["titulo"])}</th><td>4</td><td>1</td><td><a href="m4-retirar.html" aria-label="Retirar: {e(VOLTAR["titulo"])}">Ver denúncias e retirar</a></td></tr></tbody></table></div>"""


def analisar() -> str:
    return f"""{trilha(("m1-fila.html", "Moderação de encontros"), ("", "Analisar"))}
<h1>Analisar encontro</h1>
<section class="pe-previa" aria-labelledby="pe-como"><h2 id="pe-como">Como os egressos verão</h2>
<p><strong>Encontro proposto por egresso</strong></p><p><strong>{e(TEC["titulo"])}</strong></p><p>{e(TEC["descricao"])}</p>
<p>Proposto por {e(TEC["nome"])} · {e(TEC["origem"])} (registro do Ifes)</p></section>
<dl class="pe-dl">
<dt>Quando</dt><dd>Quinta-feira, 29/10/2026, 19h às 20h30</dd>
<dt>Público</dt><dd>Quem concluiu Especialização em Informática na Educação ou Licenciatura em Química. Inclui mais de uma unidade: a análise cabe à CPAEG.</dd>
<dt>Link da reunião</dt><dd><strong>{e(LINK)}</strong></dd>
<dt>Termo do organizador</dt><dd>Versão {e(VERSAO)}, aceito em 11/10/2026</dd>
</dl>
<p role="note" class="aviso">Site externo: meet.exemplo.org. O Portal não abre nem verifica o link. Confira o domínio antes de publicar.</p>
<form method="post" action="m1-fila.html"><p class="pe-acoes"><button type="submit">Publicar</button> <a href="m3-recusar.html">Recusar</a> <a href="m1-fila.html">Voltar</a></p></form>
<p>Publicar faz o encontro aparecer aos egressos com formação no público. Você e a data ficam registrados.</p>"""


def recusar() -> str:
    return f"""{trilha(("m1-fila.html", "Moderação de encontros"), ("m2-analisar.html", "Analisar"), ("", "Recusar"))}
<h1>Recusar encontro</h1>
<p><strong>{e(TEC["titulo"])}</strong> · 29/10/2026</p>
<form method="post" action="m1-fila.html" novalidate>
<fieldset class="pergunta"><legend>Motivo <span class="nota">Lista provisória; os critérios para uso real dependem de decisão institucional.</span></legend>{radios("motivo", MOTIVOS)}</fieldset>
<p><label for="complemento"><strong>Complemento</strong> (obrigatório em "Outro motivo")</label></p>
<textarea id="complemento" name="complemento" maxlength="300"></textarea>
<p>Quem propôs vê o motivo e o complemento. A recusa é definitiva; a pessoa pode propor outro encontro.</p>
<p class="pe-acoes"><button type="submit">Recusar</button> <a href="m2-analisar.html">Voltar</a></p>
</form>"""


def retirar() -> str:
    return f"""{trilha(("m1-fila.html", "Moderação de encontros"), ("", "Retirar"))}
<h1>Retirar encontro publicado</h1>
<p><strong>{e(VOLTAR["titulo"])}</strong> · 05/11/2026 · proposto por {e(VOLTAR["nome"])} · 4 confirmações</p>
<div class="rolagem" role="region" aria-label="Denúncias recebidas" tabindex="0">
<table class="pe-tabela"><caption>Denúncias recebidas (1). Você não vê quem denunciou.</caption>
<thead><tr><th scope="col">Recebida em</th><th scope="col">Motivo</th><th scope="col">Complemento</th></tr></thead>
<tbody><tr><td>15/10/2026</td><td>Link suspeito ou que não funciona</td><td>"O link pede para instalar um programa antes de entrar."</td></tr></tbody></table></div>
<form method="post" action="m1-fila.html" novalidate>
<fieldset class="pergunta"><legend>Motivo da retirada</legend>{radios("motivo", MOTIVOS, "link")}</fieldset>
<p><label for="complemento"><strong>Complemento</strong> (obrigatório em "Outro motivo")</label></p>
<textarea id="complemento" name="complemento" maxlength="300">O link leva a uma página que pede instalação de programa.</textarea>
<p>O encontro sai das listas na hora, a página passa a dizer "Retirado pela moderação" e o link some. Quem propôs vê o motivo. A retirada é definitiva.</p>
<p class="pe-acoes"><button type="submit">Retirar</button> <a href="m1-fila.html">Voltar</a></p>
</form>"""


def fila_vazia() -> str:
    return f"""{trilha(("", "Moderação de encontros"))}
<h1>Encontros propostos por egressos</h1>
<p>Nenhum encontro para análise no escopo da sua atuação.</p>
<p>Nenhum encontro publicado no escopo da sua atuação.</p>"""


# --- Montagem ------------------------------------------------------------------------------

# nome: (base servida, item atual da navegação, título, função)
TELAS = {
    "p1-inicio": ("inicio-diego", "Início", "Início", None),
    "p2-encontros": ("diego", "Encontros", "Encontros", encontros),
    "p3-encontro": ("diego", "Encontros", TEC["titulo"], encontro),
    "p4-confirmado": ("diego", "Encontros", TEC["titulo"], encontro_confirmado),
    "p5-cancelar-participacao": ("diego", "Encontros", "Cancelar sua participação", cancelar_participacao),
    "p6-sem-sessao": ("anonimo", None, "Encontro no Portal do Egresso", sem_sessao),
    "p7-fora-do-publico": ("bruno", "Encontros", TEC["titulo"], fora_do_publico),
    "p8-data-alterada": ("diego", "Encontros", TEC["titulo"], data_alterada),
    "p9-cancelado": ("diego", "Encontros", TEC["titulo"], cancelado),
    "p10-encerrado": ("diego", "Encontros", TEC["titulo"], encerrado),
    "p11-vazio": ("fernanda", "Encontros", "Encontros", vazio),
    "p12-denunciar": ("diego", "Encontros", "Denunciar este encontro", denunciar),
    "p13-denuncia-enviada": ("diego", "Encontros", TEC["titulo"], denuncia_enviada),
    "p14-conflito": ("diego", "Encontros", "Não foi possível confirmar", conflito),
    "p15-em-revisao": ("diego", "Encontros", TEC["titulo"], em_revisao),
    "o1-propor": ("maria", "Encontros", "Propor um encontro", propor),
    "o2-propor-erros": ("maria", "Encontros", "Propor um encontro", propor_erros),
    "o3-confira": ("maria", "Encontros", "Confira e envie", confira),
    "o4-em-analise": ("maria", "Encontros", TEC["titulo"], em_analise),
    "o5-seus-encontros": ("maria", "Encontros", "Seus encontros", seus_encontros),
    "o6-publicado": ("maria", "Encontros", TEC["titulo"], publicado),
    "o7-alterar-data": ("maria", "Encontros", "Alterar data e horário", alterar_data),
    "o8-cancelar": ("maria", "Encontros", "Cancelar este encontro", cancelar),
    "o9-recusado": ("maria", "Encontros", "Mentoria para concursos públicos", recusado),
    "o10-seus-vazio": ("diego", "Encontros", "Seus encontros", seus_vazio),
    "o11-corrigir-link": ("maria", "Encontros", "Corrigir o link da reunião", corrigir_link),
    "o12-alterar-encontro": ("maria", "Encontros", "Confira a alteração", alterar_encontro),
    "m1-fila": ("operador", None, "Encontros propostos por egressos", fila),
    "m2-analisar": ("operador", None, "Analisar encontro", analisar),
    "m3-recusar": ("operador", None, "Recusar encontro", recusar),
    "m4-retirar": ("operador", None, "Retirar encontro publicado", retirar),
    "m5-fila-vazia": ("operador", None, "Encontros propostos por egressos", fila_vazia),
    "m6-reanalisar": ("operador", None, "Nova análise depois de alteração", reanalisar),
}


def limpar(html: str) -> str:
    html = re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", html)
    html = html.replace('url("/fontes/', f'url("{FONTES}')
    return re.sub(r'(src|href)="/minha-trajetoria/card\.(png|svg)"', r'\1="card-diego.\2"', html)


def servidos() -> dict[str, str]:
    from django.test import Client

    bases = {}
    anonimo = Client(HTTP_HOST="127.0.0.1")
    bases["anonimo"] = anonimo.get("/entrar/").content.decode()
    for nome, (cpf, nascimento) in PESSOAS.items():
        c = Client(HTTP_HOST="127.0.0.1")
        assert c.post("/entrar/", {"cpf": cpf, "data_nascimento": nascimento}).status_code in (302, 303), nome
        r = c.get("/participacao/")
        assert r.status_code == 200, nome
        bases[nome] = r.content.decode()
        if nome == "diego":
            bases["inicio-diego"] = c.get("/inicio/").content.decode()
            for formato in ("png", "svg"):
                card = c.get(f"/minha-trajetoria/card.{formato}")
                if card.status_code == 200:
                    (PASTA / f"card-diego.{formato}").write_bytes(card.content)
                    break
    operador = Client(HTTP_HOST="127.0.0.1")
    operador.post("/demonstracao/operador/escolher/", {"operador": "demonstracao:operador-a", "destino": "curadoria"})
    r = operador.get("/curadoria/oportunidades/")
    assert r.status_code == 200, "operador fictício CPAEG sem acesso à curadoria"
    bases["operador"] = r.content.decode()
    return {k: limpar(v) for k, v in bases.items()}


def com_faixa(html: str) -> str:
    pular = '<a class="pular" href="#conteudo">Pular para o conteúdo</a>'
    assert pular in html
    return html.replace(pular, pular + "\n" + FAIXA, 1)


def com_navegacao(html: str, atual) -> str:
    """Acrescenta "Encontros" entre Oportunidades e Participação (H-3105) e marca o atual."""
    if "<nav class=\"navegacao\"" not in html:
        return html
    html = html.replace(' aria-current="page"', "")
    item = '<li><a href="p2-encontros.html" data-rotulo="Encontros">Encontros</a></li>'
    html = re.sub(r'(<li><a href="/oportunidades/"[^>]*>Oportunidades</a></li>)', r"\1" + item, html, count=1)
    if atual:
        html = re.sub(rf'(data-rotulo="{atual}")>', r'\1 aria-current="page">', html, count=1)
    destinos = {"/inicio/": "p1-inicio.html"}
    for de, para in destinos.items():
        html = html.replace(f'href="{de}" data-rotulo', f'href="{para}" data-rotulo')
    return html


def trocar_main(html: str, conteudo: str, titulo: str, css: str) -> str:
    inicio = html.index(">", html.index('<div class="coluna">', html.index("<main"))) + 1
    fim = html.rindex("</div>", 0, html.index("</main>"))
    html = html[:inicio] + "\n" + conteudo + "\n" + html[fim:]
    html = html.replace("</style>", css + "</style>", 1)
    produto = "Acompanhamento da coleta — Trajetória Ifes" if '<header class="cabecalho">' in html else "Portal do Egresso (demonstração)"
    return re.sub(r"<title>.*?</title>", f"<title>{e(titulo)} — {produto} — protótipo 031</title>", html,
                  count=1, flags=re.S)


def ler(caminho: str) -> str:
    return (RAIZ / caminho).read_text("utf-8")


def gerar() -> list[str]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    bases = servidos()
    css_egresso = ler("trajetoria/portal/templates/portal/contribuicao/estilo.css") + CSS
    feitas = []
    for nome, (base, atual, titulo, fazer) in TELAS.items():
        html = bases[base]
        if nome == "p1-inicio":
            alvo = '<section class="inicio-oportunidades'
            assert alvo in html, "seção de oportunidades do Início não encontrada"
            html = html.replace(alvo, secao_inicio() + alvo, 1).replace("</style>", css_egresso + "</style>", 1)
            html = re.sub(r"<title>.*?</title>", "<title>Início — Portal do Egresso (demonstração) — protótipo 031</title>",
                          html, count=1, flags=re.S)
        elif base == "operador":
            html = trocar_main(html, fazer(), titulo, CSS_OPERADOR)
        else:
            html = trocar_main(html, fazer(), titulo, css_egresso)
        html = com_navegacao(com_faixa(html), atual)
        (PASTA / f"{nome}.html").write_text(html, "utf-8")
        feitas.append(nome)
    (PASTA / "exemplo.ics").write_bytes(ics())
    return feitas


def dobrar(linha: str) -> str:
    """RFC 5545, 3.1: linhas de até 75 octetos, continuação com um espaço."""
    partes, atual = [], b""
    for ch in linha:
        b = ch.encode("utf-8")
        if len(atual) + len(b) > (75 if not partes else 74):
            partes.append(atual)
            atual = b""
        atual += b
    partes.append(atual)
    return "\r\n ".join(p.decode("utf-8") for p in partes)


def ics() -> bytes:
    """O `.ics` do FR-027: aponta para a página, sem o link da reunião nem dado de pessoas."""
    def esc(t):
        return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    linhas = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ifes//Portal do Egresso (demonstracao)//PT-BR",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
        "UID:7f3c2a9e-5b1d-4c8e-9a0f-3d2e1c0b9a31@portal-do-egresso.demonstracao",
        "DTSTAMP:20261014T130000Z", "SEQUENCE:0",
        "DTSTART:20261029T220000Z", "DTEND:20261029T233000Z",
        f"SUMMARY:{esc(TEC['titulo'])}",
        f"URL:{ENDERECO}",
        "DESCRIPTION:" + esc(
            f"Encontro proposto por egresso no Portal do Egresso. O link da reunião está na página do "
            f"encontro, para quem confirmou: {ENDERECO}\nSe a data mudar ou o encontro for cancelado, "
            "este arquivo não muda sozinho. Confira a página."),
        "END:VEVENT", "END:VCALENDAR",
    ]
    return ("\r\n".join(dobrar(linha) for linha in linhas) + "\r\n").encode("utf-8")


# --- Medidas e capturas ---------------------------------------------------------------------

GRUPOS = {
    "p": "Participante (Diego; Bruno fora do público; Fernanda sem encontros)",
    "o": "Organizadora (Maria)",
    "m": "Moderação (operador fictício CPAEG)",
}
DESKTOP = {"p1-inicio", "p2-encontros", "p3-encontro", "p4-confirmado", "o1-propor", "o3-confira", "o6-publicado"}


def medidor():
    spec = importlib.util.spec_from_file_location("prototipo_029", RAIZ / "specs/029-pagina-publica-portal/prototipo/gerar.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    m, moldura = g.medidor()
    m.PASTA = PASTA
    moldura = moldura.replace(".pp-lead, .portal-hero .proposta", ".pe-data, .pe-lead, .inicio-sintese")
    moldura = moldura.replace(".pp-acoes .portal-botao, .portal-hero .portal-botao", ".pe-acao-principal")
    return m, moldura


def medir(nomes) -> dict:
    m, moldura = medidor()
    (PASTA / "_moldura.html").write_text(moldura, "utf-8")
    CAPTURAS.mkdir(exist_ok=True)
    medidas = {}
    try:
        for nome in nomes:
            pagina = f"{nome}.html"
            v = {}
            larguras = (320, 375, 768, 1024, 1440) if not nome.startswith("m") else (320, 375, 1024, 1280)
            for largura in larguras:
                for fonte in (100, 200):
                    v[f"{largura}@{fonte}"] = m.medir(pagina, largura, fonte=fonte)
            v["375x812"] = m.medir(pagina, 375, 812)
            if nome.startswith("m"):
                m.capturar(pagina, 1280, v["1280@100"]["altura_doc"], CAPTURAS / f"{nome}-1280.png")
            else:
                m.capturar(pagina, 375, v["375@100"]["altura_doc"], CAPTURAS / f"{nome}-375.png")
                if nome in DESKTOP:
                    m.capturar(pagina, 1440, v["1440@100"]["altura_doc"], CAPTURAS / f"{nome}-1440.png")
            medidas[nome] = v
            print(nome, resumo(nome, v), flush=True)
    finally:
        (PASTA / "_moldura.html").unlink(missing_ok=True)
    return medidas


def resumo(nome, v) -> dict:
    rolagem = sorted(k for k, r in v.items() if "@" in k and r["rolagem"] > r["largura"])
    pequenos = sorted(k for k, r in v.items() if "@100" in k and r["alvos_pequenos"])
    c = v["375x812"]
    faixa = c["faixa_prototipo"]
    r = {"rolagem_horizontal": rolagem, "h1": c["h1s"], "alvos_menores_que_44": pequenos}
    if nome in ("p3-encontro", "p4-confirmado", "p7-fora-do-publico", "o6-publicado"):
        r["375x812_titulo_e_data_sem_rolar"] = bool(c["h1"] and c["fato"] and max(c["h1"], c["fato"]) - faixa <= 812)
        r["375x812_fim_da_data_px"] = round((c["fato"] or 0) - faixa)
    return r


def indice(medidas: dict) -> str:
    def figura(nome):
        cap = f"capturas/{nome}-{'1280' if nome.startswith('m') else '375'}.png"
        desk = f' · <a href="capturas/{nome}-1440.png">1440 px</a>' if nome in DESKTOP else ""
        r = resumo(nome, medidas[nome]) if nome in medidas else {}
        ok = r and not r["rolagem_horizontal"] and r["h1"] == 1 and not r["alvos_menores_que_44"] and r.get("375x812_titulo_e_data_sem_rolar", True)
        marca = ("medidas ok" if ok else "ver medidas.json") if r else "sem medidas"
        return (f'<figure><figcaption><a href="{nome}.html">{e(nome)}</a> · {e(TELAS[nome][2])}'
                f'<br><small>{marca}{desk}</small></figcaption><a href="{cap}"><img loading="lazy" src="{cap}" '
                f'alt="Captura da tela {e(nome)}"></a></figure>')
    secoes = "".join(
        f'<h2>{e(titulo)}</h2><div class="grade">' + "".join(figura(n) for n in TELAS if n.startswith(prefixo)) + "</div>"
        for prefixo, titulo in GRUPOS.items())
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>031 — protótipo conceitual dos encontros propostos por egressos</title>
<style>body{{margin:0;font-family:system-ui,sans-serif;color:#1b1b1b;line-height:1.5;background:#fff}}main{{max-width:90rem;margin:0 auto;padding:1rem 1.5rem 4rem}}
a{{color:#195128}}.grade{{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:1.5rem;align-items:start}}
figure{{margin:0}}figure img{{width:100%;border:1px solid #c6cace}}figure>a{{display:block;max-height:36rem;overflow-y:auto}}
figcaption{{font-weight:700;margin-bottom:.25rem}}h2{{border-top:4px solid #2f9e41;padding-top:1rem;margin-top:2.5rem}}
.alerta{{background:#1b1b1b;color:#fff;padding:1rem 1.25rem}}.alerta strong{{color:#ffdd00}}table{{border-collapse:collapse}}td,th{{border:1px solid #c6cace;padding:.35rem .6rem;text-align:left;vertical-align:top}}</style></head><body><main>
<h1>Feature 031 — Encontros propostos por egressos: protótipo conceitual</h1>
<p class="alerta"><strong>Nada disto existe no Portal.</strong> É um protótipo estático para a spec e para o bloco Comunidade do Checkpoint 2. Dados fictícios; textos provisórios (DP-801). As telas servidas não mudaram.</p>
<p>Cada tela parte do HTML servido pela demonstração na versão C (cabeçalho, navegação, fontes e tokens reais), com o conteúdo principal trocado. O item "Encontros" na navegação é hipótese (H-3105). Só as ligações entre telas do protótipo funcionam; as demais (Minha trajetória, Oportunidades, Participação, cabeçalho da operação) apontam para rotas da aplicação real e não abrem a partir dos arquivos. Spec: <a href="../spec.md">spec.md</a>. Calendário de exemplo: <a href="exemplo.ics">exemplo.ics</a> (aponta para a página, sem o link da reunião). Nome e origem do organizador seguem a <a href="../../../docs/adr/0010-dado-de-egresso-visivel-a-outros-egressos.md">ADR 0010</a>. Quem modera (CSAEG ou CPAEG) é hipótese da demonstração, e não competência institucional aprovada (H-3102; D8).</p>
<h2>Como ler</h2>
<table><thead><tr><th>Percurso</th><th>Telas</th></tr></thead><tbody>
<tr><td>Organizadora propõe e envia</td><td>o1 → o2 (erros) → o3 → o4</td></tr>
<tr><td>Moderação analisa, publica ou recusa</td><td>m1 → m2 → m3; vazio em m5</td></tr>
<tr><td>Organizadora acompanha</td><td>o5 (todas as situações) → o6 → o7 / o8; recusa em o9; vazio em o10</td></tr>
<tr><td>Correção operacional depois da publicação</td><td>o6 → o7 (data e horário) → p8; o6 → o11 (link na mesma plataforma)</td></tr>
<tr><td>Mudança substancial, com nova análise</td><td>o6 → o12 → m6; participante vê p15</td></tr>
<tr><td>Participante descobre e confirma</td><td>p1 (Início) → p2 → p3 → p4 → p5; vazio em p11</td></tr>
<tr><td>Endereço compartilhado; público como descoberta</td><td>p6 (sem sessão) → p3; p7 (fora do público, pode participar)</td></tr>
<tr><td>Mudanças depois de confirmar</td><td>p8 (data alterada), p9 (cancelado), p10 (encerrado), p14 (conflito)</td></tr>
<tr><td>Denúncia</td><td>p12 → p13 → m4 (retirada)</td></tr>
</tbody></table>
<p>Medidas (verificação técnica, <strong>não</strong> é validação com egressos): sem rolagem horizontal de 320 a 1440 px com fonte a 100% e 200%; um h1; alvos de 44 px; título e data a 375×812 na página do encontro. Detalhe em <a href="medidas.json">medidas.json</a>.</p>
{secoes}
</main></body></html>"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sem-capturas", action="store_true")
    p.add_argument("telas", nargs="*", help="mede só estas telas e mescla com o medidas.json existente")
    args = p.parse_args()
    feitas = gerar()
    if args.sem_capturas:
        return
    anteriores = {}
    if args.telas and (PASTA / "medidas.json").exists():
        anteriores = {k: v["medidas"] for k, v in json.loads((PASTA / "medidas.json").read_text("utf-8")).items()}
    medidas = {**anteriores, **medir(args.telas or feitas)}
    medidas = {nome: medidas[nome] for nome in TELAS if nome in medidas}
    resumo_json = {nome: {"resumo": resumo(nome, v), "medidas": v} for nome, v in medidas.items()}
    (PASTA / "medidas.json").write_text(json.dumps(resumo_json, indent=1, ensure_ascii=False), "utf-8")
    (PASTA / "index.html").write_text(indice(medidas), "utf-8")


if __name__ == "__main__":
    main()

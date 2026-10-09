"""Gera os protótipos da camada visual do Portal (ADR 0009, decisão 10).

Três direções (A institucional, B trajetória, C combinação) x três telas (página pública,
Início da Ana, Início do Diego). HTML estático, sem JavaScript, com os tokens da 015 e a
camada do Portal. Os cards são gerados pelo código real da 021, com a legenda da decisão 5.

Uso, na raiz do repositório:

    uv run python docs/prototipos/2026-10-09-portal/gerar.py

Protótipo, não produto: nada aqui é importado pela aplicação.
"""

import os
import re
import sys
from html import escape
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))

# --- Dados das personas fictícias (fonte_academica/cenarios.py; textos dos catálogos) -------

PROVENIENCIA = (
    "Essas informações vêm dos registros acadêmicos do Ifes. Nada aqui foi respondido por você."
)
TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"

ANA = {
    "pessoa": "Ana Exemplo",
    "sintese": "O Ifes registra 1 formação concluída por você.",
    "formacoes": [
        {
            "ano": 2022,
            "frase": f"Em 2022, você concluiu {TADS} na unidade Serra.",
            "curso": TADS,
            "atributos": "Serra · Graduação · Presencial",
            "derivado": "Há 3 anos desde essa conclusão.",
        }
    ],
    "numeros": [
        (27, f"Em 2022, 27 conclusões de {TADS} foram registradas na unidade Serra, "
             "incluindo a sua."),
        (812, "Em 2022, 812 conclusões foram registradas na unidade Serra."),
    ],
    "apuracao": "Dados institucionais apurados em 31/01/2026.",
    "oportunidade": {
        "titulo": "Especialização em Segurança da Informação",
        "por_que": f"Aparece porque você concluiu {TADS} na unidade Serra.",
        "origem": "Oferecida pela unidade Serra · site externo: oportunidades.example",
        "ver": "Ver as 2 oportunidades",
    },
    "convite": (
        f"Há uma pesquisa aberta sobre {TADS}. Respondê-la é como você atualiza sua "
        "trajetória com o Ifes.",
        "Responder",
    ),
    "card": "card-ana.png",
    "card_alt": (
        "Card vertical Minha trajetória no Ifes: 2022, " + TADS + ", Serra, Graduação, "
        "Presencial; 27 conclusões deste curso e 812 conclusões na unidade Serra em 2022; "
        "Essa história também é minha. #SouEgressoIfes."
    ),
}

DIEGO = {
    "pessoa": "Diego Exemplo",
    "sintese": "O Ifes registra 3 formações concluídas por você.",
    "formacoes": [
        {
            "ano": 2012,
            "frase": "Em 2012, você concluiu Técnico em Química na unidade Vila Velha.",
            "curso": "Técnico em Química",
            "atributos": "Vila Velha · Técnico · Presencial · Integrado",
        },
        {
            "ano": 2017,
            "frase": "Em 2017, você concluiu Licenciatura em Química na unidade Vila Velha.",
            "curso": "Licenciatura em Química",
            "atributos": "Vila Velha · Graduação · Presencial",
        },
        {
            "ano": 2020,
            "frase": "Em 2020, você concluiu Mestrado Profissional em Química na unidade "
                     "Vila Velha.",
            "curso": "Mestrado Profissional em Química",
            "atributos": "Vila Velha · Pós-graduação · Presencial",
        },
    ],
    "numeros": [],
    "oportunidade": {
        "titulo": "Programa de estágio em laboratórios parceiros",
        "por_que": "Aparece porque você concluiu Técnico em Química na unidade Vila Velha.",
        "origem": "Oferecida pela unidade Vila Velha · site externo: oportunidades.example",
        "ver": "Ver as 3 oportunidades",
    },
    "convite": (
        "Há pesquisas abertas sobre 2 das suas formações. Respondê-las é como você atualiza "
        "sua trajetória com o Ifes.",
        "Escolher a formação",
    ),
    "card": "card-diego.png",
    "card_alt": (
        "Card vertical Minha trajetória no Ifes: 2012, Técnico em Química; 2017, "
        "Licenciatura em Química; 2020, Mestrado Profissional em Química; todos na unidade "
        "Vila Velha. Essa história também é minha. #SouEgressoIfes."
    ),
}

EXEMPLO_ALT = (
    "Exemplo de card com dados fictícios: 2014, Técnico em Edificações; 2020, Bacharelado em "
    "Engenharia Civil; unidade Vitória. Essa história também é minha. #SouEgressoIfes."
)

# Textos provisórios da página pública (ADR 0009, decisão 6): escritos pela equipe, sem
# slogan; para uso real, a ACS aprova com a CPAEG (D2, DP-801).
PUBLICO = {
    "rotulo": "Portal do Egresso",
    "h1": "Veja o que o Ifes registra sobre a sua formação",
    "proposta": (
        "No Portal do Egresso, você encontra as formações que concluiu no Ifes, de onde vêm "
        "essas informações e um card da sua trajetória para compartilhar."
    ),
    "entrar": "Entrar no Portal",
    "como_entrar": "Para entrar, confirme seu CPF e sua data de nascimento.",
    "blocos": [
        ("Sua trajetória", "As formações que você concluiu no Ifes, com ano, curso e unidade, "
                           "a partir dos registros acadêmicos."),
        ("Seu card", "Uma imagem vertical da sua trajetória para o story ou o status das "
                     "redes sociais."),
        ("Oportunidades", "Cursos, eventos e programas divulgados pelo Ifes, quando houver "
                          "algum para a sua formação."),
        ("Seu e-mail", "O endereço que o Ifes usa para falar com você, mantido por você."),
    ],
    "passos": [
        ("Confirme seus dados", "CPF e data de nascimento, para o Ifes localizar suas "
                                "formações."),
        ("Veja sua trajetória", "As formações registradas pelo Ifes, com a origem de cada "
                                "informação."),
        ("Compartilhe, se quiser", "Baixe o card e publique no story ou no status."),
    ],
    "voz_titulo": "Pesquisa de acompanhamento",
    "voz": (
        "Quando o Ifes abre uma pesquisa de acompanhamento para a sua formação, o Portal mostra "
        "o convite. Responder é como você atualiza sua trajetória com o Ifes. Você vê sua "
        "trajetória sem precisar responder."
    ),
}

DIRECOES = {
    "a": "Direção A — institucional",
    "b": "Direção B — trajetória",
    "c": "Combinação (A + B)",
}

# --- Cards (código real da 021) ----------------------------------------------------------


def gerar_cards():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_SECRET_KEY", "prototipo")
    import django

    django.setup()
    from trajetoria.narrativa import card, catalogo, rasterizacao
    from trajetoria.narrativa.contrato import (
        Compartilhavel,
        ContextoCompartilhavel,
        FormacaoCompartilhavel,
    )
    from trajetoria.narrativa.montagem import METRICA_CURSO_UNIDADE_ANO

    def formacao(curso, unidade, nivel, modalidade, ano):
        return FormacaoCompartilhavel(
            curso, unidade, nivel, modalidade, ano,
            card.quebrar_linhas(curso, card.TAMANHO_CURSO, True, card.LIMITE_ITEM),
            card.quebrar_atributos([unidade, nivel, modalidade], card.TAMANHO_DETALHE,
                                   limite=card.LIMITE_ITEM),
        )

    def destaque(metrica, par, n):
        rotulo = tuple(l.format(unidade="Serra", ano=2022) for l in catalogo.plural(par, n))
        return ContextoCompartilhavel(metrica, n, rotulo)

    # unidade_da_imagem=None: a imagem é a genérica, legenda "Ifes · ilustração" (decisão 5).
    cards = {
        "card-ana.png": Compartilhavel(
            (formacao(TADS, "Serra", "Graduação", "Presencial", 2022),), 0, 1,
            (destaque(METRICA_CURSO_UNIDADE_ANO, catalogo.DESTAQUE_CURSO, 27),
             destaque("conclusoes_unidade_ano", catalogo.DESTAQUE_UNIDADE, 812)),
            True, catalogo.CARD_APURACAO.format(apuracao="31/01/2026"),
        ),
        "card-diego.png": Compartilhavel(
            (formacao("Técnico em Química", "Vila Velha", "Técnico", "Presencial", 2012),
             formacao("Licenciatura em Química", "Vila Velha", "Graduação", "Presencial", 2017),
             formacao("Mestrado Profissional em Química", "Vila Velha", "Pós-graduação",
                      "Presencial", 2020)),
            0, 3, (), True,
        ),
        "card-exemplo.png": Compartilhavel(
            (formacao("Técnico em Edificações", "Vitória", "Técnico", "Presencial", 2014),
             formacao("Bacharelado em Engenharia Civil", "Vitória", "Graduação", "Presencial",
                      2020)),
            0, 2, (), True,
        ),
    }
    for nome, compartilhavel in cards.items():
        (PASTA / nome).write_bytes(rasterizacao.png_de(card.card_svg(compartilhavel)))


# --- Estilo -------------------------------------------------------------------------------

BASE_CSS = """
/* Tokens da 015 (estilo.css), inalterados. */
:root {
  --cor-marca: #2f9e41; --cor-sucesso: #195128; --cor-institucional: #eef7f0;
  --cor-texto: #1b1b1b; --cor-texto-suave: #565c65; --cor-fundo: #ffffff;
  --cor-borda-suave: #c6cace; --cor-foco: #1b1b1b; --cor-foco-halo: #ffdd00;
  --cor-demonstracao: #fff1d2;
  --fonte: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --fonte-1: 1.75rem; --fonte-2: 1.375rem; --fonte-3: 1.125rem; --fonte-4: 1rem;
  --fonte-5: 0.9375rem;
  --espaco-1: .25rem; --espaco-2: .5rem; --espaco-3: .75rem; --espaco-4: 1rem;
  --espaco-5: 1.5rem; --espaco-6: 2rem; --espaco-7: 3rem;
  --raio: 4px; --borda-acento: 4px; --alvo: 2.75rem;
}
/* Camada do Portal (ADR 0009): incluída depois, sem alterar os tokens acima. */
:root {
  --cor-acao: #195128;            /* decisão 3: 9,3:1 no branco */
  --cor-acao-forte: #00420c;      /* 11,8:1 */
  --portal-container: 72rem;      /* decisão 1 */
  --portal-profundo: #0e3b23;     /* do card; branco ≈ 12:1 */
  --portal-profundo-texto: #cfe6d6;
  --portal-creme: #f6f2e8;
  --portal-ano: #257a33;          /* ano no creme: 4,8:1 (021) */
  --portal-destaque: 2.5rem;      /* decisão 4: 40 px, peso 700, só no h1 */
  --portal-numero: 3rem;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; font-family: var(--fonte); font-size: var(--fonte-4); line-height: 1.5;
  color: var(--cor-texto); background: var(--cor-fundo); overflow-wrap: anywhere; }
a { color: var(--cor-acao); text-underline-offset: 3px; }
a:hover { color: var(--cor-acao-forte); text-decoration-thickness: 2px; }
:focus-visible { outline: 3px solid var(--cor-foco); box-shadow: 0 0 0 6px var(--cor-foco-halo); }
h1, h2, h3 { line-height: 1.25; margin: 0 0 var(--espaco-3); }
h1 { font-size: var(--fonte-1); font-weight: 700; }
h2 { font-size: var(--fonte-2); }
h3 { font-size: var(--fonte-3); }
p { margin: 0 0 var(--espaco-3); }
main p { max-width: 36rem; }  /* ≈ 70 caracteres (ADR 0009) */
img { max-width: 100%; height: auto; }
.container { max-width: var(--portal-container); margin: 0 auto; padding: 0 var(--espaco-4); }
.texto { max-width: 36rem; }
.visualmente-oculto { position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap; }

.prototipo { background: #3d3d3d; color: #fff; font-size: var(--fonte-5); padding: var(--espaco-1) 0; }
.prototipo strong { color: var(--cor-foco-halo); }
.demonstracao { background: var(--cor-demonstracao); font-size: var(--fonte-5);
  padding: var(--espaco-2) 0; border-bottom: var(--borda-acento) solid var(--cor-marca); }
.demonstracao .container { display: flex; flex-wrap: wrap; gap: var(--espaco-1) var(--espaco-5); }
.demonstracao a { color: var(--cor-texto); }

.cabecalho { border-bottom: 1px solid var(--cor-borda-suave); }
.cabecalho .container { display: flex; flex-wrap: wrap; align-items: center; gap: var(--espaco-2) var(--espaco-4);
  min-height: 4.5rem; padding-top: var(--espaco-2); padding-bottom: var(--espaco-2); }
.assinatura svg { display: block; height: 2.75rem; width: auto; }
.produto { margin: 0; border-left: 1px solid var(--cor-borda-suave); padding-left: var(--espaco-4);
  font-weight: 700; font-size: var(--fonte-3); line-height: 1.25; }
.produto span { display: block; font-weight: 400; font-size: var(--fonte-5); color: var(--cor-texto-suave); }
.cabecalho .entrar-topo { margin-left: auto; }
.navegacao { border-bottom: 1px solid var(--cor-borda-suave); }
.navegacao ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 0 var(--espaco-5); }
.navegacao a { display: inline-flex; align-items: center; min-height: var(--alvo); color: var(--cor-texto);
  text-decoration: none; border-bottom: var(--borda-acento) solid transparent; }
.navegacao a:hover { border-bottom-color: var(--cor-borda-suave); }
.navegacao a[aria-current] { font-weight: 700; border-bottom-color: var(--cor-acao); }

.botao { display: inline-flex; align-items: center; justify-content: center; min-height: var(--alvo);
  padding: 0 var(--espaco-5); background: var(--cor-acao); color: #fff; font-weight: 700;
  border-radius: var(--raio); text-decoration: none; }
.botao:hover { background: var(--cor-acao-forte); color: #fff; }
.botao-claro { background: #fff; color: var(--portal-profundo); }
.botao-claro:hover { background: var(--cor-institucional); color: var(--portal-profundo); }
.ligacao { display: inline-flex; align-items: center; min-height: var(--alvo); font-weight: 600; }
.origem { color: var(--cor-texto-suave); font-size: var(--fonte-5); font-weight: 400; }
.suave { color: var(--cor-texto-suave); font-size: var(--fonte-5); }
.blocos { display: grid; gap: var(--espaco-4); }
.bloco { border: 1px solid var(--cor-borda-suave); border-radius: var(--raio); padding: min(var(--espaco-5), 5vw);
  display: flex; flex-direction: column; background: #fff; }
.bloco p { color: var(--cor-texto-suave); flex: 1; }
.numeros { display: grid; gap: var(--espaco-4); margin-bottom: var(--espaco-3); }
.numero { background: var(--cor-institucional); border-left: var(--borda-acento) solid var(--cor-marca);
  padding: var(--espaco-4) var(--espaco-5); border-radius: 0 var(--raio) var(--raio) 0; }
.numero strong { display: block; font-size: var(--portal-numero); line-height: 1.1; color: var(--portal-profundo); }
.numero p { margin: 0; }
.oportunidade-titulo { font-weight: 600; font-size: var(--fonte-3); }
.convite { border: 2px solid var(--cor-acao); border-radius: var(--raio); padding: var(--espaco-5); }
.card-previa { display: block; width: 100%; max-width: 270px; border-radius: var(--raio);
  box-shadow: 0 0 0 1px rgba(0,0,0,.1); }
.selo { display: inline-block; background: var(--cor-demonstracao); color: var(--cor-texto);
  font-size: var(--fonte-5); font-weight: 700; padding: var(--espaco-1) var(--espaco-3);
  border-radius: 999px; margin-bottom: var(--espaco-3); }
.foto { border: 2px dashed var(--cor-texto-suave); border-radius: var(--raio); display: flex;
  align-items: center; justify-content: center; text-align: center; padding: var(--espaco-5);
  color: var(--cor-texto-suave); background: var(--cor-institucional); min-height: 10rem; }
.foto strong { display: block; color: var(--cor-texto); }
.secao { padding: var(--espaco-6) 0; }
.secao + .secao { padding-top: 0; }
.rodape { border-top: 1px solid var(--cor-borda-suave); padding: var(--espaco-5) 0;
  font-size: var(--fonte-5); color: var(--cor-texto-suave); }
.rodape p { margin: 0; }

@media (min-width: 768px) {
  .container { padding: 0 var(--espaco-6); }
  h1 { font-size: var(--portal-destaque); }
  .numeros, .blocos { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 767px) {
  .produto span { display: none; }
  .cabecalho .entrar-topo { display: none; }
}
"""

CSS = {
    # A — institucional: hero dividido com foto, superfícies tonais, ações em blocos.
    "a": """
.hero { background: var(--cor-institucional); padding: var(--espaco-6) 0; }
.hero .container { display: grid; gap: var(--espaco-6); align-items: center; }
.hero h1 { color: var(--portal-profundo); }
.hero .proposta { font-size: var(--fonte-3); }
.blocos-4 .bloco { border-top: var(--borda-acento) solid var(--cor-marca); }
.voz { background: var(--cor-institucional); border-radius: var(--raio); padding: var(--espaco-5); }
.abertura-foto { min-height: 8.75rem; margin-top: var(--espaco-5); }
.titulo-inicio { background: var(--cor-institucional); padding: var(--espaco-5); border-radius: 0 0 var(--raio) var(--raio); }
.titulo-inicio h1 { color: var(--portal-profundo); margin-bottom: var(--espaco-2); }
.titulo-inicio p { margin: 0; font-size: var(--fonte-3); }
.grade { display: grid; gap: var(--espaco-6); padding: var(--espaco-6) 0; }
.grade > * { min-width: 0; }
.formacoes { list-style: none; margin: 0 0 var(--espaco-4); padding: 0; }
.formacoes li { border-left: var(--borda-acento) solid var(--cor-marca); background: var(--cor-institucional);
  padding: var(--espaco-3) var(--espaco-4); margin-bottom: var(--espaco-3); }
.formacoes p { margin: 0 0 var(--espaco-1); }
.formacoes .fato { font-weight: 600; }
.acoes-a .bloco { margin-bottom: var(--espaco-4); }
.acoes-a .bloco h3 { font-size: var(--fonte-4); }
@media (min-width: 768px) { .blocos-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (min-width: 1024px) {
  .hero { padding: var(--espaco-7) 0; }
  .hero .container { grid-template-columns: 7fr 5fr; }
  .hero .foto { min-height: 20rem; }
  .blocos-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .abertura-foto { min-height: 15rem; }
  .grade { grid-template-columns: 2fr 1fr; column-gap: var(--espaco-7); }
}
""",
    # B — trajetória: faixa profunda com a linha do tempo, card como protagonista, creme.
    "b": """
.faixa { background: var(--portal-profundo); color: #fff; padding: var(--espaco-6) 0; }
.faixa h1, .faixa h2, .faixa h3 { color: #fff; }
.faixa .proposta, .faixa .sintese { font-size: var(--fonte-3); }
.faixa .suave, .faixa .origem { color: var(--portal-profundo-texto); }
.faixa a:not(.botao) { color: #fff; }
.hero-b .container { display: grid; gap: var(--espaco-6); align-items: center; }
.hero-b .card-previa { margin: 0 auto; max-width: 300px; }
.hero-b figure { margin: 0; text-align: center; }
.hero-b figcaption { margin-top: var(--espaco-2); color: var(--portal-profundo-texto); font-size: var(--fonte-5); }
.passos { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--espaco-4); counter-reset: passo; }
.passos li { background: var(--portal-creme); border-radius: var(--raio); padding: var(--espaco-5);
  counter-increment: passo; }
.passos li::before { content: counter(passo); display: inline-flex; align-items: center; justify-content: center;
  width: 2.25rem; height: 2.25rem; border-radius: 50%; background: var(--portal-profundo); color: #fff;
  font-weight: 700; margin-bottom: var(--espaco-3); }
.passos p { margin: 0; color: var(--cor-texto-suave); }
.linha { list-style: none; margin: var(--espaco-5) 0; padding: 0; display: grid; gap: var(--espaco-5); }
.linha li { position: relative; padding-left: 2.5rem; }
.linha li::before { content: ""; position: absolute; left: 0; top: .15rem; width: 1.5rem; height: 1.5rem;
  border: .4rem solid var(--cor-marca); border-radius: 50%; background: var(--portal-profundo); }
.linha .ano { display: block; font-size: var(--fonte-2); font-weight: 700; line-height: 1.2; }
.linha p { margin: 0 0 var(--espaco-1); }
.linha .curso { font-weight: 600; font-size: var(--fonte-3); }
.faixa .numeros .numero { background: rgba(255,255,255,.08); border-left-color: var(--cor-marca); }
.faixa .numero strong { color: #fff; }
.faixa .proveniencia { border-top: 1px solid rgba(255,255,255,.25); padding-top: var(--espaco-4); margin: 0; }
.creme { background: var(--portal-creme); }
.acoes-b { display: grid; gap: var(--espaco-5); }
.acoes-b .card-bloco { background: #fff; border-radius: var(--raio); padding: var(--espaco-5);
  display: grid; gap: var(--espaco-5); }
.acoes-b .card-bloco .card-previa { max-width: 240px; }
.acoes-b .bloco { margin-bottom: var(--espaco-4); }
@media (min-width: 1024px) {
  .hero-b { padding: var(--espaco-7) 0; }
  .hero-b .container { grid-template-columns: 7fr 5fr; }
  .passos { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .linha.horizontal { grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); gap: var(--espaco-5); }
  .linha.horizontal li { padding-left: 0; padding-top: 2.5rem; }
  .linha.horizontal li::after { content: ""; position: absolute; left: 1.5rem; right: calc(-1 * var(--espaco-5));
    top: calc(.75rem - 2px); height: 4px; background: var(--cor-marca); }
  .linha.horizontal li:last-child::after { display: none; }
  .faixa-b .container { display: grid; grid-template-columns: 7fr 5fr; column-gap: var(--espaco-7); }
  .faixa-b .container.sem-numeros { grid-template-columns: 1fr; }
  .faixa-b .proveniencia { grid-column: 1 / -1; }
  .acoes-b { grid-template-columns: 2fr 1fr; column-gap: var(--espaco-7); }
  .acoes-b .card-bloco { grid-template-columns: auto 1fr; align-items: start; }
}
""",
    # C — combinação: estrutura da A, protagonismo da B (faixa, números, card ao lado).
    "c": """
.hero { background: var(--cor-institucional); padding: var(--espaco-6) 0; }
.hero .container { display: grid; gap: var(--espaco-6); align-items: center; }
.hero h1 { color: var(--portal-profundo); }
.hero .proposta { font-size: var(--fonte-3); }
.hero figure { margin: 0; text-align: center; }
.hero figure .card-previa { margin: 0 auto; max-width: 260px; }
.hero figcaption { margin-top: var(--espaco-2); }
.blocos-4 .bloco { border-top: var(--borda-acento) solid var(--cor-marca); }
.voz { background: var(--portal-creme); border-radius: var(--raio); padding: var(--espaco-5); }
.faixa { background: var(--portal-profundo); color: #fff; padding: var(--espaco-6) 0; }
.faixa h1 { color: #fff; }
.faixa .container { display: grid; gap: var(--espaco-6); }
.faixa .sintese { font-size: var(--fonte-3); }
.faixa .origem, .faixa .suave { color: var(--portal-profundo-texto); }
.faixa .foto { background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.55);
  color: var(--portal-profundo-texto); min-height: 8.75rem; }
.faixa .foto strong { color: #fff; }
.linha { list-style: none; margin: var(--espaco-5) 0; padding: 0; }
.linha li { position: relative; padding-left: 2.5rem; margin-bottom: var(--espaco-4); }
.linha li::before { content: ""; position: absolute; left: 0; top: .15rem; width: 1.5rem; height: 1.5rem;
  border: .4rem solid var(--cor-marca); border-radius: 50%; background: var(--portal-profundo); }
.linha .ano { display: block; font-size: var(--fonte-2); font-weight: 700; line-height: 1.2; }
.linha p { margin: 0 0 var(--espaco-1); }
.linha .curso { font-weight: 600; }
.faixa .proveniencia { border-top: 1px solid rgba(255,255,255,.25); padding-top: var(--espaco-4); margin: 0; }
.grade { display: grid; gap: var(--espaco-6); padding-top: var(--espaco-6); padding-bottom: var(--espaco-7); }
.grade > * { min-width: 0; }
.card-lateral { background: var(--portal-creme); border-radius: var(--raio); padding: var(--espaco-5); align-self: start; }
.card-lateral .card-previa { margin: 0 auto var(--espaco-4); }
.card-lateral .botao { width: 100%; }
.card-lateral .ligacao { display: flex; justify-content: center; }
@media (min-width: 1024px) {
  .hero { padding: var(--espaco-7) 0; }
  .hero .container { grid-template-columns: 7fr 5fr; }
  .blocos-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .faixa { padding: var(--espaco-7) 0; }
  .faixa .container { grid-template-columns: 7fr 5fr; align-items: stretch; }
  .faixa .foto { min-height: 13.75rem; }
  .grade { grid-template-columns: 2fr 1fr; column-gap: var(--espaco-7); }
  .grade > * { grid-column: 1; }
  .grade > .card-lateral { grid-column: 2; grid-row: 1 / span 5; }
}
""",
}

# --- Fragmentos ---------------------------------------------------------------------------


def assinatura() -> str:
    svg = (RAIZ / "trajetoria/interface/templates/interface/assinatura.svg").read_text("utf-8")
    svg = re.sub(r"<\?xml[^>]*>\s*", "", svg)
    svg = re.sub(r'width="[^"]*pt" height="[^"]*pt" ', "", svg, count=1)
    return svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)


ASSINATURA = None


def e(texto) -> str:
    return escape(str(texto), quote=True)


def com_origem(frase: str, origem: str) -> str:
    """Frase seguida da origem, presa à última palavra (P9: sem "·" órfão)."""
    return f'{e(frase)}&nbsp;<span class="origem">·&nbsp;{e(origem)}</span>'


def pagina(direcao: str, titulo: str, corpo: str, pessoa: str | None, navegacao: bool) -> str:
    demo = (
        f'<span><strong>Pessoa fictícia:</strong> {e(pessoa)}</span><a href="#">Sair</a>'
        if pessoa else ""
    )
    nav = ""
    if navegacao:
        itens = ["Início", "Minha trajetória", "Oportunidades", "Pesquisa", "Meu e-mail"]
        nav = (
            '<nav class="navegacao" aria-label="Portal do Egresso"><div class="container"><ul>'
            + "".join(
                f'<li><a href="#"{" aria-current=\"page\"" if i == 0 else ""}>{e(t)}</a></li>'
                for i, t in enumerate(itens)
            )
            + "</ul></div></nav>"
        )
    entrar_topo = "" if navegacao else '<a class="ligacao entrar-topo" href="#">Entrar no Portal</a>'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} — {e(DIRECOES[direcao])} (protótipo)</title>
<style>{BASE_CSS}{CSS[direcao]}</style>
</head>
<body>
<div class="prototipo" data-medida="faixa"><div class="container"><strong>Protótipo</strong> · {e(DIRECOES[direcao])} · ADR 0009. Não é o produto.</div></div>
<div class="demonstracao" data-medida="faixa"><div class="container"><span><strong>Ambiente de demonstração.</strong> Dados fictícios.</span>{demo}</div></div>
<header class="cabecalho"><div class="container" data-medida="container">
<span class="assinatura" role="img" aria-label="Instituto Federal do Espírito Santo">{ASSINATURA}</span>
<p class="produto">Portal do Egresso <span>Instituto Federal do Espírito Santo</span></p>
{entrar_topo}
</div></header>
{nav}
<main>
{corpo}
</main>
<footer class="rodape"><div class="container">
<p>Instituto Federal do Espírito Santo</p>
<p>Portal do Egresso — demonstração local com dados fictícios.</p>
</div></footer>
</body>
</html>
"""


def foto(rotulo="Fotografia institucional") -> str:
    return (f'<div class="foto" aria-hidden="true"><div><strong>{e(rotulo)}</strong>'
            "aguarda ACS (ADR 0009, decisão 5)</div></div>")


def card_exemplo(classe="") -> str:
    return (
        f'<figure class="{classe}"><span class="selo">Exemplo com dados fictícios</span>'
        f'<img class="card-previa" src="card-exemplo.png" width="270" height="480" '
        f'alt="{e(EXEMPLO_ALT)}"><figcaption class="suave">O card que você baixa no Portal.'
        "</figcaption></figure>"
    )


def blocos_publico(classe="blocos blocos-4") -> str:
    itens = "".join(
        f'<div class="bloco"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in PUBLICO["blocos"]
    )
    return (
        '<section class="secao" aria-labelledby="o-que-encontra"><div class="container">'
        '<h2 id="o-que-encontra">O que você encontra no Portal</h2>'
        f'<div class="{classe}">{itens}</div></div></section>'
    )


def voz(classe="voz") -> str:
    return (
        '<section class="secao" aria-labelledby="voz"><div class="container">'
        f'<div class="{classe}"><h2 id="voz">{e(PUBLICO["voz_titulo"])}</h2>'
        f'<p class="texto">{e(PUBLICO["voz"])}</p>'
        f'<a class="botao" href="#">{e(PUBLICO["entrar"])}</a></div></div></section>'
    )


def chamada(classe_botao="botao") -> str:
    return (
        f'<p class="rotulo suave">{e(PUBLICO["rotulo"])}</p>'
        f'<h1>{e(PUBLICO["h1"])}</h1>'
        f'<p class="proposta texto">{e(PUBLICO["proposta"])}</p>'
        f'<p><a class="{classe_botao}" href="#" data-medida="entrar">{e(PUBLICO["entrar"])}</a></p>'
        f'<p class="suave">{e(PUBLICO["como_entrar"])}</p>'
    )


def acoes_blocos(p, com_card=True) -> list[str]:
    blocos = [
        ("Sua trajetória", "Os capítulos da sua formação no Ifes, com a linha do tempo.",
         "Ver minha trajetória no Ifes"),
    ]
    if com_card:
        blocos.append(("Seu card", "Uma imagem vertical para o story ou o status.",
                       "Baixar o card da sua trajetória"))
    blocos.append(("Seu e-mail", "O endereço que o Ifes usa para falar com você.",
                   "Manter seu e-mail com o Ifes"))
    return [
        f'<div class="bloco"><h3>{e(t)}</h3><p>{e(d)}</p><a class="ligacao" href="#"'
        f'{" data-medida=\"acao\"" if i == 0 else ""}>{e(a)}</a></div>'
        for i, (t, d, a) in enumerate(blocos)
    ]


def numeros(p) -> str:
    if not p["numeros"]:
        return ""
    itens = "".join(
        f'<div class="numero"><strong>{n}</strong><p>{e(t)}</p></div>' for n, t in p["numeros"]
    )
    return (
        '<section aria-labelledby="naquele-ano"><h2 id="naquele-ano">Naquele ano no Ifes</h2>'
        f'<div class="numeros">{itens}</div><p class="suave">{e(p["apuracao"])}</p></section>'
    )


def oportunidades(p) -> str:
    o = p["oportunidade"]
    return (
        '<section aria-labelledby="oportunidades"><h2 id="oportunidades">Oportunidades</h2>'
        f'<p class="oportunidade-titulo"><a href="#">{e(o["titulo"])}</a></p>'
        f'<p class="suave">{e(o["por_que"])}</p><p class="suave">{e(o["origem"])}</p>'
        f'<p><a class="ligacao" href="#">{e(o["ver"])}</a></p></section>'
    )


def convite(p) -> str:
    texto, acao = p["convite"]
    return (
        '<section class="convite" aria-labelledby="convite"><h2 id="convite">'
        f'Pesquisa de acompanhamento</h2><p class="texto">{e(texto)}</p>'
        f'<a class="botao" href="#">{e(acao)}</a></section>'
    )


def card_previa(p) -> str:
    return (f'<img class="card-previa" src="{p["card"]}" width="270" height="480" '
            f'alt="{e(p["card_alt"])}" data-medida="card">')


def linha_do_tempo(p, classe="linha") -> str:
    itens = []
    for i, f in enumerate(p["formacoes"]):
        fato = ' data-medida="fato"' if i == 0 else ""
        derivado = (
            f'<p>{com_origem(f["derivado"], "Calculado a partir dos registros")}</p>'
            if f.get("derivado") else ""
        )
        itens.append(
            f'<li><span class="ano">{f["ano"]}</span>'
            f'<p class="curso"{fato}>{com_origem(f["frase"], "Registro do Ifes")}</p>'
            f'<p class="suave">{e(f["atributos"])}</p>{derivado}</li>'
        )
    return f'<ol class="{classe}">{"".join(itens)}</ol>'


# --- Telas --------------------------------------------------------------------------------


def publico(d: str) -> str:
    if d == "a":
        corpo = (
            f'<div class="hero"><div class="container"><div>{chamada()}</div>'
            f'{foto()}</div></div>' + blocos_publico() + voz()
        )
    elif d == "b":
        passos = "".join(
            f"<li><h3>{e(t)}</h3><p>{e(x)}</p></li>" for t, x in PUBLICO["passos"]
        )
        corpo = (
            f'<div class="faixa hero-b"><div class="container"><div>'
            f'{chamada("botao botao-claro")}</div>{card_exemplo()}</div></div>'
            '<section class="secao" aria-labelledby="como-funciona"><div class="container">'
            f'<h2 id="como-funciona">Como funciona</h2><ol class="passos">{passos}</ol>'
            "</div></section>" + voz("")
        )
    else:
        corpo = (
            f'<div class="hero"><div class="container"><div>{chamada()}</div>'
            f'{card_exemplo()}</div></div>' + blocos_publico() + voz()
        )
    return pagina(d, "Portal do Egresso", corpo, None, navegacao=False)


def inicio(d: str, p: dict) -> str:
    h1 = '<h1>Sua história com o Ifes</h1>'
    if d == "a":
        formacoes = "".join(
            f'<li><p class="fato"{" data-medida=\"fato\"" if i == 0 else ""}>'
            f'{com_origem(f["frase"], "Registro do Ifes")}</p>'
            f'<p class="suave">{e(f["atributos"])}</p>'
            + (f'<p>{com_origem(f["derivado"], "Calculado a partir dos registros")}</p>'
               if f.get("derivado") else "")
            + "</li>"
            for i, f in enumerate(p["formacoes"])
        )
        corpo = (
            f'<div class="container"><div class="abertura-foto foto" aria-hidden="true"><div>'
            "<strong>Fotografia institucional da unidade</strong>aguarda ACS (ADR 0009, "
            f'decisão 5)</div></div><div class="titulo-inicio">{h1}'
            f'<p>{e(p["sintese"])}</p></div>'
            f'<div class="grade" data-medida="grade"><div>'
            f'<ul class="formacoes">{formacoes}</ul><p class="suave">{e(PROVENIENCIA)}</p></div>'
            '<section class="acoes-a" aria-labelledby="acoes"><h2 id="acoes">O que você pode '
            f'fazer</h2>{"".join(acoes_blocos(p))}</section></div>'
            f'{oportunidades(p)}<div style="height:var(--espaco-6)"></div>{convite(p)}'
            '<div style="height:var(--espaco-7)"></div></div>'
        )
    elif d == "b":
        horizontal = "linha horizontal" if len(p["formacoes"]) > 1 else "linha"
        numeros_faixa = ""
        if p["numeros"]:
            itens = "".join(
                f'<div class="numero"><strong>{n}</strong><p>{e(t)}</p></div>'
                for n, t in p["numeros"]
            )
            numeros_faixa = (
                '<section aria-labelledby="naquele-ano"><h2 id="naquele-ano">Naquele ano no '
                f'Ifes</h2><div class="numeros" style="grid-template-columns:1fr">{itens}</div>'
                f'<p class="suave">{e(p["apuracao"])}</p></section>'
            )
        classe = "container" if p["numeros"] else "container sem-numeros"
        blocos = acoes_blocos(p, com_card=False)
        corpo = (
            f'<div class="faixa faixa-b"><div class="{classe}"><div>{h1}'
            f'<p class="sintese">{e(p["sintese"])}</p>{linha_do_tempo(p, horizontal)}</div>'
            f'{numeros_faixa}<p class="proveniencia suave">{e(PROVENIENCIA)}</p></div></div>'
            '<div class="creme secao"><div class="container">'
            '<section aria-labelledby="acoes"><h2 id="acoes">O que você pode fazer</h2>'
            f'<div class="acoes-b" data-medida="grade"><div class="card-bloco">{card_previa(p)}'
            '<div><h3>Seu card</h3><p class="suave">Uma imagem vertical da sua trajetória para '
            'o story ou o status das redes sociais.</p><p><a class="botao" href="#" '
            'data-medida="acao">Baixar o card da sua trajetória</a></p></div></div>'
            f'<div>{"".join(blocos)}</div></div></section></div></div>'
            f'<div class="secao"><div class="container">{oportunidades(p)}'
            f'<div style="height:var(--espaco-6)"></div>{convite(p)}</div></div>'
        )
    else:
        corpo = (
            f'<div class="faixa"><div class="container"><div>{h1}'
            f'<p class="sintese">{e(p["sintese"])}</p>{linha_do_tempo(p)}'
            f'<p class="proveniencia suave">{e(PROVENIENCIA)}</p></div>'
            f'{foto("Fotografia institucional da unidade")}</div></div>'
            f'<div class="container grade" data-medida="grade">{numeros(p)}'
            '<section aria-labelledby="acoes"><h2 id="acoes">O que você pode fazer</h2>'
            f'<div class="blocos">{"".join(acoes_blocos(p, com_card=False))}</div></section>'
            '<section class="card-lateral" aria-labelledby="seu-card"><h2 id="seu-card">Seu '
            f'card</h2>{card_previa(p)}<p class="suave">Uma imagem vertical para o story ou o '
            'status das redes sociais.</p><a class="botao" href="#" data-medida="acao">'
            'Baixar o card (PNG)</a><a class="ligacao" href="#">Ver a trajetória completa</a>'
            f'</section>{oportunidades(p)}{convite(p)}</div>'
        )
    return pagina(d, "Início", corpo, p["pessoa"], navegacao=True)


TELAS = {
    "publico": ("Página pública", lambda d: publico(d)),
    "inicio-ana": ("Início — Ana (1 formação)", lambda d: inicio(d, ANA)),
    "inicio-diego": ("Início — Diego (3 formações)", lambda d: inicio(d, DIEGO)),
}


def main():
    global ASSINATURA
    ASSINATURA = assinatura()
    gerar_cards()
    for d in DIRECOES:
        for chave, (_, gerar) in TELAS.items():
            (PASTA / f"{d}-{chave}.html").write_text(gerar(d), "utf-8")
    print("ok:", sorted(p.name for p in PASTA.glob("*.html")))


if __name__ == "__main__":
    main()

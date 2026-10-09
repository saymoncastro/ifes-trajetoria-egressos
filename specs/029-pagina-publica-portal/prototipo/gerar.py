# ruff: noqa: E501 — HTML e CSS embutidos em linhas longas (protótipo).
"""Protótipo comparativo da página pública (Feature 029): versão atual (028) × proposta.

A proposta parte do HTML **realmente servido** em `/` (cabeçalho, faixa de demonstração, CSS
da 015 e da camada do Portal, card de exemplo da 021) e troca só o conteúdo principal, com
uma folha própria. Os textos e os dados da demonstração vêm do código: card de
`portal/exemplo.py` e frases da montagem da narrativa da 021. Nada aqui é importado pela
aplicação; não é implementação.

Uso, na raiz do repositório, com o `.env` da demonstração:

    source .env && uv run python specs/029-pagina-publica-portal/prototipo/gerar.py

`--base` define para onde a chamada principal leva (padrão `http://127.0.0.1:8000`), para o
Checkpoint 1. Depois de gerar, mede e captura as duas versões com o medidor dos protótipos
da ADR 0009 (`docs/prototipos/2026-10-09-portal/medir.py`) e escreve `index.html`.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
CAPTURAS = PASTA / "capturas"

# --- Conteúdo da proposta (textos provisórios da equipe; FR-005 a FR-010) ----------------

CSS = """
/* 029 — protótipo da página pública. Hipótese, não produto. Só tokens da 015 e da camada
   do Portal (ADR 0009): system-ui, h1 40/28 px, verde de ação, verde profundo e creme. */
.pp-kicker { font-size: var(--fonte-5); font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; margin: 0 0 .75rem; color: var(--portal-suave); }
.pp-secao .pp-kicker { color: #257a33; }
.pp-hero { display: grid; gap: 2rem; padding-block: 2rem 2.5rem; }
.pp-hero h1 { margin: 0 0 1rem; }
.pp-lead { font-size: var(--fonte-3); }
.pp-acoes { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem 1rem; margin: 1.5rem 0 .75rem; }
.pp-acoes p { margin: 0; }
.portal-faixa a.pp-secundaria { display: inline-flex; align-items: center; min-height: 44px;
  padding: .5rem 1.25rem; border: 2px solid var(--portal-suave); border-radius: var(--raio);
  color: #fff; font-weight: 600; text-decoration: none; }
.portal-faixa a.pp-secundaria:hover { background: rgba(255,255,255,.1); }
.pp-nota { font-size: var(--fonte-5); color: var(--portal-suave); }
.pp-confianca { list-style: none; margin: 1.5rem 0 0; padding: 1rem 0 0; display: grid; gap: .5rem;
  border-top: 1px solid rgba(255,255,255,.25); }
.pp-confianca li { position: relative; padding-left: 1.75rem; }
.pp-confianca li::before { content: ""; position: absolute; left: .1rem; top: .35rem; width: .85rem;
  height: .45rem; border-left: 3px solid var(--cor-marca); border-bottom: 3px solid var(--cor-marca);
  transform: rotate(-45deg); }
.pp-visual { position: relative; }
.pp-cartao { border-radius: var(--raio); padding: 1.25rem 1.5rem; color: var(--cor-texto); }
.pp-cartao p { margin: 0 0 .25rem; }
.pp-cartao-oportunidade { background: #fff; }
.pp-cartao-oportunidade .oportunidade-titulo { font-size: var(--fonte-3); font-weight: 700; margin: .25rem 0 .5rem; }
.pp-cartao-trajetoria { background: var(--portal-creme); }
.pp-cartao .pp-ano { font-size: var(--fonte-2); font-weight: 700; color: #257a33; }
.pp-cartao .pp-origem { color: var(--cor-texto-suave); font-size: var(--fonte-5); }
.pp-card { margin: 0; text-align: center; }
.pp-card svg { display: block; width: 100%; height: auto; border: 2px solid var(--cor-borda-suave);
  border-radius: var(--raio); }
.pp-grade-oportunidades { display: grid; gap: 1.25rem; margin-top: 1.5rem; }
.pp-secao { padding-block: 2.5rem; }
.pp-claro { background: var(--portal-creme); }
.pp-secao > .portal-container > h2 { font-size: var(--fonte-1); margin: 0 0 .5rem; }
.pp-linha { display: grid; gap: 1.25rem; padding-block: 2rem; border-top: 1px solid #ddd5c3; }
.pp-linha:first-of-type { border-top: 0; }
.pp-linha h3 { font-size: var(--fonte-2); margin: 0 0 .5rem; }
.pp-ilustra { border-radius: var(--raio); padding: min(1.5rem, 5vw); }
.pp-ilustra .portal-selo { margin-bottom: 1rem; }
.pp-escuro { background: var(--portal-profundo); color: #fff; }
.pp-escuro .inicio-formacoes { margin-top: .75rem; }
.pp-branco { background: #fff; border: 1px solid var(--cor-borda-suave); }
.pp-ilustra .pp-card { width: min(100%, 15rem); margin-inline: auto; }
.pp-ilustra .oportunidade-titulo { font-size: var(--fonte-3); margin: .25rem 0 .5rem; }
.pp-participar { display: grid; gap: 1.25rem; }
.pp-participar > div { border-left: 4px solid var(--cor-marca); padding: .25rem 0 .25rem 1.25rem; }
.pp-participar h3, .pp-participar-item h3 { margin: 0 0 .5rem; }
.pp-participar-item { border-left: 4px solid var(--cor-marca); padding: .25rem 0 .25rem 1.25rem; }
.pp-contribuir { border-top: 0; padding-block: 0; margin-bottom: 2rem; }
.pp-marco { color: var(--cor-acao); font-weight: 700; }
.pp-final { padding-block: 2.5rem; }
.pp-final h2 { font-size: var(--fonte-1); margin: 0 0 .5rem; }
/* No celular a cópia decorativa do card sai: a demonstração mostra o card logo abaixo. */
@media (max-width: 767px) { .pp-visual { display: none; } }
@media (min-width: 768px) {
  .pp-card .portal-selo { white-space: nowrap; }
  .pp-grade-oportunidades { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pp-participar { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.5rem; }
  .pp-secao > .portal-container > h2, .pp-final h2 { font-size: 2rem; }
}
@media (min-width: 1024px) {
  .pp-hero { grid-template-columns: 6fr 5fr; align-items: center; gap: 3rem; padding-block: 2.5rem; }
  .pp-visual { min-height: 26rem; }
  .pp-visual { min-height: 30rem; }
  .pp-cartao { box-shadow: 0 .75rem 2rem rgba(0,0,0,.35); }
  .pp-cartao-oportunidade { position: relative; z-index: 1; width: min(26rem, 100%); margin-left: auto; }
  .pp-cartao-trajetoria { position: absolute; left: 0; bottom: 0; width: min(18rem, 80%); z-index: 2; }
  .pp-linha { grid-template-columns: 7fr 4fr; gap: 3rem; align-items: center; }
}
"""


def e(texto) -> str:
    return escape(str(texto), quote=True)


def demonstracao():
    """Frases reais da montagem da 021 para as formações fictícias do card de exemplo."""
    from trajetoria.narrativa.contrato import DERIVADO, INSTITUCIONAL, EntradaDaNarrativa
    from trajetoria.narrativa.montagem import montar
    from trajetoria.portal import mensagens
    from trajetoria.portal.exemplo import FORMACOES_FICTICIAS, card_de_exemplo

    narrativa = montar(EntradaDaNarrativa(nome=None, formacoes=FORMACOES_FICTICIAS,
                                          agregados=(), referencia=date(2026, 1, 31),
                                          demonstracao=True))
    # A mesma origem visível do Início (portal/inicio.py, _ORIGEM).
    origem = {INSTITUCIONAL: mensagens.REGISTRO_DO_IFES, DERIVADO: mensagens.DERIVADO}
    registro = narrativa.secao("o_que_o_ifes_registra")
    trajetoria = narrativa.secao("trajetoria_academica")
    itens = []
    for indice, formacao in enumerate(narrativa.formacoes):
        frases = [f for f in trajetoria.frases if f.formacao == indice]
        corpo = "".join(
            f'<p{" class=\"inicio-atributos\"" if f.tipo != "frase" else ""}>{e(f.texto)}'
            + (f' <span class="inicio-origem">{e(origem[f.origem])}</span>'
               if f.tipo == "frase" and f.origem in origem else "")
            + "</p>"
            for f in frases
        )
        itens.append(f'<li><span class="inicio-ano" aria-hidden="true">{formacao.ano_conclusao}'
                     f"</span>{corpo}</li>")
    sintese = "".join(f'<p class="inicio-sintese">{e(f.texto)}</p>' for f in registro.frases)
    return sintese, "".join(itens), str(card_de_exemplo()), narrativa


def oportunidade(categoria, titulo, resumo, por_que, origem, titulo_tag="h4") -> str:
    """Item no formato da 025 (portal/_oportunidade.html), fictício e sem link real."""
    return (f'<p class="oportunidade-categoria">{e(categoria)}</p>'
            f'<{titulo_tag} class="oportunidade-titulo">{e(titulo)}</{titulo_tag}>'
            f"<p>{e(resumo)}</p>"
            f'<p class="oportunidade-por-que">{e(por_que)}</p>'
            + (f'<p class="oportunidade-origem">{e(origem)}</p>' if origem else ""))


def contribuicao_exemplo(formacao) -> str:
    """Uma contribuição como aparece em "Suas contribuições" (026), com a formação fictícia
    do restante da página."""
    return ('<p class="oportunidade-categoria">Sua contribuição</p>'
            '<h4 class="oportunidade-titulo">Compartilhar experiência</h4>'
            f"<p>{e(formacao.curso)} · Unidade {e(formacao.unidade)} · enviada em 07/10/2026</p>"
            f'<p class="pp-marco">A unidade {e(formacao.unidade)} registrou contato em 09/10/2026.</p>')


def proposta_main(base: str) -> str:
    sintese, linha, card, narrativa = demonstracao()
    primeira, ultima = narrativa.formacoes[0], narrativa.formacoes[-1]
    selo = '<span class="portal-selo">Exemplo com dados fictícios</span>'
    entrar = f"{base}/entrar/"
    curso = oportunidade(
        "Cursos", "Especialização em Gestão de Obras",
        "Pós-graduação presencial na unidade Vitória, com aulas no período noturno.",
        f"Aparece porque você concluiu {ultima.curso} na unidade {ultima.unidade}.",
        "Oferecida pela unidade Vitória · página oficial (exemplo)")
    encontro = oportunidade(
        "Eventos", "Encontro de egressos das engenharias e edificações",
        "Tarde de conversa com egressos e professores, no campus.",
        f"Aparece porque você concluiu {primeira.curso} na unidade {primeira.unidade}.",
        "Oferecida pela unidade Vitória · página oficial (exemplo)")
    return f"""
<section class="portal-faixa" aria-labelledby="proposta-portal">
  <div class="portal-container pp-hero">
    <div>
      <p class="pp-kicker">Portal do Egresso · Ifes</p>
      <h1 id="proposta-portal">Sua história com o Ifes</h1>
      <p class="pp-lead">Encontre oportunidades que o Ifes divulgar para a sua formação, ofereça sua contribuição, participe contando como sua trajetória seguiu e veja suas formações reconhecidas pelo Ifes.</p>
      <div class="pp-acoes">
        <p><a class="portal-botao" href="{e(entrar)}">Conhecer o Portal</a></p>
        <p><a class="pp-secundaria" href="#oferece">Ver como funciona</a></p>
      </div>
      <p class="pp-nota">Para entrar, você confirma seu CPF e sua data de nascimento.</p>
      <ul class="pp-confianca">
        <li>Oportunidades divulgadas pelo próprio Ifes, com o link oficial.</li>
        <li>Suas formações vêm dos registros acadêmicos do Ifes.</li>
        <li>Participar é opcional: você vê tudo sem responder nenhuma pesquisa.</li>
      </ul>
    </div>
    <div class="pp-visual" aria-hidden="true">
      <div class="pp-cartao pp-cartao-oportunidade">{selo}{oportunidade("Eventos", "Encontro de egressos das engenharias e edificações", "Tarde de conversa com egressos e professores, no campus.", f"Aparece porque você concluiu {primeira.curso}.", "", "p")}</div>
      <div class="pp-cartao pp-cartao-trajetoria">
        <p class="pp-ano">{primeira.ano_conclusao} · {ultima.ano_conclusao}</p>
        <p><strong>{e(primeira.curso)}</strong></p>
        <p><strong>{e(ultima.curso)}</strong></p>
        <p class="pp-origem">{e(primeira.unidade)} · Registro do Ifes</p>
      </div>
    </div>
  </div>
</section>
<section class="pp-secao pp-claro" id="oferece" aria-labelledby="titulo-oferece">
  <div class="portal-container">
    <p class="pp-kicker">O Ifes para você</p>
    <h2 id="titulo-oferece">Oportunidades para a sua formação</h2>
    <p>Cursos, eventos, programas e iniciativas de carreira que o Ifes divulga para quem concluiu a sua formação. Cada uma vem com o motivo de aparecer para você e o caminho para a página oficial. Quando não há nenhuma, nada aparece.</p>
    <div class="pp-grade-oportunidades">
      <div class="pp-ilustra pp-branco">{selo}{curso}</div>
      <div class="pp-ilustra pp-branco">{selo}{encontro}</div>
    </div>
  </div>
</section>
<section class="pp-secao" aria-labelledby="titulo-participar">
  <div class="portal-container">
    <p class="pp-kicker pp-kicker-verde">Você e o Ifes</p>
    <h2 id="titulo-participar">Como você participa</h2>
    <div class="pp-linha pp-contribuir">
      <div class="pp-participar-item">
        <h3>Contribua com o Ifes</h3>
        <p>Ofereça-se para conversar com estudantes, ser mentor, divulgar uma vaga da sua área, participar de projetos ou propor uma parceria. A unidade da formação que você escolher recebe e pode entrar em contato pelo e-mail que você informar. Não há prazo garantido.</p>
        <p>Você acompanha o que enviou, vê quando a unidade registra o contato e pode retirar quando quiser.</p>
      </div>
      <div class="pp-ilustra pp-branco">{selo}{contribuicao_exemplo(ultima)}</div>
    </div>
    <div class="pp-participar">
      <div>
        <h3>Conte como sua trajetória seguiu</h3>
        <p>Quando o Ifes abre uma pesquisa de acompanhamento para a sua formação, o convite aparece no Portal. Responder é como você atualiza sua trajetória com o Ifes. É opcional.</p>
      </div>
      <div>
        <h3>Mantenha um canal com o Ifes</h3>
        <p>Você pode deixar um e-mail para o Ifes convidar você para as próximas pesquisas de acompanhamento. Também é opcional.</p>
      </div>
    </div>
  </div>
</section>
<section class="pp-secao pp-claro" aria-labelledby="titulo-trajetoria">
  <div class="portal-container">
    <p class="pp-kicker">Sua formação</p>
    <h2 id="titulo-trajetoria">Sua trajetória com o Ifes</h2>
    <p>Suas formações aparecem com curso, unidade e ano, e com a origem de cada informação. Nada disso é preenchido por você. Se quiser, guarde um card da sua trajetória para compartilhar.</p>
    <div class="pp-linha">
      <div class="pp-ilustra pp-escuro">{selo}{sintese}<ul class="inicio-formacoes">{linha}</ul></div>
      <div class="pp-ilustra pp-branco"><figure class="pp-card">{selo}{card}</figure></div>
    </div>
  </div>
</section>
<section class="portal-faixa pp-final" aria-labelledby="titulo-final">
  <div class="portal-container">
    <h2 id="titulo-final">Sua formação faz parte da história do Ifes</h2>
    <p>Entre para ver o que o Ifes tem para você e como participar.</p>
    <p><a class="portal-botao" href="{e(entrar)}">Conhecer o Portal</a></p>
  </div>
</section>
"""


# --- Geração ------------------------------------------------------------------------------

def servido() -> str:
    """O HTML que a demonstração serve hoje em `/` sem sessão (a página da 028)."""
    from django.test import Client

    resposta = Client(HTTP_HOST="127.0.0.1").get("/")
    assert resposta.status_code == 200, resposta.status_code
    html = resposta.content.decode()
    return re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", html)


def trocar(texto, antes, depois):
    if antes not in texto:
        raise SystemExit(f"medir.py mudou; trecho não encontrado: {antes!r}")
    return texto.replace(antes, depois)


def medidor():
    spec = importlib.util.spec_from_file_location(
        "medidor", RAIZ / "docs/prototipos/2026-10-09-portal/medir.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PASTA = PASTA
    moldura = trocar(m.MOLDURA, ".demonstracao", ".faixa-demonstracao")
    moldura = trocar(moldura, "[...d.querySelectorAll('main .container')]",
                     "[...d.querySelectorAll('main .portal-container')]")
    moldura = trocar(moldura, "[data-medida=grade]", ".pp-linha")
    moldura = trocar(moldura, "[data-medida=fato]", ".pp-lead, .portal-hero .proposta")
    moldura = trocar(moldura, "[data-medida=card]", ".pp-visual, .portal-exemplo")
    moldura = trocar(moldura, "[data-medida=acao]", ".pp-acoes .portal-botao, .portal-hero .portal-botao")
    moldura = trocar(moldura, "[data-medida=entrar]", ".pp-acoes .portal-botao, .portal-hero .portal-botao")
    moldura = trocar(moldura, "[...d.querySelectorAll('a')].filter(isolado)",
                     "[...d.querySelectorAll('main a, button, summary, nav a')]"
                     ".filter(e => !e.matches('main a') || isolado(e))")
    moldura = trocar(moldura, "e.getBoundingClientRect().height < 44",
                     "(e.getBoundingClientRect().height < 44 || e.getBoundingClientRect().width < 44)")
    return m, moldura


def avaliar(v):
    """Critérios medidos da spec (SC-001 a SC-006). `v` = medidas de uma versão."""
    falhas = []
    for caso, r in v.items():
        if "@" in caso and r["rolagem"] > r["largura"]:
            falhas.append(f"rolagem horizontal em {caso}")
    c = v["375x812"]
    if max(c["h1"], c["fato"], c["entrar"]) > 812:
        falhas.append("375×812: título, frase ou chamada fora da primeira tela")
    for caso, altura in (("1280x720", 720), ("1440x900", 900)):
        r = v[caso]
        limite = altura + r["faixa_demo"]
        if max(r["h1"], r["fato"], r["entrar"]) > limite:
            falhas.append(f"{caso}: título, frase ou chamada fora da primeira tela")
        if r["card"] is None or r["card"] >= limite:
            falhas.append(f"{caso}: sem peça visual na primeira tela")
        if r["conteudo"] < 1000:
            falhas.append(f"{caso}: conteúdo com menos de 1000 px")
    if v["1024x768"]["colunas"] is not None:
        if v["1024x768"]["colunas"] < 2 or v["375x812"]["colunas"] != 1:
            falhas.append("demonstração sem duas colunas a 1024 ou sem uma a 375")
    for caso, r in v.items():
        if r["h1s"] != 1 or r["alvos_pequenos"]:
            falhas.append(f"{caso}: h1 ({r['h1s']}) ou alvos pequenos ({r['alvos_pequenos']})")
            break
    if v["1440x900"]["caracteres_max"] > 80:
        falhas.append(f"linha com ~{v['1440x900']['caracteres_max']} caracteres")
    return falhas


PARES = [
    ("Branco na faixa profunda", "#ffffff", "#0e3b23"),
    ("Texto secundário na faixa (pp-nota, kicker)", "#cfe6d6", "#0e3b23"),
    ("Kicker verde no creme", "#257a33", "#f6f2e8"),
    ("Kicker verde no branco", "#257a33", "#ffffff"),
    ("Texto no creme", "#1b1b1b", "#f6f2e8"),
    ("Texto suave no creme", "#565c65", "#f6f2e8"),
    ("Selo de exemplo", "#1b1b1b", "#fff1d2"),
    ("Texto suave no branco", "#565c65", "#ffffff"),
    ("Verde profundo no botão claro", "#0e3b23", "#ffffff"),
    ("Ação verde no branco", "#195128", "#ffffff"),
]


def medir_e_capturar():
    m, moldura = medidor()
    CAPTURAS.mkdir(exist_ok=True)
    caminho = PASTA / "_moldura.html"
    caminho.write_text(moldura, "utf-8")
    medidas = {}
    try:
        for versao in ("atual", "proposta"):
            pagina = f"{versao}.html"
            v = {}
            for largura in (320, 375, 768, 1024, 1280, 1440):
                for fonte in (100, 200):
                    v[f"{largura}@{fonte}"] = m.medir(pagina, largura, fonte=fonte)
            v["375x812"] = m.medir(pagina, 375, 812)
            v["1024x768"] = m.medir(pagina, 1024, 768)
            v["1280x720"] = m.medir(pagina, 1280, 720)
            v["1440x900"] = m.medir(pagina, 1440, 900)
            for largura in (375, 1024, 1440):
                m.capturar(pagina, largura, v[f"{largura}@100"]["altura_doc"],
                           CAPTURAS / f"{versao}-{largura}.png")
            m.capturar(pagina, 375, 812, CAPTURAS / f"{versao}-375x812.png")
            for caso, largura, altura in (("1280x720", 1280, 720), ("1440x900", 1440, 900)):
                # Descontar a faixa: desloca a moldura, como nas evidências da 028.
                m.capturar(pagina, largura, altura, CAPTURAS / f"{versao}-{caso}.png",
                           topo=v[caso]["faixa_demo"])
            medidas[versao] = v
            print(versao, "medida", flush=True)
    finally:
        caminho.unlink(missing_ok=True)
    contraste = [{"par": n, "razao": round(m.contraste(a, b), 2)} for n, a, b in PARES]
    (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False), "utf-8")
    (PASTA / "contraste.json").write_text(json.dumps(contraste, indent=1, ensure_ascii=False), "utf-8")
    return medidas, contraste


def comparacao(medidas, contraste) -> str:
    linhas = []
    for nome, chave in (("Primeira tela no celular (375×812)", "375x812"),
                        ("Primeira tela no desktop (1280×720, sem a faixa)", "1280x720"),
                        ("Primeira tela no desktop (1440×900, sem a faixa)", "1440x900"),
                        ("Página inteira, celular (375)", "375"),
                        ("Página inteira, 1024", "1024"),
                        ("Página inteira, 1440", "1440")):
        linhas.append(
            f"<h2>{nome}</h2><div class=lado>"
            + "".join(f'<figure><figcaption>{"Atual (028)" if v == "atual" else "Proposta (029)"}'
                      f'</figcaption><a href="capturas/{v}-{chave}.png"><img loading=lazy '
                      f'src="capturas/{v}-{chave}.png" alt="{v}, {nome}"></a></figure>'
                      for v in ("atual", "proposta"))
            + "</div>")
    criterios = "".join(
        f"<tr><th scope=row>{'Atual (028)' if v == 'atual' else 'Proposta (029)'}</th><td>"
        + (("✗ " + "; ".join(avaliar(medidas[v]))) if avaliar(medidas[v]) else "✓ todos os critérios medidos")
        + "</td></tr>"
        for v in ("atual", "proposta"))
    pares = "".join(f"<tr><th scope=row>{c['par']}</th><td>{c['razao']:.2f}:1"
                    f"{' ✓' if c['razao'] >= 4.5 else ' ✗'}</td></tr>" for c in contraste)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>029 — página pública: atual × proposta</title>
<style>body{{margin:0;font-family:system-ui,sans-serif;color:#1b1b1b;line-height:1.5}}
main{{max-width:90rem;margin:0 auto;padding:1rem 1.5rem 4rem}} a{{color:#195128}}
table{{border-collapse:collapse;margin:1rem 0 2rem}} th,td{{border:1px solid #c6cace;padding:.5rem;text-align:left}}
.lado{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}}
figure{{margin:0}} figure img{{width:100%;border:1px solid #c6cace}} figure>a{{display:block;max-height:60rem;overflow-y:auto}}
figcaption{{font-weight:700;margin-bottom:.25rem}} h2{{border-top:4px solid #2f9e41;padding-top:1rem;margin-top:2rem}}</style>
</head><body><main>
<h1>Página pública — atual (028) × proposta (029)</h1>
<p>Protótipo da Feature 029 para avaliação do solicitante e para o bloco P do Checkpoint 1.
Não é implementação. A <a href="proposta.html">proposta</a> é o HTML servido pela
demonstração com o conteúdo principal trocado; a <a href="atual.html">atual</a> é a página
servida hoje. Avalie pelo celular primeiro (ADR 0009, decisão 2).</p>
<h2>Critérios medidos (SC-001 a SC-006)</h2>
<table><tbody>{criterios}</tbody></table>
<p>Medidas em Chrome headless (<code>gerar.py</code>, com o medidor dos protótipos da ADR
0009). No desktop a faixa de demonstração é descontada; no celular, não.</p>
<h2>Contraste dos pares novos</h2><table><tbody>{pares}</tbody></table>
{"".join(linhas)}
</main></body></html>"""


def gerar(base: str):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    atual = servido()
    (PASTA / "atual.html").write_text(atual, "utf-8")
    inicio = atual.index(">", atual.index('<div class="coluna">', atual.index("<main"))) + 1
    fim = atual.rindex("</div>", 0, atual.index("</main>"))
    oportunidades_css = (RAIZ / "trajetoria/portal/templates/portal/oportunidades.css").read_text("utf-8")
    proposta = atual[:inicio] + proposta_main(base) + atual[fim:]
    proposta = proposta.replace("</style>", oportunidades_css + CSS + "</style>", 1)
    proposta = re.sub(r"<title>.*?</title>", "<title>Sua história com o Ifes — Portal do Egresso</title>",
                      proposta, count=1, flags=re.S)
    (PASTA / "proposta.html").write_text(proposta, "utf-8")
    medidas, contraste = medir_e_capturar()
    (PASTA / "index.html").write_text(comparacao(medidas, contraste), "utf-8")
    for versao in ("atual", "proposta"):
        print(versao, avaliar(medidas[versao]) or "ok")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    gerar(parser.parse_args().base)


if __name__ == "__main__":
    main()

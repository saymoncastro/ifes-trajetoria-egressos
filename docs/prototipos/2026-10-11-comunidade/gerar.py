# ruff: noqa: E501 — HTML e CSS embutidos em linhas longas (protótipo).
"""Telas estáticas de Histórias (B) e Encontre colegas (E1) para o bloco Comunidade do
Checkpoint 2. Conceituais: completam o material comparativo junto do protótipo da 031.

Não abrem a 030 nem especificam o diretório (E1). Mostram só o necessário para as tarefas
H1, H2, D1 e D2 do protocolo e para os critérios CM-C3, CM-C4, CM-U3 e CM-U4. Reaproveitam o
gerador da 031: HTML servido pela demonstração na versão C, faixa "Protótipo: não existe no
Portal", folha `.pe-*` e o arnês de medidas da ADR 0009.

Uso, na raiz do repositório, com o `.env` da demonstração e o banco preparado:

    source .env && uv run python docs/prototipos/2026-10-11-comunidade/gerar.py
"""

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
P031 = "../../../specs/031-encontros-propostos-egressos/prototipo/"

_spec = importlib.util.spec_from_file_location("prototipo_031", RAIZ / "specs/031-encontros-propostos-egressos/prototipo/gerar.py")
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)
e = g.e

FAIXA = ('<p class="prototipo" role="note"><strong>Protótipo: não existe no Portal.</strong> '
         'Histórias e Encontre colegas, ideias para conversa, com dados fictícios.</p>')

CSS = """
/* Comunidade — protótipo conceitual. Mesma folha da 031 (.pe-*), mais a composição editorial
   das histórias e os cartões do diretório. Sem fotografia de pessoa (DP-2106). */
.pc-hub { display: grid; gap: 1rem; }
.pc-hub > a { display: block; background: #fff; border: 1px solid #e2ddd0; border-radius: 12px; padding: 1.25rem 1.5rem;
  text-decoration: none; color: var(--portal-profundo); }
.pc-hub > a:hover { border-color: var(--portal-profundo); }
.pc-hub strong { display: block; font-family: var(--portal-fonte-titulo); font-size: 1.5rem; line-height: 1.1; margin-bottom: .375rem; }
.pc-hub span { display: block; color: #3f5b47; }
.pc-capa { background: var(--portal-profundo); padding-block: 2rem 2.5rem; }
.pe .pc-capa h1, .pe .pc-capa p { color: var(--portal-creme); }
.pe .pc-capa .pc-chapeu { color: var(--portal-verde-medio); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: var(--fonte-5); margin: 0 0 .75rem; }
.pc-destaque { display: grid; gap: 1.25rem; margin-top: 1.5rem; }
.pc-citacao { font-family: var(--portal-fonte-titulo); font-size: clamp(1.5rem, 6.5vw, 2.25rem); line-height: 1.1;
  letter-spacing: -0.02em; color: var(--portal-creme); margin: 0; max-width: 24ch; }
.pc-citacao::before { content: "“"; color: var(--portal-verde-medio); }
.pc-citacao::after { content: "”"; color: var(--portal-verde-medio); }
.pc-autoria { display: flex; gap: 1rem; align-items: center; }
.pc-autoria p { margin: 0; }
.pe .pc-capa .pc-autoria p { color: var(--portal-suave); }
.pe .pc-capa .pc-autoria .pe-nome { color: #fff; }
.pc-capa .pe-pessoa.pc-autoria { background: transparent; border: 1px solid rgba(207, 230, 214, .35); }
.pc-historias { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
.pc-historias > li { min-width: 0; background: #fff; border: 1px solid #e2ddd0; border-radius: 10px; padding: 1.25rem min(1.25rem, 4vw);
  border-top: 6px solid var(--portal-verde-claro); }
.pc-historias h3 { margin: 0 0 .5rem; }
.pc-historias h3 a { color: var(--portal-profundo); display: inline-flex; min-height: 44px; align-items: center; }
.pc-historias p { margin: 0 0 .25rem; }
.pc-texto { max-width: 40rem; }
.pc-texto p { font-size: 1.125rem; line-height: 1.6; }
.pc-texto .pc-abre::first-letter { font-family: var(--portal-fonte-titulo); font-size: 3.25rem; float: left; line-height: .9;
  margin: .25rem .5rem 0 0; color: var(--portal-verde-rotulo); }
.pc-curadoria { border-left: 4px solid var(--portal-profundo); background: #fff; padding: .75rem 1rem; max-width: 40rem; }
.pc-curadoria p { margin: 0 0 .25rem; }
.pc-colegas { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
.pc-colegas > li { min-width: 0; background: #fff; border: 1px solid #e2ddd0; border-radius: 10px; padding: 1.25rem min(1.25rem, 4vw);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-start; }
.pc-colegas > li > div { flex: 1 1 12rem; min-width: 0; }
.pc-colegas p { margin: 0 0 .25rem; }
.pc-colegas .pe-acoes { margin-top: .5rem; }
.pc-busca { display: grid; gap: .5rem 1rem; max-width: 40rem; }
.pc-busca .campo { margin: 0; }
.pc-previa { background: #fff; border: 2px dashed var(--portal-verde-rotulo); border-radius: 10px; padding: 1rem 1.25rem; max-width: 36rem; }
.pc-previa p { margin: 0 0 .25rem; }
@media (min-width: 768px) {
  .pc-hub { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .pc-historias, .pc-colegas { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1024px) {
  .pc-destaque { grid-template-columns: minmax(0, 7fr) minmax(0, 4fr); align-items: end; gap: 3rem; }
  .pc-busca { grid-template-columns: repeat(3, minmax(0, 1fr)); max-width: none; align-items: end; }
}
"""


def pessoa(inicial, nome, linhas, classe="") -> str:
    return (f'<div class="pe-pessoa {classe}"><span class="pe-inicial" aria-hidden="true">{inicial}</span><div>'
            f'<p class="pe-nome">{e(nome)}</p>' + "".join(f"<p>{x}</p>" for x in linhas) + "</div></div>")


# --- Entrada comum --------------------------------------------------------------------------

def hub() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina">
<h1>Comunidade</h1>
<p class="pe-lead">Três formas de continuar a história com outros egressos do Ifes. Cada uma é escolha sua: você pode só ler, ir a um encontro ou aparecer para colegas.</p>
<nav class="pc-hub" aria-label="Comunidade">
<a href="c1-historias.html"><strong>Histórias</strong><span>Trajetórias contadas por egressos e publicadas pela unidade, com autorização de quem escreveu.</span></a>
<a href="{P031}p2-encontros.html"><strong>Encontros</strong><span>Encontros virtuais propostos por egressos e eventos divulgados pelo Ifes.</span></a>
<a href="c3-colegas-aderir.html"><strong>Encontre colegas</strong><span>Só aparece quem escolhe aparecer. O contato depende do aceite da outra pessoa.</span></a>
</nav>
</div></div>"""


# --- Histórias (B) --------------------------------------------------------------------------

HISTORIA = {
    "titulo": "Voltei para a sala de aula do outro lado da mesa",
    "citacao": "Eu achava que a química era só laboratório. Foi dando aula que descobri que eu gostava de explicar.",
    "nome": "Diego E.", "inicial": "D",
    "origem": "Licenciatura em Química · Vila Velha · 2017",
}


def historias() -> str:
    return f"""<div class="pe">
<section class="pc-capa" aria-labelledby="pe-titulo"><div class="portal-container">
<p class="pc-chapeu">Histórias de egressos</p>
<h1 id="pe-titulo">Histórias</h1>
<p class="pe-lead">Egressos contam como foi depois do Ifes. Cada história foi escrita por quem a viveu e publicada pela unidade, com autorização. Não há ranking nem história "de sucesso" mais importante que outra.</p>
<div class="pc-destaque">
<p class="pc-citacao">{e(HISTORIA["citacao"])}</p>
<div>{pessoa(HISTORIA["inicial"], HISTORIA["nome"], [e(HISTORIA["origem"]) + ' · Registro do Ifes'], "pc-autoria")}
<p class="pe-acoes"><a class="pe-botao" href="c2-historia.html" style="background:var(--portal-creme);color:var(--portal-profundo);border-color:var(--portal-creme)">Ler a história</a></p></div>
</div></div></section>
<section class="pe-grupo" aria-labelledby="pc-mais"><div class="portal-container">
<h2 id="pc-mais">Outras histórias</h2>
<ul class="pc-historias">
<li><p class="pe-selo pe-selo-f">Contada por egresso</p><h3><a href="c2-historia.html">O curso técnico que me levou de volta à agricultura da família</a></h3><p>Elisa E. · Técnico em Agropecuária · Alegre · 2019</p><p class="pe-nota">Publicada pela unidade Alegre</p></li>
<li><p class="pe-selo pe-selo-f">Contada por egresso</p><h3><a href="c2-historia.html">Mudar de área aos 30 e poucos</a></h3><p>Bruno E. · Bacharelado em Engenharia Civil · Vitória · 2020</p><p class="pe-nota">Publicada pela unidade Vitória</p></li>
</ul>
<div class="pe-vazio" style="margin-top:1.5rem"><p><strong>Quer contar a sua?</strong></p><p>Use "Contar sua história" em Participação. A unidade lê, combina o texto com você e só publica com a sua autorização. Você pode retirar a publicação quando quiser.</p></div>
</div></section></div>"""


def historia() -> str:
    return f"""<div class="pe">
<section class="pc-capa" aria-labelledby="pe-titulo"><div class="portal-container">
<p class="pc-chapeu">História de egresso</p>
<h1 id="pe-titulo">{e(HISTORIA["titulo"])}</h1>
{pessoa(HISTORIA["inicial"], HISTORIA["nome"], [e(HISTORIA["origem"]) + ' · Registro do Ifes', 'Nome escolhido por quem escreveu'], "pc-autoria")}
</div></section>
<div class="portal-container pe-pagina">
<div class="pc-texto">
<p class="pc-abre">Entrei no técnico em Química porque era perto de casa. Gostava do laboratório, das aulas práticas, e achava que ia trabalhar numa indústria a vida toda.</p>
<p>Na licenciatura, o estágio numa escola pública mudou o plano. Percebi que o que me prendia não era o experimento, era o momento em que alguém entendia por que a reação acontecia.</p>
<p>Hoje dou aula numa escola estadual. Às vezes uso os mesmos roteiros que aprendi no Ifes, adaptados para uma sala sem laboratório. Quando um estudante pergunta se vale a pena fazer um curso técnico, eu conto essa história.</p>
</div>
<div class="pc-curadoria" role="note">
<p><strong>Escrita por Diego E.</strong> Revisada e publicada pela unidade Vila Velha em 08/10/2026, com a autorização de quem escreveu.</p>
<p>Quem escreveu pode retirar a publicação quando quiser. Não há comentários nem curtidas.</p>
</div>
<p class="pe-acoes"><a href="c1-historias.html">Ver outras histórias</a> <a href="c0-comunidade.html">Voltar à Comunidade</a></p>
</div></div>"""


# --- Encontre colegas (E1) ------------------------------------------------------------------

def aderir() -> str:
    return f"""<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Encontre colegas</h1>
<p class="pe-lead">Uma lista de egressos que <strong>escolheram</strong> aparecer, para quem quer reencontrar alguém do Ifes. Ninguém entra nela automaticamente.</p>
<ul class="pe-ciencia">
<li>Os outros veem só o que você escolher abaixo. Nunca seu e-mail, telefone ou CPF.</li>
<li>Para falar com você, alguém faz um pedido. Você aceita ou recusa; pode também bloquear a pessoa.</li>
<li>Você pode sair da lista quando quiser.</li>
</ul>
<form method="post" action="c4-colegas-lista.html" novalidate>
<div class="campo"><label for="nome">Como você quer aparecer</label><p class="dica" id="nome-dica">Pode ser só o primeiro nome e a inicial.</p><input type="text" id="nome" name="nome" maxlength="40" value="Maria E." aria-describedby="nome-dica"></div>
<fieldset class="pergunta"><legend>Quais formações mostrar <span class="nota">Registro do Ifes. Mostre pelo menos uma.</span></legend>
{g.caixas("formacao", ["Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022", "Especialização em Informática na Educação · Cefor · 2025"], ("Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022",))}</fieldset>
<div class="campo"><label for="frase">Uma frase sobre você <span class="opcional">(opcional)</span></label><p class="dica" id="frase-dica">Até 120 caracteres. Não inclua contatos.</p><textarea id="frase" name="frase" maxlength="120" aria-describedby="frase-dica" style="min-height:6rem">Trabalho com formação de professores e gosto de conversar sobre tecnologia na escola.</textarea></div>
<div class="pc-previa" aria-labelledby="pc-previa-t"><p class="pe-rotulo" id="pc-previa-t">Como os outros vão ver</p>
<p><strong>Maria E.</strong></p><p>Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022 · Registro do Ifes</p><p>"Trabalho com formação de professores e gosto de conversar sobre tecnologia na escola."</p></div>
<p class="pe-acoes"><button type="submit" class="pe-botao">Aparecer em Encontre colegas</button> <a href="c0-comunidade.html">Agora não</a></p>
</form></div></div>"""


COLEGAS = [
    ("A", "Ana E.", "Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022", "Desenvolvo sistemas para prefeituras."),
    ("C", "Carla E.", "Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2021", ""),
    ("R", "Rafael E.", "Técnico em Informática · Serra · 2016", "Voltei a estudar à noite; hoje faço a graduação."),
]


def lista() -> str:
    cartoes = "".join(
        f'<li><span class="pe-inicial" aria-hidden="true">{i}</span><div><p class="pe-nome">{e(n)}</p><p>{e(f)} · Registro do Ifes</p>'
        + (f'<p>"{e(x)}"</p>' if x else "")
        + f'<p class="pe-acoes"><a class="pe-contorno" href="c5-colegas-pedido.html" aria-label="Pedir contato a {e(n)}">Pedir contato</a></p></div></li>'
        for i, n, f, x in COLEGAS)
    return f"""<div class="pe"><div class="portal-container pe-pagina">
<h1>Encontre colegas</h1>
<p class="pe-lead">Só aparece aqui quem escolheu aparecer, e cada pessoa decidiu o que mostrar.</p>
<form class="pc-busca" method="get" action="c4-colegas-lista.html" role="search" aria-label="Procurar colegas">
<div class="campo"><label for="busca">Nome</label><input type="text" id="busca" name="busca" value=""></div>
<div class="campo"><label for="curso">Curso</label><input type="text" id="curso" name="curso" value="Tecnologia em Análise e Desenvolvimento de Sistemas"></div>
<p class="pe-acoes" style="margin:0"><button type="submit" class="pe-botao">Procurar</button></p>
</form>
<h2 style="margin-top:2rem">Quem concluiu este curso e escolheu aparecer</h2>
<ul class="pc-colegas">{cartoes}</ul>
<p class="pe-nota" style="margin-top:1.5rem">A lista não mostra quantas pessoas há nem quem não escolheu aparecer. Você está nela como Maria E.; <a href="c6-colegas-pedidos.html">pedidos e saída da lista</a>.</p>
</div></div>"""


def pedido() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Pedir contato a Ana E.</h1>
<p class="pe-lead">Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022</p>
<ul class="pe-ciencia">
<li>Ana E. recebe o pedido com o seu nome de apresentação, as formações que você mostra e a mensagem abaixo.</li>
<li>Ana E. decide aceitar ou recusar. Se recusar, você não recebe motivo.</li>
<li>Só se houver aceite, cada pessoa vê o contato que a outra escolher informar nesse momento. Nenhum contato aparece antes.</li>
<li>Não há conversa dentro do Portal.</li>
</ul>
<form method="post" action="c4-colegas-lista.html" novalidate>
<div class="campo"><label for="mensagem">Mensagem <span class="opcional">(opcional)</span></label><p class="dica" id="mensagem-dica">Até 300 caracteres. Diga de onde vocês se conhecem.</p>
<textarea id="mensagem" name="mensagem" maxlength="300" aria-describedby="mensagem-dica">Oi, Ana! Fizemos a disciplina de banco de dados na mesma época, em 2020. Queria trocar uma ideia sobre trabalho em prefeituras.</textarea></div>
<p class="pe-acoes"><button type="submit" class="pe-botao">Enviar pedido</button> <a href="c4-colegas-lista.html">Voltar</a></p>
</form></div></div>"""


def pedidos() -> str:
    return """<div class="pe"><div class="portal-container pe-pagina pe-pagina-estreita">
<h1>Seus pedidos de contato</h1>
<h2>Recebidos</h2>
<ul class="pc-colegas"><li><span class="pe-inicial" aria-hidden="true">R</span><div><p class="pe-nome">Rafael E.</p><p>Técnico em Informática · Serra · 2016 · Registro do Ifes</p>
<p>"Você deu monitoria de algoritmos em 2019? Queria agradecer a ajuda daquela época."</p>
<p class="pe-acoes"><a class="pe-botao" href="c6-colegas-pedidos.html">Aceitar</a> <a class="pe-contorno" href="c6-colegas-pedidos.html">Recusar</a> <a href="c6-colegas-pedidos.html">Bloquear</a></p>
<p class="pe-nota">Se aceitar, você escolhe qual contato mostrar a Rafael. Recusar não avisa o motivo. Bloquear impede novos pedidos dessa pessoa. <a href="c6-colegas-pedidos.html">Denunciar</a></p></div></li></ul>
<h2 style="margin-top:2rem">Enviados</h2>
<ul class="pc-colegas"><li><div><p class="pe-nome">Ana E.</p><p>Enviado em 11/10/2026. Aguardando resposta.</p><p class="pe-acoes"><a href="c6-colegas-pedidos.html">Cancelar pedido</a></p></div></li></ul>
<div class="pe-vazio" style="margin-top:2rem"><p><strong>Sair de Encontre colegas</strong></p><p>Você deixa de aparecer na lista na hora. Pedidos pendentes são cancelados.</p>
<p class="pe-acoes"><a class="pe-contorno" href="c0-comunidade.html">Sair da lista</a></p></div>
</div></div>"""


TELAS = {
    "c0-comunidade": ("diego", "Comunidade", hub),
    "c1-historias": ("diego", "Histórias", historias),
    "c2-historia": ("diego", "Voltei para a sala de aula do outro lado da mesa", historia),
    "c3-colegas-aderir": ("maria", "Encontre colegas", aderir),
    "c4-colegas-lista": ("maria", "Encontre colegas", lista),
    "c5-colegas-pedido": ("maria", "Pedir contato", pedido),
    "c6-colegas-pedidos": ("maria", "Seus pedidos de contato", pedidos),
}


def com_navegacao(html: str) -> str:
    """Item "Comunidade" no lugar de "Encontros" da 031 (hipótese; revisão 12 sugere outros
    rótulos). Nenhum item marcado como atual além dele."""
    html = g.com_navegacao(html, None)
    html = html.replace('<li><a href="p2-encontros.html" data-rotulo="Encontros">Encontros</a></li>',
                        '<li><a href="c0-comunidade.html" data-rotulo="Comunidade" aria-current="page">Comunidade</a></li>')
    return html.replace('href="p1-inicio.html" data-rotulo', f'href="{P031}p1-inicio.html" data-rotulo')


def gerar() -> list[str]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    bases = g.servidos()
    css = g.ler("trajetoria/portal/templates/portal/contribuicao/estilo.css") + g.CSS + CSS
    feitas = []
    for nome, (base, titulo, fazer) in TELAS.items():
        html = g.trocar_main(bases[base], fazer(), titulo, css)
        html = html.replace(g.FAIXA, FAIXA)
        pular = '<a class="pular" href="#conteudo">Pular para o conteúdo</a>'
        html = html.replace(pular, pular + "\n" + FAIXA, 1)
        html = re.sub(r"— protótipo 031</title>", "— protótipo Comunidade</title>", html)
        (PASTA / f"{nome}.html").write_text(com_navegacao(html), "utf-8")
        feitas.append(nome)
    return feitas


def medir(nomes) -> dict:
    m, moldura = g.medidor()
    m.PASTA = PASTA
    (PASTA / "_moldura.html").write_text(moldura, "utf-8")
    (PASTA / "capturas").mkdir(exist_ok=True)
    medidas = {}
    try:
        for nome in nomes:
            pagina, v = f"{nome}.html", {}
            for largura in (320, 375, 768, 1024, 1440):
                for fonte in (100, 200):
                    v[f"{largura}@{fonte}"] = m.medir(pagina, largura, fonte=fonte)
            v["375x812"] = m.medir(pagina, 375, 812)
            m.capturar(pagina, 375, v["375@100"]["altura_doc"], PASTA / "capturas" / f"{nome}-375.png")
            if nome in ("c1-historias", "c2-historia", "c4-colegas-lista"):
                m.capturar(pagina, 1440, v["1440@100"]["altura_doc"], PASTA / "capturas" / f"{nome}-1440.png")
            medidas[nome] = v
            print(nome, g.resumo(nome, v), flush=True)
    finally:
        (PASTA / "_moldura.html").unlink(missing_ok=True)
    return medidas


def main():
    feitas = gerar()
    if "--sem-capturas" in sys.argv:
        return
    medidas = medir(feitas)
    (PASTA / "medidas.json").write_text(json.dumps(
        {n: {"resumo": g.resumo(n, v), "medidas": v} for n, v in medidas.items()}, indent=1, ensure_ascii=False), "utf-8")


if __name__ == "__main__":
    main()

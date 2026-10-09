# ruff: noqa: E501 — HTML embutido em linhas longas (protótipo).
"""Protótipos das telas da 026 (Volte ao Ifes): percurso do egresso e da unidade.

Cada tela parte do HTML **realmente servido** pela demonstração (Início e Oportunidades do
Diego; curadoria com operador fictício) e troca só o conteúdo principal, com a marcação da
015 (`fieldset.pergunta`, `.opcao`, `.campo`, `.aviso`, tabela da curadoria). Textos
provisórios (DP-801). Nada aqui é importado pela aplicação; não é implementação.

Uso, na raiz do repositório, com o `.env` da demonstração:

    source .env && uv run python specs/026-volte-ao-ifes/prototipo/gerar.py
"""

import importlib.util
import os
import re
import sys
from html import escape
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
CAPTURAS = PASTA / "capturas"
VERSAO = "2026-10-09.1 (provisória)"

FORMAS = [
    ("mentoria", "Mentoria", "Acompanhar estudantes ou recém-formados da sua área."),
    ("experiencia", "Compartilhar experiência", "Conversa, palestra ou roda com estudantes."),
    ("oportunidade", "Oferecer oportunidade", "Vaga, estágio, curso ou programa da organização em que você atua."),
    ("pesquisa_extensao", "Pesquisa e extensão", "Participar de projetos com professores e estudantes."),
    ("parceria", "Parceria", "Aproximar o Ifes da organização em que você atua."),
    ("historia", "Contar sua história", "Dizer à unidade que você topa contar sua trajetória."),
]
FORMACOES = [
    ("c1", "Técnico em Química", "Vila Velha", 2012),
    ("c2", "Licenciatura em Química", "Vila Velha", 2017),
    ("c3", "Mestrado Profissional em Química", "Vila Velha", 2020),
]
CSS = """
/* 026 — protótipo. Só tokens e componentes existentes (015, camada do Portal, 025). */
.pc-ciencia, .pc-lista > li, textarea, input[type=email] { box-sizing: border-box; min-width: 0; }
.pc-resumo { margin: 0 0 1.5rem; max-width: 40rem; }
.pc-resumo dt { font-weight: 700; margin-top: .75rem; }
.pc-resumo dt:first-child { margin-top: 0; }
.pc-resumo dd { margin: 0; }
.pc-ciencia { background: var(--portal-creme, #f6f2e8); border-left: 4px solid var(--cor-marca); padding: 1rem min(1.25rem, 4vw); margin: 0 0 1.5rem; max-width: 40rem; }
.pc-ciencia h2 { margin-top: 0; font-size: var(--fonte-2); }
.pc-ciencia ul { margin: 0 0 .5rem; padding-left: 1.25rem; }
.pc-ciencia li { margin-bottom: .35rem; }
.pc-versao { font-size: var(--fonte-5); color: var(--cor-texto-suave); margin: 0; }
.pc-situacao { font-weight: 700; }
.pc-lista { list-style: none; padding: 0; margin: 0 0 1.5rem; display: grid; gap: 1rem; max-width: 44rem; }
.pc-lista > li { border: 1px solid var(--cor-borda-suave); border-radius: var(--raio); padding: 1rem min(1.25rem, 4vw); background: #fff; }
.pc-lista h2 { font-size: var(--fonte-3); margin: 0 0 .25rem; }
.pc-lista p { margin: 0 0 .25rem; }
.pc-marco { color: var(--cor-acao); }
.pc-retirada { color: var(--cor-texto-suave); }
.inicio-contribuir { margin-block: 0 2rem; }
.inicio-contribuir h2 { margin-top: 0; }
textarea { font: inherit; width: 100%; max-width: 36rem; min-height: 7rem; padding: .5rem; border: 2px solid #565c65; border-radius: 0; }
input[type=email] { font: inherit; width: 100%; max-width: 36rem; min-height: 2.75rem; padding: .5rem; border: 2px solid #565c65; border-radius: 0; }
.campo { margin-bottom: 1.5rem; }
.campo label { display: block; font-weight: 700; margin-bottom: .25rem; }
.dica { color: var(--cor-texto-suave); font-size: var(--fonte-5); margin: 0 0 .5rem; }
.pc-sub { font-weight: 400; font-size: var(--fonte-5); color: var(--cor-texto-suave); }
#conteudo .rolagem .pc-tabela th, #conteudo .rolagem .pc-tabela td { white-space: normal; vertical-align: top; }
.pc-tabela td:nth-child(3) { min-width: 16rem; }
.pc-acoes { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
"""


def e(t) -> str:
    return escape(str(t), quote=True)


def radios(nome, itens, marcado=None) -> str:
    return "".join(
        f'<div class="opcao"><input type="radio" id="{nome}-{v}" name="{nome}" value="{v}"'
        f'{" checked" if v == marcado else ""}><label for="{nome}-{v}">{rotulo}</label></div>'
        for v, rotulo in itens)


def escolha() -> str:
    formas = [(v, f"<strong>{e(t)}</strong>. {e(d)}") for v, t, d in FORMAS]
    formacoes = [(v, f"{e(c)} · {e(u)} · {a}") for v, c, u, a in FORMACOES]
    return f"""
<h1>Contribuir com o Ifes</h1>
<p>Escolha como você quer contribuir. A unidade da formação que você escolher recebe e pode entrar em contato com você.</p>
<form method="post" action="e3-confirmar.html" novalidate>
<fieldset class="pergunta"><legend>Como você quer contribuir?</legend>{radios("forma", formas, "experiencia")}</fieldset>
<fieldset class="pergunta"><legend>Por qual formação? <span class="nota">A unidade dessa formação recebe.</span></legend>{radios("formacao", formacoes, "c2")}</fieldset>
<div class="campo"><label for="mensagem">Mensagem <span class="opcional">(opcional)</span></label>
<p class="dica" id="mensagem-dica">Até 500 caracteres. Não inclua CPF, endereço ou outros dados pessoais.</p>
<textarea id="mensagem" name="mensagem" maxlength="500" aria-describedby="mensagem-dica">Trabalho com controle de qualidade em uma indústria química e posso conversar com as turmas da licenciatura sobre a carreira.</textarea></div>
<div class="pc-acoes"><button type="submit">Continuar</button></div>
</form>
<p><a href="e1-inicio.html">Voltar ao Início</a></p>"""


def resumo(com_mensagem=True) -> str:
    msg = ('<dt>Mensagem</dt><dd>Trabalho com controle de qualidade em uma indústria química e '
           'posso conversar com as turmas da licenciatura sobre a carreira.</dd>') if com_mensagem else ""
    return ('<dl class="pc-resumo"><dt>Como</dt><dd>Compartilhar experiência</dd>'
            '<dt>Formação</dt><dd>Licenciatura em Química · Vila Velha · 2017</dd>'
            f'<dt>Quem recebe</dt><dd>Unidade Vila Velha</dd>{msg}</dl>')


def ciencia() -> str:
    return f"""<section class="pc-ciencia" aria-labelledby="o-que-acontece">
<h2 id="o-que-acontece">O que acontece depois</h2>
<ul>
<li>A unidade Vila Velha recebe sua contribuição.</li>
<li>Se houver interesse, ela entra em contato pelo e-mail que você informar. Não há prazo garantido.</li>
<li>Quando a unidade registrar o contato, isso aparece em Suas contribuições.</li>
<li>Este e-mail é usado só para responder sobre esta contribuição. Ele não inclui você em convites de pesquisa.</li>
<li>Você pode retirar a contribuição quando quiser.</li>
</ul>
<p class="pc-versao">Texto de ciência, versão {e(VERSAO)}.</p>
</section>"""


def confirmar() -> str:
    return f"""
<h1>Confira e envie</h1>
{resumo()}
{ciencia()}
<form method="post" action="e4-enviada.html" novalidate>
<div class="campo"><label for="email">E-mail para a resposta</label>
<p class="dica" id="email-dica">Pode ser o mesmo que você usa em outros contatos com o Ifes.</p>
<input type="email" id="email" name="email" autocomplete="email" inputmode="email" maxlength="254" required aria-describedby="email-dica"></div>
<div class="pc-acoes"><button type="submit">Enviar contribuição</button> <a href="e2-contribuir.html">Voltar e alterar</a></div>
</form>"""


def enviada() -> str:
    return f"""
<p role="status" class="aviso aviso-sucesso">Contribuição enviada.</p>
<h1>Sua contribuição</h1>
<p class="pc-situacao">Enviada em 09/10/2026. Aguardando contato da unidade Vila Velha.</p>
{resumo()}
{ciencia()}
<ul class="lista-simples">
<li><a href="e5-contribuicoes.html">Suas contribuições</a></li>
<li><a href="e6-retirar.html">Retirar esta contribuição</a></li>
<li><a href="e1-inicio.html">Voltar ao Início</a></li>
</ul>"""


def contribuicoes() -> str:
    return """
<h1>Suas contribuições</h1>
<ul class="pc-lista">
<li><h2>Compartilhar experiência</h2>
<p>Licenciatura em Química · Unidade Vila Velha · enviada em 09/10/2026</p>
<p class="pc-situacao pc-marco">A unidade Vila Velha registrou contato em 12/10/2026.</p>
<p><a href="e4-enviada.html">Ver detalhes</a></p></li>
<li><h2>Mentoria</h2>
<p>Mestrado Profissional em Química · Unidade Vila Velha · enviada em 09/10/2026</p>
<p class="pc-situacao">Aguardando contato da unidade.</p>
<p><a href="e6-retirar.html">Retirar</a></p></li>
<li><h2>Oferecer oportunidade</h2>
<p>Técnico em Química · Unidade Vila Velha · enviada em 01/10/2026</p>
<p class="pc-situacao pc-retirada">Retirada em 05/10/2026.</p></li>
</ul>
<ul class="lista-simples">
<li><a href="e2-contribuir.html">Contribuir de novo</a></li>
<li><a href="e1-inicio.html">Voltar ao Início</a></li>
</ul>"""


def retirar() -> str:
    return """
<h1>Retirar contribuição</h1>
<h2>Mentoria</h2>
<p>Mestrado Profissional em Química · Unidade Vila Velha · enviada em 09/10/2026.</p>
<p>Depois de retirada, ela sai da lista da unidade Vila Velha. Para contribuir de novo, envie uma nova.</p>
<form method="post" action="e5-contribuicoes.html"><div class="pc-acoes"><button type="submit">Retirar</button> <a href="e5-contribuicoes.html">Cancelar</a></div></form>"""


def lista_unidade() -> str:
    linhas = [
        ("09/10/2026", "Diego Exemplo", "Licenciatura em Química · Vila Velha · 2017", "Compartilhar experiência",
         "Trabalho com controle de qualidade em uma indústria química e posso conversar com as turmas…",
         "diego@exemplo.test", "Sem contato registrado", True),
        ("09/10/2026", "Diego Exemplo", "Mestrado Profissional em Química · Vila Velha · 2020", "Mentoria",
         "—", "diego@exemplo.test", "Contato registrado em 12/10/2026", False),
    ]
    corpo = "".join(
        f"<tr><td>{d}</td><th scope=row>{e(p)}<br><span class=pc-sub>{e(em)}</span></th>"
        f"<td>{e(fm)}<br><span class=pc-sub>{e(f)}</span>"
        + (f"<br><span class=pc-sub>“{e(m)}”</span>" if m != "—" else "")
        + f"</td><td>{e(s)}</td><td>"
        + (f'<a href="u2-contato.html" aria-label="Registrar contato feito: {e(p)}, {e(fm)}">Registrar contato feito</a>' if acao else "—")
        + "</td></tr>"
        for d, p, f, fm, m, em, s, acao in linhas)
    return f"""
<h1>Contribuições recebidas</h1>
<p>Contribuições ativas das unidades da sua atuação. O contato com o egresso é feito fora do sistema, pelo e-mail informado para a contribuição.</p>
<p><a href="exemplo.csv">Exportar CSV</a></p>
<div class="rolagem" role="region" aria-label="Contribuições recebidas" tabindex="0">
<table class="pc-tabela"><caption>Contribuições recebidas no escopo da sua atuação</caption>
<thead><tr><th scope="col">Recebida em</th><th scope="col">Egresso e e-mail</th><th scope="col">Contribuição e formação</th><th scope="col">Situação</th><th scope="col">Ações</th></tr></thead>
<tbody>{corpo}</tbody></table></div>"""


def contato() -> str:
    return """
<h1>Registrar contato feito</h1>
<h2>Diego Exemplo · Compartilhar experiência</h2>
<p>Registre só depois de entrar em contato com o egresso. Ele verá em Suas contribuições: "A unidade Vila Velha registrou contato em 12/10/2026". O registro não pode ser desfeito.</p>
<form method="post" action="u1-lista.html"><button type="submit">Registrar contato feito</button> <a href="u1-lista.html">Cancelar</a></form>"""


TELAS = {
    "e2-contribuir": ("egresso", "Contribuir com o Ifes", escolha),
    "e3-confirmar": ("egresso", "Confira e envie", confirmar),
    "e4-enviada": ("egresso", "Sua contribuição", enviada),
    "e5-contribuicoes": ("egresso", "Suas contribuições", contribuicoes),
    "e6-retirar": ("egresso", "Retirar contribuição", retirar),
    "u1-lista": ("unidade", "Contribuições recebidas", lista_unidade),
    "u2-contato": ("unidade", "Registrar contato feito", contato),
}


def trocar_main(html: str, conteudo: str, titulo: str) -> str:
    inicio = html.index(">", html.index('<div class="coluna">', html.index("<main"))) + 1
    fim = html.rindex("</div>", 0, html.index("</main>"))
    html = html[:inicio] + conteudo + html[fim:]
    html = html.replace("</style>", CSS + "</style>", 1)
    return re.sub(r"<title>.*?</title>", f"<title>{e(titulo)} — Portal do Egresso</title>", html,
                  count=1, flags=re.S)


def com_navegacao(html: str, atual: bool) -> str:
    """Acrescenta "Contribuir" depois de Oportunidades (plan, R9)."""
    item = ('<li><a href="e2-contribuir.html" data-rotulo="Contribuir"'
            + (' aria-current="page"' if atual else "") + ">Contribuir</a></li>")
    html = re.sub(r'(<li><a href="/oportunidades/"[^>]*>Oportunidades</a></li>)', r"\1" + item, html, count=1)
    if atual:
        html = html.replace(' aria-current="page">Início<', '>Início<', 1)
    return html


def servidos():
    from django.test import Client

    diego = Client(HTTP_HOST="127.0.0.1")
    diego.post("/entrar/", {"cpf": "000.000.003-53", "data_nascimento": "08/02/1994"})
    inicio, base_egresso = diego.get("/inicio/"), diego.get("/oportunidades/")
    assert inicio.status_code == base_egresso.status_code == 200
    for formato in ("png", "svg"):  # a prévia do Início, como servida, para o arquivo estático
        card = diego.get(f"/minha-trajetoria/card.{formato}")
        if card.status_code == 200:
            (PASTA / f"card-diego.{formato}").write_bytes(card.content)
            break
    base_unidade = None
    for op in ("demonstracao:operador-a", "demonstracao:operador-b"):
        operador = Client(HTTP_HOST="127.0.0.1")
        operador.post("/demonstracao/operador/escolher/", {"operador": op, "destino": "curadoria"})
        r = operador.get("/curadoria/oportunidades/")
        if r.status_code == 200:
            base_unidade = r.content.decode()
            break
    assert base_unidade, "nenhum operador fictício com vínculo na demonstração"
    limpar = lambda h: re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", h)  # noqa: E731
    return limpar(inicio.content.decode()), limpar(base_egresso.content.decode()), limpar(base_unidade)


def gerar():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    inicio, base_egresso, base_unidade = servidos()
    bloco = """<section class="inicio-contribuir" aria-labelledby="inicio-contribuir">
<h2 id="inicio-contribuir">Contribuir com o Ifes</h2>
<p>Você pode se oferecer para conversar com estudantes, ser mentor, divulgar uma oportunidade da sua área ou propor uma parceria. A unidade da sua formação recebe.</p>
<p><a href="e2-contribuir.html">Quero contribuir</a> · <a href="e5-contribuicoes.html">Suas contribuições (2)</a></p>
</section>
"""
    alvo = '<section class="inicio-convite"'
    assert alvo in inicio, "convite do Início não encontrado"
    e1 = com_navegacao(inicio.replace(alvo, bloco + alvo, 1).replace("</style>", CSS + "</style>", 1), False)
    e1 = re.sub(r'src="/minha-trajetoria/card\.(png|svg)"', r'src="card-diego.\1"', e1)
    (PASTA / "e1-inicio.html").write_text(e1, "utf-8")
    for nome, (quem, titulo, fazer) in TELAS.items():
        base = base_egresso if quem == "egresso" else base_unidade
        html = trocar_main(base, fazer(), titulo)
        if quem == "egresso":
            html = com_navegacao(html.replace(' aria-current="page">Oportunidades<', '>Oportunidades<', 1),
                                 nome in ("e2-contribuir", "e3-confirmar", "e4-enviada", "e5-contribuicoes", "e6-retirar"))
        (PASTA / f"{nome}.html").write_text(html, "utf-8")
    (PASTA / "exemplo.csv").write_text(
        "recebida_em,egresso,formacao,unidade,forma,mensagem,email,situacao\n"
        "2026-10-09,Diego Exemplo,Licenciatura em Química,Vila Velha,Compartilhar experiência,"
        "\"Trabalho com controle de qualidade em uma indústria química e posso conversar com as turmas da licenciatura sobre a carreira.\","
        "diego@exemplo.test,Sem contato registrado\n"
        "2026-10-09,Diego Exemplo,Mestrado Profissional em Química,Vila Velha,Mentoria,,diego@exemplo.test,Contato registrado em 2026-10-12\n",
        "utf-8")
    capturar()


def capturar():
    spec = importlib.util.spec_from_file_location(
        "medidor", RAIZ / "docs/prototipos/2026-10-09-portal/medir.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PASTA = PASTA
    moldura = m.MOLDURA.replace(".demonstracao", ".faixa-demonstracao")
    (PASTA / "_moldura.html").write_text(moldura, "utf-8")
    CAPTURAS.mkdir(exist_ok=True)
    problemas = []
    try:
        for nome in ["e1-inicio", *TELAS]:
            larguras = (375, 1440) if nome.startswith("e") else (1280,)
            for largura in larguras:
                v = m.medir(f"{nome}.html", largura)
                m.capturar(f"{nome}.html", largura, v["altura_doc"], CAPTURAS / f"{nome}-{largura}.png")
            for largura in (320, 375, 1024, 1440):
                for fonte in (100, 200):
                    v = m.medir(f"{nome}.html", largura, fonte=fonte)
                    if v["rolagem"] > v["largura"] and not nome.startswith("u"):
                        problemas.append(f"{nome}: rolagem a {largura}@{fonte}")
                    if v["h1s"] != 1:
                        problemas.append(f"{nome}: {v['h1s']} h1")
            print(nome, "ok", flush=True)
    finally:
        (PASTA / "_moldura.html").unlink(missing_ok=True)
    (PASTA / "index.html").write_text(indice(problemas), "utf-8")
    print("problemas:", sorted(set(problemas)) or "nenhum")


def indice(problemas) -> str:
    def fig(nome, largura, titulo):
        return (f'<figure><figcaption><a href="{nome}.html">{e(titulo)}</a> · {largura} px</figcaption>'
                f'<a href="capturas/{nome}-{largura}.png"><img loading=lazy src="capturas/{nome}-{largura}.png" '
                f'alt="{e(titulo)}, {largura} px"></a></figure>')
    egresso = [("e1-inicio", "1. Início com o bloco Contribuir")] + [
        (n, f"{i}. {t}") for i, (n, (q, t, _)) in enumerate(TELAS.items(), start=2) if q == "egresso"]
    unidade = [(n, t) for n, (q, t, _) in TELAS.items() if q == "unidade"]
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>026 — protótipos do percurso</title>
<style>body{{margin:0;font-family:system-ui,sans-serif;color:#1b1b1b;line-height:1.5}}main{{max-width:90rem;margin:0 auto;padding:1rem 1.5rem 4rem}}
a{{color:#195128}}.grade{{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1.5rem;align-items:start}}
figure{{margin:0}}figure img{{width:100%;border:1px solid #c6cace}}figure>a{{display:block;max-height:40rem;overflow-y:auto}}
figcaption{{font-weight:700;margin-bottom:.25rem}}h2{{border-top:4px solid #2f9e41;padding-top:1rem;margin-top:2rem}}</style></head><body><main>
<h1>Feature 026 — Volte ao Ifes: protótipos do percurso</h1>
<p>Telas estáticas sobre o HTML servido pela demonstração (Diego, três formações; operador fictício).
Textos provisórios (DP-801). Não é implementação. Medidas: {e("; ".join(sorted(set(problemas))) or "sem rolagem horizontal de 320 a 1440 px com fonte a 100% e 200% nas telas do egresso; um h1 por tela")}.</p>
<h2>Percurso do egresso (celular, 375 px)</h2><div class=grade>{"".join(fig(n, 375, t) for n, t in egresso)}</div>
<h2>Percurso do egresso (desktop, 1440 px)</h2><div class=grade>{"".join(fig(n, 1440, t) for n, t in egresso)}</div>
<h2>Unidade (1280 px)</h2><div class=grade>{"".join(fig(n, 1280, t) for n, t in unidade)}</div>
<p><a href="exemplo.csv">CSV de exemplo</a> (só ativas; sem CPF nem data de nascimento).</p>
</main></body></html>"""


if __name__ == "__main__":
    gerar()

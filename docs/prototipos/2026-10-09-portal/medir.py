"""Captura e mede os protótipos (ADR 0009, critérios de aceitação da camada visual).

O Chrome headless não abre janela com menos de 500 px. Por isso cada tela é carregada numa
moldura (`_moldura.html`) dentro de um iframe com a largura exata: as media queries respondem
à largura do iframe. A fonte a 200% é simulada com `font-size: 200%` na raiz da página.

Uso, na raiz do repositório, depois de `gerar.py`:

    python3 docs/prototipos/2026-10-09-portal/medir.py
"""

import json
import re
import subprocess
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CAPTURAS = PASTA / "capturas"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DIRECOES = {"a": "Direção A — institucional", "b": "Direção B — trajetória",
            "c": "Combinação (A + B)"}
TELAS = {"publico": "Página pública", "inicio-ana": "Início — Ana (1 formação)",
         "inicio-diego": "Início — Diego (3 formações)"}

MOLDURA = """<!doctype html><meta charset="utf-8"><style>body{margin:0}iframe{border:0;display:block}</style>
<iframe id="f"></iframe><pre id="r"></pre><script>
const q = new URLSearchParams(location.search), f = document.getElementById('f');
f.width = q.get('largura'); f.height = q.get('altura');
f.style.marginLeft = (q.get('margem') || 0) + 'px';
f.style.marginTop = -(q.get('topo') || 0) + 'px';
f.onload = () => {
  const w = f.contentWindow, d = f.contentDocument;
  if (!d || !d.body || w.location.href === 'about:blank') return;
  if (q.get('fonte') === '200') d.documentElement.style.fontSize = '200%';
  const r = s => { const e = d.querySelector(s); return e ? e.getBoundingClientRect() : null; };
  const soma = s => [...d.querySelectorAll(s)].reduce((t, e) => t + e.getBoundingClientRect().height, 0);
  const c = d.querySelector('[data-medida=container]'), cs = c && w.getComputedStyle(c);
  const grade = d.querySelector('[data-medida=grade]');
  const colunas = grade ? new Set([...grade.children].filter(e => e.offsetHeight > 0)
    .map(e => Math.round(e.getBoundingClientRect().left))).size : null;
  const alvos = [...d.querySelectorAll('a.botao, a.ligacao, nav a')]
    .filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 44).length;
  const caracteres = Math.max(...[...d.querySelectorAll('main p')].map(p => {
    const fs = parseFloat(w.getComputedStyle(p).fontSize);
    const porLargura = Math.round(p.getBoundingClientRect().width / (fs * 0.5));
    return Math.min(porLargura, p.textContent.trim().length);
  }));
  const res = {
    largura: w.innerWidth, rolagem: d.documentElement.scrollWidth,
    altura_doc: d.documentElement.scrollHeight,
    faixa_prototipo: soma('.prototipo'), faixa_demo: soma('.demonstracao'),
    h1: r('h1') && r('h1').bottom, fato: r('[data-medida=fato]') && r('[data-medida=fato]').bottom,
    card: r('[data-medida=card]') && r('[data-medida=card]').top,
    acao: r('[data-medida=acao]') && r('[data-medida=acao]').top,
    entrar: r('[data-medida=entrar]') && r('[data-medida=entrar]').bottom,
    convite: r('.convite') && r('.convite').top,
    conteudo: c ? c.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) : null,
    colunas, h1s: d.querySelectorAll('h1').length, alvos_pequenos: alvos, caracteres_max: caracteres,
  };
  f.height = res.altura_doc;
  document.getElementById('r').textContent = 'MEDIDA' + JSON.stringify(res) + 'FIM';
};
f.src = q.get('pagina');
</script>"""


def chrome(*args) -> str:
    return subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--allow-file-access-from-files",
         "--virtual-time-budget=3000", *args],
        capture_output=True, text=True, timeout=60,
    ).stdout


def url(pagina, largura, altura=900, fonte=100, margem=0, topo=0) -> str:
    return (f"file://{PASTA}/_moldura.html?pagina={pagina}&largura={largura}"
            f"&altura={altura}&fonte={fonte}&margem={margem}&topo={topo}")


def medir(pagina, largura, altura=900, fonte=100) -> dict:
    for _ in range(3):  # o headless às vezes entrega a página antes do iframe
        saida = chrome("--window-size=1600,1000", "--dump-dom", url(pagina, largura, altura, fonte))
        achado = re.search(r'<pre id="r">MEDIDA(.*?)FIM', saida, re.S)
        if achado:
            return json.loads(achado.group(1))
    raise RuntimeError(f"sem medida: {pagina} {largura} {fonte}")


def capturar(pagina, largura, altura, destino, topo=0):
    """Abaixo de 500 px, a janela tem 500 px e o iframe fica centralizado nela; o `sips`
    recorta pelo centro, o que coincide com o iframe."""
    margem = max(0, -(-(500 - largura) // 2))
    janela = largura + 2 * margem
    chrome(f"--window-size={janela},{altura}", f"--screenshot={destino}",
           url(pagina, largura, altura, margem=margem, topo=topo))
    if margem:
        subprocess.run(["sips", "-c", str(altura), str(largura), str(destino)],
                       capture_output=True)


# --- Contraste (WCAG 2.1) dos tokens novos -------------------------------------------------

def luminancia(hexa):
    canais = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


PARES = [
    ("Ação verde no branco", "#195128", "#ffffff"),
    ("Branco no botão verde", "#ffffff", "#195128"),
    ("Ação forte no branco", "#00420c", "#ffffff"),
    ("Branco na faixa profunda", "#ffffff", "#0e3b23"),
    ("Texto secundário na faixa profunda", "#cfe6d6", "#0e3b23"),
    ("Texto no creme", "#1b1b1b", "#f6f2e8"),
    ("Texto suave no creme", "#565c65", "#f6f2e8"),
    ("Ação verde no creme", "#195128", "#f6f2e8"),
    ("Texto suave no tonal", "#565c65", "#eef7f0"),
    ("Ação verde no tonal", "#195128", "#eef7f0"),
    ("Verde profundo no botão claro", "#0e3b23", "#ffffff"),
]


# --- Critérios ----------------------------------------------------------------------------

def avaliar(tela, m):
    """Cada critério: (nome, aprovado, detalhe)."""
    r = []
    rolagens = [f"{k}" for k, v in m["rolagem"].items() if v["rolagem"] > v["largura"]]
    r.append(("Sem rolagem horizontal, 320–1440 px, fonte 100% e 200%", not rolagens,
              "excede em: " + ", ".join(rolagens) if rolagens else "nenhuma"))
    cel = m["375x812"]
    limite = 812 + cel["faixa_prototipo"]  # a faixa cinza do protótipo não existe no produto
    if tela == "publico":
        ok = cel["h1"] <= limite
        r.append(("375×812: título sem rolar", ok, f"h1 termina em {cel['h1'] - cel['faixa_prototipo']:.0f} px"))
        for chave, altura in (("1280x720", 720), ("1440x900", 900)):
            v = m[chave]
            lim = altura + v["faixa_prototipo"] + v["faixa_demo"]
            ok = v["h1"] <= lim and v["entrar"] <= lim
            r.append((f"{chave}: proposta e ação de entrar sem rolar (descontadas as faixas)", ok,
                      f"h1 {v['h1'] - lim + altura:.0f} px; entrar {v['entrar'] - lim + altura:.0f} px"))
    else:
        ok = cel["h1"] <= limite and cel["fato"] <= limite
        r.append(("375×812: título e primeiro fato sem rolar", ok,
                  f"fato termina em {cel['fato'] - cel['faixa_prototipo']:.0f} px"))
        for chave, altura in (("1280x720", 720), ("1440x900", 900)):
            v = m[chave]
            lim = altura + v["faixa_prototipo"] + v["faixa_demo"]
            terceiro = min(x for x in (v["card"], v["acao"]) if x is not None)
            ok = v["h1"] <= lim and v["fato"] <= lim and terceiro < lim
            r.append((f"{chave}: título, primeiro fato e card ou ação (descontadas as faixas)", ok,
                      f"fato {v['fato'] - lim + altura:.0f} px; card/ação começa em "
                      f"{terceiro - lim + altura:.0f} px"))
        cols = {k: m[k]["colunas"] for k in ("375x812", "1024", "1440x900")}
        ok = cols["375x812"] == 1 and cols["1024"] >= 2 and cols["1440x900"] >= 2
        r.append(("Duas colunas a partir de 1024 px; uma no celular", ok,
                  f"375: {cols['375x812']}; 1024: {cols['1024']}; 1440: {cols['1440x900']}"))
    larguras = [m[k]["conteudo"] for k in ("1280x720", "1440x900")]
    r.append(("Área de conteúdo ≥ 1000 px entre 1280 e 1440", min(larguras) >= 1000,
              f"{larguras[0]:.0f} e {larguras[1]:.0f} px"))
    r.append(("Um h1 por página", m["1440x900"]["h1s"] == 1, f"{m['1440x900']['h1s']}"))
    pequenos = max(m[k]["alvos_pequenos"] for k in ("375x812", "1440x900"))
    r.append(("Alvos de ação ≥ 44 px", pequenos == 0, f"{pequenos} abaixo de 44 px"))
    chars = m["1440x900"]["caracteres_max"]
    r.append(("Linha de texto ≤ ~75 caracteres (estimativa)", chars <= 80, f"~{chars}"))
    return r


def main():
    CAPTURAS.mkdir(exist_ok=True)
    (PASTA / "_moldura.html").write_text(MOLDURA, "utf-8")
    medidas, avaliacoes = {}, {}
    for d in DIRECOES:
        for t in TELAS:
            pagina = f"{d}-{t}.html"
            m = {"rolagem": {}}
            for largura in (320, 375, 768, 1024, 1280, 1440):
                for fonte in (100, 200):
                    v = medir(pagina, largura, fonte=fonte)
                    m["rolagem"][f"{largura}@{fonte}%"] = {"largura": v["largura"],
                                                           "rolagem": v["rolagem"]}
            m["375x812"] = medir(pagina, 375, 812)
            m["1024"] = medir(pagina, 1024, 768)
            m["1280x720"] = medir(pagina, 1280, 720)
            m["1440x900"] = medir(pagina, 1440, 900)
            medidas[pagina] = m
            avaliacoes[pagina] = avaliar(t, m)
            for largura in (375, 1024, 1440):
                altura = m["375x812"]["altura_doc"] if largura == 375 else medir(
                    pagina, largura)["altura_doc"]
                capturar(pagina, largura, altura, CAPTURAS / f"{d}-{t}-{largura}.png")
            capturar(pagina, 1280, 720, CAPTURAS / f"{d}-{t}-1280x720.png")
            capturar(pagina, 375, 812, CAPTURAS / f"{d}-{t}-375x812.png")
            print(pagina, "ok")
    passagem()
    (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False), "utf-8")
    (PASTA / "index.html").write_text(comparacao(avaliacoes), "utf-8")
    (PASTA / "_moldura.html").unlink()


def passagem():
    """Recorte do convite (combinação, Ana, 375 px) e a tela atual da pesquisa (main)."""
    import shutil

    topo = int(medir("c-inicio-ana.html", 375, 812)["convite"])
    capturar("c-inicio-ana.html", 375, 700, CAPTURAS / "passagem-portal.png",
             topo=max(0, topo - 380))
    shutil.copy(PASTA.parents[1] / "auditorias/evidencias-2026-10-08-ux-portal/"
                "08-instrumento-formacoes-ana-375.png", CAPTURAS / "passagem-instrumento.png")


def comparacao(avaliacoes) -> str:
    def celula(ok, detalhe):
        marca = "✓" if ok else "✗"
        return f'<td class="{"ok" if ok else "falha"}"><b>{marca}</b> {detalhe}</td>'

    tabelas = []
    for t, nome in TELAS.items():
        criterios = [c[0] for c in avaliacoes[f"a-{t}.html"]]
        linhas = "".join(
            f"<tr><th scope=row>{c}</th>"
            + "".join(celula(*avaliacoes[f"{d}-{t}.html"][i][1:]) for d in DIRECOES)
            + "</tr>"
            for i, c in enumerate(criterios)
        )
        figuras = "".join(
            f'<h3>{largura} px</h3><div class="linha">'
            + "".join(
                f'<figure><figcaption><a href="{d}-{t}.html">{DIRECOES[d]}</a></figcaption>'
                f'<a href="capturas/{d}-{t}-{largura}.png"><img loading="lazy" '
                f'src="capturas/{d}-{t}-{largura}.png" alt="{DIRECOES[d]}, {nome}, {largura} px">'
                "</a></figure>"
                for d in DIRECOES
            )
            + "</div>"
            for largura in ("375x812", "375", "1280x720", "1024", "1440")
        )
        tabelas.append(
            f'<section id="{t}"><h2>{nome}</h2><table><thead><tr><th>Critério (ADR 0009)</th>'
            + "".join(f"<th>{n}</th>" for n in DIRECOES.values())
            + f"</tr></thead><tbody>{linhas}</tbody></table>{figuras}</section>"
        )
    contrastes = "".join(
        f"<tr><th scope=row>{n}</th><td><span class=amostra style='color:{a};background:{b}'>"
        f"Aa</span> {a} sobre {b}</td>{celula(contraste(a, b) >= 4.5, f'{contraste(a, b):.1f}:1')}</tr>"
        for n, a, b in PARES
    )
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Protótipos do Portal — comparação</title>
<style>
body{{margin:0;font-family:system-ui,sans-serif;color:#1b1b1b;line-height:1.5}}
main{{max-width:90rem;margin:0 auto;padding:1rem 1.5rem 4rem}}
nav a{{margin-right:1rem}} a{{color:#195128}}
table{{border-collapse:collapse;width:100%;margin:1rem 0 2rem;font-size:.9375rem}}
th,td{{border:1px solid #c6cace;padding:.5rem;text-align:left;vertical-align:top}}
thead th{{background:#eef7f0}} td.ok b{{color:#195128}} td.falha{{background:#fdeeee}} td.falha b{{color:#b50909}}
.linha{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;align-items:start}}
figure{{margin:0}} figure img{{width:100%;border:1px solid #c6cace;display:block}}
figure>a{{display:block;max-height:56rem;overflow-y:auto}}
figcaption{{font-weight:600;margin-bottom:.25rem}}
.amostra{{display:inline-block;padding:0 .4rem;font-weight:700;border:1px solid #c6cace}}
section{{border-top:4px solid #2f9e41;margin-top:2rem}}
</style></head><body><main>
<h1>Protótipos do Portal do Egresso — comparação</h1>
<p>ADR 0009, decisão 10. Três direções, três telas, dados das personas fictícias. Avalie
<strong>pelo celular primeiro</strong> (decisão 2). Clique no nome da direção para abrir o
HTML e redimensionar a janela; clique na captura para vê-la inteira.</p>
<p>Medidas automáticas em Chrome headless (<code>medir.py</code>): a fonte a 200% é simulada
na raiz da página; a contagem de caracteres por linha é estimativa. A faixa cinza
"Protótipo" é descontada em todas as medidas; nas medidas de desktop, a faixa de
demonstração também é descontada, como manda a ADR.</p>
<nav><a href="#publico">Página pública</a><a href="#inicio-ana">Início — Ana</a>
<a href="#inicio-diego">Início — Diego</a><a href="#contraste">Contraste</a>
<a href="#passagem">Passagem para o instrumento</a></nav>
{"".join(tabelas)}
<section id="contraste"><h2>Contraste dos tokens novos (AA: 4,5:1)</h2>
<table><thead><tr><th>Par</th><th>Cores</th><th>Razão</th></tr></thead><tbody>{contrastes}</tbody></table></section>
<section id="passagem"><h2>Passagem do Portal para o instrumento (decisão 3)</h2>
<p>À esquerda, o convite no Início (combinação) com a ação em verde. À direita, a primeira
tela da pesquisa como está hoje na <code>main</code>, com a ação em azul (Direção B da 015,
mantida no instrumento até a D-02).</p>
<div class="linha" style="grid-template-columns:1fr 1fr">
<figure><figcaption>Início, convite (375 px)</figcaption><img src="capturas/passagem-portal.png" alt="Convite no Início com botão verde"></figure>
<figure><figcaption>Pesquisa, escolha de formações (375 px)</figcaption><img src="capturas/passagem-instrumento.png" alt="Primeira tela da pesquisa com botão azul"></figure>
</div></section>
</main></body></html>"""


if __name__ == "__main__":
    main()

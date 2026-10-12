# ruff: noqa: E501 — HTML e JavaScript embutidos em linhas longas (evidência).
"""Captura e mede as telas da 034 a partir do HTML servido (`gerar_html.py`).

Variante enxuta do arnês dos protótipos (`docs/prototipos/2026-10-12-conclusao/capturar.py`):
o Chrome headless não abre janela com menos de 500 px, então cada tela é carregada num iframe
com a largura exata. Quatro verificações, registradas separadamente:

- **375 px** e **1280 px**: captura; fim da ação principal e do conteúdo;
- **fonte a 200%** (só o texto, `font-size: 200%` na raiz) a 375 e a 1280 px (WCAG 1.4.4);
- **refluxo a 320 CSS px** (equivalente a 1280 px com zoom de 400%; WCAG 1.4.10).

Nas variantes de fonte e de refluxo, além da rolagem horizontal, confere cada elemento
esperado: visível (largura e altura maiores que zero), dentro da largura da tela e sem
conteúdo cortado (`scrollWidth` não maior que `clientWidth`). A revisão aberta é medida numa
cópia do HTML com `<details open>`.

Uso, na raiz do repositório, depois de `gerar_html.py`:

    python3 specs/034-refinamento-conclusao-confirmacao/evidencias/capturar.py
"""

import json
import re
import subprocess
from pathlib import Path

PASTA = Path(__file__).resolve().parent
HTML = PASTA / "html"
CAPTURAS = PASTA / "capturas"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Elementos esperados por tela (o que não pode sumir, ser cortado ou sair da tela).
ESPERADOS = {
    "conclusao": ["main .parte", "main h1", ".contexto-compacto", "details.revisao summary", ".decisao p", "main button.primario"],
    "conclusao-aberta": ["details.revisao summary", ".lista-revisao a", ".lista-revisao .numero", "main button.primario"],
    "conclusao-parte-salva": [".aviso", "main h1", "details.revisao summary", "main button.primario"],
    "secao-aviso-parte-nova": [".aviso", ".parte", "main h1", "main button.primario"],
    "concluida": ["main h1", ".confirmacao p", ".formacao-concluida", ".encerramento", ".continuidade h2", ".acao-principal a", ".convite-contato a"],
    "concluida-com-proxima": ["main h1", ".formacao-concluida", ".proxima-formacao button", ".continuidade a"],
    "concluida-declarada": ["main h1", ".confirmacao p", ".contexto"],
}
# (nome, largura, altura, fonte): 320 é o refluxo; "200" é a fonte a 200%.
VARIANTES = [("375", 375, 2400, "100"), ("1280", 1280, 1600, "100"), ("375-fonte200", 375, 5200, "200"),
             ("1280-fonte200", 1280, 2600, "200"), ("refluxo320", 320, 3200, "100")]

MOLDURA = """<!doctype html><meta charset="utf-8"><style>body{margin:0}iframe{border:0;display:block}</style>
<iframe id="f"></iframe><pre id="r"></pre><script>
const q = new URLSearchParams(location.search), f = document.getElementById('f');
f.width = q.get('largura'); f.height = q.get('altura');
f.onload = () => setTimeout(() => {
  const d = f.contentDocument, w = f.contentWindow;
  if (!d || !d.body) return;
  if (q.get('fonte') === '200') d.documentElement.style.fontSize = '200%';
  const largura = d.documentElement.clientWidth;
  const problemas = [];
  for (const seletor of JSON.parse(q.get('esperados'))) {
    const els = [...d.querySelectorAll(seletor)];
    if (!els.length) { problemas.push(seletor + ': ausente'); continue; }
    for (const e of els) {
      const r = e.getBoundingClientRect();
      if (!(r.width > 0 && r.height > 0)) problemas.push(seletor + ': invisível');
      else if (r.left < -0.5 || r.right > largura + 0.5) problemas.push(seletor + ': fora da tela');
      else if (e.scrollWidth > e.clientWidth + 1 && w.getComputedStyle(e).overflowX !== 'visible') problemas.push(seletor + ': cortado');
    }
  }
  const acao = ['main button.primario', '.acao-principal a', 'main a'].map(s => d.querySelector(s)).find(Boolean);
  document.getElementById('r').textContent = JSON.stringify({
    fim_da_acao: acao ? Math.round(acao.getBoundingClientRect().bottom) : null,
    fim_do_conteudo: Math.round(d.querySelector('main').getBoundingClientRect().bottom),
    rolagem_horizontal: d.documentElement.scrollWidth > largura,
    problemas,
  });
}, 300);
f.src = q.get('tela');
</script>"""


def chrome(*argumentos: str) -> str:
    comando = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--allow-file-access-from-files", "--virtual-time-budget=3000", *argumentos]
    return subprocess.run(comando, capture_output=True, text=True, check=True).stdout


def _telas() -> dict[str, Path]:
    telas = {p.stem: p for p in sorted(HTML.glob("*.html")) if not p.stem.startswith("_")}
    aberta = HTML / "_conclusao-aberta.html"
    aberta.write_text(
        telas["conclusao"].read_text("utf-8").replace('<details class="revisao">', '<details class="revisao" open>'),
        "utf-8",
    )
    telas["conclusao-aberta"] = aberta
    return telas


def main() -> None:
    CAPTURAS.mkdir(exist_ok=True)
    moldura = PASTA / "_moldura.html"
    moldura.write_text(MOLDURA)
    medidas = {}
    try:
        for nome, arquivo in _telas().items():
            for variante, largura, altura, fonte in VARIANTES:
                esperados = json.dumps(ESPERADOS[nome])
                url = (f"{moldura.as_uri()}?tela={arquivo.as_uri()}&largura={largura}&altura={altura}"
                       f"&fonte={fonte}&esperados={esperados}")
                janela = max(largura, 500)
                if variante in ("375", "1280", "375-fonte200", "refluxo320"):
                    chrome(f"--window-size={janela},{altura}", f"--screenshot={CAPTURAS / f'{nome}-{variante}.png'}", url)
                dom = chrome(f"--window-size={janela},{altura}", "--dump-dom", url)
                achado = re.search(r'<pre id="r">(.*?)</pre>', dom, re.S)
                bruto = achado.group(1).replace("&quot;", '"') if achado else ""
                medidas.setdefault(nome, {})[variante] = json.loads(bruto) if bruto else None
    finally:
        moldura.unlink(missing_ok=True)
        (HTML / "_conclusao-aberta.html").unlink(missing_ok=True)
    (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=2, ensure_ascii=False) + "\n")
    for nome, por_variante in medidas.items():
        for variante, m in por_variante.items():
            print(f"{nome:24} {variante:14} {m}")


if __name__ == "__main__":
    main()

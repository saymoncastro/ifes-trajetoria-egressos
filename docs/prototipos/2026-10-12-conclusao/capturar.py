# ruff: noqa: E501 — HTML e JavaScript embutidos em linhas longas (protótipo).
"""Captura e mede as telas do protótipo (variante enxuta de `2026-10-09-portal/medir.py`).

O Chrome headless não abre janela com menos de 500 px: cada tela é carregada num iframe com a
largura exata, numa moldura. Mede, sem a faixa "Protótipo", o fim da primeira ação
principal do conteúdo, o fim do conteúdo e se há rolagem horizontal, a 375 px, a 320 px e a
375 px com a fonte a 200% (simulada com `font-size: 200%` na raiz). A primeira tela tem 812 px.

Uso, na raiz do repositório, depois de `gerar.py`:

    python3 docs/prototipos/2026-10-12-conclusao/capturar.py
"""

import json
import re
import subprocess
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CAPTURAS = PASTA / "capturas"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TELAS = ["atual-conclusao", "proposta-conclusao", "proposta-conclusao-revisao",
         "atual-concluida", "proposta-concluida"]
# (largura, altura, fonte): 375 é a referência; 320 e a fonte a 200% verificam a quebra.
VARIANTES = [("375", 1700, "100"), ("320", 1900, "100"), ("375", 3800, "200"), ("1280", 1300, "100")]

MOLDURA = """<!doctype html><meta charset="utf-8"><style>body{margin:0}iframe{border:0;display:block}</style>
<iframe id="f"></iframe><pre id="r"></pre><script>
const q = new URLSearchParams(location.search), f = document.getElementById('f');
f.width = q.get('largura'); f.height = q.get('altura');
f.onload = () => setTimeout(() => {
  const d = f.contentDocument;
  if (!d || !d.body) return;
  if (q.get('fonte') === '200') d.documentElement.style.fontSize = '200%';
  const largura_rolagem = d.documentElement.scrollWidth;
  // A faixa "Protótipo" não existe na aplicação: as medidas a descontam.
  const faixa = d.querySelector('.prototipo').getBoundingClientRect().height;
  const acao = ['main button.primario', 'main a.botao', 'main a'].map(c => d.querySelector(c)).find(Boolean);
  const fim = e => Math.round(e.getBoundingClientRect().bottom - faixa);
  document.getElementById('r').textContent = JSON.stringify({
    fim_da_acao: acao ? fim(acao) : null,
    fim_do_conteudo: fim(d.querySelector('main')),
    rolagem_horizontal: largura_rolagem > d.documentElement.clientWidth,
  });
}, 300);
f.src = q.get('tela');
</script>"""


def chrome(*argumentos: str) -> str:
    comando = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--allow-file-access-from-files", "--virtual-time-budget=3000", *argumentos]
    return subprocess.run(comando, capture_output=True, text=True, check=True).stdout


def main() -> None:
    CAPTURAS.mkdir(exist_ok=True)
    moldura = PASTA / "_moldura.html"
    moldura.write_text(MOLDURA)
    medidas = {}
    try:
        for tela in TELAS:
            for largura, altura, fonte in VARIANTES:
                url = f"{moldura.as_uri()}?tela={(PASTA / f'{tela}.html').as_uri()}&largura={largura}&altura={altura}&fonte={fonte}"
                janela = max(int(largura), 500)
                nome = f"{tela}-{largura}" + ("-fonte200" if fonte == "200" else "")
                saida = CAPTURAS / f"{nome}.png"
                chrome(f"--window-size={janela},{altura}", f"--screenshot={saida}", url)
                if largura != "1280":
                    dom = chrome(f"--window-size={janela},{altura}", "--dump-dom", url)
                    achado = re.search(r'<pre id="r">(.*?)</pre>', dom)
                    medidas[nome] = json.loads(achado.group(1).replace("&quot;", '"')) if achado and achado.group(1) else None
                print(saida)
    finally:
        moldura.unlink(missing_ok=True)
    (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(medidas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

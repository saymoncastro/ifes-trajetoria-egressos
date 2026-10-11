# ruff: noqa: E501 — JavaScript embutido em linhas longas.
"""Medidas e capturas reais da 032 (SC-001 a SC-004, SC-007).

Pede as telas à aplicação de verdade (cliente de teste do Django, sobre o banco da
demonstração), salva o HTML numa pasta temporária, junto com as fontes servidas, e mede com o
arnês dos protótipos (`docs/prototipos/2026-10-09-portal/medir.py`) e os critérios da 029
(`prototipo/gerar.py`, `avaliar`).

Uso, na raiz do repositório, com o `.env` da demonstração:

    source .env && uv run python specs/032-convergencia-visual-c/evidencias/medir.py [publica] [inicio] [outras]
"""

import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
CAPTURAS = PASTA / "capturas"
PESSOAS = {"diego": ("000.000.003-53", "08/02/1994"), "ana": ("000.000.001-91", "12/04/1998"),
           "bruno": ("111.444.777-35", "03/09/1990")}


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _limpar(html: str, nome: str) -> str:
    """Cada pessoa com o próprio card, salvo como `card-<nome da tela>.<formato>`."""
    html = re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", html)
    html = html.replace('url("/fontes/', 'url("fontes/')
    return re.sub(r'(src|href)="/minha-trajetoria/card\.(png|svg)"', rf'\1="card-{nome}.\2"', html)


def telas(quais) -> dict[str, str]:
    from django.test import Client

    paginas = {}
    if "publica" in quais:
        paginas["publica"] = Client(HTTP_HOST="127.0.0.1").get("/").content.decode()
    for nome, (cpf, nascimento) in PESSOAS.items():
        if not {"inicio", "outras"} & quais:
            break
        c = Client(HTTP_HOST="127.0.0.1")
        assert c.post("/entrar/", {"cpf": cpf, "data_nascimento": nascimento}).status_code in (302, 303)
        paginas[f"inicio-{nome}"] = c.get("/inicio/").content.decode()
        for formato in ("png", "svg"):
            r = c.get(f"/minha-trajetoria/card.{formato}")
            if r.status_code == 200:
                paginas[f"_card-inicio-{nome}.{formato}"] = r.content
                break
        if nome == "diego":
            participacao = c.get("/participacao/")
            if participacao.status_code == 200:  # só a partir do PR 2
                paginas["participacao-diego"] = participacao.content.decode()
            if "outras" in quais:  # T007: as demais telas do Portal, com as fontes e os tokens
                for rotulo, url in (("trajetoria", "/minha-trajetoria/"),
                                    ("oportunidades", "/oportunidades/"),
                                    ("contribuir", "/contribuir/"), ("email", "/meu-email/")):
                    paginas[f"{rotulo}-diego"] = c.get(url).content.decode()
    return paginas


def main(quais):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    g = _modulo("prototipo_029", RAIZ / "specs/029-pagina-publica-portal/prototipo/gerar.py")
    temporaria = Path(tempfile.mkdtemp(prefix="032-"))
    (temporaria / "fontes").mkdir()
    for arquivo in (RAIZ / "trajetoria/portal/fontes").glob("*.woff2"):
        (temporaria / "fontes" / arquivo.name).write_bytes(arquivo.read_bytes())
    m, moldura = g.medidor()
    m.PASTA = temporaria
    moldura = moldura.replace(".pp-lead, .portal-hero .proposta", ".publico-lead, .inicio-sintese")
    moldura = moldura.replace(".pp-visual, .portal-exemplo", ".publico-linha, .inicio-linha")
    moldura = moldura.replace(".pp-acoes .portal-botao, .portal-hero .portal-botao", ".publico-acoes .portal-botao, .inicio-acoes-c a")
    moldura = moldura.replace(".pp-linha", ".publico-duas, .inicio-duas")
    (temporaria / "_moldura.html").write_text(moldura, "utf-8")
    CAPTURAS.mkdir(exist_ok=True)
    medidas = {}
    for nome, conteudo in telas(quais).items():
        if nome.startswith("_card"):
            (temporaria / nome[1:]).write_bytes(conteudo)
            continue
        (temporaria / f"{nome}.html").write_text(_limpar(conteudo, nome), "utf-8")
    for nome in sorted(p.stem for p in temporaria.glob("*.html") if not p.stem.startswith("_")):
        pagina = f"{nome}.html"
        v = {}
        for largura in (320, 375, 768, 1024, 1440):
            for fonte in (100, 200):
                v[f"{largura}@{fonte}"] = m.medir(pagina, largura, fonte=fonte)
        for chave, (largura, altura) in {"375x812": (375, 812), "1024x768": (1024, 768),
                                         "1280x720": (1280, 720), "1440x900": (1440, 900)}.items():
            v[chave] = m.medir(pagina, largura, altura)
            m.capturar(pagina, largura, altura, CAPTURAS / f"{nome}-{chave}.png")
        for largura in (375, 1024, 1440):
            m.capturar(pagina, largura, v[f"{largura}@100"]["altura_doc"], CAPTURAS / f"{nome}-{largura}.png")
        medidas[nome] = v
        rolagem = [k for k, r in v.items() if "@" in k and r["rolagem"] > r["largura"]]
        pequenos = sorted({k for k, r in v.items() if r["alvos_pequenos"]})
        print(nome, "| rolagem:", rolagem or "nenhuma", "| h1:", v["1440x900"]["h1s"],
              "| alvos <44:", pequenos or "nenhum",
              "| 375x812 h1/frase/chamada:", [round(v["375x812"][k] or 0) for k in ("h1", "fato", "entrar")],
              "| 1280x720:", [round(v["1280x720"][k] or 0) for k in ("h1", "fato", "entrar", "card")],
              "faixa", round(v["1280x720"]["faixa_demo"]), flush=True)
    anterior = json.loads((PASTA / "medidas.json").read_text("utf-8")) if (PASTA / "medidas.json").exists() else {}
    (PASTA / "medidas.json").write_text(json.dumps({**anterior, **medidas}, indent=1, ensure_ascii=False), "utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or {"publica", "inicio", "outras"})

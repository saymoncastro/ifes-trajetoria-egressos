# ruff: noqa: E501 — JavaScript embutido em linhas longas.
"""Medidas e capturas reais da 031, incremento 1 (T035; FR-036; SC-009).

Pede as telas à aplicação de verdade (cliente de teste do Django, sobre o banco da
demonstração preparado), salva o HTML numa pasta temporária com as fontes servidas e mede com
o arnês do protótipo da 031 (que usa o dos protótipos da ADR 0009). Não é validação com
egressos.

Uso, na raiz do repositório, com o `.env` da demonstração e o banco preparado:

    source .env && uv run python specs/031-encontros-propostos-egressos/evidencias/medir.py
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
PESSOAS = {"diego": ("000.000.003-53", "08/02/1994"), "maria": ("000.000.002-72", "25/11/1997")}
MODERACAO = {"analise", "moderacao"}


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _limpar(html: str) -> str:
    html = re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", html)
    return html.replace('url("/fontes/', 'url("fontes/')


def telas() -> dict[str, str]:
    from django.test import Client

    from trajetoria.portal.encontros.demonstracao import identificador as idf

    e = {k: f"/encontros/{idf(k)}/" for k in ("E1", "E2", "E3", "E4", "E5")}
    clientes = {}
    for nome, (cpf, nascimento) in PESSOAS.items():
        cliente = Client(HTTP_HOST="127.0.0.1")
        cliente.post("/entrar/", {"cpf": cpf, "data_nascimento": nascimento})
        clientes[nome] = cliente
    diego, maria = clientes["diego"], clientes["maria"]
    operador = Client(HTTP_HOST="127.0.0.1")
    operador.post("/demonstracao/operador/escolher/",
                  {"operador": "demonstracao:operador-a", "destino": "encontros"})
    paginas = {
        "lista": diego.get("/encontros/"),
        "confirmado": diego.get(e["E1"]),
        "vou-participar": diego.get(e["E2"]),
        "cancelar-participacao": diego.get(f"{e['E1']}cancelar-participacao/"),
        "encerrado": diego.get(e["E5"]),
        "sem-sessao": Client(HTTP_HOST="127.0.0.1").get(e["E1"]),
        "propor": maria.get("/encontros/propor/"),
        "propor-erros": maria.post("/encontros/propor/", {"titulo": "", "publico": "formacoes"}),
        "organizador": maria.get(e["E1"]),
        "recusado": maria.get(e["E4"]),
        "seus": maria.get("/encontros/seus/"),
        "moderacao": operador.get("/curadoria/encontros/"),
        "analise": operador.get(f"/curadoria/encontros/{idf('E3')}/"),
    }
    for nome, resposta in paginas.items():
        assert resposta.status_code in (200, 422), (nome, resposta.status_code)
    return {nome: _limpar(r.content.decode()) for nome, r in paginas.items()}


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    g = _modulo("prototipo_031", RAIZ / "specs/031-encontros-propostos-egressos/prototipo/gerar.py")
    temporaria = Path(tempfile.mkdtemp(prefix="031-"))
    (temporaria / "fontes").mkdir()
    for arquivo in (RAIZ / "trajetoria/portal/fontes").glob("*.woff2"):
        (temporaria / "fontes" / arquivo.name).write_bytes(arquivo.read_bytes())
    m, moldura = g.medidor()
    m.PASTA = temporaria
    (temporaria / "_moldura.html").write_text(moldura, "utf-8")
    CAPTURAS.mkdir(exist_ok=True)
    resultado = {}
    for nome, html in telas().items():
        (temporaria / f"{nome}.html").write_text(html, "utf-8")
        pagina = f"{nome}.html"
        v = {}
        larguras = (320, 375, 1024, 1280) if nome in MODERACAO else (320, 375, 768, 1024, 1440)
        for largura in larguras:
            for fonte in (100, 200):
                v[f"{largura}@{fonte}"] = m.medir(pagina, largura, fonte=fonte)
        v["375x812"] = m.medir(pagina, 375, 812)
        if nome in MODERACAO:
            m.capturar(pagina, 1280, v["1280@100"]["altura_doc"], CAPTURAS / f"{nome}-1280.png")
        else:
            m.capturar(pagina, 375, v["375@100"]["altura_doc"], CAPTURAS / f"{nome}-375.png")
            if nome in ("lista", "confirmado", "organizador", "propor"):
                m.capturar(pagina, 1440, v["1440@100"]["altura_doc"], CAPTURAS / f"{nome}-1440.png")
        resumo = g.resumo("p3-encontro" if nome in ("confirmado", "vou-participar", "organizador") else nome, v)
        resultado[nome] = {"resumo": resumo, "medidas": v}
        print(nome, resumo, flush=True)
    (PASTA / "medidas.json").write_text(json.dumps(resultado, indent=1, ensure_ascii=False), "utf-8")


if __name__ == "__main__":
    main()

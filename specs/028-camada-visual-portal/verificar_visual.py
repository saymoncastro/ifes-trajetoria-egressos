"""Mede HTML servido pela demonstração da 028, com Chrome local e sem dependência nova.

Uso: uv run python specs/028-camada-visual-portal/verificar_visual.py
Requer o servidor em 127.0.0.1:8028 e o cenário fictício do guia de ambiente local.
Os snapshots são temporários; medidas e capturas ficam em evidencias/.
"""

import argparse
import importlib.util
import json
import re
import tempfile
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, build_opener

RAIZ = Path(__file__).resolve().parents[2]
PASTA = Path(__file__).with_name("evidencias")
BASE = "http://127.0.0.1:8028"


def navegador():
    return build_opener(HTTPCookieProcessor(CookieJar()))


def ler(opener, url, dados=None):
    return opener.open(BASE + url, dados, timeout=30).read().decode()


def entrar(opener, cpf, nascimento):
    html = ler(opener, "/entrar/")
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)[1]
    ler(opener, "/entrar/", urlencode({"csrfmiddlewaretoken": token, "cpf": cpf,
                                       "data_nascimento": nascimento}).encode())


def executar(tela=None):
    spec = importlib.util.spec_from_file_location(
        "medidor", RAIZ / "docs/prototipos/2026-10-09-portal/medir.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    PASTA.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="trajetoria-028-") as diretorio:
        m.PASTA = Path(diretorio)
        moldura = m.MOLDURA.replace(".demonstracao", ".faixa-demonstracao")
        moldura = moldura.replace("d.querySelector('[data-medida=container]')",
            "(d.querySelector('.portal-container') || d.querySelector('main > .coluna'))")
        moldura = moldura.replace("[data-medida=grade]", ".inicio-acoes-grade")
        moldura = moldura.replace("[data-medida=fato]", ".inicio-formacoes li:first-child p")
        moldura = moldura.replace("[data-medida=card]", ".inicio-card img")
        moldura = moldura.replace("[data-medida=acao]", ".inicio-acoes li a")
        moldura = moldura.replace("[data-medida=entrar]", ".portal-hero a")
        moldura = moldura.replace(".convite", ".inicio-convite")
        moldura = moldura.replace("a.botao, a.ligacao, nav a",
            "main a, button, summary, nav a, .narrativa-nome-card label")
        moldura = moldura.replace("e.getBoundingClientRect().height < 44",
                                   "(e.getBoundingClientRect().height < 44 || "
                                   "e.getBoundingClientRect().width < 44)")
        moldura = moldura.replace("colunas, h1s:",
            "oportunidade_altura: r('.inicio-oportunidades')?.height ?? null, colunas, h1s:")
        (m.PASTA / "_moldura.html").write_text(moldura)
        ana, diego = navegador(), navegador()
        telas = {"publico": (ana, "/"), "entrar": (ana, "/entrar/")}
        htmls = {chave: ler(o, url) for chave, (o, url) in telas.items()}
        entrar(ana, "00000000191", "12/04/1998")
        entrar(diego, "00000000353", "08/02/1994")
        telas = {"inicio-ana": (ana, "/inicio/"), "inicio-diego": (diego, "/inicio/"),
                 "trajetoria": (ana, "/minha-trajetoria/"), "email": (ana, "/meu-email/"),
                 "oportunidades": (ana, "/oportunidades/"), "instrumento": (ana, "/formacoes/")}
        htmls.update({chave: ler(o, url) for chave, (o, url) in telas.items()})
        if tela:
            htmls = {tela: htmls[tela]}
        # Mesmas imagens retornadas pelo endpoint, copiadas apenas para o snapshot local.
        for chave, html in htmls.items():
            if chave in telas:
                o = telas[chave][0]
                for endereco in set(re.findall(r'src="(/minha-trajetoria/card\.[^"?]+)"', html)):
                    arquivo = chave + "-card." + endereco.rsplit(".", 1)[1]
                    (m.PASTA / arquivo).write_bytes(o.open(BASE + endereco).read())
                    html = html.replace('src="' + endereco + '"', 'src="' + arquivo + '"')
            # Só a moldura usa script de medição; a página é verificada sem scripts próprios.
            html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
            (m.PASTA / (chave + ".html")).write_text(html)
        medidas = json.loads((PASTA / "medidas.json").read_text()) if tela else {}
        for chave in htmls:
            print("Medindo", chave, flush=True)
            medidas[chave] = {}
            for largura in (320, 375, 768, 1024, 1280, 1440):
                for fonte in (100, 200):
                    medidas[chave][f"{largura}-{fonte}"] = m.medir(chave + ".html", largura,
                                                                    fonte=fonte)
            medidas[chave]["375x812"] = m.medir(chave + ".html", 375, 812)
            medidas[chave]["1280x720"] = m.medir(chave + ".html", 1280, 720)
            medidas[chave]["1440x900"] = m.medir(chave + ".html", 1440, 900)
            for largura in (375, 1024, 1440):
                altura = medidas[chave][f"{largura}-100"]["altura_doc"]
                m.capturar(chave + ".html", largura, altura,
                           PASTA / f"{chave}-{largura}.png")
            if chave in ("publico", "inicio-ana", "inicio-diego"):
                for largura, altura in ((375, 812), (1280, 720), (1440, 900)):
                    # Descontar a faixa: desloca a moldura, não aumenta a área de produto.
                    topo = medidas[chave][f"{largura}x{altura}"]["faixa_demo"]
                    m.capturar(chave + ".html", largura, altura,
                               PASTA / f"{chave}-{largura}x{altura}.png", topo=topo)
        (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=2, ensure_ascii=False))
        contrastes = [{"par": titulo, "razao": round(m.contraste(a, b), 2)}
                      for titulo, a, b in m.PARES]
        # Fundo efetivo dos destaques do Início.
        contrastes.append({"par": "Branco no destaque do Início",
                           "razao": round(m.contraste("#ffffff", "#214a35"), 2)})
        (PASTA / "contraste.json").write_text(json.dumps(contrastes, indent=2, ensure_ascii=False))
        falhas = []
        for tela, matriz in medidas.items():
            for caso, v in matriz.items():
                # Instrumento é referência preservada, não alvo da harmonização.
                alvo_novo = tela != "instrumento" and v["alvos_pequenos"]
                if v["rolagem"] > v["largura"] or alvo_novo or v["h1s"] != 1:
                    falhas.append((tela, caso, "largura, alvo ou h1", v))
            if tela.startswith("inicio"):
                v = matriz["375x812"]
                if max(v["h1"], v["fato"]) > 812:
                    falhas.append((tela, "375x812", "primeiro fato"))
                for caso, altura in (("1280x720", 720), ("1440x900", 900)):
                    v = matriz[caso]
                    ultimo = max(v["h1"], v["fato"], min(v["card"], v["acao"]))
                    if ultimo > altura + v["faixa_demo"]:
                        falhas.append((tela, caso, "primeira tela"))
                    if v["conteudo"] < 1000 or v["colunas"] < 2:
                        falhas.append((tela, caso, "container/colunas"))
                if matriz["375-100"]["oportunidade_altura"] > 270:
                    falhas.append((tela, "375", "orçamento de Oportunidades"))
            if tela == "publico":
                v = matriz["1280x720"]
                if v["entrar"] > 720 + v["faixa_demo"]:
                    falhas.append((tela, "1280x720", "entrar"))
        print(json.dumps(falhas, ensure_ascii=False, indent=2))
        print("Contrastes:", contrastes)
        if falhas:
            raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tela", choices=("publico", "entrar", "inicio-ana", "inicio-diego",
                                         "trajetoria", "email", "oportunidades", "instrumento"))
    executar(parser.parse_args().tela)

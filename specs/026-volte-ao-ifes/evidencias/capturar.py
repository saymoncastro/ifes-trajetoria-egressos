# ruff: noqa: E501 — JavaScript embutido em linhas longas.
"""Capturas e medidas do percurso real da 026 (tasks T018 e T022; plan, critérios de entrega).

Cada tela é pedida à aplicação de verdade (cliente de teste do Django, sobre o banco da
demonstração já preparado), salva como HTML estático numa pasta temporária e medida com o
mesmo arnês dos protótipos (`docs/prototipos/2026-10-09-portal/medir.py`). Tudo roda numa
transação desfeita no fim: a manifestação enviada, o contato e a retirada usados nas telas não
ficam no banco.

Uso, na raiz do repositório, com o `.env` da demonstração:

    source .env && uv run python specs/026-volte-ao-ifes/evidencias/capturar.py
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
DIEGO = {"cpf": "000.000.003-53", "data_nascimento": "08/02/1994"}

MEDIDAS_EXTRAS = """conteudo,
    contribuir: r('.inicio-contribuir') && r('.inicio-contribuir').height,
    nav_linhas: new Set([...d.querySelectorAll('nav.navegacao li')].map(e => Math.round(e.getBoundingClientRect().top))).size,
    alvos_lista: [...d.querySelectorAll('main a, main button, nav a')].filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 44).map(e => e.textContent.trim().slice(0, 40)),
"""


class Desfazer(Exception):
    pass


def telas() -> dict[str, str]:
    from django.db import transaction
    from django.test import Client
    from django.utils import timezone

    from trajetoria.portal.contribuicao import operacoes
    from trajetoria.portal.contribuicao.demonstracao import identificador
    from trajetoria.portal.models import Manifestacao

    paginas = {}
    try:
        with transaction.atomic():
            diego = Client(HTTP_HOST="127.0.0.1")
            assert diego.post("/entrar/", DIEGO).status_code in (302, 303)
            paginas["e1-inicio"] = diego.get("/inicio/")
            paginas["e2-contribuir"] = diego.get("/contribuir/")
            pessoa_id = Manifestacao.objects.get(pk=identificador("M1")).pessoa_id
            from trajetoria.academico.models import ConclusaoAcademica, Pessoa

            pessoa = Pessoa.objects.get(pk=pessoa_id)
            mestrado = ConclusaoAcademica.objects.get(pessoa=pessoa, curso__startswith="Mestrado")
            escolha = {"forma": "mentoria", "formacao": str(mestrado.pk),
                       "mensagem": "Posso acompanhar estudantes do mestrado em projetos aplicados."}
            paginas["e2b-erros"] = diego.post("/contribuir/", {"mensagem": "a" * 501})
            paginas["e3-confirmar"] = diego.post("/contribuir/", escolha)
            paginas["e3b-email-invalido"] = diego.post(
                "/contribuir/confirmar/", {**escolha, "email": "diego@", "versao": "2026-10-09.1"})
            enviada = diego.post("/contribuir/confirmar/", {
                **escolha, "email": "sim-p-0004.contribuicao@example.invalid",
                "versao": "2026-10-09.1"})
            assert enviada.status_code == 303, enviada.status_code
            paginas["e4-enviada"] = diego.get(enviada["Location"])
            operacoes.registrar_contato(identificador("M1"), operador="demonstracao:operador-a",
                                        escopo=_institucional(), agora=timezone.now())
            nova = Manifestacao.objects.get(pk=enviada["Location"].split("/")[2])
            paginas["e6-retirar"] = diego.get(f"/contribuicoes/{nova.pk}/retirar/")
            paginas["e5-contribuicoes"] = diego.get("/contribuicoes/")
            operador = Client(HTTP_HOST="127.0.0.1")
            operador.post("/demonstracao/operador/escolher/",
                          {"operador": "demonstracao:operador-a", "destino": "contribuicoes"})
            paginas["u1-lista"] = operador.get("/curadoria/contribuicoes/")
            paginas["u2-contato"] = operador.get(f"/curadoria/contribuicoes/{nova.pk}/contato/")
            paginas["u3-csv"] = operador.get("/curadoria/contribuicoes/exportar.csv")
            for nome, resposta in paginas.items():
                assert resposta.status_code in (200, 422), (nome, resposta.status_code)
            paginas = {n: r.content for n, r in paginas.items()}
            card = diego.get("/minha-trajetoria/card.png")
            if card.status_code != 200:
                card = diego.get("/minha-trajetoria/card.svg")
            paginas["_card"] = (card["Content-Type"], card.content)
            raise Desfazer
    except Desfazer:
        pass
    return paginas


def _institucional():
    from trajetoria.governanca.regras import EscopoDeAcompanhamento

    return EscopoDeAcompanhamento(institucional=True, unidades=frozenset())


def medir_e_capturar(paginas):
    spec = importlib.util.spec_from_file_location(
        "medidor", RAIZ / "docs/prototipos/2026-10-09-portal/medir.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    temporaria = Path(tempfile.mkdtemp(prefix="026-telas-"))
    m.PASTA = temporaria
    moldura = m.MOLDURA.replace(".demonstracao", ".faixa-demonstracao")
    assert "conteudo,\n" in moldura
    (temporaria / "_moldura.html").write_text(moldura.replace("conteudo,\n", MEDIDAS_EXTRAS, 1), "utf-8")
    tipo, card = paginas.pop("_card")
    extensao = "png" if "png" in tipo else "svg"
    (temporaria / f"card.{extensao}").write_bytes(card)
    (PASTA / "exemplo-real.csv").write_bytes(paginas.pop("u3-csv"))
    CAPTURAS.mkdir(exist_ok=True)
    medidas, problemas = {}, []
    for nome, conteudo in paginas.items():
        html = conteudo.decode()
        html = re.sub(r'(csrfmiddlewaretoken" value=")[^"]*', r"\1", html)
        html = re.sub(r'src="/minha-trajetoria/card\.(png|svg)"', f'src="card.{extensao}"', html)
        (temporaria / f"{nome}.html").write_text(html, "utf-8")
        larguras = (1280,) if nome.startswith("u") else (375, 1440)
        for largura in larguras:
            v = m.medir(f"{nome}.html", largura)
            m.capturar(f"{nome}.html", largura, v["altura_doc"], CAPTURAS / f"{nome}-{largura}.png")
        medidas[nome] = {}
        for largura in (320, 375, 768, 1024, 1440):
            for fonte in (100, 200):
                v = m.medir(f"{nome}.html", largura, fonte=fonte)
                medidas[nome][f"{largura}@{fonte}"] = {
                    k: v[k] for k in ("rolagem", "largura", "h1s", "contribuir", "nav_linhas",
                                      "alvos_lista")}
                if v["rolagem"] > v["largura"] and not nome.startswith("u"):
                    problemas.append(f"{nome}: rolagem a {largura}@{fonte}")
                if v["h1s"] != 1:
                    problemas.append(f"{nome}: {v['h1s']} h1")
        print(nome, "ok", flush=True)
    (PASTA / "medidas.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False), "utf-8")
    inicio = medidas["e1-inicio"]["375@100"]
    print("bloco Contribuir a 375 px:", inicio["contribuir"], "px (orçamento: 200)")
    for chave in ("375@100", "320@200", "375@200"):
        print(f"navegação em {chave}:", medidas["e2-contribuir"][chave]["nav_linhas"], "linha(s)")
    print("problemas:", sorted(set(problemas)) or "nenhum")


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    medir_e_capturar(telas())

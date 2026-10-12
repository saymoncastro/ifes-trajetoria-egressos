# ruff: noqa: E402 — o Django precisa ser configurado antes dos imports do projeto.
"""Guarda o HTML **servido** das telas da 034, para captura e medida (`capturar.py`).

Usa o cliente de teste do Django contra um banco de demonstração próprio e recém-preparado,
com as personas fictícias. As telas carregam o CSS inline, então o HTML guardado renderiza
igual ao servido. Nada aqui é importado pela aplicação.

Uso, na raiz do repositório, com um `.env` cujo PGDATABASE seja um banco descartável:

    source .env && uv run python manage.py migrate && \
        uv run python manage.py preparar_demonstracao && \
        uv run python specs/034-refinamento-conclusao-confirmacao/evidencias/gerar_html.py
"""

import os
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.test import Client
from django.utils import timezone

from tests.declaracao import construcao as cd
from tests.interface import construcao_interface as ci
from tests.participacao.construcao_entrada import pessoa_da_fonte
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.participacao.models import Participacao

HTML = PASTA / "html"
ANA, DIEGO = "SIM-P-0001", "SIM-P-0004"


def _guardar(nome: str, resposta) -> None:
    assert resposta.status_code == 200, (nome, resposta.status_code)
    (HTML / f"{nome}.html").write_text(resposta.content.decode(), "utf-8")
    print(HTML / f"{nome}.html")


def _escolhas(versao) -> dict:
    """Percurso "trabalha e estuda" de uma graduação: "Graduação" onde houver; nas demais
    escolhas, a primeira Opção ("Sim" nas que decidem o caminho)."""
    return {
        p.id: "Graduação"
        for s in conteudo_da_versao(versao).secoes
        for p in s.perguntas
        if any(o.texto == "Graduação" for o in p.opcoes)
    }


def _cliente() -> Client:
    return Client(HTTP_HOST="127.0.0.1")


def main() -> None:
    assert settings.TRAJETORIA_DEMONSTRACAO, "exige TRAJETORIA_DEMONSTRACAO=1"
    HTML.mkdir(exist_ok=True)

    # Ana: conclusão, volta de uma revisão, parte nova com o aviso B6 e confirmação.
    cliente = _cliente()
    pk = ci.participacao_de(ci.iniciar(cliente, pessoa_da_fonte(ANA)))
    versao = Participacao.objects.get(pk=pk).campanha.versao
    _, url = ci.percorrer_pela_interface(cliente, pk, versao, _escolhas(versao))
    assert url.endswith("/concluir/"), url
    base = f"/participacoes/{pk}/"
    _guardar("conclusao", cliente.get(base + "concluir/"))
    _guardar("conclusao-parte-salva", cliente.get(base + "concluir/?aviso=revisada&secao=2"))
    avaliacao = ci.secao_do_conteudo(versao, 8)
    trabalha = next(p for p in avaliacao.perguntas if p.texto == "Atualmente você trabalha?")
    dados = ci.dados_validos(avaliacao, {**_escolhas(versao), trabalha.id: "Não"})
    destino = cliente.post(base + "secoes/8/", {**dados, "revisao": "1"})["Location"]
    _guardar("secao-aviso-parte-nova", cliente.get(destino))
    dez = ci.secao_do_conteudo(versao, 10)
    cliente.post(base + "secoes/10/", {**ci.dados_validos(dez), "revisao": "1"})
    _guardar("concluida", cliente.get(cliente.post(base + "concluir/")["Location"]))

    # Diego: confirmação com outra formação pendente (Termos "Não" encurta o percurso).
    cliente = _cliente()
    diego = pessoa_da_fonte(DIEGO)
    primeira = diego.conclusoes.order_by("ano_conclusao", "id").first()
    pk = ci.participacao_de(ci.iniciar(cliente, diego, primeira))
    cliente.post(f"/participacoes/{pk}/secoes/1/", {"p1": "2"})
    destino = cliente.post(f"/participacoes/{pk}/concluir/")["Location"]
    _guardar("concluida-com-proxima", cliente.get(destino))

    # Declarante: confirmação da declarada, que não muda (FR-007).
    campanha = Participacao.objects.get(pk=pk).campanha
    formacao = cd.declaracao_concluida(campanha)
    cliente = _cliente()
    agora = timezone.now().isoformat()
    sessao = cliente.session
    sessao.update({
        "declaracao.formacoes": [str(formacao.pk)],
        "declaracao.confirmada_em": agora,
        "declaracao.ultimo_uso": agora,
    })  # fmt: skip
    sessao.save()
    cliente.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key
    participacao = Participacao.objects.get(formacao_declarada=formacao)
    _guardar("concluida-declarada", cliente.get(f"/participacoes/{participacao.pk}/concluida/"))


if __name__ == "__main__":
    main()

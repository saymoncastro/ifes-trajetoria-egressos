"""Auxiliares dos testes do editor (Feature 009; não são testes).

Versões de teste são montadas pelas operações da 002, em RASCUNHO, a partir das mesmas
descrições em memória da 006 (`secao_mem`, `pergunta_mem`). Somente dados fictícios.
"""

import re
from html.parser import HTMLParser

from django.apps import apps

from tests.participacao.construcao import FIM, SecaoMem, _textos_das_opcoes
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento import regras as regras_002
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta, Secao, TipoPergunta, Versao

PADROES_TECNICOS = (
    re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I),
    re.compile(r"\bFR-\d{3}\b"),
    re.compile(r"Traceback|OperacaoRejeitada|ParticipacaoRejeitada"),
    re.compile(
        r"\b(" + "|".join(m.name for m in regras_002.Motivo) + r"|ESTRUTURA_NAO_SUPORTADA)\b"
    ),
)


def retrato(versao) -> tuple:
    """Linha da Versão e conteúdo completo (com identidades), para comparar antes e depois."""
    return Versao.objects.filter(pk=versao.pk).values().get(), conteudo_da_versao(versao)


def contagens() -> dict[str, int]:
    return {m.__name__: m.objects.count() for m in apps.get_models()}


class _Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes: list[str] = []
        self._ignorar = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._ignorar += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._ignorar -= 1

    def handle_data(self, data):
        if not self._ignorar:
            self.partes.append(data)


def texto_visivel(resposta) -> str:
    """O texto renderizado, sem tags nem atributos."""
    parser = _Texto()
    parser.feed(resposta.content.decode())
    return re.sub(r"\s+", " ", " ".join(parser.partes))


def padroes_tecnicos(resposta) -> list[str]:
    texto = texto_visivel(resposta)
    return [m.group(0) for p in PADROES_TECNICOS for m in p.finditer(texto)]


def versao_de(pesquisa, *secoes: SecaoMem, designacao="Montada") -> Versao:
    """A descrição de `versao_mem` (006), montada em RASCUNHO pelas operações da 002."""
    versao = op.criar_versao(pesquisa, designacao)
    criadas = [op.adicionar_secao(versao, i, titulo=s.titulo) for i, s in enumerate(secoes, 1)]
    for secao, s in zip(criadas, secoes, strict=True):
        if s.encaminhamento:
            op.definir_encaminhamento(secao, criadas[s.encaminhamento - 1])
        for j, p in enumerate(s.perguntas, 1):
            escala = Escala(inicio=1, fim=5) if p.tipo == TipoPergunta.ESCALA else None
            pergunta = op.adicionar_pergunta(
                secao, j, p.tipo, f"Pergunta {j}", obrigatoria=p.obrigatoria, escala=escala
            )
            for k, texto in enumerate(_textos_das_opcoes(p), 1):
                opcao = op.adicionar_opcao(
                    pergunta, k, texto, complemento_textual=texto == "Outro:"
                )
                if texto in p.regras:
                    alvo = p.regras[texto]
                    op.definir_regra(
                        pergunta, opcao, op.FINALIZAR if alvo == FIM else criadas[alvo - 1]
                    )
    return versao


def secao(versao, n: int) -> Secao:
    """A n-ésima Seção na ordem (ordinal, 1-based)."""
    return list(versao.secoes.order_by("posicao"))[n - 1]


def pergunta(versao, s: int, p: int) -> Pergunta:
    return list(secao(versao, s).perguntas.order_by("posicao"))[p - 1]


def opcao(pergunta_, texto: str) -> Opcao:
    return pergunta_.opcoes.get(texto=texto)


def ordem(conjunto) -> list[str]:
    """Textos ou títulos na ordem atual."""
    return [
        getattr(e, "texto", None) or getattr(e, "titulo", None)
        for e in conjunto.order_by("posicao")
    ]


def posicoes(conjunto) -> list[int]:
    return list(conjunto.order_by("posicao").values_list("posicao", flat=True))

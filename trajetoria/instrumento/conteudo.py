"""Leitura do conteúdo de uma Versão (contracts/conteudo.md).

Árvore imutável, sem objetos do ORM, na ordem das posições. Duas leituras da mesma
Versão sem alteração entre elas são iguais (`==`). Não há atributo de momento de
aplicação da regra (FR-053).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db.models import Prefetch

from trajetoria.instrumento.models import (
    EstadoVersao,
    Opcao,
    Pergunta,
    Secao,
    TipoPergunta,
    Versao,
)


@dataclass(frozen=True)
class Escala:
    inicio: int
    fim: int
    rotulo_inicio: str | None = None
    rotulo_fim: str | None = None


@dataclass(frozen=True)
class RegraNavegacao:
    destino_secao_id: UUID | None  # None ⇔ finaliza
    finaliza: bool


@dataclass(frozen=True)
class ConteudoOpcao:
    id: UUID
    posicao: int
    texto: str
    complemento_textual: bool
    regra: RegraNavegacao | None


@dataclass(frozen=True)
class ConteudoPergunta:
    id: UUID
    posicao: int
    tipo: TipoPergunta
    texto: str
    texto_explicativo: str | None
    obrigatoria: bool
    escala: Escala | None
    opcoes: tuple[ConteudoOpcao, ...]


@dataclass(frozen=True)
class ConteudoSecao:
    id: UUID
    posicao: int
    titulo: str | None
    texto: str | None
    encaminhamento_id: UUID | None
    perguntas: tuple[ConteudoPergunta, ...]


@dataclass(frozen=True)
class ConteudoVersao:
    id: UUID
    pesquisa_id: UUID
    designacao: str
    estado: EstadoVersao
    publicada_em: datetime | None
    origem_id: UUID | None
    titulo: str | None
    texto_abertura: str | None
    texto_encerramento: str | None
    secoes: tuple[ConteudoSecao, ...]


def conteudo_da_versao(versao: Versao) -> ConteudoVersao:
    versao = Versao.objects.get(pk=versao.pk)
    secoes = Secao.objects.filter(versao=versao).order_by("posicao").prefetch_related(
        Prefetch(
            "perguntas",
            queryset=Pergunta.objects.order_by("posicao").prefetch_related(
                Prefetch("opcoes", queryset=Opcao.objects.order_by("posicao"))
            ),
        )
    )
    return ConteudoVersao(
        id=versao.id,
        pesquisa_id=versao.pesquisa_id,
        designacao=versao.designacao,
        estado=EstadoVersao(versao.estado),
        publicada_em=versao.publicada_em,
        origem_id=versao.origem_id,
        titulo=versao.titulo,
        texto_abertura=versao.texto_abertura,
        texto_encerramento=versao.texto_encerramento,
        secoes=tuple(_secao(s) for s in secoes),
    )


def _secao(secao: Secao) -> ConteudoSecao:
    return ConteudoSecao(
        id=secao.id,
        posicao=secao.posicao,
        titulo=secao.titulo,
        texto=secao.texto,
        encaminhamento_id=secao.encaminhamento_id,
        perguntas=tuple(_pergunta(p) for p in secao.perguntas.all()),
    )


def _pergunta(pergunta: Pergunta) -> ConteudoPergunta:
    escala = None
    if pergunta.tipo == TipoPergunta.ESCALA:
        escala = Escala(
            pergunta.escala_inicio,
            pergunta.escala_fim,
            pergunta.escala_rotulo_inicio,
            pergunta.escala_rotulo_fim,
        )
    return ConteudoPergunta(
        id=pergunta.id,
        posicao=pergunta.posicao,
        tipo=TipoPergunta(pergunta.tipo),
        texto=pergunta.texto,
        texto_explicativo=pergunta.texto_explicativo,
        obrigatoria=pergunta.obrigatoria,
        escala=escala,
        opcoes=tuple(_opcao(o) for o in pergunta.opcoes.all()),
    )


def _opcao(opcao: Opcao) -> ConteudoOpcao:
    regra = (
        RegraNavegacao(opcao.regra_destino_id, opcao.regra_finaliza)
        if opcao.tem_regra
        else None
    )
    return ConteudoOpcao(
        id=opcao.id,
        posicao=opcao.posicao,
        texto=opcao.texto,
        complemento_textual=opcao.complemento_textual,
        regra=regra,
    )

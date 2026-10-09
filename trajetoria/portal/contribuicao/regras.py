"""Regras puras da Manifestação (026; plan, "Modelo de dados"; R3 a R6).

Sem banco e sem relógio. Vocabulário de rejeição no padrão de `oportunidades/regras.py`.
"""

from dataclasses import dataclass
from enum import Enum

from trajetoria.contato.endereco import EnderecoInvalido, normalizar_email
from trajetoria.portal.models import MENSAGEM_MAXIMA, Forma


class Situacao(Enum):
    """Situação observável, derivada (FR-013; D-2601). A retirada prevalece."""

    ENVIADA = "enviada"
    CONTATO_REGISTRADO = "contato_registrado"
    RETIRADA = "retirada"


class Motivo(Enum):
    FORMA = "forma"  # FR-002
    FORMACAO = "formacao"  # FR-013a: não é Conclusão da Pessoa
    MENSAGEM = "mensagem"  # FR-003
    EMAIL = "email"  # FR-004
    CIENCIA = "ciencia"  # FR-007: a versão confirmada não é a vigente
    DUPLICADA = "duplicada"  # FR-006
    ESTADO = "estado"  # retirada ou contato já registrado (conflito)
    FORA_DO_ESCOPO = "fora_do_escopo"  # de outra Pessoa ou fora do escopo do operador


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None


class ManifestacaoRejeitada(Exception):
    """Operação rejeitada; nada foi gravado."""

    def __init__(self, violacoes):
        violacoes = tuple(violacoes)
        if not violacoes:
            raise ValueError("ManifestacaoRejeitada exige ao menos uma violação")
        self.violacoes = violacoes
        super().__init__("; ".join(f"{v.motivo.name} ({v.campo or '—'})" for v in violacoes))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)


def situacao(manifestacao) -> Situacao:
    if manifestacao.retirada_em is not None:
        return Situacao.RETIRADA
    if manifestacao.contato_registrado_em is not None:
        return Situacao.CONTATO_REGISTRADO
    return Situacao.ENVIADA


def normalizar_mensagem(texto) -> str:
    """Quebras de linha do navegador (CRLF) contam como uma, como no `maxlength`."""
    if not isinstance(texto, str):
        return ""
    return texto.replace("\r\n", "\n").replace("\r", "\n").strip()


def violacoes_da_escolha(forma, mensagem: str) -> list[Violacao]:
    """Forma da lista fechada e mensagem dentro do limite. A formação é verificada contra as
    Conclusões da Pessoa por quem as conhece (formulário e operação)."""
    violacoes = []
    if forma not in Forma.values:
        violacoes.append(Violacao(Motivo.FORMA, "forma"))
    if len(mensagem) > MENSAGEM_MAXIMA:
        violacoes.append(Violacao(Motivo.MENSAGEM, "mensagem"))
    return violacoes


def email_da_contribuicao(valor) -> str:
    """Normaliza como a 020 (R3), sem gravar contato. Levanta `ManifestacaoRejeitada`."""
    try:
        return normalizar_email(valor)
    except EnderecoInvalido:
        raise ManifestacaoRejeitada([Violacao(Motivo.EMAIL, "email")]) from None

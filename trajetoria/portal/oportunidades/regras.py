"""Regras puras da Oportunidade (025; data-model.md; research R5, R6).

Sem banco e sem relógio: quem chama passa `hoje`. Vocabulário de rejeição no padrão de
`trajetoria/campanha/regras.py`.
"""

import ipaddress
from dataclasses import dataclass
from datetime import date
from enum import Enum
from urllib.parse import urlsplit

ENDERECO_MAXIMO = 500
_DOMINIO_DO_IFES = "ifes.edu.br"


class Estado(Enum):
    """Estados observáveis, derivados (FR-009; spec, "Estados de publicação")."""

    RASCUNHO = "Rascunho"
    AGENDADA = "Agendada"
    EM_DIVULGACAO = "Em divulgação"
    ENCERRADA = "Encerrada"
    RETIRADA = "Retirada"


EDITAVEIS = frozenset({Estado.RASCUNHO, Estado.AGENDADA, Estado.EM_DIVULGACAO})
RETIRAVEIS = EDITAVEIS


class Motivo(Enum):
    TITULO = "titulo"  # FR-002
    RESUMO = "resumo"  # FR-002
    CATEGORIA = "categoria"  # FR-003
    UNIDADE_FORA_DO_ESCOPO = "unidade_fora_do_escopo"  # FR-026
    ENDERECO = "endereco"  # FR-004; R6
    PERIODO_INVERTIDO = "periodo_invertido"  # FR-006
    FIM_ANTES_DE_HOJE = "fim_antes_de_hoje"  # FR-029, FR-030
    PUBLICO = "publico"  # FR-007
    ESTADO = "estado"  # FR-034 (conflito)
    FORA_DO_ESCOPO = "fora_do_escopo"  # FR-026 (registro de outra unidade)


@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None
    detalhe: str


class OportunidadeRejeitada(Exception):
    """Operação rejeitada; nada foi gravado."""

    def __init__(self, violacoes):
        violacoes = tuple(violacoes)
        if not violacoes:
            raise ValueError("OportunidadeRejeitada exige ao menos uma violação")
        self.violacoes = violacoes
        super().__init__(str(self))

    @property
    def motivos(self) -> tuple[Motivo, ...]:
        return tuple(v.motivo for v in self.violacoes)

    def __str__(self) -> str:
        return "; ".join(
            f"{v.motivo.name} ({v.campo or '—'}): {v.detalhe}" for v in self.violacoes
        )


def estado(oportunidade, hoje: date) -> Estado:
    """A data nunca autoriza sozinha; a retirada prevalece; início e fim são inclusivos."""
    if oportunidade.retirada_em is not None:
        return Estado.RETIRADA
    if oportunidade.publicada_em is None:
        return Estado.RASCUNHO
    if hoje < oportunidade.inicio:
        return Estado.AGENDADA
    if hoje > oportunidade.fim:
        return Estado.ENCERRADA
    return Estado.EM_DIVULGACAO


def _nome_de_maquina(texto: str) -> str | None:
    try:
        partes = urlsplit(texto)
        nome = partes.hostname
        partes.port  # noqa: B018 — porta inválida levanta ValueError
    except ValueError:
        return None
    if partes.scheme != "https" or not nome:
        return None
    if partes.username is not None or partes.password is not None or "@" in partes.netloc:
        return None
    try:
        ipaddress.ip_address(nome)
        return None
    except ValueError:
        pass
    if "." not in nome:
        return None
    return nome.lower()


def endereco_invalido(texto: str) -> str | None:
    """Motivo da recusa do endereço oficial, ou `None` se aceito (FR-004; research R6).

    Recusa: esquema diferente de https; sem nome de máquina; usuário ou senha; número IP;
    espaço ou caractere de controle; mais de 500 caracteres. Nada é acessado na rede."""
    if not texto:
        return "vazio"
    if len(texto) > ENDERECO_MAXIMO:
        return "longo"
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in texto):
        return "espaco"
    if _nome_de_maquina(texto) is None:
        return "forma"
    return None


def origem_do_site(endereco: str) -> tuple[bool, str]:
    """(é do Ifes, domínio) só para exibição (research R6). `ifes.edu.br` e subdomínios são
    do Ifes; o resto é externo. Supõe endereço já validado."""
    nome = _nome_de_maquina(endereco) or ""
    do_ifes = nome == _DOMINIO_DO_IFES or nome.endswith("." + _DOMINIO_DO_IFES)
    return do_ifes, nome

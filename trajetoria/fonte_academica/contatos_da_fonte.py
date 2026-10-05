"""Capacidade de contatos da fonte (Feature 020; contracts/fonte-de-contatos.md).

Fronteira **separada** da `FonteAcademica` (contrato.py, inalterado), no precedente da 021
FR-071: identificação (018), incorporação (001), declaração e validação (019), narrativa
(021) e vídeo (022) nunca dependem dela. Informa, para Pessoas já incorporadas, zero ou mais
e-mails na ordem de preferência que o adaptador declara. Peculiaridades da fonte real
ficam no adaptador, escrito só depois do Gate A (DP-1601). Sem telefone (E1).

Python puro: não importa Django nem fonte concreta.
"""

from typing import Protocol


class ContatosIndisponiveis(Exception):
    """A fonte não pôde responder. Nunca equivale a "sem e-mail"."""


class FonteDeContatos(Protocol):
    codigo: str

    def obter_emails(self, id_externo_pessoa: str) -> tuple[str, ...]:
        """Zero ou mais e-mails, em ordem de preferência; pode levantar
        `ContatosIndisponiveis`."""
        ...

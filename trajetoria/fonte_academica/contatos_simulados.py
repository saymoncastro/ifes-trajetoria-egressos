"""Adaptador simulado de contatos (Feature 020; contracts/fonte-de-contatos.md).

Somente endereços fictícios no domínio reservado `example.invalid`. Não afirma que a fonte
acadêmica real oferece e-mail (Gate A). O acervo histórico (019) não tem adaptador de
contatos.
"""

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contatos_da_fonte import ContatosIndisponiveis


class ContatosSimulados:
    codigo = "simulada"

    def __init__(self, emails=None, indisponivel: bool = False) -> None:
        self._emails = cenarios.EMAILS if emails is None else emails
        self._indisponivel = indisponivel

    def obter_emails(self, id_externo_pessoa: str) -> tuple[str, ...]:
        if self._indisponivel:
            raise ContatosIndisponiveis("fonte de contatos simulada configurada como indisponível")
        return tuple(self._emails.get(id_externo_pessoa, ()))

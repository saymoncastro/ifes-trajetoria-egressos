"""Normalização única de e-mail (Feature 020, research R4).

A mesma função serve à carga da fonte, à página do egresso e à política de escolha. A
restrição a `example.invalid` não está aqui: é barreira do modo de demonstração do
transporte (`comunicacao/seguranca.py`).
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

TAMANHO_MAXIMO = 254
_PROIBIDOS = "\r\n<>,; \t"


class EnderecoInvalido(ValueError):
    """Nunca carrega o valor recebido: a mensagem é fixa (Observabilidade)."""

    def __init__(self):
        super().__init__("endereco_invalido")


def normalizar_email(valor) -> str:
    if not isinstance(valor, str) or "\r" in valor or "\n" in valor:
        raise EnderecoInvalido  # quebra de linha nunca é só "espaço externo"
    valor = valor.strip(" ")
    if not valor or len(valor) > TAMANHO_MAXIMO or any(c in valor for c in _PROIBIDOS):
        raise EnderecoInvalido
    try:
        validate_email(valor)
    except ValidationError:
        raise EnderecoInvalido from None
    local, dominio = valor.rsplit("@", 1)
    return f"{local}@{dominio.lower()}"


def email_valido(valor) -> bool:
    try:
        normalizar_email(valor)
    except EnderecoInvalido:
        return False
    return True

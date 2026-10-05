"""Informe voluntário de e-mail pelo egresso (Feature 020, FR-009 a FR-014).

Acrescenta um registro `EGRESSO`; nunca altera nem apaga outro (FR-002). Informe igual ao
último `EGRESSO` não grava. Sem confirmação por link ou código (DP-2004). Não toca
Participação, Resposta, Versão ou acesso.
"""

from django.utils import timezone

from trajetoria.contato.endereco import normalizar_email
from trajetoria.contato.models import Canal, ContatoDaPessoa, Origem


def informar_email(pessoa, valor, *, agora=None) -> bool:
    """`True` se gravou; `False` se igual ao último informe. `EnderecoInvalido` se inválido."""
    normalizado = normalizar_email(valor)
    ultimo = (
        ContatoDaPessoa.objects.filter(pessoa=pessoa, origem=Origem.EGRESSO)
        .order_by("-obtido_em", "-pk")
        .values_list("valor", flat=True)
        .first()
    )
    if ultimo == normalizado:
        return False
    ContatoDaPessoa.objects.create(
        pessoa=pessoa,
        canal=Canal.EMAIL,
        valor=normalizado,
        origem=Origem.EGRESSO,
        obtido_em=agora or timezone.now(),
    )
    return True

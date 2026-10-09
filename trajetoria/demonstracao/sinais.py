"""Sinais neutros da demonstração (025 research R4).

`cenario_preparado` é enviado no fim de `cenario.preparar()`, dentro da transação, com a
`data` local do preparo. O emissor não conhece os receptores: outro módulo pode carregar
dados fictícios próprios sem que o cenário o importe.

O receptor que tiver uma operação recusada levanta `CargaRecusada`: o preparo desfaz a
transação e responde com a mensagem orientada, como para as recusas do próprio cenário.
"""

from django.dispatch import Signal

cenario_preparado = Signal()


class CargaRecusada(Exception):
    """Um receptor de `cenario_preparado` teve uma operação recusada."""

"""Portal do Egresso em demonstração (Feature 024; ADR 0008; Constituição 2.1.0).

Camada de relacionamento sobre o núcleo: entrada, identificação pelo Portal, Início e
navegação; Oportunidades (025) e contribuição do egresso (026). Depende do núcleo, nunca o
contrário: seus fatos (`models.py`) não têm chave estrangeira para ele. Desligável por
`TRAJETORIA_PORTAL=0`.
"""

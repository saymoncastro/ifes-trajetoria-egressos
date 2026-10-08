"""Portal do Egresso em demonstração (Feature 024; ADR 0008; Constituição 2.1.0).

Camada de relacionamento sobre o núcleo: entrada, identificação pelo Portal, Início e
navegação. Depende do núcleo, nunca o contrário, e não grava nada (sem `models.py`).
Desligável por `TRAJETORIA_PORTAL=0`.
"""

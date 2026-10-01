"""Baseline do Formulário Egresso Ifes 2024 (specs/003-migracao-semantica-instrumento).

Pacote Python, não app Django: sem modelos, migrações nem comandos.
"""

from trajetoria.formulario_2024.materializacao import (
    BaselineDivergente,
    MaterializacaoRecusada,
    PesquisaAmbigua,
    Resultado,
    forma_da_versao,
    forma_esperada,
    materializar,
)

__all__ = [
    "BaselineDivergente",
    "MaterializacaoRecusada",
    "PesquisaAmbigua",
    "Resultado",
    "forma_da_versao",
    "forma_esperada",
    "materializar",
]

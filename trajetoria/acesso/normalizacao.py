"""Forma canônica dos dados de acesso; nenhuma persistência."""

import re
from datetime import datetime


def cpf_utilizavel(cpf11):
    if not isinstance(cpf11, str) or not re.fullmatch(r"[0-9]{11}", cpf11) or len(set(cpf11)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(
            int(c) * peso
            for c, peso in zip(cpf11[:tamanho], range(tamanho + 1, 1, -1), strict=True)
        )
        dv = (soma * 10 % 11) % 10
        if dv != int(cpf11[tamanho]):
            return False
    return True


def normalizar_cpf(texto):
    if not isinstance(texto, str):
        return None
    cpf = re.sub(r"[.\- ]", "", texto)
    return cpf if cpf_utilizavel(cpf) else None


def normalizar_data(texto, hoje):
    if not isinstance(texto, str) or not re.fullmatch(
        r"(?:[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{8})", texto
    ):
        return None
    try:
        data = datetime.strptime(texto.replace("/", ""), "%d%m%Y").date()
    except ValueError:
        return None
    return data if 1900 <= data.year and data <= hoje else None

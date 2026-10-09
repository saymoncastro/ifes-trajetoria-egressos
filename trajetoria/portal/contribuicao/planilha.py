"""CSV da unidade (026 FR-010; plan R8). Fica na camada: a exportação analítica não conhece
a Manifestação (FR-016).

Só as manifestações ativas do escopo, com o e-mail da contribuição, sem CPF nem data de
nascimento. Toda célula que começa como fórmula de planilha (`=`, `+`, `-`, `@`, tabulação ou
retorno) recebe um apóstrofo na frente: o texto continua legível e não é executado.
"""

import csv
import io

from django.utils import timezone

from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao.regras import Situacao, situacao
from trajetoria.portal.models import Forma

_INICIO_DE_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def neutralizar(valor) -> str:
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto.startswith(_INICIO_DE_FORMULA) else texto


def _dia(momento) -> str:
    return timezone.localdate(momento).isoformat()


def _situacao(manifestacao) -> str:
    if situacao(manifestacao) is Situacao.CONTATO_REGISTRADO:
        return m.CONTATO_EM.format(data=_dia(manifestacao.contato_registrado_em))
    return m.SEM_CONTATO


def linhas(descritas) -> list[list[str]]:
    """Cabeçalho e uma linha por manifestação descrita (`consultas.descrever`, com o nome)."""
    resultado = [list(m.CSV_CABECALHO)]
    for d in descritas:
        manifestacao = d.manifestacao
        resultado.append([neutralizar(v) for v in (
            _dia(manifestacao.registrada_em),
            d.nome or m.SEM_NOME,
            d.conclusao.curso if d.conclusao else m.FORMACAO_NAO_ENCONTRADA,
            manifestacao.unidade,
            Forma(manifestacao.forma).label,
            manifestacao.mensagem,
            manifestacao.email,
            _situacao(manifestacao),
        )])
    return resultado


def csv_da_unidade(descritas) -> bytes:
    """UTF-8 com BOM, para abrir com acentos nas planilhas mais comuns."""
    saida = io.StringIO()
    csv.writer(saida, lineterminator="\r\n").writerows(linhas(descritas))
    return ("﻿" + saida.getvalue()).encode("utf-8")

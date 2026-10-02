"""Leitura do dataset lógico por nome de coluna (auxiliar dos testes da 013)."""

from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.pseudonimos import pseudonimo


def linhas(snapshot) -> list[dict]:
    dados = dataset_exportado(snapshot).dados
    return [dict(zip(dados.cabecalho, linha, strict=True)) for linha in dados.linhas]


def por_conclusao(snapshot, chave) -> dict:
    """`{conclusao_analitica_id: linha}`; use `id_de(conclusao, chave)` para localizar."""
    return {linha["conclusao_analitica_id"]: linha for linha in linhas(snapshot)}


def id_de(conclusao, chave) -> str:
    return pseudonimo("conclusao", conclusao.pk, chave)


def linha_de(snapshot, conclusao, chave) -> dict:
    return por_conclusao(snapshot, chave)[id_de(conclusao, chave)]


def metadados(snapshot) -> dict:
    return {chave: valor for chave, valor, _ in dataset_exportado(snapshot).metadados.linhas}

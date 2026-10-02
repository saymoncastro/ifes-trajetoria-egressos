"""Serialização do dataset lógico em CSV e XLSX (contracts/pacote-de-dados.md).

Os formatos **só serializam** `dataset_exportado(snapshot)`: nenhum valor é decidido aqui, e
por isso CSV e XLSX têm a mesma semântica (spec FR-070). Duas funções explícitas por formato,
sem classe base, registro de serializadores nem parâmetro de formato (spec FR-132):

- `exportar_csv(snapshot)` / `exportar_xlsx(snapshot)`: montam o dataset e serializam;
- `csv_do_dataset(dataset)` / `xlsx_do_dataset(dataset)`: serializam um dataset já montado,
  para quem precisa dos dois formatos do mesmo snapshot sem ler e montar tudo de novo. O
  dataset só nasce de `dataset_exportado(snapshot)`: o snapshot continua explícito.

Tudo em memória: nenhum arquivo em disco, nem temporário (spec FR-114).
"""

import csv
import io
import re
import zipfile
from datetime import UTC, date, datetime

import xlsxwriter

from trajetoria.analitico.models import SnapshotAnalitico
from trajetoria.exportacao.contrato import GATILHOS_DE_ESCAPE
from trajetoria.exportacao.dataset import DatasetExportado, dataset_exportado
from trajetoria.exportacao.regras import ValorNaoRepresentavel

__all__ = ["csv_do_dataset", "exportar_csv", "exportar_xlsx", "xlsx_do_dataset"]

_ARQUIVOS_CSV = ("dados.csv", "dicionario.csv", "metadados.csv")
_DATA_FIXA_NO_ZIP = (1980, 1, 1, 0, 0, 0)  # entradas sem o momento da exportação
_ABAS_XLSX = ("Dados", "Dicionário", "Metadados")
_TABELAS = ("dados", "dicionario", "metadados")

# Texto que o XLSX não grava sem alteração (research R12): além do limite de célula, com
# caractere proibido no XML 1.0, ou com o padrão `_xHHHH_`, que leitores OOXML decodificam.
_LIMITE_DA_CELULA = 32767
_NAO_REPRESENTAVEL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]|_x[0-9A-Fa-f]{4}_")


def exportar_csv(snapshot: SnapshotAnalitico) -> bytes:
    """O pacote CSV do snapshot recebido (`csv_do_dataset`)."""
    return csv_do_dataset(dataset_exportado(snapshot))


def exportar_xlsx(snapshot: SnapshotAnalitico) -> bytes:
    """A pasta de trabalho XLSX do snapshot recebido (`xlsx_do_dataset`)."""
    return xlsx_do_dataset(dataset_exportado(snapshot))


def csv_do_dataset(dataset: DatasetExportado) -> bytes:
    """O pacote ZIP com `dados.csv`, `dicionario.csv` e `metadados.csv`: UTF-8 sem BOM,
    vírgula, RFC 4180 (CRLF), cabeçalho com os nomes técnicos. O mesmo dataset gera bytes
    idênticos."""
    _exigir_dataset(dataset)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as pacote:
        for nome, tabela in zip(
            _ARQUIVOS_CSV, (dataset.dados, dataset.dicionario, dataset.metadados), strict=True
        ):
            entrada = zipfile.ZipInfo(nome, date_time=_DATA_FIXA_NO_ZIP)
            entrada.compress_type = zipfile.ZIP_DEFLATED
            entrada.external_attr = 0o644 << 16
            with (
                pacote.open(entrada, "w") as destino,
                io.TextIOWrapper(destino, encoding="utf-8", newline="") as texto,
            ):
                escritor = csv.writer(
                    texto,
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\r\n",
                )
                escritor.writerow(tabela.cabecalho)
                escritor.writerows(
                    [_campo_csv(valor) for valor in linha] for linha in tabela.linhas
                )
    return buffer.getvalue()


def _exigir_dataset(dataset) -> None:
    if not isinstance(dataset, DatasetExportado):
        raise TypeError(f"dataset deve ser DatasetExportado, não {type(dataset).__name__}")


def _campo_csv(valor) -> str:
    """Representação de um valor lógico no CSV (research R3). `bool` antes de `int`, porque
    `bool` é subclasse de `int`."""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    # Escape contra fórmula, parte do contrato (spec FR-075): reversível removendo um
    # apóstrofo inicial de qualquer campo; o próprio apóstrofo também é gatilho.
    return "'" + valor if valor.startswith(GATILHOS_DE_ESCAPE) else valor


def xlsx_do_dataset(dataset: DatasetExportado) -> bytes:
    """A pasta de trabalho com as abas Dados, Dicionário e Metadados. Escrita tipada e
    explícita: texto é sempre `write_string` — nunca fórmula, sem escape — e as conversões
    implícitas do XlsxWriter ficam desligadas (research R11). Nenhum gráfico, filtro, fórmula
    ou formatação além do cabeçalho em negrito (spec FR-079)."""
    _exigir_dataset(dataset)
    buffer = io.BytesIO()
    pasta = xlsxwriter.Workbook(
        buffer,
        {
            "in_memory": True,  # nenhum arquivo temporário em disco (spec FR-114)
            "strings_to_formulas": False,
            "strings_to_numbers": False,
            "strings_to_urls": False,
        },
    )
    # Propriedade do arquivo: o momento da captura, nunca o da exportação (spec FR-064).
    pasta.set_properties({"created": dataset.capturado_em.astimezone(UTC).replace(tzinfo=None)})
    cabecalho = pasta.add_format({"bold": True})
    data = pasta.add_format({"num_format": "yyyy-mm-dd"})
    tabelas = (dataset.dados, dataset.dicionario, dataset.metadados)
    for nome, tabela_nome, tabela in zip(_ABAS_XLSX, _TABELAS, tabelas, strict=True):
        aba = pasta.add_worksheet(nome)
        for coluna, titulo in enumerate(tabela.cabecalho):
            aba.write_string(0, coluna, titulo, cabecalho)
        for linha, valores in enumerate(tabela.linhas, start=1):
            for coluna, valor in enumerate(valores):
                if not _escrever_celula(aba, linha, coluna, valor, data):
                    raise ValorNaoRepresentavel(
                        formato="xlsx",
                        tabela=tabela_nome,
                        coluna=tabela.cabecalho[coluna],
                        linha=linha,
                    )
    pasta.close()
    return buffer.getvalue()


def _escrever_celula(aba, linha: int, coluna: int, valor, data) -> bool:
    """Uma chamada tipada por valor; `None` não escreve nada (célula vazia). Falso quando o
    texto não pode ser gravado sem alteração: nunca trunca nem substitui (spec FR-091)."""
    if valor is None:
        return True
    if isinstance(valor, bool):
        return aba.write_boolean(linha, coluna, valor) == 0
    if isinstance(valor, int):
        return aba.write_number(linha, coluna, valor) == 0
    if isinstance(valor, datetime):
        return aba.write_string(linha, coluna, valor.isoformat()) == 0
    if isinstance(valor, date):
        return aba.write_datetime(linha, coluna, valor, data) == 0
    if len(valor) > _LIMITE_DA_CELULA or _NAO_REPRESENTAVEL.search(valor):
        return False
    return aba.write_string(linha, coluna, valor) == 0

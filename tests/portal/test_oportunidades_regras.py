"""Regras puras da Oportunidade (025 FR-004, FR-009; research R5, R6; T013)."""

from datetime import date, datetime
from types import SimpleNamespace

import pytest

from trajetoria.portal.oportunidades.regras import (
    Estado,
    endereco_invalido,
    estado,
    origem_do_site,
)

D = date(2026, 10, 8)
PUBLICADA = datetime(2026, 10, 1, 9, 0)
RETIRADA = datetime(2026, 10, 5, 9, 0)


def _o(*, inicio=D, fim=D, publicada=None, retirada=None):
    return SimpleNamespace(inicio=inicio, fim=fim, publicada_em=publicada, retirada_em=retirada)


def test_rascunho_com_periodo_em_curso_continua_rascunho():
    """A data nunca autoriza sozinha (spec, "Estados de publicação", regra 1)."""
    assert estado(_o(inicio=date(2026, 10, 1), fim=date(2026, 10, 30)), D) is Estado.RASCUNHO


@pytest.mark.parametrize(
    "hoje, esperado",
    [
        (date(2026, 10, 7), Estado.AGENDADA),
        (D, Estado.EM_DIVULGACAO),  # início inclusivo
        (date(2026, 10, 20), Estado.EM_DIVULGACAO),  # fim inclusivo
        (date(2026, 10, 21), Estado.ENCERRADA),
    ],
)
def test_publicada_pelas_datas(hoje, esperado):
    assert estado(_o(inicio=D, fim=date(2026, 10, 20), publicada=PUBLICADA), hoje) is esperado


def test_retirada_prevalece_sobre_tudo():
    em_curso = _o(inicio=date(2026, 10, 1), fim=date(2026, 10, 30), publicada=PUBLICADA,
                  retirada=RETIRADA)
    assert estado(em_curso, D) is Estado.RETIRADA
    rascunho_descartado = _o(retirada=RETIRADA)
    assert estado(rascunho_descartado, D) is Estado.RETIRADA


@pytest.mark.parametrize(
    "endereco",
    [
        "https://www.ifes.edu.br/x",
        "https://oportunidades.example/a?b=1",
        "https://cursos.ifes.edu.br/especializacao#inscricao",
        "https://1password.example/",  # rótulo numérico só no início não é IP
        "https://www.123.com.br/",
    ],
)
def test_endereco_aceito(endereco):
    assert endereco_invalido(endereco) is None


@pytest.mark.parametrize(
    "endereco",
    [
        "",
        "http://www.ifes.edu.br/",
        "https://user:pw@host.example/",
        "https://user@host.example/",
        "https://10.0.0.1/",
        "https://[::1]/",
        "https://host.example/com espaco",
        "https://host.example/\ttab",
        "https://host.example/" + "a" * 481,
        "javascript:alert(1)",
        "https:///sem-maquina",
        "https://localhost/",
        "ftp://host.example/",
        "//host.example/",
        # IPv4 abreviado, octal ou hexadecimal: o navegador os lê como IP (code review #49).
        "https://127.1/",
        "https://10.1/",
        "https://0177.0.0.1/",
        "https://0x0a.0.0.1/",
        "https://192.168.0.1./",
        "https://2130706433/",
    ],
)
def test_endereco_recusado(endereco):
    assert endereco_invalido(endereco) is not None


def test_limite_de_500_caracteres():
    base = "https://host.example/"
    assert endereco_invalido(base + "a" * (500 - len(base))) is None
    assert endereco_invalido(base + "a" * (501 - len(base))) is not None


@pytest.mark.parametrize(
    "endereco, esperado",
    [
        ("https://ifes.edu.br/", (True, "ifes.edu.br")),
        ("https://CURSOS.Ifes.edu.br/a", (True, "cursos.ifes.edu.br")),
        ("https://ifes.edu.br.evil.example/", (False, "ifes.edu.br.evil.example")),
        ("https://falsoifes.edu.br/", (False, "falsoifes.edu.br")),
        ("https://www.gov.br/x", (False, "www.gov.br")),
    ],
)
def test_origem_do_site(endereco, esperado):
    assert origem_do_site(endereco) == esperado

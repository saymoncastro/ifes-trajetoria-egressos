from datetime import timedelta
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from django.utils import timezone

from tests.declaracao.construcao import CPF, DADOS, DATA
from trajetoria.declaracao import selo


def _caminho_de_declaracao_indisponivel():
    # A 018 sela só com a chave A (`acesso.transito`); a 019 valida A e B antes de consumir
    # qualquer selo (FR-117). Com qualquer chave inadequada, o caminho falha antes de gravar.
    with pytest.raises(selo.ChaveIndisponivel):
        selo.abrir_transito(selo.selar_transito(CPF, DATA), timezone.now())


@pytest.mark.parametrize(
    "campo", ["TRAJETORIA_CHAVE_SELO_DECLARACAO", "TRAJETORIA_CHAVE_CONSULTA_ACERVO"]
)
@pytest.mark.parametrize("valor", ["", "invalida", None])
def test_chaves_invalidas(settings, campo, valor):
    setattr(settings, campo, valor)
    _caminho_de_declaracao_indisponivel()


@pytest.mark.parametrize("valor", ["", "invalida", None])
def test_chave_do_selo_invalida_impede_a_018_de_selar(settings, valor):
    settings.TRAJETORIA_CHAVE_SELO_DECLARACAO = valor
    with pytest.raises(selo.ChaveIndisponivel):
        selo.selar_transito(CPF, DATA)


@pytest.mark.parametrize(
    "outra",
    [
        "TRAJETORIA_CHAVE_CONSULTA_ACERVO",
        "SECRET_KEY",
        "TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO",
        "TRAJETORIA_CHAVE_ACESSO_VERIFICACAO",
        "TRAJETORIA_CHAVE_PSEUDONIMIZACAO",
    ],
)
def test_chave_reutilizada(settings, outra):
    setattr(settings, outra, settings.TRAJETORIA_CHAVE_SELO_DECLARACAO)
    _caminho_de_declaracao_indisponivel()


def test_finalidade_validade_adulteracao(settings, caplog):
    agora = timezone.now()
    transito = selo.selar_transito(CPF, DATA)
    assert selo.abrir_transito(transito, agora) == (CPF, DATA)
    inicio = selo.selar_inicio(CPF, DATA, DADOS)
    cpf, data, dados, chave = selo.abrir_inicio(inicio, agora)
    assert (cpf, data, dados) == (CPF, DATA, DADOS)
    assert chave
    for token in [
        inicio,
        transito[:-3] + "abc",
        Fernet(settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO).encrypt(b"{}").decode(),
    ]:
        with pytest.raises(selo.SeloInvalido):
            selo.abrir_transito(token, agora)
    with pytest.raises(selo.SeloInvalido):
        selo.abrir_transito(
            transito, agora + settings.TRAJETORIA_SELO_DECLARACAO_VALIDADE + timedelta(seconds=2)
        )
    assert CPF not in caplog.text and transito not in caplog.text


def test_consulta_vinculada():
    from types import SimpleNamespace

    id = uuid4()
    token = selo.selar_consulta(id, CPF, DATA)
    dados = SimpleNamespace(formacao_id=id, selado=token)
    assert selo.abrir_consulta(dados) == (CPF, DATA)
    dados.formacao_id = uuid4()
    with pytest.raises(selo.SeloInvalido):
        selo.abrir_consulta(dados)

from datetime import timedelta

import pytest
from django.core.cache import caches

from tests.acesso.construcao import ANA, linhas_de_dominio

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("cpf", [ANA.cpf, "000.000.009-49"])
def test_esperas_identicas_sem_bloqueio(preparado, client, relogio, cpf, caplog):
    caplog.set_level("INFO", logger="trajetoria.acesso")
    antes = linhas_de_dominio()
    dados = {"cpf": cpf, "data_nascimento": "13/04/1998"}
    for _ in range(3):
        assert client.post("/acesso/", dados).status_code == 200
    for segundos in (5, 15, 45, 135, 300, 300):
        assert client.post("/acesso/", dados).status_code == 200
        r = client.post("/acesso/", dados)
        assert r.status_code == 429 and r["Retry-After"] == str(segundos)
        assert "Aguarde alguns instantes antes de tentar novamente." in r.content.decode()
        relogio.agora += timedelta(seconds=1)
        assert client.post("/acesso/", dados)["Retry-After"] == str(segundos - 1)
        relogio.agora += timedelta(seconds=segundos - 1)
    if cpf == ANA.cpf:
        r = client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento})
        assert r.status_code == 303
    assert linhas_de_dominio() == antes
    assert any(r.levelname == "INFO" and "LIMITE_TEMPORARIO" in r.message for r in caplog.records)
    assert not any(r.levelname == "WARNING" for r in caplog.records)


def test_origem_inclui_formato_invalido(preparado, client, relogio):
    for _ in range(31):
        assert client.post("/acesso/", {"cpf": "123", "data_nascimento": "x"}).status_code == 200
    r = client.post("/acesso/", {"cpf": "123", "data_nascimento": "x"})
    assert r.status_code == 429 and r["Retry-After"] == "5"
    relogio.agora += timedelta(seconds=5)
    assert (
        client.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}).status_code
        == 303
    )


def test_falha_cache_e_chave(preparado, client, monkeypatch, settings, caplog):
    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = ""
    dados = {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}
    assert client.post("/acesso/", dados).status_code == 503
    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = "a1" * 32

    def falhar(*args, **kwargs):
        raise RuntimeError("SENTINELA-cache-chave")

    monkeypatch.setattr(caches["acesso"], "get", falhar)
    r = client.post("/acesso/", dados)
    assert r.status_code == 503
    assert "Não foi possível verificar agora. Tente novamente em instantes." in r.content.decode()
    assert "SENTINELA" not in caplog.text + r.content.decode()


def test_confirmacoes_nao_punem_a_origem(preparado, client):
    """Revisão 018: um laboratório atrás do mesmo endereço confirma sem acumular espera."""
    dados = {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}
    for _ in range(45):
        assert client.post("/acesso/", dados).status_code == 303


def test_verificacao_simultanea_do_mesmo_cpf_e_recusada(preparado, client):
    """Revisão 018: enquanto uma verificação do CPF está em andamento, outra não é avaliada."""
    from trajetoria.acesso.chaves import chaves_de_acesso, identificador_cpf
    from trajetoria.acesso.limitacao import liberar, travar

    chave = "acesso:cpf:" + identificador_cpf(ANA.cpf11, chaves_de_acesso())
    dados = {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}
    assert travar(chave)
    r = client.post("/acesso/", dados)
    assert r.status_code == 429 and r["Retry-After"] == "1"
    liberar(chave)
    assert client.post("/acesso/", dados).status_code == 303

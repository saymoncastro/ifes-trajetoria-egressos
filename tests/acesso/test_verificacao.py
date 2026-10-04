import pytest

from tests.acesso.construcao import AGORA, ANA, DIEGO, linhas_de_dominio

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("dados", [ANA, DIEGO])
@pytest.mark.parametrize("formatado", [True, False])
def test_confirma_sem_fonte_ou_escrita(preparado, monkeypatch, dados, formatado):
    from trajetoria.academico import incorporacao
    from trajetoria.acesso import material
    from trajetoria.acesso import verificacao as v
    from trajetoria.fonte_academica.simulada import FonteSimulada

    def proibido(*args, **kwargs):
        pytest.fail("acesso consultou fonte ou incorporou")

    monkeypatch.setattr(FonteSimulada, "obter_pessoa", proibido)
    monkeypatch.setattr(material, "incorporar_com_material", proibido)
    monkeypatch.setattr(incorporacao, "incorporar_encontrada", proibido)
    antes = linhas_de_dominio()
    r = v.verificar(
        dados.cpf if formatado else dados.cpf11,
        dados.nascimento if formatado else dados.nascimento.replace("/", ""),
        "127.0.0.1",
        agora=AGORA,
    )
    assert isinstance(r, v.Confirmada)
    assert r.pessoa.id_externo == ("SIM-P-0001" if dados == ANA else "SIM-P-0004")
    assert r.versao_material is not None
    assert linhas_de_dominio() == antes


def test_formato_e_chave(settings):
    from trajetoria.acesso import verificacao as v

    r = v.verificar("123", "31/02/2000", "127.0.0.1", agora=AGORA)
    assert isinstance(r, v.FormatoInvalido) and set(r.campos) == {"cpf", "data_nascimento"}
    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = ""
    r = v.verificar(ANA.cpf, ANA.nascimento, "127.0.0.1", agora=AGORA)
    assert (
        isinstance(r, v.Indisponivel) and r.causa == v.CausaIndisponibilidade.CHAVE_NAO_CONFIGURADA
    )


def test_falha_tecnica_segura(preparado, monkeypatch, caplog):
    from trajetoria.acesso import verificacao as v
    from trajetoria.acesso.models import MaterialDeVerificacao

    def falhar(*args, **kwargs):
        raise RuntimeError("SENTINELA-cpf-data-chave")

    monkeypatch.setattr(MaterialDeVerificacao.objects, "filter", falhar)
    r = v.verificar(ANA.cpf, ANA.nascimento, "127.0.0.1", agora=AGORA)
    assert r.causa == v.CausaIndisponibilidade.FALHA_TECNICA
    assert "RuntimeError" in caplog.text and "SENTINELA" not in caplog.text


CASOS_NAO_CONFIRMADOS = (
    ("000.000.009-49", "12/04/1998"),
    ("000.000.001-91", "13/04/1998"),
    ("000.000.009-49", "30/06/2001"),
    ("000.000.007-87", "12/04/1998"),
    ("000.000.008-68", "05/05/1992"),
    ("000.000.008-68", "19/10/1995"),
    ("000.000.004-34", "14/03/2003"),
)


@pytest.mark.parametrize("cpf,data", CASOS_NAO_CONFIRMADOS + ((ANA.cpf, ANA.nascimento),))
def test_uniformidade_sem_causa(preparado, monkeypatch, cpf, data):
    from unittest.mock import Mock

    from trajetoria.acesso import verificacao as v
    from trajetoria.acesso.models import MaterialDeVerificacao

    for nome in ("identificador_cpf", "verificador"):
        monkeypatch.setattr(v, nome, Mock(wraps=getattr(v, nome)))
    comparacao = Mock(wraps=v.hmac.compare_digest)
    monkeypatch.setattr(v.hmac, "compare_digest", comparacao)
    consulta = Mock(wraps=MaterialDeVerificacao.objects.filter)
    monkeypatch.setattr(MaterialDeVerificacao.objects, "filter", consulta)
    antes = linhas_de_dominio()
    resultado = v.verificar(cpf, data, "127.0.0.1", agora=AGORA)
    assert (
        v.identificador_cpf.call_count
        == v.verificador.call_count
        == comparacao.call_count
        == consulta.call_count
        == 1
    )
    assert linhas_de_dominio() == antes
    if (cpf, data) != (ANA.cpf, ANA.nascimento):
        assert isinstance(resultado, v.NaoConfirmada) and not vars(resultado)


def test_data_futura_usa_a_data_local(db):
    """Revisão 018: às 22h em Brasília (já amanhã em UTC), amanhã local continua futuro."""
    from datetime import UTC, datetime

    from trajetoria.acesso.verificacao import FormatoInvalido, verificar

    agora = datetime(2026, 10, 4, 1, tzinfo=UTC)  # 03/10/2026 22:00 em America/Sao_Paulo
    resultado = verificar("000.000.001-91", "04/10/2026", "127.0.0.1", agora=agora)
    assert resultado == FormatoInvalido(("data_nascimento",))

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory

from tests.acesso.construcao import AGORA, ANA, preparar_material

pytestmark = pytest.mark.django_db


def test_estabelece_e_le_uma_vez(relogio, django_assert_num_queries):
    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import dados_de_sessao, estabelecer, pessoa_em_uso
    from trajetoria.acesso.verificacao import Confirmada

    p = preparar_material("SIM-P-0001")[0].pessoa
    m = MaterialDeVerificacao.objects.get(pessoa=p)
    request = RequestFactory().get("/")
    request.session = SessionStore()
    request.session["antigo"] = "descartar"
    request.session.save()
    antiga = request.session.session_key
    estabelecer(request, Confirmada(p, m.atualizado_em), AGORA)
    assert request.session.session_key != antiga
    assert dict(request.session) == dados_de_sessao(p, m.atualizado_em, AGORA)
    assert len(dict(request.session)) == 4
    assert ANA.cpf11 not in repr(dict(request.session))
    del request._pessoa_de_acesso
    with django_assert_num_queries(1):
        assert pessoa_em_uso(request) == pessoa_em_uso(request) == p


@pytest.mark.parametrize("valor", [None, {}, {"acesso.pessoa": "malformado"}])
def test_ausente_corrompida(valor):
    from trajetoria.acesso.sessao import pessoa_em_uso

    r = RequestFactory().get("/")
    r.session = SessionStore()
    if valor:
        r.session.update(valor)
    assert pessoa_em_uso(r) is None


def _confirmar(client, dados=ANA):
    return client.post("/acesso/", {"cpf": dados.cpf, "data_nascimento": dados.nascimento})


@pytest.mark.parametrize("limite", ["inatividade", "maxima"])
def test_expiracao(preparado, client, relogio, settings, limite):
    from datetime import timedelta

    assert settings.TRAJETORIA_SESSAO_INATIVIDADE == timedelta(minutes=30)
    assert settings.TRAJETORIA_SESSAO_DURACAO_MAXIMA == timedelta(hours=8)
    assert _confirmar(client).status_code == 303
    if limite == "inatividade":
        settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=1)
        relogio.agora += timedelta(seconds=61)
    else:
        settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(days=1)
        relogio.agora += timedelta(hours=8, seconds=1)
    assert client.get("/formacoes/")["Location"] == "/acesso/?aviso=sessao"  # 023 FR-001
    assert not dict(client.session)


def test_renovacao_material_e_pessoa(preparado, client, relogio):
    from datetime import timedelta

    from trajetoria.acesso.models import MaterialDeVerificacao

    assert _confirmar(client).status_code == 303
    primeiro = client.session["acesso.ultimo_uso"]
    relogio.agora += timedelta(seconds=59)
    client.get("/formacoes/")
    assert client.session["acesso.ultimo_uso"] == primeiro
    relogio.agora += timedelta(seconds=1)
    client.get("/formacoes/")
    assert client.session["acesso.ultimo_uso"] == relogio.agora.isoformat()
    MaterialDeVerificacao.objects.filter(pessoa__id_externo="SIM-P-0001").update(
        atualizado_em=relogio.agora
    )
    assert client.get("/formacoes/")["Location"] == "/acesso/?aviso=sessao"  # 023 FR-001
    assert not dict(client.session)
    sessao = client.session
    sessao.update(
        {
            "acesso.pessoa": "00000000-0000-0000-0000-000000000001",
            "acesso.confirmada_em": relogio.agora.isoformat(),
            "acesso.ultimo_uso": relogio.agora.isoformat(),
            "acesso.versao_material": None,
        }
    )
    sessao.save()
    assert client.get("/formacoes/")["Location"] == "/acesso/"
    assert not dict(client.session)


def test_sair_cookie_e_troca_independente(preparado, client, relogio):
    from django.test import Client

    from tests.acesso.construcao import BRUNO
    from trajetoria.demonstracao.operador import COOKIE

    client.post("/demonstracao/operador/escolher/", {"operador": "demonstracao:operador-b"})
    operador = client.cookies[COOKIE].value
    r = _confirmar(client)
    cookie = r.cookies["trajetoria_sessao_egresso"]
    assert cookie["httponly"] and cookie["samesite"] == "Lax"
    assert not cookie["expires"] and not cookie["max-age"]
    chave = client.session.session_key
    assert _confirmar(client, BRUNO).status_code == 303
    assert client.session.session_key != chave
    assert "Bruno Exemplo" in client.get("/formacoes/").content.decode()
    assert 'action="/acesso/sair/"' in client.get("/formacoes/").content.decode()
    assert client.get("/acesso/sair/").status_code == 405
    assert Client(enforce_csrf_checks=True).post("/acesso/sair/").status_code == 403
    r = client.post("/acesso/sair/")
    assert r.status_code == 303 and r["Location"] == "/acesso/"
    assert not dict(client.session) and client.cookies[COOKIE].value == operador
    assert client.get("/formacoes/")["Location"] == "/acesso/"


def test_expiracao_preserva_rascunho(preparado, client, relogio, settings):
    from datetime import timedelta

    from trajetoria.participacao.models import Resposta

    assert _confirmar(client).status_code == 303
    entrada = client.post("/formacoes/entrar/")
    base = entrada["Location"]
    secao = client.get(base)["Location"]
    client.post(secao, {"p1": "1"})
    antes = list(Resposta.objects.values())
    assert antes
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(seconds=1)
    relogio.agora += timedelta(seconds=2)
    assert client.get(secao)["Location"] == "/acesso/?aviso=sessao"  # 023 FR-001
    assert list(Resposta.objects.values()) == antes
    assert _confirmar(client).status_code == 303
    assert "checked" in client.get(secao).content.decode()

import pytest
from django.core import mail

from tests.editor.construcao_editor import A, B
from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.operacoes import simular_comunicacao

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("operador,n", [(A, 4), (B, 1)])
def test_execucoes_independentes(campanha, operador, n, snapshot):
    antes = snapshot()
    for _ in range(2):
        r = simular_comunicacao(campanha.pk, operador)
        assert r.totais["submetidas"] == r.totais["aceitas"] == n
        assert r.totais["falhas"] == 0
        assert r.totais["sem_contato"] == 1
        assert all(set(i.__dict__) == {"pessoa_id", "situacao"} for i in r.individuais)
    assert len(mail.outbox) == n * 2
    assert snapshot() == antes


def test_encerrada_apos_preview(campanha):
    from trajetoria.campanha.operacoes import encerrar

    campanha = campanha.__class__.objects.get(nome="Demonstração — coleta ampla")
    encerrar(campanha)
    with pytest.raises(RecusaComunicacao) as erro:
        simular_comunicacao(campanha.pk, A)
    assert erro.value.status == 409
    assert not getattr(mail, "outbox", [])


def test_zero_contato_nao_constroi_backend(campanha, monkeypatch):
    from trajetoria.comunicacao.seguranca import TransporteLocal

    campanha.ano_minimo = 3000
    campanha.save()
    monkeypatch.setattr(
        TransporteLocal, "conexao", lambda self: pytest.fail("backend não deve existir")
    )
    assert simular_comunicacao(campanha.pk, B).totais["submetidas"] == 0


def test_contato_externo_aborta_todo_conjunto(campanha, monkeypatch, settings):
    from trajetoria.comunicacao import consultas
    from trajetoria.comunicacao.seguranca import TransporteLocal

    original = consultas.contato_ficticio
    monkeypatch.setattr(
        consultas,
        "contato_ficticio",
        lambda p: "real@external.test" if p.id_externo == "SIM-P-0003" else original(p),
    )
    monkeypatch.setattr(TransporteLocal, "conexao", lambda self: pytest.fail("nenhuma conexão"))
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.incorreto.test"
    with pytest.raises(RecusaComunicacao):
        simular_comunicacao(campanha.pk, A)
    assert not getattr(mail, "outbox", [])


def test_contato_ausente_e_publico_atual(campanha):
    from trajetoria.academico.models import ConclusaoAcademica

    pessoa = ConclusaoAcademica.objects.get(id_externo="SIM-C-0006").pessoa
    ConclusaoAcademica.objects.create(
        fonte="simulada", id_externo="SIM-C-extra", pessoa=pessoa, unidade="Vitória"
    )
    r = simular_comunicacao(campanha.pk, B)
    assert r.totais["pessoas"] == 3 and r.totais["aceitas"] == 2


def test_renderer_falha_apos_mensagem_valida_sem_transporte(campanha, monkeypatch, snapshot):
    from trajetoria.comunicacao import operacoes
    from trajetoria.comunicacao.seguranca import TransporteLocal

    antes = snapshot()
    original = operacoes.renderizar_convite
    calls = []

    def renderizar(*args):
        calls.append(args)
        if len(calls) == 2:
            raise RuntimeError("SENTINELA-corpo-credencial")
        return original(*args)

    monkeypatch.setattr(operacoes, "renderizar_convite", renderizar)
    monkeypatch.setattr(TransporteLocal, "conexao", lambda self: pytest.fail("zero transporte"))
    with pytest.raises(RecusaComunicacao) as erro:
        simular_comunicacao(campanha.pk, A)
    assert erro.value.status == 422
    assert len(calls) == 2 and not getattr(mail, "outbox", [])
    assert snapshot() == antes

"""Página "Meu e-mail" (020 FR-009 a FR-014; US4; T044)."""

import pytest
from django.test import Client

from tests.acesso.construcao import ANA
from tests.contato.conftest import contato
from trajetoria.academico.models import Pessoa
from trajetoria.contato.models import ContatoDaPessoa, Origem
from trajetoria.demonstracao.cenario import preparar
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db
URL = "/meu-email/"


@pytest.fixture
def ana(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar()
    cliente = Client()
    assert cliente.post(
        "/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento}
    ).status_code == 303
    return cliente, Pessoa.objects.get(id_externo="SIM-P-0001")


def _egresso(pessoa):
    return list(
        ContatoDaPessoa.objects.filter(pessoa=pessoa, origem=Origem.EGRESSO)
        .order_by("obtido_em").values_list("valor", flat=True)
    )


def test_exige_sessao_de_pessoa(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar()
    for metodo in ("get", "post"):
        resposta = getattr(Client(), metodo)(URL)
        assert (resposta.status_code, resposta["Location"]) == (303, "/acesso/")


def test_get_nao_exibe_contato_guardado(ana):
    cliente, pessoa = ana
    contato(pessoa, "marcador-informado@example.invalid", Origem.EGRESSO)
    resposta = cliente.get(URL)
    html = resposta.content.decode()
    assert resposta.status_code == 200
    assert "sim-p-0001" not in html and "marcador-informado" not in html
    assert "não será público" in html and "opcional" in html
    assert 'autocomplete="email"' in html and '<label for="email">' in html
    assert html.count('class="secundario"') == 2  # Salvar e Agora não com o mesmo peso
    assert "no-cache" in resposta["Cache-Control"] or "no-store" in resposta["Cache-Control"]


def test_salvar_acrescenta_registro_sem_apagar_o_importado(ana):
    cliente, pessoa = ana
    antes = (Participacao.objects.count(), Resposta.objects.count())
    resposta = cliente.post(URL, {"acao": "salvar", "email": " Novo.Email@Example.Invalid "})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Pronto." in html and "Novo.Email" not in html
    assert _egresso(pessoa) == ["Novo.Email@example.invalid"]
    assert ContatoDaPessoa.objects.filter(pessoa=pessoa, origem=Origem.FONTE_ACADEMICA).exists()
    cliente.post(URL, {"acao": "salvar", "email": "novo.email@example.invalid"})
    cliente.post(URL, {"acao": "salvar", "email": "Novo.Email@example.invalid"})
    assert _egresso(pessoa) == ["Novo.Email@example.invalid", "novo.email@example.invalid",
                                "Novo.Email@example.invalid"]
    cliente.post(URL, {"acao": "salvar", "email": "Novo.Email@example.invalid"})
    assert len(_egresso(pessoa)) == 3  # igual ao último: não grava
    assert (Participacao.objects.count(), Resposta.objects.count()) == antes


def test_invalido_422_sem_gravar(ana):
    cliente, pessoa = ana
    resposta = cliente.post(URL, {"acao": "salvar", "email": "nao-e-email"})
    assert resposta.status_code == 422
    html = resposta.content.decode()
    assert 'aria-invalid="true"' in html and "nao-e-email" not in html
    assert _egresso(pessoa) == []


def test_agora_nao_nao_grava(ana):
    cliente, pessoa = ana
    resposta = cliente.post(URL, {"acao": "agora_nao", "email": "a@example.invalid"})
    assert "Nada foi alterado" in resposta.content.decode()
    assert _egresso(pessoa) == []


def test_links_de_saida(ana):
    cliente, _ = ana
    html = cliente.post(URL, {"acao": "agora_nao"}).content.decode()
    assert 'href="/formacoes/"' in html
    # 024 FR-009 (revisa 021 FR-001): a trajetória não depende de participação concluída.
    assert 'href="/minha-trajetoria/">Ver minha trajetória no Ifes' in html


def test_csrf_exigido(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar()
    cliente = Client(enforce_csrf_checks=True)
    pagina = cliente.get("/acesso/")
    token = pagina.cookies["csrftoken"].value
    cliente.post("/acesso/", {"cpf": ANA.cpf, "data_nascimento": ANA.nascimento,
                              "csrfmiddlewaretoken": token})
    assert cliente.post(URL, {"acao": "salvar", "email": "a@example.invalid"}).status_code == 403

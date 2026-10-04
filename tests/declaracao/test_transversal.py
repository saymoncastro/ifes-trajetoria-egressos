"""Invariantes de sigilo, acesso e incorporação nas fronteiras da 019."""

import pytest
from django.apps import apps
from django.test import Client

from tests.acompanhamento.construcao import A, atuar_como
from tests.declaracao.construcao import CPF, DADOS, DATA, declaracao_concluida
from tests.declaracao.test_rotas_egresso import preparar, token
from tests.governanca.test_governanca_regras import CPAEG, CSAEG_VITORIA
from tests.participacao import construcao as c
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.declaracao.models import AcessoAosDadosDeConsulta, DadosConsultaAcervo
from trajetoria.declaracao.operacoes import (
    FonteIndisponivel,
    ForaDoEscopo,
    ReferenciaInexistente,
    registrar_validacao,
    revelar_dados,
)
from trajetoria.declaracao.selo import SeloInvalido, selar_transito
from trajetoria.fonte_academica.contrato import FonteAcademicaIndisponivel
from trajetoria.governanca.models import Papel
from trajetoria.governanca.operacoes import registrar_vinculo

pytestmark = pytest.mark.django_db


def retrato():
    return {m._meta.label: list(m.objects.values()) for m in apps.get_models()}


def test_referencia_digital_incorpora_somente_por_atestacao():
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    assert not Pessoa.objects.exists()
    v = registrar_validacao(
        f,
        vinculos=[CPAEG],
        operador="A",
        agora=c.NO_PERIODO,
        resultado="CONFIRMADA",
        referencia_fonte="SIM-C-0014",
    )
    assert v.conclusao.id_externo == "SIM-C-0014"
    assert v.conclusao.pessoa.id_externo == "SIM-P-0012"
    assert MaterialDeVerificacao.objects.filter(pessoa=v.conclusao.pessoa).exists()
    assert f.participacao.conclusao_id is None


@pytest.mark.parametrize("referencia", ["SIM-C-9999", "SIM-C-0901"])
def test_referencia_inexistente_ou_nao_concluida_sem_escrita(referencia):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    antes = retrato()
    with pytest.raises(ReferenciaInexistente):
        registrar_validacao(
            f,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            referencia_fonte=referencia,
        )
    assert retrato() == antes


def test_fonte_indisponivel_sem_escrita(monkeypatch):
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao))
    antes = retrato()

    def indisponivel(*args):
        raise FonteAcademicaIndisponivel

    monkeypatch.setattr(
        "trajetoria.declaracao.operacoes.FonteSimulada.obter_conclusao", indisponivel
    )
    with pytest.raises(FonteIndisponivel):
        registrar_validacao(
            f,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            referencia_fonte="SIM-C-0014",
        )
    assert retrato() == antes


def test_escopo_confirmado_e_auditoria_adulterada():
    f = declaracao_concluida(c.campanha_aberta(c.instrumento().versao), unidade="Vitória")
    antes = retrato()
    with pytest.raises(ForaDoEscopo):
        registrar_validacao(
            f,
            vinculos=[CSAEG_VITORIA],
            operador="B",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            referencia_fonte="SIM-C-0014",
        )
    assert retrato() == antes
    DadosConsultaAcervo.objects.filter(formacao=f).update(selado="adulterado")
    with pytest.raises(SeloInvalido):
        revelar_dados(f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO)
    assert not AcessoAosDadosDeConsulta.objects.exists()
    DadosConsultaAcervo.objects.filter(formacao=f).delete()
    assert revelar_dados(f, vinculos=[CPAEG], operador="A", agora=c.NO_PERIODO) is None
    assert not AcessoAosDadosDeConsulta.objects.exists()


def test_sinal_de_coincidencia_sem_fusao(client):
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    x = c.conclusao()
    MaterialDeVerificacao.objects.create(
        pessoa=x.pessoa,
        identificador_cpf=f.identificador_cpf,
        atualizado_em=c.NO_PERIODO,
    )
    registrar_vinculo(A, Papel.CPAEG)
    atuar_como(client, A)
    html = client.get(f"/validacoes-formacao/{f.pk}/").content.decode()
    assert "mesmo CPF na fonte digital" in html and CPF not in html
    dados = {k: v for k, v in DADOS.items() if k != "nome"} | {"referencia": "Livro 3 folha 12"}
    v = registrar_validacao(
        f,
        vinculos=[CPAEG],
        operador="A",
        agora=c.NO_PERIODO,
        resultado="CONFIRMADA",
        acervo=dados,
    )
    assert v.conclusao.pessoa_id != x.pessoa_id and Pessoa.objects.count() == 2
    assert MaterialDeVerificacao.objects.count() == 1
    assert ConclusaoAcademica.objects.count() == 2


def test_urls_sessao_redirects_logs_e_csrf(client, caplog):
    preparar()
    transito = selar_transito(CPF, DATA)
    respostas = [client.post("/declaracao/", {"selo": transito})]
    respostas.append(client.post("/declaracao/nova/", {"selo": transito, **DADOS}))
    inicio = token(respostas[-1])
    respostas.append(client.post("/declaracao/comecar/", {"selo": inicio}))
    sessao = str(dict(client.session))
    assert transito not in sessao and inicio not in sessao
    for valor in (CPF, DATA.isoformat(), DATA.strftime("%d/%m/%Y")):
        assert valor not in sessao and valor not in caplog.text
    for r in respostas:
        assert "no-store" in r["Cache-Control"]
        local = r.headers.get("Location", "")
        assert all(v not in local for v in (CPF, DATA.isoformat(), transito, inicio))
    for rota in ("/declaracao/", "/declaracao/nova/", "/declaracao/comecar/"):
        assert Client(enforce_csrf_checks=True).post(rota, {"selo": transito}).status_code == 403
    # A declaração não dá acesso a uma Participação institucional.
    from trajetoria.campanha.models import Campanha
    from trajetoria.participacao.models import Participacao

    p = Participacao.objects.create(
        campanha=Campanha.objects.get(),
        conclusao=c.conclusao(),
        iniciada_em=c.NO_PERIODO,
    )
    assert client.get(f"/participacoes/{p.pk}/").status_code == 404
    assert client.get("/")["Location"] == "/declaracao/"


def test_barreira_acervo_local_e_base_real(client):
    from trajetoria.demonstracao.base import base_somente_simulada

    x = c.conclusao()
    x.fonte = "acervo_historico"
    x.save()
    x.pessoa.fonte = "acervo_historico"
    x.pessoa.save()
    assert base_somente_simulada() and client.get("/acesso/").status_code == 200
    x.pessoa.fonte = "real"
    x.pessoa.save()
    assert not base_somente_simulada() and client.get("/acesso/").status_code == 422

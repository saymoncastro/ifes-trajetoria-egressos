import pytest

from tests.editor.construcao_editor import A, B
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.comunicacao.acesso import RecusaComunicacao, autorizar_operador
from trajetoria.comunicacao.consultas import publico_atual
from trajetoria.governanca.regras import EscopoDeAcompanhamento

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("operador,contagens", [(A, (13, 9, 8, 1, 8)), (B, (3, 2, 1, 1, 1))])
def test_publico_atual(campanha, operador, contagens, snapshot):
    antes = snapshot()
    p = publico_atual(campanha, autorizar_operador(operador).escopo)
    assert tuple(p.totais.values()) == contagens
    assert snapshot() == antes


def test_recorte_antes_da_deduplicacao(campanha):
    maria = Pessoa.objects.get(id_externo="SIM-P-0003")
    ConclusaoAcademica.objects.create(
        pessoa=maria, fonte="simulada", id_externo="SIM-C-extra", unidade="Vitória"
    )
    p = publico_atual(campanha, EscopoDeAcompanhamento(False, frozenset({"Vitória"})))
    assert p.totais["conclusoes"] == 4
    assert p.totais["pessoas"] == 3
    assert len([i for i in p.itens if i.pessoa.pk == maria.pk]) == 1
    assert {i.pessoa.id_externo for i in p.itens} == {"SIM-P-0002", "SIM-P-0003", "SIM-P-0010"}


def test_inelegiveis_unidade_nula_e_zero(campanha):
    assert (
        publico_atual(campanha, EscopoDeAcompanhamento(False, frozenset({"Viana"}))).totais[
            "pessoas"
        ]
        == 0
    )
    campanha.ano_minimo = 3000
    assert publico_atual(campanha, autorizar_operador(A).escopo).totais == dict(
        conclusoes=0, pessoas=0, com_contato=0, sem_contato=0, previstas=0
    )


def test_falha_resolver_nao_vira_ausencia(campanha, monkeypatch, caplog):
    from trajetoria.comunicacao import consultas

    def falhar(pessoa):
        raise RuntimeError("nome-email-conteudo-credencial-SENTINELA")

    monkeypatch.setattr(consultas, "contato_ficticio", falhar)
    with pytest.raises(RecusaComunicacao) as erro:
        publico_atual(campanha, autorizar_operador(A).escopo)
    assert erro.value.categoria == "falha_preparacao"
    assert "SENTINELA" not in caplog.text + str(erro.value)


def test_tres_conclusoes_e_recorte_exato_sem_unidade(campanha, snapshot):
    from django.core import mail

    from trajetoria.comunicacao.operacoes import simular_comunicacao

    campanha.unidades = None
    campanha.ano_minimo = 2010
    campanha.ano_maximo = 2020
    campanha.save()
    bruno = Pessoa.objects.get(id_externo="SIM-P-0002")
    for n, (unidade, ano) in enumerate(
        [("Vitória", 2018), ("Vitória", 2000), ("vitória", 2018), (None, 2018)]
    ):
        ConclusaoAcademica.objects.create(
            pessoa=bruno,
            fonte="simulada",
            id_externo=f"SIM-C-caso-{n}",
            unidade=unidade,
            ano_conclusao=ano,
        )
    antes = snapshot()
    publico = publico_atual(campanha, autorizar_operador(B).escopo)
    assert tuple(publico.totais.values()) == (4, 2, 1, 1, 1)
    resultado = simular_comunicacao(campanha.pk, B)
    assert resultado.totais["aceitas"] == 1
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ["sim-p-0002@example.invalid"]
    assert snapshot() == antes

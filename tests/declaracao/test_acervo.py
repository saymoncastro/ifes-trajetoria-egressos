import pytest

from tests.declaracao.construcao import DADOS, declaracao_concluida
from tests.governanca.test_governanca_regras import CPAEG
from tests.participacao import construcao as c
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.declaracao.acervo import (
    FonteAcervoHistorico,
    ReferenciaDivergente,
    registrar_referencia,
)
from trajetoria.declaracao.operacoes import registrar_validacao
from trajetoria.fonte_academica.contrato import (
    ConclusaoEncontrada,
    PessoaEncontrada,
    PessoaInexistente,
)

pytestmark = pytest.mark.django_db


def test_fonte_e_convergencia():
    dados = {k: v for k, v in DADOS.items() if k != "nome"} | {"referencia": "Livro   2 folha  1"}
    r = registrar_referencia(dados, operador="A", agora=c.NO_PERIODO)
    assert (
        registrar_referencia(
            dados | {"referencia": "Livro 2 folha 1"}, operador="B", agora=c.NO_PERIODO
        )
        == r
    )
    with pytest.raises(ReferenciaDivergente):
        registrar_referencia(dados | {"curso": "Outro curso"}, operador="A", agora=c.NO_PERIODO)
    fonte = FonteAcervoHistorico()
    p = fonte.obter_pessoa(f"acervo:{r.pk}")
    assert isinstance(p, PessoaEncontrada) and p.cpf is None and p.data_nascimento is None
    assert isinstance(fonte.obter_conclusao(str(r.pk)), ConclusaoEncontrada)
    assert isinstance(fonte.obter_pessoa("malformada"), PessoaInexistente)
    campanha = c.campanha_aberta(c.instrumento().versao)
    for _ in range(2):
        f = declaracao_concluida(campanha)
        v = registrar_validacao(
            f,
            vinculos=[CPAEG],
            operador="A",
            agora=c.NO_PERIODO,
            resultado="CONFIRMADA",
            acervo=dados,
        )
        assert v.conclusao.fonte == "acervo_historico"
    assert ConclusaoAcademica.objects.filter(fonte="acervo_historico").count() == 1


@pytest.mark.parametrize("campo,valor", [("curso", None), ("nivel", "  "), ("modalidade", "")])
def test_atributos_ausentes_ou_vazios_nao_criam_referencia(campo, valor):
    from trajetoria.declaracao.models import ReferenciaDeAcervo

    dados = {k: v for k, v in DADOS.items() if k != "nome"} | {"referencia": "Livro 3"}
    with pytest.raises(ValueError):
        registrar_referencia(dados | {campo: valor}, operador="A", agora=c.NO_PERIODO)
    assert not ReferenciaDeAcervo.objects.exists()

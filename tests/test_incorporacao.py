"""Incorporação de Pessoas e Conclusões a partir de uma fonte acadêmica."""

import logging
import random
from dataclasses import replace
from datetime import date

import pytest

from tests.fontes_de_teste import FonteAlternativa, variante_canonica
from trajetoria.academico.incorporacao import (
    Divergencia,
    SituacaoIncorporacao,
    TipoDivergencia,
    incorporar_pessoa,
)
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.cenarios import PessoaSimulada, RegistroSimulado
from trajetoria.fonte_academica.contrato import ConclusaoInexistente, FonteAcademicaIndisponivel
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db


# --- US1: Pessoa com sua Conclusão Acadêmica ---------------------------------------------


def test_cenario_a_incorpora_pessoa_com_uma_conclusao(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0001")

    assert resultado.situacao is SituacaoIncorporacao.INCORPORADA
    assert resultado.pessoa_criada is True
    assert Pessoa.objects.count() == 1
    assert ConclusaoAcademica.objects.count() == 1

    conclusao = resultado.pessoa.conclusoes.get()
    assert conclusao.curso == "Tecnologia em Análise e Desenvolvimento de Sistemas"
    assert conclusao.unidade == "Serra"
    assert conclusao.nivel == "Graduação"
    assert conclusao.modalidade == "Presencial"
    assert conclusao.ano_conclusao == 2022
    assert conclusao.data_conclusao == date(2022, 12, 16)
    # Não informado pela fonte: fica ausente, sem valor padrão (FR-010).
    assert conclusao.forma_oferta is None


def test_conclusao_so_com_ano_nao_fabrica_data(fonte_simulada):
    incorporar_pessoa(fonte_simulada, "SIM-P-0002")

    conclusao = ConclusaoAcademica.objects.get(id_externo="SIM-C-0002")
    assert conclusao.ano_conclusao == 2014
    assert conclusao.data_conclusao is None


# --- US2: uma Pessoa, múltiplas Conclusões -----------------------------------------------


@pytest.mark.parametrize(
    ("id_pessoa", "quantidade"), [("SIM-P-0002", 2), ("SIM-P-0003", 2), ("SIM-P-0004", 3)]
)
def test_pessoa_com_varias_conclusoes_e_uma_unica_pessoa(fonte_simulada, id_pessoa, quantidade):
    resultado = incorporar_pessoa(fonte_simulada, id_pessoa)

    assert Pessoa.objects.count() == 1
    conclusoes = list(resultado.pessoa.conclusoes.all())
    assert len(conclusoes) == quantidade
    assert len({c.id for c in conclusoes}) == quantidade


def test_conclusoes_em_unidades_diferentes(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0003")
    assert {c.unidade for c in resultado.pessoa.conclusoes.all()} == {"Serra", "Cefor"}


def test_conclusoes_em_niveis_diferentes(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0004")
    assert {c.nivel for c in resultado.pessoa.conclusoes.all()} == {
        "Técnico", "Graduação", "Pós-graduação",
    }


def test_homonimos_sao_pessoas_distintas(fonte_simulada):
    # O nome não identifica nem deduplica (FR-005, FR-031).
    a = incorporar_pessoa(fonte_simulada, "SIM-P-0010").pessoa
    b = incorporar_pessoa(fonte_simulada, "SIM-P-0011").pessoa

    assert a.nome == b.nome == "Carla Exemplo"
    assert a.id != b.id
    assert Pessoa.objects.count() == 2


def test_pessoa_sem_nome_e_incorporada(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0009")

    assert resultado.pessoa.nome is None
    assert resultado.pessoa.conclusoes.count() == 1


def test_conclusoes_parecidas_com_origens_distintas_nao_se_fundem():
    # Mesmo curso e unidade, id_externo diferente: duas conclusões (FR-014).
    registros = [
        RegistroSimulado(
            f"SIM-C-T{n}", "SIM-P-T1", "concluida", "Técnico em Informática", "Serra",
            "Técnico", "Presencial", "Subsequente", ano,
        )
        for n, ano in ((1, 2015), (2, 2019))
    ]
    fonte = FonteSimulada(pessoas=[PessoaSimulada("SIM-P-T1", None)], registros=registros)

    resultado = incorporar_pessoa(fonte, "SIM-P-T1")

    assert resultado.pessoa.conclusoes.count() == 2


# --- US4: substituição da fonte ----------------------------------------------------------


def test_outra_implementacao_da_fonte_funciona_sem_ajuste_no_dominio():
    resultado = incorporar_pessoa(FonteAlternativa(), "ALT-P-1")

    assert resultado.situacao is SituacaoIncorporacao.INCORPORADA
    assert Pessoa.objects.get().fonte == "teste-alternativa"
    conclusoes = list(resultado.pessoa.conclusoes.all())
    assert len(conclusoes) == 2
    assert {c.fonte for c in conclusoes} == {"teste-alternativa"}


# --- US5: repetição sem duplicidade e divergência sinalizada -----------------------------

IDS_PESSOAS = [p.id_externo for p in cenarios.PESSOAS]


def _incorporar_catalogo(fonte, ordem=IDS_PESSOAS):
    return [incorporar_pessoa(fonte, id_pessoa) for id_pessoa in ordem]


def _retrato():
    """Todas as linhas com todos os valores, inclusive `incorporado_em`."""
    return (
        list(Pessoa.objects.order_by("id").values()),
        list(ConclusaoAcademica.objects.order_by("id").values()),
    )


def test_repetir_o_catalogo_em_ordens_diferentes_nao_duplica(fonte_simulada):
    _incorporar_catalogo(fonte_simulada)
    retrato = _retrato()

    embaralhada = list(IDS_PESSOAS)
    random.Random(2026).shuffle(embaralhada)
    for ordem in (list(reversed(IDS_PESSOAS)), embaralhada):
        for resultado in _incorporar_catalogo(fonte_simulada, ordem):
            assert resultado.pessoa_criada is False
            assert resultado.conclusoes_criadas == ()

    assert _retrato() == retrato


def test_conclusao_repetida_mantem_a_mesma_identidade(fonte_simulada):
    primeira = incorporar_pessoa(fonte_simulada, "SIM-P-0005")
    segunda = incorporar_pessoa(fonte_simulada, "SIM-P-0005")

    assert segunda.pessoa.id == primeira.pessoa.id
    assert segunda.conclusoes_existentes[0].id == primeira.conclusoes_criadas[0].id
    assert ConclusaoAcademica.objects.count() == 1


def test_nova_conclusao_e_associada_a_pessoa_existente(fonte_simulada):
    original = incorporar_pessoa(fonte_simulada, "SIM-P-0001").pessoa

    resultado = incorporar_pessoa(variante_canonica("v"), "SIM-P-0001")

    assert resultado.pessoa.id == original.id
    assert resultado.pessoa_criada is False
    assert [c.id_externo for c in resultado.conclusoes_criadas] == ["SIM-C-0099"]
    assert Pessoa.objects.count() == 1


@pytest.mark.parametrize(
    ("variante", "id_pessoa", "esperada"),
    [
        ("i", "SIM-P-0001", (TipoDivergencia.ATRIBUTOS_DIFERENTES, "conclusao", "SIM-C-0001",
                             ("curso",))),
        ("ii", "SIM-P-0002", (TipoDivergencia.AUSENTE_NA_FONTE, "conclusao", "SIM-C-0003", ())),
        ("iii", "SIM-P-0001", (TipoDivergencia.CONCLUSAO_DE_OUTRA_PESSOA, "conclusao",
                               "SIM-C-0002", ())),
        ("iv", "SIM-P-0009", (TipoDivergencia.ATRIBUTOS_DIFERENTES, "pessoa", "SIM-P-0009",
                              ("nome",))),
    ],
)
def test_divergencia_e_sinalizada_sem_alterar_nada(
    fonte_simulada, caplog, variante, id_pessoa, esperada
):
    _incorporar_catalogo(fonte_simulada)
    retrato = _retrato()

    with caplog.at_level(logging.WARNING, logger="trajetoria"):
        resultado = incorporar_pessoa(variante_canonica(variante), id_pessoa)

    tipo, registro, id_externo, campos = esperada
    assert resultado.divergencias == (
        Divergencia(tipo, registro, "simulada", id_externo, campos),
    )
    assert _retrato() == retrato  # nada sobrescrito, removido ou duplicado

    assert len(caplog.records) == 1
    mensagem = caplog.records[0].getMessage()
    for trecho in (tipo.name, registro, "simulada", id_externo):
        assert trecho in mensagem
    assert "Exemplo" not in mensagem  # nunca o nome da pessoa


def test_pessoa_nova_so_com_conclusao_de_outra_pessoa_nao_e_materializada(fonte_simulada):
    # Nenhuma conclusão pode ser associada a ela; criá-la violaria FR-039.
    incorporar_pessoa(fonte_simulada, "SIM-P-0002")
    retrato = _retrato()
    alheia = next(r for r in cenarios.REGISTROS if r.id_externo == "SIM-C-0002")
    fonte = FonteSimulada(
        pessoas=[PessoaSimulada("SIM-P-T2", None)],
        registros=[replace(alheia, id_pessoa="SIM-P-T2")],
    )

    resultado = incorporar_pessoa(fonte, "SIM-P-T2")

    assert resultado.situacao is SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL
    assert resultado.pessoa is None
    assert [d.tipo for d in resultado.divergencias] == [TipoDivergencia.CONCLUSAO_DE_OUTRA_PESSOA]
    assert _retrato() == retrato


# --- US6: proveniência mínima ------------------------------------------------------------


def test_toda_linha_tem_fonte_id_externo_e_momento_de_incorporacao(fonte_simulada):
    _incorporar_catalogo(fonte_simulada)
    pessoas_declaradas = {p.id_externo for p in cenarios.PESSOAS}
    conclusoes_declaradas = {r.id_externo for r in cenarios.REGISTROS}

    for linha in [*Pessoa.objects.all(), *ConclusaoAcademica.objects.all()]:
        assert linha.fonte == "simulada"  # o código identifica a fonte simulada
        assert linha.incorporado_em is not None
    assert {p.id_externo for p in Pessoa.objects.all()} <= pessoas_declaradas
    assert {c.id_externo for c in ConclusaoAcademica.objects.all()} <= conclusoes_declaradas


def test_momento_de_incorporacao_nao_muda_em_nova_incorporacao(fonte_simulada):
    _incorporar_catalogo(fonte_simulada)
    antes = {c.id: c.incorporado_em for c in ConclusaoAcademica.objects.all()}

    _incorporar_catalogo(fonte_simulada)

    assert {c.id: c.incorporado_em for c in ConclusaoAcademica.objects.all()} == antes


def test_proveniencia_registra_a_fonte_alternativa():
    incorporar_pessoa(FonteAlternativa(), "ALT-P-1")

    assert {p.fonte for p in Pessoa.objects.all()} == {"teste-alternativa"}
    assert {c.id_externo for c in ConclusaoAcademica.objects.all()} == {"ALT-C-1", "ALT-C-2"}


# --- US7: não concluído não vira Conclusão elegível --------------------------------------


@pytest.mark.parametrize("id_pessoa", ["SIM-P-0006", "SIM-P-0008"])
def test_pessoa_so_com_registros_nao_concluidos_nao_e_persistida(fonte_simulada, id_pessoa):
    resultado = incorporar_pessoa(fonte_simulada, id_pessoa)

    assert resultado.situacao is SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL
    assert resultado.pessoa is None
    assert Pessoa.objects.count() == 0
    assert ConclusaoAcademica.objects.count() == 0


def test_so_a_conclusao_reconhecida_e_persistida(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-0007")

    assert [c.id_externo for c in resultado.pessoa.conclusoes.all()] == ["SIM-C-0010"]


def test_nenhum_registro_nao_concluido_vira_conclusao(fonte_simulada):
    _incorporar_catalogo(fonte_simulada)

    assert not ConclusaoAcademica.objects.filter(id_externo__startswith="SIM-C-09").exists()


def test_pessoa_que_perde_as_conclusoes_e_sinalizada_sem_alteracao(fonte_simulada):
    _incorporar_catalogo(fonte_simulada)
    retrato = _retrato()

    resultado = incorporar_pessoa(variante_canonica("vi"), "SIM-P-0001")

    assert resultado.situacao is SituacaoIncorporacao.SEM_CONCLUSAO_ELEGIVEL
    assert resultado.pessoa.id_externo == "SIM-P-0001"
    assert resultado.divergencias == (
        Divergencia(TipoDivergencia.AUSENTE_NA_FONTE, "conclusao", "simulada", "SIM-C-0001"),
    )
    assert _retrato() == retrato


# --- US8: inexistência e falha da fonte --------------------------------------------------


def test_pessoa_inexistente_nao_cria_nada(fonte_simulada):
    resultado = incorporar_pessoa(fonte_simulada, "SIM-P-9999")

    assert resultado.situacao is SituacaoIncorporacao.PESSOA_INEXISTENTE
    assert resultado.pessoa is None
    assert Pessoa.objects.count() == 0


def test_pessoa_incorporada_que_some_da_fonte_e_sinalizada_sem_remocao(fonte_simulada):
    incorporar_pessoa(fonte_simulada, "SIM-P-0001")
    retrato = _retrato()

    resultado = incorporar_pessoa(variante_canonica("vii"), "SIM-P-0001")

    assert resultado.situacao is SituacaoIncorporacao.PESSOA_INEXISTENTE
    assert resultado.pessoa.id_externo == "SIM-P-0001"
    assert resultado.divergencias == (
        Divergencia(TipoDivergencia.AUSENTE_NA_FONTE, "pessoa", "simulada", "SIM-P-0001"),
    )
    assert _retrato() == retrato


def test_falha_da_fonte_e_propagada_sem_escrita(fonte_indisponivel):
    with pytest.raises(FonteAcademicaIndisponivel):
        incorporar_pessoa(fonte_indisponivel, "SIM-P-0001")

    assert Pessoa.objects.count() == 0


def test_falha_da_fonte_nao_altera_o_ja_incorporado(fonte_simulada, fonte_indisponivel):
    incorporar_pessoa(fonte_simulada, "SIM-P-0001")
    retrato = _retrato()

    with pytest.raises(FonteAcademicaIndisponivel):
        incorporar_pessoa(fonte_indisponivel, "SIM-P-0001")

    assert _retrato() == retrato


def test_resposta_fora_do_contrato_e_erro_e_nao_inexistencia():
    class FonteDefeituosa:
        codigo = "defeituosa"

        def obter_pessoa(self, id_externo):
            return ConclusaoInexistente(id_externo)  # tipo errado para esta operação

    with pytest.raises(TypeError):
        incorporar_pessoa(FonteDefeituosa(), "X")
    assert Pessoa.objects.count() == 0

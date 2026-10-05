"""Montagem pura da narrativa: o que não há, não aparece (021 US2; FR-011, FR-015 a FR-025;
research R5, R6). Sem banco e sem relógio."""

import json
from datetime import date

import pytest

from tests.narrativa import construcao as cn
from trajetoria.narrativa import card, catalogo
from trajetoria.narrativa.contrato import serializar
from trajetoria.narrativa.montagem import montar

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
ESPECIALIZACAO = "Especialização em Informática na Educação"


def _textos(narrativa, chave=None):
    return [
        f.texto for s in narrativa.secoes if chave in (None, s.chave) for f in s.frases
    ]


def _maria(**extra):
    return cn.entrada(
        [
            cn.fato(curso=TADS, unidade="Serra", nivel="Graduação", modalidade="Presencial",
                    ano_conclusao=2022),
            cn.fato(curso=ESPECIALIZACAO, unidade="Cefor", nivel="Pós-graduação",
                    modalidade="A distância", ano_conclusao=2025,
                    data_conclusao=date(2025, 3, 28)),
        ],
        nome="Maria Exemplo",
        **extra,
    )


def _diego():
    return cn.entradas_dos_cenarios()["SIM-P-0004"]


# --- Ordem e continuidade (FR-019; R5) ----------------------------------------------------


def test_diego_tres_formacoes_em_ordem_com_duas_continuidades():
    n = montar(_diego())
    assert [f.ano_conclusao for f in n.formacoes] == [2012, 2017, 2020]
    assert _textos(n, "outras_formacoes") == [
        "Depois dessa formação, você também concluiu Licenciatura em Química.",
        "Depois dessa formação, você também concluiu Mestrado Profissional em Química.",
    ]
    assert [f.relacao.indice if f.relacao else None for f in n.formacoes] == [None, 0, 1]


def test_maria_uma_continuidade():
    assert _textos(montar(_maria()), "outras_formacoes") == [
        f"Depois dessa formação, você também concluiu {ESPECIALIZACAO}."
    ]


def test_ana_formacao_unica_sem_outras_formacoes():
    n = montar(cn.entradas_dos_cenarios()["SIM-P-0001"])
    assert n.secao("outras_formacoes") is None
    assert not any(d.tipo == "primeira_formacao" for d in n.derivados) or len(n.formacoes) == 1


def test_mesmo_ano_sem_relacao_nem_primeira():
    n = montar(cn.entrada([cn.fato(curso="A", ano_conclusao=2020),
                           cn.fato(curso="B", ano_conclusao=2020)]))
    assert n.secao("outras_formacoes") is None
    assert all(f.relacao is None for f in n.formacoes)
    assert not any(d.tipo == "primeira_formacao" for d in n.derivados)
    assert not any(p in t.lower() for t in _textos(n) for p in ("antes", "depois", "primeira"))


def test_ano_ausente_sem_relacao():
    n = montar(cn.entrada([cn.fato(curso="A", ano_conclusao=2018), cn.fato(curso="B")]))
    assert all(f.relacao is None for f in n.formacoes)


def test_grupo_anterior_com_duas_formacoes_sem_frase():
    n = montar(cn.entrada([cn.fato(curso="A", ano_conclusao=2018),
                           cn.fato(curso="B", ano_conclusao=2018),
                           cn.fato(curso="C", ano_conclusao=2021)]))
    assert n.secao("outras_formacoes") is None


def test_primeira_formacao_so_com_menor_ano_unico():
    n = montar(_diego())
    primeira = [d for d in n.derivados if d.tipo == "primeira_formacao"]
    assert len(primeira) == 1 and primeira[0].valor == 0


# --- Tempo (FR-020; R6) -------------------------------------------------------------------


def test_so_ano_nunca_conta_anos():
    n = montar(cn.entrada([cn.fato(curso="A", unidade="Serra", ano_conclusao=2022)],
                          referencia=date(2025, 1, 10)))
    textos = _textos(n)
    assert "Em 2022, você concluiu A na unidade Serra." in textos
    assert not any(t.startswith("Há ") for t in textos)
    assert not any(d.tipo == "tempo_desde_conclusao" for d in n.derivados)


def test_com_data_anos_completos():
    bruno = cn.entradas_dos_cenarios()["SIM-P-0002"]
    n = montar(bruno)  # 2020-07-10 → 2026-10-04
    assert "Há 6 anos desde essa conclusão." in _textos(n, "trajetoria_academica")
    tempo = [d for d in n.derivados if d.tipo == "tempo_desde_conclusao"]
    assert [(d.formacao, d.valor) for d in tempo] == [(1, 6)]


def test_um_ano_singular_e_zero_nada():
    assert "Há 1 ano desde essa conclusão." in _textos(montar(_maria()))
    recente = cn.entrada([cn.fato(curso="A", ano_conclusao=2026,
                                  data_conclusao=date(2026, 3, 1))])
    assert not any(t.startswith("Há ") for t in _textos(montar(recente)))


def test_referencia_anterior_a_conclusao_nada():
    futura = cn.entrada([cn.fato(curso="A", ano_conclusao=2027,
                                 data_conclusao=date(2027, 1, 1))])
    assert not any(t.startswith("Há ") for t in _textos(montar(futura)))


# --- Ausências (FR-017, FR-021) -----------------------------------------------------------


def test_sem_unidade_usa_variante():
    n = montar(cn.entrada([cn.fato(curso="A", ano_conclusao=2019)]))
    assert "Em 2019, você concluiu A." in _textos(n)
    assert not any("unidade" in t for t in _textos(n))


def test_sem_ano_e_so_curso():
    assert "Você concluiu A na unidade Serra." in _textos(
        montar(cn.entrada([cn.fato(curso="A", unidade="Serra")]))
    )
    assert "Você concluiu A." in _textos(montar(cn.entrada([cn.fato(curso="A")])))


def test_nada_de_marcadores_de_ausencia():
    for entrada in cn.entradas_dos_cenarios().values():
        for texto in _textos(montar(entrada)):
            assert "—" not in texto and "não informado" not in texto.lower()
            assert "None" not in texto


def test_atributos_so_os_informados():
    n = montar(_maria())
    atributos = [f.texto for s in n.secoes for f in s.frases if f.tipo == "atributos"]
    assert atributos == ["Graduação · Presencial", "Pós-graduação · A distância"]


# --- Nome (FR-025) ------------------------------------------------------------------------


def test_sem_nome_nenhuma_frase_com_nome():
    n = montar(cn.entradas_dos_cenarios()["SIM-P-0009"])
    assert n.nome is None
    assert not any(t.startswith("Registros de") for t in _textos(n))


def test_nome_so_em_registros():
    n = montar(_maria())
    com_nome = [t for t in _textos(n) if "Maria Exemplo" in t]
    assert com_nome == ["Registros de Maria Exemplo"]


# --- Pessoa do acervo histórico (019): mínima, sem nome nem curso -------------------------


def test_pessoa_do_acervo():
    n = montar(cn.entrada([cn.fato(unidade="Serra", nivel="Técnico", ano_conclusao=2004)]))
    textos = _textos(n)
    assert "O Ifes registra 1 formação concluída por você." in textos
    assert "Concluída em 2004." in textos
    assert "Serra · Técnico" in textos
    assert not any("concluiu" in t for t in textos)


# --- Derivados e P1 sem ingresso ----------------------------------------------------------


def test_formacoes_registradas():
    n = montar(_diego())
    assert "O Ifes registra 3 formações concluídas por você." in _textos(n)
    assert [d.valor for d in n.derivados if d.tipo == "formacoes_registradas"] == [3]


def test_p1_sem_ingresso():
    assert not any("começou" in t for e in cn.entradas_dos_cenarios().values()
                   for t in _textos(montar(e)))


# --- Compartilhável (FR-033; card) --------------------------------------------------------


def test_compartilhavel_conservador():
    n = montar(_maria())
    dados = json.dumps(serializar(n)["compartilhavel"], ensure_ascii=False)
    assert "Maria Exemplo" not in dados and "Presencial" in dados
    assert "2025-03-28" not in dados and "Há " not in dados
    assert n.compartilhavel.nome_disponivel


def test_compartilhavel_ate_quatro_e_omitidas():
    entrada = cn.entrada([cn.fato(curso=f"Curso {i}", ano_conclusao=2010 + i) for i in range(5)])
    c = montar(entrada).compartilhavel
    assert len(c.formacoes) == 4 and c.formacoes_omitidas == 1 and c.formacoes_registradas == 5


def test_compartilhavel_linhas_da_quebra_do_card():
    c = montar(_maria()).compartilhavel
    assert c.formacoes[0].linhas_curso == card.quebrar_linhas(
        TADS, card.TAMANHO_CURSO, True, card.LIMITE_ITEM
    )
    # O ano vai no nó da linha do tempo, não no detalhe (FR-077).
    assert c.formacoes[0].linhas_detalhe == ("Serra · Graduação · Presencial",)
    assert c.unidade_da_imagem == "Serra" and c.apuracao is None


def test_compartilhavel_sem_forma_de_oferta():
    c = montar(cn.entradas_dos_cenarios()["SIM-P-0004"]).compartilhavel
    assert not any("Integrado" in linha for f in c.formacoes for linha in f.linhas_detalhe)


# --- Determinismo e pureza (FR-011) -------------------------------------------------------


@pytest.mark.parametrize("id_externo", sorted(cn.entradas_dos_cenarios()))
def test_deterministico(id_externo):
    entrada = cn.entradas_dos_cenarios()[id_externo]
    assert json.dumps(serializar(montar(entrada)), ensure_ascii=False) == json.dumps(
        serializar(montar(entrada)), ensure_ascii=False
    )


def test_nao_usa_relogio(monkeypatch):
    def proibido():
        raise AssertionError("montar não lê o relógio")

    monkeypatch.setattr("django.utils.timezone.now", proibido)
    montar(_maria())


def test_secoes_em_ordem_e_sem_vazias():
    n = montar(_maria())
    assert [s.chave for s in n.secoes] == [
        "o_que_o_ifes_registra", "trajetoria_academica", "outras_formacoes",
    ]
    assert all(s.frases for s in n.secoes)
    assert catalogo.TITULOS_DAS_SECOES["trajetoria_academica"] == n.secoes[1].titulo

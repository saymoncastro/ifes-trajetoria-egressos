"""Fidelidade da baseline ao Formulário Egresso Ifes 2024 (specs/003, US2, US3, US5, US6,
US7, US9).

O oráculo é o manifesto de `formulario_2024_esperado.py` (transcrito da Matriz da spec) e
o inventário lido como texto bruto. A declaração não é usada como expectativa, exceto no
teste de coerência da própria declaração (US3).
"""

# As fixtures do manifesto são importadas pelo nome; o parâmetro do teste as "redefine".
# ruff: noqa: F401, F811

import dataclasses
import re
from collections import Counter

import pytest

from tests.instrumento.formulario_2024_esperado import (
    CONTAGENS,
    ESPERADO,
    LISTAS,
    ROTULOS_FINAIS,
    SECOES_ESPERADAS,
    TEXTOS_EXPLICATIVOS,
    baseline,
    inventario_bruto,
    normalizado,
    perguntas_por_chave,
    secao_da_pergunta,
    textos,
)
from trajetoria.formulario_2024 import declaracao as d
from trajetoria.instrumento.conteudo import ConteudoOpcao
from trajetoria.instrumento.models import Opcao, Pergunta, Secao, TipoPergunta

pytestmark = pytest.mark.django_db

CONCORDO = "Concordo totalmente"


# --- US2: conteúdo integral -------------------------------------------------------------


def test_secoes(baseline):
    obtidas = tuple(
        (f"S{n}", s.titulo, s.texto is not None, len(s.perguntas))
        for n, s in enumerate(baseline.secoes, 1)
    )
    assert obtidas == SECOES_ESPERADAS


def test_textos_da_versao_e_dos_termos(baseline, inventario_bruto):
    assert baseline.titulo == "Egresso Ifes"
    abertura = baseline.texto_abertura.split("\n\n")
    encerramento = baseline.texto_encerramento.split("\n\n")
    termos = baseline.secoes[0].texto.split("\n\n")
    assert (len(abertura), len(encerramento), len(termos)) == (4, 2, 2)
    assert encerramento[0] == "Este formulário chegou ao fim!"
    for texto in (baseline.texto_abertura, baseline.secoes[0].texto, *abertura, *termos,
                  *encerramento):
        # O texto inteiro, e não só cada parágrafo, protege a ordem dos parágrafos.
        assert normalizado(texto) in inventario_bruto, texto[:60]


def test_perguntas_conforme_a_matriz(baseline, inventario_bruto):
    perguntas = perguntas_por_chave(baseline)
    secao = secao_da_pergunta(baseline)
    assert list(perguntas) == list(ESPERADO)

    diferencas = []
    for chave, (sn, posicao, tipo, obrigatoria, trecho, opcoes) in ESPERADO.items():
        p = perguntas[chave]
        obtido = (secao[chave], p.posicao, p.tipo, p.obrigatoria)
        if obtido != (sn, posicao, tipo, obrigatoria):
            diferencas.append((chave, obtido))
        # O trecho identifica a pergunta: só ela (e as de texto idêntico) o contém (C1).
        com_trecho = {c for c, q in perguntas.items() if trecho in q.texto}
        mesmo_trecho = {c for c, e in ESPERADO.items() if e[4] == trecho}
        if com_trecho != mesmo_trecho:
            diferencas.append((chave, "trecho", sorted(com_trecho)))
        textos_opcoes = tuple(o.texto for o in p.opcoes)
        if isinstance(opcoes, str):
            quantidade, primeiro, ultimo = LISTAS[opcoes]
            # Fatias, não índices: lista vazia vira diferença, não IndexError.
            if (len(textos_opcoes), textos_opcoes[:1], textos_opcoes[-1:]) != (
                quantidade, (primeiro,), (ultimo,)
            ):
                diferencas.append((chave, opcoes, len(textos_opcoes)))
            # Sequência completa documentada no inventário: perda, troca de ordem ou
            # alteração de qualquer item quebra a ocorrência literal.
            if "; ".join(textos_opcoes) not in inventario_bruto:
                diferencas.append((chave, opcoes, "sequência não documentada"))
        elif textos_opcoes != opcoes:
            diferencas.append((chave, textos_opcoes))
    assert diferencas == []


def test_listas_iguais_sao_opcoes_proprias(baseline):
    perguntas = perguntas_por_chave(baseline)
    q8, q9 = perguntas["Q8"].opcoes, perguntas["Q9"].opcoes
    assert [o.texto for o in q8] == [o.texto for o in q9]
    assert not {o.id for o in q8} & {o.id for o in q9}


def test_contagens(baseline):
    perguntas = [p for s in baseline.secoes for p in s.perguntas]
    opcoes = [o for p in perguntas for o in p.opcoes]
    tipos = Counter(p.tipo for p in perguntas)
    obtidas = {
        "secoes": len(baseline.secoes),
        "perguntas": len(perguntas),
        **{tipo: tipos[tipo] for tipo in ("ESCOLHA_UNICA", "ESCOLHA_MULTIPLA",
                                          "TEXTO_CURTO", "ESCALA")},
        "obrigatorias": sum(p.obrigatoria for p in perguntas),
        "opcionais": sum(not p.obrigatoria for p in perguntas),
        "perguntas_com_opcoes": sum(bool(p.opcoes) for p in perguntas),
        "opcoes": len(opcoes),
        "opcoes_com_complemento": sum(o.complemento_textual for o in opcoes),
        "perguntas_com_texto_explicativo": sum(
            p.texto_explicativo is not None for p in perguntas
        ),
        "secoes_com_texto": sum(s.texto is not None for s in baseline.secoes),
        "secoes_sem_titulo": sum(s.titulo is None for s in baseline.secoes),
    }
    assert obtidas == CONTAGENS


def test_todo_texto_esta_documentado_no_inventario(baseline, inventario_bruto):
    # Sem exceção explícita: o rótulo corrigido de Q52–Q54 (E-08) passa porque "Concordo
    # totalmente" também consta do inventário, nas demais escalas. A correção em si é
    # verificada em test_correcao_editorial_somente_em_q52_a_q54.
    nao_documentados = [t for t in textos(baseline) if normalizado(t) not in inventario_bruto]
    assert nao_documentados == []


def test_escalas(baseline):
    perguntas = perguntas_por_chave(baseline)
    escalas = {c: p.escala for c, p in perguntas.items() if p.escala is not None}
    assert set(escalas) == set(ROTULOS_FINAIS)
    for chave, escala in escalas.items():
        assert (escala.inicio, escala.fim) == (1, 5), chave
        # E-09, DP-301: rótulo inicial ausente, nunca inferido nem vazio.
        assert escala.rotulo_inicio is None, chave
        assert escala.rotulo_fim == ROTULOS_FINAIS[chave], chave


def test_textos_explicativos(baseline):
    obtidos = {
        c: p.texto_explicativo
        for c, p in perguntas_por_chave(baseline).items()
        if p.texto_explicativo is not None
    }
    assert obtidos == TEXTOS_EXPLICATIVOS


def test_complemento_textual_so_no_outro(baseline):
    com_complemento = {
        (c, o.texto, o.posicao == len(p.opcoes))
        for c, p in perguntas_por_chave(baseline).items()
        for o in p.opcoes
        if o.complemento_textual
    }
    assert com_complemento == {("Q26", "Outro:", True), ("Q32", "Outro:", True),
                               ("Q45", "Outro:", True)}


# --- US3: rastreabilidade Q1–Q54 -------------------------------------------------------


def test_coerencia_da_declaracao():
    secoes = d.SECOES
    chaves_secoes = [s.chave for s in secoes]
    chaves_perguntas = [p.chave for s in secoes for p in s.perguntas]
    assert chaves_secoes == [f"S{n}" for n in range(1, 14)]
    assert chaves_perguntas == [f"Q{n}" for n in range(1, 55)]

    posicao = {chave: n for n, chave in enumerate(chaves_secoes, 1)}
    escolha = {TipoPergunta.ESCOLHA_UNICA, TipoPergunta.ESCOLHA_MULTIPLA}
    for n, s in enumerate(secoes, 1):
        if s.encaminhamento:
            assert posicao[s.encaminhamento] > n, s.chave
        for p in s.perguntas:
            assert (p.escala is not None) == (p.tipo == TipoPergunta.ESCALA), p.chave
            assert bool(p.opcoes) == (p.tipo in escolha), p.chave
            assert p.complemento is None or p.complemento in p.opcoes, p.chave
            for texto, destino in p.regras:
                assert texto in p.opcoes, p.chave
                assert destino is d.FINALIZAR or posicao[destino] > n, p.chave


def test_n_esima_pergunta_e_qn(baseline):
    declaradas = {p.chave: p for s in d.SECOES for p in s.perguntas}
    perguntas = perguntas_por_chave(baseline)
    assert list(perguntas) == list(declaradas)
    assert all(perguntas[c].texto == declaradas[c].texto for c in perguntas)


def test_identificadores_legados_nao_sao_persistidos(baseline):
    com_identificador = [t for t in textos(baseline) if re.search(r"\b[QS]\d{1,2}\b", t)]
    assert com_identificador == []


def test_modelos_da_002_sem_campo_legado():
    campos = {
        modelo.__name__: {f.name for f in modelo._meta.concrete_fields}
        for modelo in (Secao, Pergunta, Opcao)
    }
    assert campos == {
        "Secao": {"id", "versao", "posicao", "titulo", "texto", "encaminhamento"},
        "Pergunta": {
            "id", "secao", "posicao", "tipo", "texto", "texto_explicativo", "obrigatoria",
            "escala_inicio", "escala_fim", "escala_rotulo_inicio", "escala_rotulo_fim",
        },
        "Opcao": {
            "id", "pergunta", "posicao", "texto", "complemento_textual", "regra_destino",
            "regra_finaliza",
        },
    }


# --- US5: notas internas não migradas ---------------------------------------------------

NOTAS_INTERNAS = ("Tem que atualizar a lista de cursos", "Verificar lugar dessa pergunta")


def test_notas_internas_nao_migradas(baseline, inventario_bruto):
    for nota in NOTAS_INTERNAS:
        assert nota in inventario_bruto  # existem no original (O-3)
        assert not [t for t in textos(baseline) if nota in t], nota  # E-05, E-06

    perguntas = perguntas_por_chave(baseline)
    assert baseline.secoes[6].texto is None  # S7
    assert perguntas["Q41"].texto_explicativo is None
    assert (secao_da_pergunta(baseline)["Q41"], perguntas["Q41"].posicao) == ("S9", 8)
    assert len(perguntas["Q19"].opcoes) == 77  # nenhum curso acrescentado (E-05, DP-310)


def test_nada_mais_excluido_como_editorial(baseline):
    assert [n for n, s in enumerate(baseline.secoes, 1) if s.texto is not None] == [1]
    com_explicativo = {
        c for c, p in perguntas_por_chave(baseline).items() if p.texto_explicativo is not None
    }
    assert com_explicativo == {"Q10", "Q32", "Q48"}


# --- US6: correção editorial E-08 -------------------------------------------------------


def test_correcao_editorial_somente_em_q52_a_q54(baseline, inventario_bruto):
    perguntas = perguntas_por_chave(baseline)
    assert "Corcordo totalmente" in inventario_bruto  # a grafia do original é conhecida
    for chave in ("Q52", "Q53", "Q54"):
        assert perguntas[chave].escala.rotulo_fim == CONCORDO, chave
    assert not [t for t in textos(baseline) if "Corcordo" in t]

    rotulos = Counter(p.escala.rotulo_fim for p in perguntas.values() if p.escala)
    assert rotulos == {CONCORDO: 10, "concordo totalmente": 1}  # E-10: Q48 minúsculo (U2)
    assert "auxilio estudantil" in perguntas["Q32"].texto_explicativo  # E-19


# --- US7: candidatas a contexto continuam perguntas comuns -----------------------------

CANDIDATAS = ("Q3", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19",
              "Q22", "Q23", "Q24", "Q27", "Q31", "Q32")


def test_candidatas_permanecem_perguntas_declaradas(baseline):
    perguntas = perguntas_por_chave(baseline)
    for chave in CANDIDATAS:
        assert perguntas[chave].obrigatoria, chave
    for chave in ("Q3", "Q10"):
        p = perguntas[chave]
        assert (p.tipo, p.opcoes, p.escala) == (TipoPergunta.TEXTO_CURTO, (), None), chave
    # Nenhum "perguntar só se a fonte não tiver": das candidatas, só Q14 tem regras, e são
    # as do ramo de cursos (test_regras).
    com_regras = {c for c in CANDIDATAS if any(o.regra for o in perguntas[c].opcoes)}
    assert com_regras == {"Q14"}


# --- US9: nenhuma revisão metodológica silenciosa --------------------------------------


def test_preservacoes_metodologicas(baseline):
    perguntas = perguntas_por_chave(baseline)

    def opcoes(chave):
        return [o.texto for o in perguntas[chave].opcoes]

    # DP-305: faixas de Q38 (limites sobrepostos) e Q39 (500 sem faixa).
    assert opcoes("Q38") == [
        "Até 1 salário mínimo", "De 1 até 2,5 salários mínimos",
        "De 2,5 até 5,5 salários mínimos", "De 5,5 até 10 salários mínimos",
        "Acima de 10 salários mínimos",
    ]
    assert "Média empresa/organização (de 100 a 499 colaboradores)" in opcoes("Q39")
    assert "Grande empresa/organização (acima de 500 colaboradores)" in opcoes("Q39")
    # DP-306: referência ao campus em Q40.
    assert all("campus" in texto for texto in opcoes("Q40")[:3])
    # DP-307: Q13 com as três Opções originais.
    assert len(opcoes("Q13")) == 3
    # DP-303: Q6 logo após Q5, opcional, sem regra; S2 sem regras.
    q6 = perguntas["Q6"]
    assert (secao_da_pergunta(baseline)["Q6"], q6.posicao, q6.obrigatoria) == ("S2", 5, False)
    assert not any(o.regra for p in baseline.secoes[1].perguntas for o in p.opcoes)
    # DP-304: Q42 e Q44 opcionais, Q43 obrigatória.
    assert [perguntas[c].obrigatoria for c in ("Q42", "Q43", "Q44")] == [False, True, False]
    # DP-309: só Q2 tem "Prefiro não responder"; Q4, Q5 e Q7 obrigatórias.
    assert "Prefiro não responder" in opcoes("Q2")
    for chave in ("Q4", "Q5", "Q7"):
        assert perguntas[chave].obrigatoria and "Prefiro não responder" not in opcoes(chave)
    # 002/DP-005: nenhuma marca de exclusividade na Opção ("Não houve", "Não recebi"…).
    assert {f.name for f in dataclasses.fields(ConteudoOpcao)} == {
        "id", "posicao", "texto", "complemento_textual", "regra"
    }

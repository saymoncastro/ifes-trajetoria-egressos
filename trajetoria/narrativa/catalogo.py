"""Catálogo fechado de formulações da narrativa (Feature 021; contracts/catalogo.md).

Toda frase da página e do card sai daqui, preenchida só com valores presentes na narrativa
(FR-022). O texto pode ser revisto sem mudar comportamento: a linguagem definitiva é
008/DP-801. A unidade é escrita como a fonte a informa, sempre "na unidade {unidade}", nunca
com "Campus" acrescentado (FR-017). Contagens agregadas têm sempre "conclusões" como sujeito,
nunca pessoas (FR-061).
"""

TITULO = "Minha trajetória no Ifes"

TITULOS_DAS_SECOES = {
    "o_que_o_ifes_registra": "O que o Ifes registra sobre você",
    "trajetoria_academica": "Sua trajetória acadêmica",
    "outras_formacoes": "Outras formações no Ifes",
    "naquele_ano": "Naquele ano no Ifes",
}
TITULO_DO_CARD = "Seu card"

# P1 — pares (singular, plural) escolhidos por `plural`.
REGISTRADAS = (
    "O Ifes registra {n} formação concluída por você.",
    "O Ifes registra {n} formações concluídas por você.",
)
NOME_REGISTROS = "Registros de {nome}"
CONCLUIU_COMPLETO = "Em {ano}, você concluiu {curso} na unidade {unidade}."
CONCLUIU_SEM_UNIDADE = "Em {ano}, você concluiu {curso}."
CONCLUIU_SEM_ANO = "Você concluiu {curso} na unidade {unidade}."
CONCLUIU_SO_CURSO = "Você concluiu {curso}."
DEPOIS = "Depois dessa formação, você também concluiu {curso}."
HA_ANOS = ("Há {n} ano desde essa conclusão.", "Há {n} anos desde essa conclusão.")
CONCLUIDA_EM = "Concluída em {ano}."
CARD_MAIS = ("e mais {n} formação registrada", "e mais {n} formações registradas")
CARD_REGISTRADAS = ("{n} formação registrada no Ifes", "{n} formações registradas no Ifes")
CARD_RODAPE = "Instituto Federal do Espírito Santo"
CARD_DEMO = "Demonstração — dados fictícios"

# P2.
INICIO = "Sua trajetória no Ifes começou em {ano}, em {curso}."
AGREGADO_CURSO = (
    "Em {ano}, {n} conclusão de {curso} foi registrada na unidade {unidade}: a sua.",
    "Em {ano}, {n} conclusões de {curso} foram registradas na unidade {unidade}, incluindo a "
    "sua.",
)
AGREGADO_UNIDADE = (
    "Em {ano}, {n} conclusão foi registrada na unidade {unidade}.",
    "Em {ano}, {n} conclusões foram registradas na unidade {unidade}.",
)
APURACAO = "Dados institucionais apurados em {apuracao}."

FORMULACOES = (
    *REGISTRADAS, NOME_REGISTROS, CONCLUIU_COMPLETO, CONCLUIU_SEM_UNIDADE, CONCLUIU_SEM_ANO,
    CONCLUIU_SO_CURSO, DEPOIS, *HA_ANOS, CONCLUIDA_EM, *CARD_MAIS, *CARD_REGISTRADAS,
    CARD_RODAPE, CARD_DEMO, INICIO, *AGREGADO_CURSO, *AGREGADO_UNIDADE, APURACAO,
)

# Rede de segurança contra o erro grosseiro (contracts/catalogo.md). A garantia principal é
# que toda frase emitida seja uma formulação acima.
VEDADAS = (
    "tudo começou", "turma", "geração", "coorte", "colegas", "se formaram com você",
    "formaram com você", "matriculad", "ingressantes", "estudantes", "alunos", "egressos",
    "%", "taxa", "mais que", "melhores", "entre os", "época especial", "viveu", "verticaliza",
)


def plural(par: tuple[str, str], n: int) -> str:
    return par[0] if n == 1 else par[1]

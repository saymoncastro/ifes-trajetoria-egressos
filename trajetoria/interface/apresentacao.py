"""Apresentação do contexto institucional da formação (008 data-model §3).

O contexto vem da Conclusão Acadêmica (001), é **institucional** e só é exibido: nunca
vira Resposta, valor inicial de campo ou sugestão (FR-028). Atributo não informado pela
fonte é omitido; nada é deduzido nem inventado (FR-026; 007/DP-702).
"""

from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.percurso import maximo_restante
from trajetoria.participacao.regras import ParticipacaoRejeitada


def contexto_da_formacao(conclusao) -> list[tuple[str, str]]:
    """Pares (rótulo, valor) só para os atributos informados, na ordem: curso, unidade,
    ano (ou data) de conclusão, nível, modalidade, forma de oferta."""
    pares = [("Curso", conclusao.curso), ("Unidade", conclusao.unidade)]
    if getattr(conclusao, "data_conclusao", None) is not None:
        pares.append(
            ("Data de conclusão", getattr(conclusao, "data_conclusao", None).strftime("%d/%m/%Y"))
        )
    elif conclusao.ano_conclusao is not None:
        pares.append(("Ano de conclusão", str(conclusao.ano_conclusao)))
    pares += [
        ("Nível", conclusao.nivel),
        ("Modalidade", getattr(conclusao, "modalidade", None)),
        ("Forma de oferta", getattr(conclusao, "forma_oferta", None)),
    ]
    return [(rotulo, valor) for rotulo, valor in pares if valor is not None]


def resumo_da_formacao(conclusao) -> str:
    """Uma linha "curso · unidade · ano" com os atributos existentes, para distinguir
    formações (e homônimos) na entrada de demonstração e como contexto compacto nas telas de
    Seção. Vazio se nada foi informado."""
    ano = conclusao.ano_conclusao
    if ano is None and getattr(conclusao, "data_conclusao", None) is not None:
        ano = getattr(conclusao, "data_conclusao", None).year
    partes = (conclusao.curso, conclusao.unidade, None if ano is None else str(ano))
    return " · ".join(p for p in partes if p)


def complemento_da_formacao(conclusao) -> str:
    """Linha complementar da formação na trajetória (014 FR-034): nível · modalidade · forma
    de oferta, só os informados. Vazio se nada foi informado. Sem desempate entre formações
    nem atributo deduzido (007/DP-702)."""
    partes = (
        conclusao.nivel,
        getattr(conclusao, "modalidade", None),
        getattr(conclusao, "forma_oferta", None),
    )
    return " · ".join(p for p in partes if p)


def formacao_exibida(participacao):
    """Contexto sempre pela âncora original; nunca pela decisão posterior."""
    return participacao.conclusao if participacao.conclusao_id else participacao.formacao_declarada


def conclusao_efetiva(participacao):
    """A Conclusão observada: a âncora institucional ou a vinculada pela validação (019).
    Só para Participação oficial; nunca para declaração pendente."""
    if participacao.conclusao_id:
        return participacao.conclusao
    return participacao.formacao_declarada.validacao.conclusao


def rotulo_da_formacao_declarada():
    return "Formação informada por você"


def rotulo_da_formacao(participacao):
    return "Sobre a sua formação" if participacao.conclusao_id else rotulo_da_formacao_declarada()


# --- 023: parte, máximo restante e "você parou em" (FR-013, FR-015, FR-017) ------------------


def rotulo_da_secao(secao, parte: int) -> str:
    """Título da Seção ou "Parte X" (FR-015): nunca "Seção {posição}", número interno."""
    return secao.titulo or f"Parte {parte}"


def _restantes(maximo: int) -> str:
    if maximo == 0:
        return "última parte"
    return "falta no máximo 1 parte" if maximo == 1 else f"faltam no máximo {maximo} partes"


def linha_da_parte(parte: int, maximo: int) -> str:
    """ "Parte 4 · faltam no máximo 4 partes" (FR-013): nunca percentual nem tempo."""
    return f"Parte {parte} · {_restantes(maximo)}"


def onde_parou(jornada) -> str:
    """Onde a pessoa parou numa Participação em rascunho (FR-017), pela jornada da 006."""
    if jornada.finalizada:
        return "Falta só concluir."
    secao = jornada.secao_atual
    parte = len(jornada.passagens)
    lugar = (
        f"Você parou em «{secao.titulo}»" if secao.titulo else f"Você parou na parte {parte}"
    )
    maximo = maximo_restante(jornada.conteudo, secao.id)
    resto = "é a última parte" if maximo == 0 else _restantes(maximo)
    return f"{lugar} · {resto}."


def onde_parou_da_participacao(participacao) -> str | None:
    """"Você parou em…" de uma Participação em rascunho (FR-017), para as formações e para a
    lista do declarante; nada quando a estrutura está fora da capacidade da 006."""
    try:
        return onde_parou(situacao_da_jornada(participacao))
    except ParticipacaoRejeitada:
        return None

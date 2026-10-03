"""Apresentação do contexto institucional da formação (008 data-model §3).

O contexto vem da Conclusão Acadêmica (001), é **institucional** e só é exibido: nunca
vira Resposta, valor inicial de campo ou sugestão (FR-028). Atributo não informado pela
fonte é omitido; nada é deduzido nem inventado (FR-026; 007/DP-702).
"""


def contexto_da_formacao(conclusao) -> list[tuple[str, str]]:
    """Pares (rótulo, valor) só para os atributos informados, na ordem: curso, unidade,
    ano (ou data) de conclusão, nível, modalidade, forma de oferta."""
    pares = [("Curso", conclusao.curso), ("Unidade", conclusao.unidade)]
    if conclusao.data_conclusao is not None:
        pares.append(("Data de conclusão", conclusao.data_conclusao.strftime("%d/%m/%Y")))
    elif conclusao.ano_conclusao is not None:
        pares.append(("Ano de conclusão", str(conclusao.ano_conclusao)))
    pares += [
        ("Nível", conclusao.nivel),
        ("Modalidade", conclusao.modalidade),
        ("Forma de oferta", conclusao.forma_oferta),
    ]
    return [(rotulo, valor) for rotulo, valor in pares if valor is not None]


def resumo_da_formacao(conclusao) -> str:
    """Uma linha "curso · unidade · ano" com os atributos existentes, para distinguir
    formações (e homônimos) na entrada de demonstração e como contexto compacto nas telas de
    Seção. Vazio se nada foi informado."""
    ano = conclusao.ano_conclusao
    if ano is None and conclusao.data_conclusao is not None:
        ano = conclusao.data_conclusao.year
    partes = (conclusao.curso, conclusao.unidade, None if ano is None else str(ano))
    return " · ".join(p for p in partes if p)


def complemento_da_formacao(conclusao) -> str:
    """Linha complementar da formação na trajetória (014 FR-034): nível · modalidade · forma
    de oferta, só os informados. Vazio se nada foi informado. Sem desempate entre formações
    nem atributo deduzido (007/DP-702)."""
    partes = (conclusao.nivel, conclusao.modalidade, conclusao.forma_oferta)
    return " · ".join(p for p in partes if p)

"""Pertinência e explicação (025 FR-011 a FR-016; research R7; contracts/pertinencia.md).

Funções puras: não leem o relógio, não consultam o banco além do que recebem, não gravam.
Todos os critérios definidos precisam valer **na mesma Conclusão**, por igualdade exata;
`NULL` na Conclusão não satisfaz. A explicação cita, em cada formação, o valor satisfeito
de cada critério definido.
"""

from dataclasses import dataclass

from trajetoria.portal.models import Categoria
from trajetoria.portal.oportunidades import mensagens
from trajetoria.portal.oportunidades.regras import origem_do_site

FORMACAO, TODOS = "formacao", "todos"

# (critério da Oportunidade, atributo da Conclusão)
_CRITERIOS = (
    ("publico_cursos", "curso"),
    ("publico_niveis", "nivel"),
    ("publico_unidades", "unidade"),
)


@dataclass(frozen=True)
class Item:
    oportunidade: object
    grupo: str
    formacoes: tuple
    explicacao: str
    categoria: str
    oferecida: str
    do_ifes: bool
    dominio: str

    @property
    def origem_do_site(self) -> str:
        return mensagens.SITE_DO_IFES if self.do_ifes else mensagens.SITE_EXTERNO


def satisfaz(oportunidade, conclusao) -> bool:
    for criterio, atributo in _CRITERIOS:
        valores = getattr(oportunidade, criterio)
        if valores is not None and getattr(conclusao, atributo) not in valores:
            return False
    return True


def _juntar(partes: list[str]) -> str:
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " e " + partes[-1]


def _descrever(oportunidade, conclusao) -> str:
    texto = conclusao.curso or mensagens.UMA_FORMACAO
    if oportunidade.publico_niveis is not None and conclusao.nivel:
        texto += mensagens.FORMACAO_DE_NIVEL.format(nivel=conclusao.nivel)
    com_unidade = oportunidade.publico_unidades is not None
    if com_unidade and conclusao.unidade:
        texto += mensagens.NA_UNIDADE.format(unidade=conclusao.unidade)
    dados = [str(conclusao.ano_conclusao)] if conclusao.ano_conclusao else []
    if not com_unidade and conclusao.unidade:
        dados.insert(0, conclusao.unidade)
    return f"{texto} ({', '.join(dados)})" if dados else texto


def explicacao(oportunidade, formacoes) -> str:
    """Modelos de contracts/pertinencia.md. Nenhum dado além da Conclusão; nenhum texto
    livre do operador (FR-013)."""
    if not oportunidade.tem_publico:
        return mensagens.ABERTA_A_TODOS
    return mensagens.APARECE_PORQUE.format(
        formacoes=_juntar([_descrever(oportunidade, c) for c in formacoes])
    )


def oferecida(oportunidade) -> str:
    if oportunidade.institucional:
        return mensagens.OFERECIDA_PELO_IFES
    return mensagens.OFERECIDA_PELA_UNIDADE.format(unidade=oportunidade.unidade_responsavel)


def _item(oportunidade, grupo: str, formacoes: tuple) -> Item:
    do_ifes, dominio = origem_do_site(oportunidade.endereco)
    return Item(
        oportunidade=oportunidade,
        grupo=grupo,
        formacoes=formacoes,
        explicacao=explicacao(oportunidade, formacoes),
        categoria=Categoria(oportunidade.categoria).label,
        oferecida=oferecida(oportunidade),
        do_ifes=do_ifes,
        dominio=dominio,
    )


def pertinentes(oportunidades, conclusoes) -> list[Item]:
    """Itens para a Pessoa, na ordem do FR-016. `conclusoes` chega na ordem da 007.

    Sem Conclusão, nada (FR-011). Cada oportunidade aparece no máximo uma vez."""
    conclusoes = tuple(conclusoes)
    if not conclusoes:
        return []
    itens = []
    for oportunidade in oportunidades:
        if not oportunidade.tem_publico:
            itens.append(_item(oportunidade, TODOS, ()))
            continue
        formacoes = tuple(c for c in conclusoes if satisfaz(oportunidade, c))
        if formacoes:
            itens.append(_item(oportunidade, FORMACAO, formacoes))
    return sorted(
        itens,
        key=lambda i: (
            i.grupo != FORMACAO,
            -i.oportunidade.inicio.toordinal(),
            i.oportunidade.titulo,
            str(i.oportunidade.pk),
        ),
    )

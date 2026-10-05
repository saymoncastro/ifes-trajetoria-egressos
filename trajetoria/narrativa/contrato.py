"""Contrato da narrativa "Minha trajetória no Ifes" (Feature 021; contracts/narrativa.md).

Python puro: nem Django nem banco. `EntradaDaNarrativa` traz os fatos já lidos (valores, não
models); `TrajetoriaNarrativa` é o que a página, o card e, futuramente, o renderer de vídeo
(Feature 022) consomem. Nada aqui é persistido (FR-015). `serializar` produz a forma JSON
estável, versão 1: ausência é omitida, nunca `null`.
"""

from dataclasses import dataclass, field
from datetime import date

VERSAO_CONTRATO = 1

INSTITUCIONAL, DERIVADO, AGREGADO = "institucional", "derivado", "agregado"

# As duas métricas fechadas do contexto agregado (FR-053), pelos mesmos valores da
# capacidade de contexto da trajetória (P2).
METRICA_CURSO_UNIDADE_ANO = "conclusoes_curso_unidade_ano"
METRICA_UNIDADE_ANO = "conclusoes_unidade_ano"


# --- Entrada ------------------------------------------------------------------------------


@dataclass(frozen=True)
class FatoDaFormacao:
    """Uma Conclusão Acadêmica como valores: só o contexto e, em P2, o ingresso. Sem
    identificadores técnicos nem de fonte (FR-013)."""

    curso: str | None = None
    unidade: str | None = None
    nivel: str | None = None
    modalidade: str | None = None
    forma_oferta: str | None = None
    ano_conclusao: int | None = None
    data_conclusao: date | None = None
    ingresso_ano: int | None = None
    ingresso_data: date | None = None


@dataclass(frozen=True)
class ContextoSelecionado:
    """Agregado institucional já selecionado (FR-058 a FR-060), ligado à formação que o
    sustenta pelo índice na entrada."""

    metrica: str
    unidade: str
    ano: int
    valor: int
    apurado_em: date
    formacao: int
    curso: str | None = None


@dataclass(frozen=True)
class EntradaDaNarrativa:
    nome: str | None
    formacoes: tuple[FatoDaFormacao, ...]
    agregados: tuple[ContextoSelecionado, ...]
    referencia: date
    demonstracao: bool


# --- Saída --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Relacao:
    tipo: str
    indice: int


@dataclass(frozen=True)
class Formacao:
    curso: str | None = None
    unidade: str | None = None
    nivel: str | None = None
    modalidade: str | None = None
    forma_oferta: str | None = None
    ano_conclusao: int | None = None
    data_conclusao: date | None = None
    relacao: Relacao | None = None
    ingresso_ano: int | None = None
    ingresso_data: date | None = None


@dataclass(frozen=True)
class Derivado:
    tipo: str
    valor: int
    regra: str
    formacao: int | None = None


@dataclass(frozen=True)
class ContextoAgregado:
    metrica: str
    unidade: str
    ano: int
    valor: int
    apurado_em: date
    curso: str | None = None


@dataclass(frozen=True)
class Frase:
    """Texto pronto. `tipo` "frase" vem do catálogo; "atributos" é só a junção dos atributos
    informados ("Graduação · Presencial"). `formacao` agrupa o texto na sua formação."""

    texto: str
    origem: str
    formacao: int | None = None
    tipo: str = "frase"


@dataclass(frozen=True)
class Secao:
    chave: str
    titulo: str
    frases: tuple[Frase, ...]


@dataclass(frozen=True)
class FormacaoCompartilhavel:
    curso: str | None
    unidade: str | None
    nivel: str | None
    modalidade: str | None
    ano_conclusao: int | None
    linhas_curso: tuple[str, ...]
    linhas_detalhe: tuple[str, ...]


@dataclass(frozen=True)
class ContextoCompartilhavel:
    texto: str
    linhas: tuple[str, ...]


@dataclass(frozen=True)
class Compartilhavel:
    """Subconjunto do card (FR-033). Sem nome: a rota o acrescenta por escolha (FR-034)."""

    formacoes: tuple[FormacaoCompartilhavel, ...]
    formacoes_omitidas: int
    formacoes_registradas: int
    contextos_agregados: tuple[ContextoCompartilhavel, ...]
    nome_disponivel: bool


@dataclass(frozen=True)
class TrajetoriaNarrativa:
    referencia: date
    nome: str | None
    formacoes: tuple[Formacao, ...]
    derivados: tuple[Derivado, ...]
    contextos_agregados: tuple[ContextoAgregado, ...]
    secoes: tuple[Secao, ...]
    compartilhavel: Compartilhavel
    marcos: tuple = field(default=())
    versao_contrato: int = VERSAO_CONTRATO

    def secao(self, chave: str) -> Secao | None:
        return next((s for s in self.secoes if s.chave == chave), None)


# --- Serialização -------------------------------------------------------------------------

_ATRIBUTOS = ("curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao")


def _valor(v):
    return v.isoformat() if isinstance(v, date) else v


def _sem_ausentes(pares) -> dict:
    return {chave: _valor(v) for chave, v in pares if v is not None}


def _formacao(f: Formacao) -> dict:
    dados = {"origem": INSTITUCIONAL}
    dados.update(_sem_ausentes((a, getattr(f, a)) for a in _ATRIBUTOS))
    dados.update(_sem_ausentes([("data_conclusao", f.data_conclusao)]))
    if f.ingresso_ano is not None:
        dados["ingresso"] = _sem_ausentes([("ano", f.ingresso_ano), ("data", f.ingresso_data)])
    if f.relacao is not None:
        dados["relacao"] = {"tipo": f.relacao.tipo, "indice": f.relacao.indice}
    return dados


def _contexto(c: ContextoAgregado) -> dict:
    return {
        "metrica": c.metrica,
        "recorte": _sem_ausentes([("curso", c.curso), ("unidade", c.unidade), ("ano", c.ano)]),
        "valor": c.valor,
        "apurado_em": c.apurado_em.isoformat(),
        "origem": AGREGADO,
    }


def serializar(n: TrajetoriaNarrativa) -> dict:
    return {
        "versao_contrato": n.versao_contrato,
        "referencia": n.referencia.isoformat(),
        "identidade": {} if n.nome is None else {"nome": n.nome, "origem": INSTITUCIONAL},
        "formacoes": [_formacao(f) for f in n.formacoes],
        "marcos": list(n.marcos),
        "derivados": [
            _sem_ausentes(
                [("tipo", d.tipo), ("formacao", d.formacao), ("valor", d.valor),
                 ("origem", DERIVADO), ("regra", d.regra)]
            )
            for d in n.derivados
        ],
        "contextos_agregados": [_contexto(c) for c in n.contextos_agregados],
        "secoes": [
            {
                "chave": s.chave,
                "titulo": s.titulo,
                "frases": [
                    _sem_ausentes(
                        [("texto", f.texto), ("origem", f.origem), ("formacao", f.formacao),
                         ("tipo", f.tipo)]
                    )
                    for f in s.frases
                ],
            }
            for s in n.secoes
        ],
        "compartilhavel": {
            "formacoes": [
                {
                    **_sem_ausentes(
                        (a, getattr(f, a))
                        for a in ("curso", "unidade", "nivel", "modalidade", "ano_conclusao")
                    ),
                    "linhas_curso": list(f.linhas_curso),
                    "linhas_detalhe": list(f.linhas_detalhe),
                }
                for f in n.compartilhavel.formacoes
            ],
            "formacoes_omitidas": n.compartilhavel.formacoes_omitidas,
            "formacoes_registradas": n.compartilhavel.formacoes_registradas,
            "contextos_agregados": [
                {"texto": c.texto, "linhas": list(c.linhas)}
                for c in n.compartilhavel.contextos_agregados
            ],
            "nome_disponivel": n.compartilhavel.nome_disponivel,
        },
    }

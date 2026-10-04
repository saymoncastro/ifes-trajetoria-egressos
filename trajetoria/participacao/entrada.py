"""Contextualização da formação e entrada na pesquisa (007 contracts/entrada.md).

Composição das Features 001, 004, 005 e 006, sem dado próprio: a partir de uma Pessoa já
resolvida (a identificação está fora do escopo — FR-001), lê suas Conclusões Acadêmicas
(001), as Campanhas aplicáveis a cada uma (004, `campanhas_em_coleta_para`) e a
Participação do par quando há exatamente uma Campanha (005/006). Daí deriva a situação
de cada formação e a resolução da entrada. A única escrita possível é a de
`iniciar_participacao` (005).

- A formação é a Conclusão Acadêmica; o egresso escolhe formação, nunca Campanha.
- Uma formação já concluída é informação, não alternativa de ação.
- Ambiguidade operacional (duas ou mais Campanhas aplicáveis) é local à formação e nunca
  é desempatada pelo estado de uma Participação (004/DP-404).
- `entrar` sempre reavalia a situação no seu próprio momento; não há token nem snapshot.

Origem dos dados: o contexto acadêmico é institucional e lido da própria Conclusão, nunca
copiado; nenhuma Resposta é criada (FR-040, FR-041). Nada é persistido além do que a 005
grava ao iniciar.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha.consultas import campanhas_em_coleta_para, momento_de_referencia
from trajetoria.campanha.models import Campanha
from trajetoria.participacao.consultas import participacoes_oficiais
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import SituacaoInicio, _exigir, iniciar_participacao

__all__ = [
    "Entrada",
    "Formacao",
    "FormacaoDeOutraPessoa",
    "ResolucaoDaEntrada",
    "SituacaoDaFormacao",
    "SituacaoDeEntrada",
    "entrar",
    "situacao_de_entrada",
]


class SituacaoDaFormacao(Enum):
    SEM_PESQUISA = "sem_pesquisa"  # nenhuma Campanha aplicável
    DISPONIVEL_PARA_INICIAR = "disponivel_para_iniciar"  # 1 Campanha, sem Participação
    DISPONIVEL_PARA_RETOMAR = "disponivel_para_retomar"  # 1 Campanha, rascunho
    JA_CONCLUIDA = "ja_concluida"  # 1 Campanha, Participação concluída
    AMBIGUIDADE_OPERACIONAL = "ambiguidade_operacional"  # 2+ Campanhas (004/DP-404)

    @property
    def pendente(self) -> bool:
        """Entrada pendente: a formação é alternativa de ação (iniciar ou retomar)."""
        return self in (
            SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR,
            SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR,
        )


@dataclass(frozen=True)
class Formacao:
    """Uma Conclusão Acadêmica da Pessoa e sua situação no momento de referência. O
    contexto (curso, unidade, nível, modalidade, forma de oferta, ano/data) é lido de
    `conclusao`, com `None` = não informado pela fonte; não há rótulo (DP-702)."""

    conclusao: ConclusaoAcademica
    situacao: SituacaoDaFormacao
    campanhas: tuple[Campanha, ...]  # aplicáveis, na ordem (inicio, id) da 004
    participacao: Participacao | None  # só em DISPONIVEL_PARA_RETOMAR e JA_CONCLUIDA

    @property
    def campanha(self) -> Campanha | None:
        """A única Campanha aplicável; `None` sem Campanha ou na ambiguidade."""
        return self.campanhas[0] if len(self.campanhas) == 1 else None


class ResolucaoDaEntrada(Enum):
    SEM_FORMACAO = "sem_formacao"
    SEM_PESQUISA = "sem_pesquisa"
    SEM_ENTRADA_PENDENTE = "sem_entrada_pendente"
    ENTRADA_RESOLVIDA = "entrada_resolvida"
    SELECAO_NECESSARIA = "selecao_necessaria"


@dataclass(frozen=True)
class SituacaoDeEntrada:
    """Todas as formações da Pessoa, qualquer que seja a situação (FR-017), e a resolução
    derivada delas. Valor de leitura, recalculado a cada chamada e nunca gravado."""

    formacoes: tuple[Formacao, ...]
    resolucao: ResolucaoDaEntrada

    @property
    def pendentes(self) -> tuple[Formacao, ...]:
        """As alternativas de ação, na ordem das formações. Em `ENTRADA_RESOLVIDA`, a
        formação resolvida é `pendentes[0]`."""
        return tuple(f for f in self.formacoes if f.situacao.pendente)


@dataclass(frozen=True)
class Entrada:
    """Resultado de `entrar`. Iniciada = `criada`; concluída = `concluida_em` preenchido;
    em rascunho = demais casos com Participação; não realizada = sem Participação, com o
    motivo em `situacao` (FR-034)."""

    situacao: SituacaoDeEntrada  # reavaliada no momento da entrada
    participacao: Participacao | None
    criada: bool


class FormacaoDeOutraPessoa(Exception):
    """A formação informada não é uma Conclusão desta Pessoa (FR-044): de outra Pessoa ou
    inexistente. Os dois casos são indistinguíveis de propósito, para que a rejeição não
    revele se um identificador é Conclusão de alguém; a mensagem não contém dados da
    Conclusão nem de outra Pessoa (FR-045)."""

    def __init__(self):
        super().__init__("a formação informada não pertence à Pessoa")


# --- Regras puras ---------------------------------------------------------------------------


def _classificar(
    conclusao: ConclusaoAcademica,
    campanhas: tuple[Campanha, ...],
    participacao: Participacao | None,
) -> Formacao:
    """Situação de uma formação, sem acesso ao banco (FR-014). Na ambiguidade, a
    Participação é descartada: seu estado nunca escolhe Campanha (FR-027)."""
    if not campanhas:
        return Formacao(conclusao, SituacaoDaFormacao.SEM_PESQUISA, (), None)
    if len(campanhas) > 1:
        return Formacao(conclusao, SituacaoDaFormacao.AMBIGUIDADE_OPERACIONAL, campanhas, None)
    if participacao is None:
        situacao = SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR
    elif participacao.concluida_em is None:
        situacao = SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR
    else:
        situacao = SituacaoDaFormacao.JA_CONCLUIDA
    return Formacao(conclusao, situacao, campanhas, participacao)


def _resolver(formacoes: tuple[Formacao, ...]) -> ResolucaoDaEntrada:
    """Resolução global (FR-018 a FR-023). Só formações pendentes contam como
    alternativas; concluídas e ambíguas são informadas, nunca contadas."""
    if not formacoes:
        return ResolucaoDaEntrada.SEM_FORMACAO
    pendentes = sum(f.situacao.pendente for f in formacoes)
    if pendentes == 1:
        return ResolucaoDaEntrada.ENTRADA_RESOLVIDA
    if pendentes > 1:
        return ResolucaoDaEntrada.SELECAO_NECESSARIA
    if all(f.situacao is SituacaoDaFormacao.SEM_PESQUISA for f in formacoes):
        return ResolucaoDaEntrada.SEM_PESQUISA
    return ResolucaoDaEntrada.SEM_ENTRADA_PENDENTE


# --- Consulta e entrada ---------------------------------------------------------------------


def situacao_de_entrada(pessoa, *, agora: datetime | None = None) -> SituacaoDeEntrada:
    """Todas as formações da Pessoa, com a situação de cada uma, e a resolução da entrada
    no momento de referência. Nunca grava (FR-024).

    Consultas: Pessoa gravada (1), Conclusões (1), Campanhas aplicáveis pela 004 (1 por
    Conclusão) e Participações dos pares com exatamente uma Campanha (0 ou 1). Estado,
    período e elegibilidade vêm só de `campanhas_em_coleta_para`; nenhum filtro da 004 é
    reproduzido aqui (FR-012, FR-013). Formações ambíguas não consultam Participação: o
    estado dela nunca desempata Campanhas (FR-027).

    Pessoa não gravada é erro de uso da fronteira (`ValueError`), nunca "sem formação"
    (FR-003)."""
    _exigir(pessoa, Pessoa, "pessoa")
    agora = momento_de_referencia(agora)
    if not Pessoa.objects.filter(pk=pessoa.pk).exists():
        raise ValueError("pessoa não está gravada")
    conclusoes = tuple(ConclusaoAcademica.objects.filter(pessoa=pessoa))  # ordem da 001
    aplicaveis = [(c, campanhas_em_coleta_para(c, agora=agora)) for c in conclusoes]
    pares = {(campanhas[0].pk, c.pk) for c, campanhas in aplicaveis if len(campanhas) == 1}
    # Só há pares de formações com exatamente 1 Campanha: para as ambíguas o `get` dá
    # `None`, e `_classificar` decide o resto.
    participacoes = _participacoes_dos_pares(pares)
    formacoes = tuple(
        _classificar(
            c, campanhas, participacoes.get((campanhas[0].pk, c.pk)) if campanhas else None
        )
        for c, campanhas in aplicaveis
    )
    return SituacaoDeEntrada(formacoes, _resolver(formacoes))


def _participacoes_dos_pares(pares: set) -> dict:
    """As Participações existentes dos pares (Campanha, Conclusão), numa única consulta e
    sem criar nada — a semântica de `localizar_participacao` (005 FR-046). O filtro por
    `__in` pode trazer pares cruzados; o índice por par os descarta."""
    if not pares:
        return {}
    campanhas = {campanha for campanha, _ in pares}
    conclusoes = {conclusao for _, conclusao in pares}
    encontradas = participacoes_oficiais().filter(
        campanha__in=campanhas, conclusao_efetiva_id__in=conclusoes
    )
    return {
        (p.campanha_id, p.conclusao_efetiva_id): p
        for p in encontradas
        if (p.campanha_id, p.conclusao_efetiva_id) in pares
    }


def entrar(pessoa, formacao=None, *, agora: datetime | None = None) -> Entrada:
    """Inicia ou retoma a Participação da formação, ou devolve o que impede a entrada.

    A situação é sempre **reavaliada** no momento da entrada; nada de consulta anterior é
    reaproveitado (FR-032). Sem `formacao`, só procede com exatamente uma formação
    pendente (FR-030). A Participação vem sempre de `iniciar_participacao` (005), que cria
    ou devolve a existente (FR-033); `ParticipacaoRejeitada` dela é propagada (FR-046)."""
    if formacao is not None:
        _exigir(formacao, ConclusaoAcademica, "formacao")
    situacao = situacao_de_entrada(pessoa, agora=momento_de_referencia(agora))
    if formacao is None:
        if situacao.resolucao is not ResolucaoDaEntrada.ENTRADA_RESOLVIDA:
            return Entrada(situacao, None, False)
        escolhida = situacao.pendentes[0]
    else:
        escolhida = next((f for f in situacao.formacoes if f.conclusao.pk == formacao.pk), None)
        if escolhida is None:
            # Antes de qualquer chamada à 005 (FR-044). Alheia ou inexistente, a mesma
            # rejeição: não há consulta que distinga os dois casos (FR-045).
            raise FormacaoDeOutraPessoa
        if escolhida.situacao is SituacaoDaFormacao.JA_CONCLUIDA:
            # Informação, não alternativa: nada a criar nem a retomar (FR-035).
            return Entrada(situacao, escolhida.participacao, False)
        if not escolhida.situacao.pendente:
            # Sem pesquisa, ou ambígua: nada a iniciar nem a retomar; o motivo está na
            # situação da formação. A ambiguidade não é desempatada (FR-027).
            return Entrada(situacao, None, False)
    # `agora` original, não o instante da avaliação: sem `agora` explícito, a 005 lê o
    # relógio de novo e uma Campanha encerrada nesse intervalo rejeita o início
    # (`ParticipacaoRejeitada`, propagada — FR-046), em vez de ser julgada no passado.
    inicio = iniciar_participacao(escolhida.campanha, escolhida.conclusao, agora=agora)
    return Entrada(situacao, inicio.participacao, inicio.situacao is SituacaoInicio.CRIADA)

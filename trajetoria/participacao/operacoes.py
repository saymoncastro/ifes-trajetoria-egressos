"""Operações de escrita de Participação e Resposta (contracts/operacoes.md).

Único caminho de escrita suportado. Toda operação roda numa transação e valida tudo antes
da primeira gravação: ou tudo é gravado, ou nada (FR-051).

- Criar Participação exige a admissão da 004 (Campanha EM_COLETA e Conclusão ELEGÍVEL,
  por `estado` e `avaliar`, equivalente a `admite_participacao`).
- Escrever Resposta exige só a Campanha EM_COLETA no momento de referência; a
  elegibilidade não é reavaliada depois da criação (FR-034).
- As escritas de resposta bloqueiam a linha da Participação; escritas na mesma
  Participação ficam serializadas (FR-053, research R11).
- Participação, Campanha, Pergunta e Opções são relidas do banco; atributos das
  instâncias recebidas não são confiados (research R9).

Argumento estrutural de classe errada é erro de programação (`TypeError`); Campanha ou
Conclusão não gravada é `ValueError`. Valor declarado
de forma ou conteúdo inválido é `ParticipacaoRejeitada` (research R8). Nenhuma mensagem
contém valor declarado (FR-059).
"""

from collections.abc import Callable, Iterable
from datetime import datetime
from enum import Enum
from typing import NamedTuple, NoReturn

from django.db import IntegrityError, transaction

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.campanha.consultas import (
    EstadoCampanha,
    avaliar,
    estado,
    momento_de_referencia,
)
from trajetoria.campanha.models import Campanha
from trajetoria.instrumento.models import Opcao, Pergunta, TipoPergunta
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada, Violacao

__all__ = [
    "Inicio",
    "SituacaoInicio",
    "SituacaoRemocao",
    "iniciar_participacao",
    "remover_resposta",
    "responder_escala",
    "responder_escolha_multipla",
    "responder_escolha_unica",
    "responder_texto",
]


def _rejeitar(motivo: Motivo, campo: str | None, detalhe: str) -> NoReturn:
    raise ParticipacaoRejeitada((Violacao(motivo, campo, detalhe),))


def _exigir(valor, classe, nome: str):
    if not isinstance(valor, classe):
        raise TypeError(f"{nome} deve ser {classe.__name__}, não {type(valor).__name__}")
    return valor


# --- Iniciar ------------------------------------------------------------------------------


class SituacaoInicio(Enum):
    CRIADA = "criada"
    JA_EXISTENTE = "ja_existente"  # nada gravado (FR-013)


class Inicio(NamedTuple):
    participacao: Participacao
    situacao: SituacaoInicio


def _gravada(modelo, instancia, nome: str):
    """Relê do banco; instância não gravada (ou removida) é erro do chamador."""
    gravada = modelo.objects.filter(pk=instancia.pk).first()
    if gravada is None:
        raise ValueError(f"{nome} não está gravada")
    return gravada


def _participacao_existente(campanha: Campanha, conclusao: ConclusaoAcademica):
    return Participacao.objects.filter(campanha=campanha, conclusao=conclusao).first()


def _violacoes_de_admissao(campanha, conclusao, agora: datetime) -> list[Violacao]:
    """A admissão da 004 (FR-053) pelos seus próprios contratos, `estado` e `avaliar`, sem
    reescrever regra: lista vazia ⇔ `admite_participacao` (verificado em teste). Cada
    condição é avaliada uma vez e todas as falhas são reunidas (FR-012, FR-014). O detalhe
    cita só critério e motivo, nunca o valor da Conclusão."""
    violacoes = []
    if estado(campanha, agora=agora) is not EstadoCampanha.EM_COLETA:
        violacoes.append(
            Violacao(Motivo.COLETA_NAO_ADMITIDA, "campanha", "a Campanha não está em coleta")
        )
    if pendencias := avaliar(campanha, conclusao).pendencias:
        criterios = ", ".join(f"{p.criterio.value} ({p.motivo.value})" for p in pendencias)
        violacoes.append(
            Violacao(Motivo.CONCLUSAO_NAO_ELEGIVEL, "conclusao", f"não elegível: {criterios}")
        )
    return violacoes


def iniciar_participacao(campanha, conclusao, *, agora: datetime | None = None) -> Inicio:
    """Devolve a Participação do par, criando-a só se a 004 a admite (FR-011 a FR-013).

    Se o par já tem Participação, devolve-a sem consultar estado nem elegibilidade e sem
    gravar, inclusive com a Campanha encerrada; isso não autoriza escrita de respostas.
    Inícios simultâneos: o `UNIQUE (campanha, conclusao)` decide; quem perde a corrida
    relê e devolve a Participação da outra transação (research R11)."""
    _exigir(campanha, Campanha, "campanha")
    _exigir(conclusao, ConclusaoAcademica, "conclusao")
    agora = momento_de_referencia(agora)
    with transaction.atomic():
        if existente := _participacao_existente(campanha, conclusao):
            return Inicio(existente, SituacaoInicio.JA_EXISTENTE)
        campanha = _gravada(Campanha, campanha, "campanha")
        conclusao = _gravada(ConclusaoAcademica, conclusao, "conclusao")
        if violacoes := _violacoes_de_admissao(campanha, conclusao, agora):
            raise ParticipacaoRejeitada(violacoes)
        try:
            with transaction.atomic():
                nova = Participacao.objects.create(
                    campanha=campanha, conclusao=conclusao, iniciada_em=agora
                )
        except IntegrityError:
            da_outra = Participacao.objects.filter(campanha=campanha, conclusao=conclusao).first()
            if da_outra is None:
                raise
            return Inicio(da_outra, SituacaoInicio.JA_EXISTENTE)
    return Inicio(nova, SituacaoInicio.CRIADA)


# --- Esqueleto das escritas de resposta ------------------------------------------------------


def _bloquear(participacao) -> Participacao:
    """Bloqueia só a linha da Participação (`of=("self",)`), não a Campanha: escritas na
    mesma Participação ficam serializadas sem travar a rodada inteira (research R11)."""
    gravada = (
        Participacao.objects.select_for_update(of=("self",))
        .select_related("campanha")
        .filter(pk=participacao.pk)
        .first()
    )
    if gravada is None:
        _rejeitar(Motivo.PARTICIPACAO_INEXISTENTE, "participacao", "Participação inexistente")
    return gravada


def _escrever(participacao, pergunta, agora, tipo: TipoPergunta | None, aplicar: Callable):
    """Passos comuns (contrato, "Esqueleto"): tipos → bloqueio → coleta → Versão → tipo da
    Pergunta → `aplicar(participacao, pergunta)`, que valida o valor e grava. Tudo numa
    transação; a validação vem antes da primeira gravação (FR-051)."""
    _exigir(participacao, Participacao, "participacao")
    _exigir(pergunta, Pergunta, "pergunta")
    if agora is not None:
        momento_de_referencia(agora)  # `TypeError` antes de qualquer acesso ao banco
    with transaction.atomic():
        participacao = _bloquear(participacao)
        # O relógio é lido só depois do bloqueio: uma escrita que esperou pela de outra não
        # é julgada por um instante anterior à espera (FR-039).
        agora = momento_de_referencia(agora)
        # Sem reavaliar elegibilidade: ela só vale na criação (FR-034).
        if estado(participacao.campanha, agora=agora) is not EstadoCampanha.EM_COLETA:
            _rejeitar(Motivo.COLETA_NAO_ADMITIDA, "campanha", "a Campanha não está em coleta")
        pergunta = Pergunta.objects.select_related("secao").filter(pk=pergunta.pk).first()
        if pergunta is None or pergunta.secao.versao_id != participacao.campanha.versao_id:
            _rejeitar(
                Motivo.PERGUNTA_DE_OUTRA_VERSAO,
                "pergunta",
                "a Pergunta não pertence à Versão aplicada pela Campanha",
            )
        if tipo is not None and pergunta.tipo != tipo:
            _rejeitar(
                Motivo.VALOR_INCOMPATIVEL,
                "pergunta",
                f"operação de {tipo.value} em Pergunta {pergunta.id} de tipo {pergunta.tipo}",
            )
        return aplicar(participacao, pergunta)


def _gravar(
    participacao, pergunta, *, opcao=None, texto=None, escala=None, complemento=None, opcoes=None
) -> Resposta:
    """Grava o valor inteiro no lugar (mesmo `id`) ou cria a Resposta. As colunas das outras
    formas e o complemento ausente ficam `NULL`. Em escolha múltipla (`opcoes` informado), o
    conjunto é substituído; nos demais tipos não há seleções a tocar, porque o tipo da
    Pergunta não muda (002 FR-062)."""
    resposta, _ = Resposta.objects.update_or_create(
        participacao=participacao,
        pergunta=pergunta,
        defaults={"opcao": opcao, "texto": texto, "escala": escala, "complemento": complemento},
    )
    if opcoes is not None:
        RespostaOpcao.objects.filter(resposta=resposta).delete()
        RespostaOpcao.objects.bulk_create(RespostaOpcao(resposta=resposta, opcao=o) for o in opcoes)
    return resposta


# --- Validação de valores ------------------------------------------------------------------
# Ausência × vazio: `None`, texto em branco e coleção vazia são sempre VALOR_VAZIO,
# verificado antes da forma do valor. "Não respondida" é só a ausência de Resposta.


def _vazio(campo: str) -> NoReturn:
    _rejeitar(Motivo.VALOR_VAZIO, campo, f"{campo} ausente ou vazio")


def _incompativel(campo: str) -> NoReturn:
    _rejeitar(Motivo.VALOR_INCOMPATIVEL, campo, f"{campo} de forma incompatível com o tipo")


def _texto_declarado(valor, campo: str) -> str:
    if valor is None:
        _vazio(campo)
    if not isinstance(valor, str):
        _incompativel(campo)
    if not valor.strip():
        _vazio(campo)
    return valor  # gravado como recebido, sem strip()


def _opcao_da_pergunta(pergunta: Pergunta, opcao) -> Opcao:
    if opcao is None:
        _vazio("opcao")
    if not isinstance(opcao, Opcao):
        _incompativel("opcao")
    gravada = Opcao.objects.filter(pk=opcao.pk, pergunta=pergunta).first()
    if gravada is None:
        _rejeitar(Motivo.OPCAO_DE_OUTRA_PERGUNTA, "opcao", f"Opção {opcao.pk} não é da Pergunta")
    return gravada


def _opcoes_da_pergunta(pergunta: Pergunta, opcoes) -> list[Opcao]:
    if opcoes is None:
        _vazio("opcoes")
    if isinstance(opcoes, (str, bytes, Opcao)) or not isinstance(opcoes, Iterable):
        _incompativel("opcoes")
    opcoes = list(opcoes)
    if not all(isinstance(o, Opcao) for o in opcoes):
        _incompativel("opcoes")
    ids = list(dict.fromkeys(o.pk for o in opcoes))  # conjunto: repetição não conta
    if not ids:
        _vazio("opcoes")
    gravadas = list(Opcao.objects.filter(pk__in=ids, pergunta=pergunta))
    if len(gravadas) != len(ids):
        _rejeitar(Motivo.OPCAO_DE_OUTRA_PERGUNTA, "opcoes", "alguma Opção não é da Pergunta")
    return gravadas


def _complemento(complemento, selecionadas: list[Opcao]) -> str | None:
    """Só com a Opção que o admite selecionada; a 002 garante no máximo uma por Pergunta,
    então uma coluna basta (research R6)."""
    if complemento is None:
        return None
    if not isinstance(complemento, str):
        _incompativel("complemento")
    if not complemento.strip():
        _vazio("complemento")
    if not any(o.complemento_textual for o in selecionadas):
        _rejeitar(
            Motivo.COMPLEMENTO_NAO_ADMITIDO,
            "complemento",
            "nenhuma Opção selecionada admite complemento",
        )
    return complemento


# --- Responder e remover -----------------------------------------------------------------


def responder_escolha_unica(
    participacao, pergunta, opcao, *, complemento=None, agora: datetime | None = None
) -> Resposta:
    """Exatamente uma Opção da própria Pergunta, por identidade (FR-024)."""

    def aplicar(participacao, pergunta):
        escolhida = _opcao_da_pergunta(pergunta, opcao)
        return _gravar(
            participacao,
            pergunta,
            opcao=escolhida,
            complemento=_complemento(complemento, [escolhida]),
        )

    return _escrever(participacao, pergunta, agora, TipoPergunta.ESCOLHA_UNICA, aplicar)


def responder_escolha_multipla(
    participacao, pergunta, opcoes, *, complemento=None, agora: datetime | None = None
) -> Resposta:
    """Conjunto não vazio de Opções da própria Pergunta, sem ordem nem repetição (FR-025).
    Para "desmarcar tudo", `remover_resposta`."""

    def aplicar(participacao, pergunta):
        escolhidas = _opcoes_da_pergunta(pergunta, opcoes)
        # `resposta.opcoes.all()` lê o conjunto sob demanda, na ordem do instrumento.
        return _gravar(
            participacao,
            pergunta,
            complemento=_complemento(complemento, escolhidas),
            opcoes=escolhidas,
        )

    return _escrever(participacao, pergunta, agora, TipoPergunta.ESCOLHA_MULTIPLA, aplicar)


def responder_texto(participacao, pergunta, texto, *, agora: datetime | None = None) -> Resposta:
    """Texto não vazio, exatamente como recebido; sem regex, máscara ou conversão (FR-026)."""

    def aplicar(participacao, pergunta):
        return _gravar(participacao, pergunta, texto=_texto_declarado(texto, "texto"))

    return _escrever(participacao, pergunta, agora, TipoPergunta.TEXTO_CURTO, aplicar)


def responder_escala(participacao, pergunta, valor, *, agora: datetime | None = None) -> Resposta:
    """Inteiro entre os limites da Pergunta histórica, inclusive (FR-027)."""

    def aplicar(participacao, pergunta):
        if valor is None:
            _vazio("escala")
        if type(valor) is not int:  # exclui bool, float e texto
            _incompativel("escala")
        if not pergunta.escala_inicio <= valor <= pergunta.escala_fim:
            _rejeitar(
                Motivo.ESCALA_FORA_DOS_LIMITES,
                "escala",
                f"fora de [{pergunta.escala_inicio}, {pergunta.escala_fim}]",
            )
        return _gravar(participacao, pergunta, escala=valor)

    return _escrever(participacao, pergunta, agora, TipoPergunta.ESCALA, aplicar)


class SituacaoRemocao(Enum):
    REMOVIDA = "removida"
    INEXISTENTE = "inexistente"  # nada mudou (FR-036)


def remover_resposta(participacao, pergunta, *, agora: datetime | None = None) -> SituacaoRemocao:
    """A Pergunta volta a não respondida. Obrigatoriedade não é verificada (FR-037); as
    seleções saem por `CASCADE`. Nenhum histórico (FR-035)."""

    def aplicar(participacao, pergunta):
        removidas, _ = Resposta.objects.filter(
            participacao=participacao, pergunta=pergunta
        ).delete()
        return SituacaoRemocao.REMOVIDA if removidas else SituacaoRemocao.INEXISTENTE

    return _escrever(participacao, pergunta, agora, None, aplicar)

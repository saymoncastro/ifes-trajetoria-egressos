"""Prévia, confirmação e envio de Lotes (Feature 020; contracts/transporte.md).

Escrita só por aqui. Toda operação reautoriza o operador por conta própria (como a 016):
a view nunca é a única barreira. O cliente nunca define lista, contagem, contato,
destinatário, remetente ou URL (FR-020, FR-026).

Nenhuma operação cria ou altera Pessoa, Conclusão, Campanha, Versão, Participação,
Resposta ou Formação Declarada (FR-041), nem participa da admissão (ADR 0004).
"""

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.mobilizacao.acesso import (
    RecusaDeLote,
    campanha_autorizada,
    contexto_do_operador,
)
from trajetoria.mobilizacao.models import LoteDeMobilizacao, MembroDoLote, SituacaoDoMembro
from trajetoria.mobilizacao.selecao import Filtros, FiltrosInvalidos, selecionar

S = SituacaoDoMembro
TAMANHO_DO_NOME = 120


@dataclass(frozen=True)
class Previa:
    campanha: Campanha
    filtros: Filtros
    conclusoes: int
    pessoas: int
    com_contato: int
    sem_contato: int
    excluidas: int
    exige_confirmacao_de_abrangencia: bool


def _exigir_filtros_no_escopo(filtros: Filtros, escopo) -> None:
    """CSAEG: filtro de unidades obrigatório e contido nas suas unidades (FR-037)."""
    if escopo.institucional:
        return
    if filtros.unidades is None or not set(filtros.unidades) <= set(escopo.unidades):
        raise RecusaDeLote("unidade_fora_do_escopo", 403)


def _preparacao(campanha_id, operador, filtros):
    contexto = contexto_do_operador(operador)
    if not contexto.preparar:
        raise RecusaDeLote()
    campanha = campanha_autorizada(campanha_id, contexto)
    if not isinstance(filtros, Filtros):
        try:
            filtros = Filtros.de(**filtros)
        except FiltrosInvalidos:
            raise RecusaDeLote("filtros_invalidos", 422) from None
    _exigir_filtros_no_escopo(filtros, contexto.escopo)
    return contexto, campanha, filtros


def _exige_confirmacao(filtros, escopo) -> bool:
    return escopo.institucional and filtros.vazio


def previa(campanha_id, operador, filtros, *, agora=None) -> Previa:
    """Recalculada a cada ajuste; nada é gravado (FR-019)."""
    contexto, campanha, filtros = _preparacao(campanha_id, operador, filtros)
    selecao = selecionar(campanha, contexto.escopo, filtros, agora or timezone.now())
    return Previa(
        campanha,
        filtros,
        selecao.conclusoes,
        len(selecao.pessoas),
        selecao.com_contato,
        selecao.sem_contato,
        selecao.excluidas,
        _exige_confirmacao(filtros, contexto.escopo),
    )


def _nome_valido(nome) -> str:
    if not isinstance(nome, str):
        raise RecusaDeLote("nome_invalido", 422)
    nome = nome.strip()
    if not nome or len(nome) > TAMANHO_DO_NOME or any(c in nome for c in "\r\n\x00"):
        raise RecusaDeLote("nome_invalido", 422)
    return nome


def confirmar_lote(
    campanha_id, operador, nome, filtros, confirmo_abrangencia=False, *, agora=None
) -> LoteDeMobilizacao:
    """Recalcula a seleção no servidor e grava Lote e membros numa transação, com a linha da
    Campanha travada: confirmações da mesma Campanha são serializadas (research R5)."""
    contexto, campanha, filtros = _preparacao(campanha_id, operador, filtros)
    nome = _nome_valido(nome)
    if _exige_confirmacao(filtros, contexto.escopo) and confirmo_abrangencia is not True:
        raise RecusaDeLote("confirmacao_de_abrangencia", 422)
    agora = agora or timezone.now()
    try:
        with transaction.atomic():
            campanha = Campanha.objects.select_for_update().get(pk=campanha.pk)
            if estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA:
                raise RecusaDeLote("campanha_encerrada", 409)
            selecao = selecionar(campanha, contexto.escopo, filtros, agora)
            if not selecao.pessoas:
                raise RecusaDeLote("lote_vazio", 422)
            lote = LoteDeMobilizacao.objects.create(
                campanha=campanha,
                nome=nome,
                unidades=list(filtros.unidades) if filtros.unidades else None,
                nivel=filtros.nivel,
                ano_minimo=filtros.ano_minimo,
                ano_maximo=filtros.ano_maximo,
                curso=filtros.curso,
                escopo_institucional=contexto.escopo.institucional,
                escopo_unidades=sorted(contexto.escopo.unidades),
                excluidas_por_mobilizacao=selecao.excluidas,
                confirmado_em=agora,
                operador=contexto.operador,
            )
            membros = []
            for pessoa_id, contato in selecao.pessoas:
                if contato is not None and contato.pessoa_id != pessoa_id:
                    raise RecusaDeLote("falha_preparacao", 422)
                membros.append(
                    MembroDoLote(
                        lote=lote,
                        campanha=campanha,
                        pessoa_id=pessoa_id,
                        contato=contato,
                        situacao=S.NAO_TENTADO if contato else S.SEM_CONTATO,
                    )
                )
            MembroDoLote.objects.bulk_create(membros)
    except IntegrityError:
        # Restrição `membro_uma_abordagem_por_campanha` (FR-025): nada foi gravado.
        raise RecusaDeLote("mobilizacao_concorrente", 409) from None
    return lote


# --- Envio ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultadoDoEnvio:
    """Somente totais; nunca endereço, nome ou texto de exceção (FR-039)."""

    processados: int
    submetidos: int
    falhas: int
    restantes_nao_tentados: int
    interrompido: bool = False
    # Membros cuja mensagem foi recusada pela validação do modo antes de qualquer tentativa
    # (ex.: contato fora de `example.invalid` na demonstração). Continuam `NAO_TENTADO`.
    nao_enviaveis: int = 0
    # A Campanha deixou de estar em coleta durante a ação; nada mais foi tentado.
    saiu_da_coleta: bool = False


def _reservar(membro_id, agora) -> MembroDoLote | None:
    """(a) Transação curta: trava o membro sem esperar e grava `EM_TENTATIVA` antes de
    qualquer envio. Outra ação concorrente nunca pega o mesmo membro (research R7)."""
    with transaction.atomic():
        membro = (
            MembroDoLote.objects.select_for_update(skip_locked=True, of=("self",))
            .select_related("contato", "pessoa")
            .filter(pk=membro_id, situacao=S.NAO_TENTADO)
            .first()
        )
        if membro is None:
            return None
        MembroDoLote.objects.filter(pk=membro.pk).update(
            situacao=S.EM_TENTATIVA, tentativa_iniciada_em=agora
        )
    return membro


def _registrar(membro, situacao) -> None:
    """(c) Resultado conhecido do transporte. `EM_TENTATIVA` nunca volta a `NAO_TENTADO`."""
    MembroDoLote.objects.filter(pk=membro.pk, situacao=S.EM_TENTATIVA).update(
        situacao=situacao, resultado_em=timezone.now()
    )


def enviar_lote(lote_id, operador, *, agora=None) -> ResultadoDoEnvio:
    """Uma tentativa por membro `NAO_TENTADO`, até o limite por ação; retomável sem reenvio.

    Algoritmo (contracts/transporte.md, "Envio"): revalida tudo; para cada membro, (a) grava
    `EM_TENTATIVA`, (b) envia fora de transação pelo contato **congelado**, (c) grava o
    resultado. Exceção inesperada interrompe a ação e deixa o membro em `EM_TENTATIVA`
    (resultado incerto), que nunca é tentado de novo. Sem retry, fila ou worker (FR-029).
    """
    from smtplib import SMTPException

    from django.conf import settings

    from trajetoria.comunicacao.convite import renderizar_convite
    from trajetoria.comunicacao.transporte import RecusaDeTransporte, transporte_de_envio
    from trajetoria.mobilizacao.acesso import lote_visivel

    contexto = contexto_do_operador(operador)
    if not contexto.enviar:
        raise RecusaDeLote()
    lote = LoteDeMobilizacao.objects.select_related("campanha").filter(pk=lote_id).first()
    if lote is None:
        raise RecusaDeLote("inexistente", 404)
    campanha = campanha_autorizada(lote.campanha_id, contexto)
    if not lote_visivel(lote, contexto.escopo):
        raise RecusaDeLote("fora_do_escopo", 403)
    if estado(campanha, agora=agora) is not EstadoCampanha.EM_COLETA:
        raise RecusaDeLote(
            "campanha_encerrada"
            if estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA
            else "campanha_fora_da_coleta",
            409,
        )
    try:
        transporte = transporte_de_envio()
    except RecusaDeTransporte as exc:
        raise RecusaDeLote(exc.categoria, exc.status) from None

    limite = settings.TRAJETORIA_LOTE_ENVIO_POR_ACAO
    candidatos = list(
        lote.membros.filter(situacao=S.NAO_TENTADO).order_by("pk").values_list("pk", flat=True)
    )
    processados = submetidos = falhas = nao_enviaveis = 0
    interrompido = saiu_da_coleta = False
    membros = {
        m.pk: m
        for m in MembroDoLote.objects.select_related("contato", "pessoa").filter(
            pk__in=candidatos
        )
    }
    for membro_id in candidatos:
        if processados >= limite:
            break
        # Revalidação a cada membro: uma ação longa não envia depois do encerramento.
        if _estado_atual(campanha.pk, agora) is not EstadoCampanha.EM_COLETA:
            saiu_da_coleta = True
            break
        # Validação determinística ANTES de reservar: se o modo recusa a mensagem (contato,
        # conteúdo ou cabeçalho), nada é transmitido e o membro continua `NAO_TENTADO`,
        # nunca "resultado incerto".
        try:
            mensagem = _mensagem(membros[membro_id], campanha, transporte, renderizar_convite)
        except (RecusaDeTransporte, ValueError):
            nao_enviaveis += 1
            continue
        membro = _reservar(membro_id, agora or timezone.now())
        if membro is None:
            continue  # outra ação já o pegou
        processados += 1
        conexao = None
        try:
            conexao = transporte.conexao()
            # (b) fora de transação; destino exclusivamente o contato congelado (E6).
            mensagem.connection = conexao
            enviado = mensagem.send(fail_silently=False) == 1
        except (SMTPException, OSError):
            enviado = False  # falha de transporte; nunca o texto da exceção
        except Exception:
            interrompido = True  # membro fica EM_TENTATIVA: resultado incerto
            break
        finally:
            if conexao is not None:
                try:
                    conexao.close()
                except Exception:  # o retorno do envio não é desfeito no fechamento
                    pass
        if enviado:
            _registrar(membro, S.SUBMETIDO_AO_TRANSPORTE)
            submetidos += 1
        else:
            _registrar(membro, S.FALHA_DE_TRANSPORTE)
            falhas += 1
    restantes = lote.membros.filter(situacao=S.NAO_TENTADO).count()
    return ResultadoDoEnvio(
        processados, submetidos, falhas, restantes, interrompido, nao_enviaveis, saiu_da_coleta
    )


def _estado_atual(campanha_id, agora):
    return estado(Campanha.objects.get(pk=campanha_id), agora=agora)


def _mensagem(membro, campanha, transporte, renderizar_convite):
    """Renderiza e valida a mensagem do membro no modo do transporte, sem conexão."""
    convite = renderizar_convite(
        membro.pessoa.nome, campanha.nome, transporte.url,
        modo=transporte.modo, remetente=transporte.remetente,
    )
    return convite.mensagem(membro.contato.valor)

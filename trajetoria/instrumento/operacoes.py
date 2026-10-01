"""Operações de escrita do instrumento (contracts/operacoes.md).

Único caminho de escrita suportado (research R8, R9). Toda operação sobre uma Versão ou
seus elementos roda numa transação, bloqueia a linha da Versão, rejeita com
`VERSAO_PUBLICADA` se ela estiver publicada e só então verifica as regras da operação.
Nenhuma operação volta uma Versão a RASCUNHO, muda sua Pesquisa ou a exclui.

Argumento de tipo errado (texto que não é `str`, `obrigatoria` ou `complemento_textual`
que não é `bool`, destino que não é `Secao`) é erro de programação: levanta `TypeError`
antes de qualquer escrita. Valor inválido para o domínio levanta `OperacaoRejeitada`.
"""

from enum import Enum
from typing import NoReturn
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import (
    EstadoVersao,
    Opcao,
    Pergunta,
    Pesquisa,
    Secao,
    TipoPergunta,
    Versao,
)
from trajetoria.instrumento.regras import (
    Motivo,
    OperacaoRejeitada,
    Violacao,
    verificar_completude,
)

__all__ = [
    "FINALIZAR",
    "Finalizar",
    "SituacaoPublicacao",
    "adicionar_opcao",
    "adicionar_pergunta",
    "adicionar_secao",
    "alterar_opcao",
    "alterar_pergunta",
    "alterar_secao",
    "alterar_versao",
    "criar_pesquisa",
    "criar_versao",
    "criar_versao_a_partir_de",
    "definir_encaminhamento",
    "definir_regra",
    "mover_pergunta",
    "publicar",
    "remover_opcao",
    "remover_pergunta",
    "remover_regra",
    "remover_secao",
    "renomear_pesquisa",
    "reordenar_opcoes",
    "reordenar_perguntas",
    "reordenar_secoes",
]

# Sentinela de "não informado" nos `alterar_*`: `None` significa remover um texto opcional.
_MANTER = object()


def _rejeitar(motivo: Motivo, elemento: UUID | None = None, detalhe: str = "") -> NoReturn:
    raise OperacaoRejeitada((Violacao(motivo, elemento, detalhe),))


def _bloquear(versao_id: UUID) -> Versao:
    return Versao.objects.select_for_update().get(pk=versao_id)


def _exigir_rascunho(versao: Versao) -> None:
    if versao.publicada:
        _rejeitar(Motivo.VERSAO_PUBLICADA, versao.id, "Versão publicada não pode ser alterada")


def _texto_obrigatorio(valor, elemento: UUID | None) -> str:
    # O texto é gravado como recebido, sem strip() (R16).
    if not isinstance(valor, str):
        raise TypeError(f"texto deve ser str, não {type(valor).__name__}")
    if not valor.strip():
        _rejeitar(Motivo.TEXTO_VAZIO, elemento, "texto vazio")
    return valor


def _texto_opcional(valor, elemento: UUID | None) -> str | None:
    return None if valor is None else _texto_obrigatorio(valor, elemento)


def _booleano(valor, nome: str) -> bool:
    if not isinstance(valor, bool):
        raise TypeError(f"{nome} deve ser bool, não {type(valor).__name__}")
    return valor


def _bloqueado(modelo, pk, caminho_da_versao: str, *relacionados):
    """Bloqueia a Versão do elemento, exige rascunho e devolve o elemento relido."""
    versao_id = modelo.objects.values_list(caminho_da_versao, flat=True).get(pk=pk)
    _exigir_rascunho(_bloquear(versao_id))
    return modelo.objects.select_related(*relacionados).get(pk=pk)


def _secao_da_versao(secao, versao_id: UUID) -> Secao:
    """Relê uma Seção usada como destino e exige que seja da mesma Versão (FR-058 a, g)."""
    if not isinstance(secao, Secao):
        raise TypeError(f"destino deve ser Secao, não {type(secao).__name__}")
    secao = Secao.objects.get(pk=secao.pk)
    if secao.versao_id != versao_id:
        _rejeitar(Motivo.REFERENCIA_OUTRA_VERSAO, secao.id, "Seção de outra Versão")
    return secao


def _posicao(valor, elemento: UUID | None) -> int:
    # bool é subclasse de int e não é posição.
    if type(valor) is not int or valor < 1:
        _rejeitar(Motivo.POSICAO_INVALIDA, elemento, f"posição {valor!r}")
    return valor


def _posicao_livre(conjunto: QuerySet, posicao: int, elemento: UUID | None) -> None:
    if conjunto.filter(posicao=posicao).exists():
        _rejeitar(Motivo.POSICAO_OCUPADA, elemento, f"posição {posicao}")


def _reordenar(conjunto: QuerySet, em_ordem, elemento: UUID | None) -> None:
    ids = [e.pk for e in em_ordem]
    if len(ids) != len(set(ids)) or set(ids) != set(conjunto.values_list("pk", flat=True)):
        _rejeitar(Motivo.ORDEM_INCOMPLETA, elemento, "a ordem deve conter cada elemento uma vez")
    # A unicidade de posição é adiada para o fim da transação (R4).
    for posicao, pk in enumerate(ids, start=1):
        conjunto.filter(pk=pk).update(posicao=posicao)


# --- Pesquisa -------------------------------------------------------------------------


def criar_pesquisa(nome: str) -> Pesquisa:
    return Pesquisa.objects.create(nome=_texto_obrigatorio(nome, None))


def renomear_pesquisa(pesquisa: Pesquisa, nome: str) -> Pesquisa:
    # O nome não integra o conteúdo de nenhuma Versão (FR-003): nenhuma Versão é tocada.
    with transaction.atomic():
        pesquisa = Pesquisa.objects.select_for_update().get(pk=pesquisa.pk)
        pesquisa.nome = _texto_obrigatorio(nome, pesquisa.id)
        pesquisa.save(update_fields=["nome"])
    return pesquisa


# --- Versão ---------------------------------------------------------------------------


def _designacao_livre(pesquisa_id: UUID, designacao: str, exceto: UUID | None = None) -> None:
    # Bloqueia a Pesquisa: toda operação que grava designação serializa nela, e a
    # verificação abaixo não perde para uma gravação concorrente.
    Pesquisa.objects.select_for_update().get(pk=pesquisa_id)
    repetidas = Versao.objects.filter(pesquisa_id=pesquisa_id, designacao=designacao)
    if repetidas.exclude(pk=exceto).exists():
        _rejeitar(Motivo.DESIGNACAO_REPETIDA, exceto, f"designação {designacao!r}")


def criar_versao(pesquisa: Pesquisa, designacao: str) -> Versao:
    with transaction.atomic():
        _designacao_livre(pesquisa.pk, _texto_obrigatorio(designacao, None))
        return Versao.objects.create(pesquisa_id=pesquisa.pk, designacao=designacao)


def alterar_versao(
    versao: Versao,
    *,
    designacao=_MANTER,
    titulo=_MANTER,
    texto_abertura=_MANTER,
    texto_encerramento=_MANTER,
) -> Versao:
    with transaction.atomic():
        versao = _bloquear(versao.pk)
        _exigir_rascunho(versao)
        campos = []
        if designacao is not _MANTER:
            _designacao_livre(
                versao.pesquisa_id, _texto_obrigatorio(designacao, versao.id), versao.id
            )
            versao.designacao = designacao
            campos.append("designacao")
        for campo, valor in (
            ("titulo", titulo),
            ("texto_abertura", texto_abertura),
            ("texto_encerramento", texto_encerramento),
        ):
            if valor is not _MANTER:
                setattr(versao, campo, _texto_opcional(valor, versao.id))
                campos.append(campo)
        versao.save(update_fields=campos)
    return versao


def criar_versao_a_partir_de(origem: Versao, designacao: str) -> Versao:
    """Cópia profunda em RASCUNHO, na Pesquisa da origem, com elementos próprios e
    referências traduzidas para a nova Versão (FR-019–FR-023, R11). A origem não é escrita;
    não se registra correspondência entre elementos (DP-006)."""
    with transaction.atomic():
        origem = _bloquear(origem.pk)  # só para leitura consistente
        _designacao_livre(origem.pesquisa_id, _texto_obrigatorio(designacao, origem.id))
        nova = Versao.objects.create(
            pesquisa_id=origem.pesquisa_id,
            designacao=designacao,
            origem=origem,
            titulo=origem.titulo,
            texto_abertura=origem.texto_abertura,
            texto_encerramento=origem.texto_encerramento,
        )
        secoes = list(origem.secoes.order_by("posicao"))
        copia_de = {
            s.id: Secao(versao=nova, posicao=s.posicao, titulo=s.titulo, texto=s.texto)
            for s in secoes
        }
        Secao.objects.bulk_create(copia_de.values())
        for secao in secoes:
            if secao.encaminhamento_id:
                copia_de[secao.id].encaminhamento = copia_de[secao.encaminhamento_id]
        Secao.objects.bulk_update(copia_de.values(), ["encaminhamento"])
        perguntas, opcoes = [], []
        for pergunta in Pergunta.objects.filter(secao__versao=origem).prefetch_related("opcoes"):
            copia = Pergunta(
                secao=copia_de[pergunta.secao_id],
                posicao=pergunta.posicao,
                tipo=pergunta.tipo,
                texto=pergunta.texto,
                texto_explicativo=pergunta.texto_explicativo,
                obrigatoria=pergunta.obrigatoria,
                escala_inicio=pergunta.escala_inicio,
                escala_fim=pergunta.escala_fim,
                escala_rotulo_inicio=pergunta.escala_rotulo_inicio,
                escala_rotulo_fim=pergunta.escala_rotulo_fim,
            )
            perguntas.append(copia)
            opcoes.extend(
                Opcao(
                    pergunta=copia,
                    posicao=opcao.posicao,
                    texto=opcao.texto,
                    complemento_textual=opcao.complemento_textual,
                    regra_destino=copia_de.get(opcao.regra_destino_id),
                    regra_finaliza=opcao.regra_finaliza,
                )
                for opcao in pergunta.opcoes.all()
            )
        # As chaves UUID nascem no cliente: as FKs já estão resolvidas antes dos INSERTs.
        Pergunta.objects.bulk_create(perguntas)
        Opcao.objects.bulk_create(opcoes)
    return nova


class SituacaoPublicacao(Enum):
    PUBLICADA = "publicada"  # transição feita agora; publicada_em registrado
    JA_PUBLICADA = "ja_publicada"  # nada mudou, nem publicada_em (FR-015)


def publicar(versao: Versao) -> SituacaoPublicacao:
    """Fixa definitivamente o conteúdo da Versão. É a única função que escreve `estado`, e
    só de RASCUNHO para PUBLICADA (FR-013). Não verifica quem chama: DP-001."""
    with transaction.atomic():
        versao = _bloquear(versao.pk)
        if versao.publicada:
            return SituacaoPublicacao.JA_PUBLICADA
        if violacoes := verificar_completude(versao):
            raise OperacaoRejeitada(violacoes)
        versao.estado = EstadoVersao.PUBLICADA
        versao.publicada_em = timezone.now()
        versao.save(update_fields=["estado", "publicada_em"])
    return SituacaoPublicacao.PUBLICADA


# --- Seção ----------------------------------------------------------------------------


def adicionar_secao(versao: Versao, posicao: int, *, titulo=None, texto=None) -> Secao:
    with transaction.atomic():
        versao = _bloquear(versao.pk)
        _exigir_rascunho(versao)
        _posicao_livre(versao.secoes.all(), _posicao(posicao, versao.id), versao.id)
        return Secao.objects.create(
            versao=versao,
            posicao=posicao,
            titulo=_texto_opcional(titulo, versao.id),
            texto=_texto_opcional(texto, versao.id),
        )


def alterar_secao(secao: Secao, *, titulo=_MANTER, texto=_MANTER) -> Secao:
    with transaction.atomic():
        secao = _bloqueado(Secao, secao.pk, "versao_id")
        campos = []
        for campo, valor in (("titulo", titulo), ("texto", texto)):
            if valor is not _MANTER:
                setattr(secao, campo, _texto_opcional(valor, secao.id))
                campos.append(campo)
        secao.save(update_fields=campos)
    return secao


def remover_secao(secao: Secao) -> None:
    with transaction.atomic():
        secao = _bloqueado(Secao, secao.pk, "versao_id")
        if secao.perguntas.exists():
            _rejeitar(Motivo.SECAO_COM_PERGUNTAS, secao.id, "remova as Perguntas antes")
        referenciada = (
            Secao.objects.filter(encaminhamento=secao).exclude(pk=secao.pk).exists()
            or Opcao.objects.filter(regra_destino=secao).exists()
        )
        if referenciada:
            _rejeitar(Motivo.SECAO_REFERENCIADA, secao.id, "destino de regra ou encaminhamento")
        if secao.encaminhamento_id == secao.id:
            # Encaminhamento para si mesma (aceito em rascunho) não impede a remoção.
            Secao.objects.filter(pk=secao.pk).update(encaminhamento=None)
        secao.delete()


def definir_encaminhamento(secao: Secao, destino: Secao | None) -> Secao:
    """Seção seguinte quando nenhuma regra é acionada; `None` volta ao fluxo padrão
    (FR-049). Destino não posterior é aceito em rascunho e barrado na publicação."""
    with transaction.atomic():
        secao = _bloqueado(Secao, secao.pk, "versao_id")
        if destino is not None:
            destino = _secao_da_versao(destino, secao.versao_id)
        secao.encaminhamento = destino
        secao.save(update_fields=["encaminhamento"])
    return secao


def reordenar_secoes(versao: Versao, secoes_em_ordem) -> None:
    with transaction.atomic():
        versao = _bloquear(versao.pk)
        _exigir_rascunho(versao)
        _reordenar(versao.secoes.all(), secoes_em_ordem, versao.id)


# --- Pergunta -------------------------------------------------------------------------


def _tipo(tipo, elemento: UUID | None) -> TipoPergunta:
    try:
        return TipoPergunta(tipo)
    except ValueError:
        _rejeitar(Motivo.TIPO_NAO_SUPORTADO, elemento, f"tipo {tipo!r}")


def _configuracao_escala(tipo: TipoPergunta, escala, elemento: UUID | None) -> dict:
    """Colunas de escala da Pergunta: obrigatórias e válidas em ESCALA, nulas nos demais
    tipos (FR-038)."""
    if tipo != TipoPergunta.ESCALA:
        if escala is not None:
            _rejeitar(Motivo.ESCALA_EM_TIPO_NAO_ESCALA, elemento, f"tipo {tipo}")
        return dict.fromkeys(
            ("escala_inicio", "escala_fim", "escala_rotulo_inicio", "escala_rotulo_fim")
        )
    limites_validos = (
        isinstance(escala, Escala)
        and type(escala.inicio) is int
        and type(escala.fim) is int
        and escala.inicio < escala.fim
    )
    if not limites_validos:
        _rejeitar(Motivo.ESCALA_INVALIDA, elemento, f"escala {escala!r}")
    return {
        "escala_inicio": escala.inicio,
        "escala_fim": escala.fim,
        "escala_rotulo_inicio": _texto_opcional(escala.rotulo_inicio, elemento),
        "escala_rotulo_fim": _texto_opcional(escala.rotulo_fim, elemento),
    }


def adicionar_pergunta(
    secao: Secao,
    posicao: int,
    tipo,
    texto: str,
    *,
    obrigatoria: bool,
    texto_explicativo=None,
    escala=None,
) -> Pergunta:
    with transaction.atomic():
        secao = _bloqueado(Secao, secao.pk, "versao_id")
        _posicao_livre(secao.perguntas.all(), _posicao(posicao, secao.id), secao.id)
        tipo = _tipo(tipo, secao.id)
        return Pergunta.objects.create(
            secao=secao,
            posicao=posicao,
            tipo=tipo,
            texto=_texto_obrigatorio(texto, secao.id),
            texto_explicativo=_texto_opcional(texto_explicativo, secao.id),
            obrigatoria=_booleano(obrigatoria, "obrigatoria"),
            **_configuracao_escala(tipo, escala, secao.id),
        )


def alterar_pergunta(
    pergunta: Pergunta,
    *,
    texto=_MANTER,
    texto_explicativo=_MANTER,
    obrigatoria=_MANTER,
    escala=_MANTER,
) -> Pergunta:
    # Não há parâmetro de tipo: o tipo é definido na criação (FR-062).
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        campos = []
        if texto is not _MANTER:
            pergunta.texto = _texto_obrigatorio(texto, pergunta.id)
            campos.append("texto")
        if texto_explicativo is not _MANTER:
            pergunta.texto_explicativo = _texto_opcional(texto_explicativo, pergunta.id)
            campos.append("texto_explicativo")
        if obrigatoria is not _MANTER:
            pergunta.obrigatoria = _booleano(obrigatoria, "obrigatoria")
            campos.append("obrigatoria")
        if escala is not _MANTER:
            configuracao = _configuracao_escala(pergunta.tipo, escala, pergunta.id)
            for campo, valor in configuracao.items():
                setattr(pergunta, campo, valor)
            campos.extend(configuracao)
        pergunta.save(update_fields=campos)
    return pergunta


def mover_pergunta(pergunta: Pergunta, secao_destino: Secao, posicao: int) -> Pergunta:
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        secao_destino = _secao_da_versao(secao_destino, pergunta.secao.versao_id)
        ocupadas = secao_destino.perguntas.exclude(pk=pergunta.pk)
        _posicao_livre(ocupadas, _posicao(posicao, pergunta.id), pergunta.id)
        pergunta.secao = secao_destino
        pergunta.posicao = posicao
        pergunta.save(update_fields=["secao", "posicao"])
    return pergunta


def remover_pergunta(pergunta: Pergunta) -> None:
    # Remove também as Opções e suas regras (FR-061).
    with transaction.atomic():
        _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao").delete()


def reordenar_perguntas(secao: Secao, perguntas_em_ordem) -> None:
    with transaction.atomic():
        secao = _bloqueado(Secao, secao.pk, "versao_id")
        _reordenar(secao.perguntas.all(), perguntas_em_ordem, secao.id)


# --- Opção ----------------------------------------------------------------------------

_TIPOS_DE_ESCOLHA = (TipoPergunta.ESCOLHA_UNICA, TipoPergunta.ESCOLHA_MULTIPLA)


def _texto_de_opcao_livre(pergunta: Pergunta, texto: str, exceto: UUID | None) -> None:
    if pergunta.opcoes.filter(texto=texto).exclude(pk=exceto).exists():
        _rejeitar(Motivo.OPCAO_REPETIDA, exceto or pergunta.id, f"texto {texto!r}")


def _complemento_livre(pergunta: Pergunta, exceto: UUID | None) -> None:
    if pergunta.opcoes.filter(complemento_textual=True).exclude(pk=exceto).exists():
        _rejeitar(Motivo.COMPLEMENTO_REPETIDO, exceto or pergunta.id, "já há Opção com complemento")


def adicionar_opcao(
    pergunta: Pergunta, posicao: int, texto: str, *, complemento_textual: bool = False
) -> Opcao:
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        if pergunta.tipo not in _TIPOS_DE_ESCOLHA:
            _rejeitar(Motivo.OPCAO_EM_TIPO_SEM_OPCOES, pergunta.id, f"tipo {pergunta.tipo}")
        _posicao_livre(pergunta.opcoes.all(), _posicao(posicao, pergunta.id), pergunta.id)
        _texto_de_opcao_livre(pergunta, _texto_obrigatorio(texto, pergunta.id), None)
        if _booleano(complemento_textual, "complemento_textual"):
            _complemento_livre(pergunta, None)
        return Opcao.objects.create(
            pergunta=pergunta,
            posicao=posicao,
            texto=texto,
            complemento_textual=complemento_textual,
        )


def alterar_opcao(opcao: Opcao, *, texto=_MANTER, complemento_textual=_MANTER) -> Opcao:
    # A identidade e a regra da Opção não mudam com o texto (FR-041).
    with transaction.atomic():
        opcao = _bloqueado(Opcao, opcao.pk, "pergunta__secao__versao_id", "pergunta")
        campos = []
        if texto is not _MANTER:
            _texto_de_opcao_livre(opcao.pergunta, _texto_obrigatorio(texto, opcao.id), opcao.id)
            opcao.texto = texto
            campos.append("texto")
        if complemento_textual is not _MANTER:
            if _booleano(complemento_textual, "complemento_textual"):
                _complemento_livre(opcao.pergunta, opcao.id)
            opcao.complemento_textual = complemento_textual
            campos.append("complemento_textual")
        opcao.save(update_fields=campos)
    return opcao


def remover_opcao(opcao: Opcao) -> None:
    # A regra está na própria Opção e sai com ela (FR-061).
    with transaction.atomic():
        _bloqueado(Opcao, opcao.pk, "pergunta__secao__versao_id", "pergunta").delete()


def reordenar_opcoes(pergunta: Pergunta, opcoes_em_ordem) -> None:
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        _reordenar(pergunta.opcoes.all(), opcoes_em_ordem, pergunta.id)


# --- Regra de navegação condicional ---------------------------------------------------


class Finalizar:
    """Destino "finalizar o instrumento". Use a sentinela única `FINALIZAR`."""

    def __repr__(self) -> str:
        return "FINALIZAR"


FINALIZAR = Finalizar()


def definir_regra(pergunta: Pergunta, opcao: Opcao, destino: Secao | Finalizar) -> Opcao:
    """"Se `pergunta` = `opcao`, ir para `destino`" ou "…, finalizar" (FR-050). A regra
    pertence à Pergunta e à Opção, não à Seção; o momento em que é aplicada na jornada não
    é modelado (FR-053)."""
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        if pergunta.tipo != TipoPergunta.ESCOLHA_UNICA:
            _rejeitar(Motivo.REGRA_EM_TIPO_INCOMPATIVEL, pergunta.id, f"tipo {pergunta.tipo}")
        opcao = _opcao_da_pergunta(pergunta, opcao)
        if destino is not FINALIZAR:
            # Para limpar a regra use remover_regra; None não é destino.
            destino = _secao_da_versao(destino, pergunta.secao.versao_id)
        if opcao.tem_regra:
            _rejeitar(Motivo.REGRA_JA_DEFINIDA, opcao.id, "remova a regra antes")
        if destino is FINALIZAR:
            opcao.regra_finaliza = True
        else:
            opcao.regra_destino = destino
        opcao.save(update_fields=["regra_destino", "regra_finaliza"])
    return opcao


def remover_regra(pergunta: Pergunta, opcao: Opcao) -> Opcao:
    """A Opção volta ao fluxo padrão. Sem regra, nada muda."""
    with transaction.atomic():
        pergunta = _bloqueado(Pergunta, pergunta.pk, "secao__versao_id", "secao")
        opcao = _opcao_da_pergunta(pergunta, opcao)
        opcao.regra_destino = None
        opcao.regra_finaliza = False
        opcao.save(update_fields=["regra_destino", "regra_finaliza"])
    return opcao


def _opcao_da_pergunta(pergunta: Pergunta, opcao: Opcao) -> Opcao:
    opcao = Opcao.objects.get(pk=opcao.pk)
    if opcao.pergunta_id != pergunta.id:
        _rejeitar(Motivo.OPCAO_DE_OUTRA_PERGUNTA, opcao.id, "a Opção não é desta Pergunta")
    return opcao

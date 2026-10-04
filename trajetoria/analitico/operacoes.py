"""Captura do snapshot analítico (contracts/operacoes.md). Único caminho de escrita do app.

**Atomicidade**: o snapshot e **todos** os seus registros são gravados numa transação, ou
nada é (spec FR-052). Sem estado "processando" ou "falhou".

**Corte histórico**: os valores efetivamente lidos e copiados pela captura (spec FR-054).
Não há leitura isolada entre as consultas, nível de isolamento mais forte nem lock: com a
Campanha encerrada, a 004/005/006 já bloqueiam novas escritas de Participação e Resposta.
Uma escrita concorrente iniciada antes do encerramento e confirmada depois da leitura é
detectada pela verificação final, que desfaz a captura inteira; ela pode ser repetida.

**Momento**: `capturado_em` é lido do relógio pela própria operação, uma vez, e é o mesmo
instante usado para verificar o estado da Campanha. Desvio consciente do padrão `agora=` das
operações da 004 e da 005: aqui o instante é o dado histórico gravado e não pode ser
escolhido pelo chamador (spec FR-016; research R8). É o momento técnico da captura, não o
instante de uma leitura isolada.

**Elegibilidade**: só pelo contrato público da 004, `populacao_no_momento`; nenhum critério da
Campanha é lido aqui (spec FR-020; research R7).

**Exposição**: nenhuma rota, view, command ou regra de governança chama esta operação nesta
feature. Quando houver exposição institucional, a competência (CPAEG; spec FR-102) precisará
ser aplicada por quem expuser (research R14).
"""

from django.db import transaction

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.analitico.regras import CapturaInconsistente, Motivo, SnapshotRecusado
from trajetoria.campanha.consultas import (
    EstadoCampanha,
    estado,
    momento_de_referencia,
    populacao_no_momento,
)
from trajetoria.campanha.models import Campanha
from trajetoria.fonte_academica.acervo_historico import CODIGO as ACERVO_HISTORICO
from trajetoria.fonte_academica.contrato import CAMPOS_DE_CONTEXTO
from trajetoria.instrumento.models import EstadoVersao, Versao
from trajetoria.participacao.consultas import participacoes_oficiais

__all__ = ["capturar_snapshot"]

_LOTE = 1000  # batch_size do bulk_create; sem framework de lotes


def capturar_snapshot(campanha: Campanha) -> SnapshotAnalitico:
    """Cria e devolve o snapshot completo da Campanha (contracts/operacoes.md, "Passos")."""
    if not isinstance(campanha, Campanha):
        raise TypeError(f"campanha deve ser Campanha, não {type(campanha).__name__}")
    with transaction.atomic():
        capturado_em = momento_de_referencia(None)
        campanha = Campanha.objects.filter(pk=campanha.pk).first()
        if campanha is None:
            raise ValueError("campanha não está gravada")
        _exigir_captura_permitida(campanha, capturado_em)
        if Versao.objects.get(pk=campanha.versao_id).estado != EstadoVersao.PUBLICADA:
            raise CapturaInconsistente(f"a Versão da Campanha {campanha.pk} não está publicada")
        universo = _universo(campanha)
        participantes = _participantes_por_conclusao(campanha)
        if participantes.keys() - universo.keys():
            raise CapturaInconsistente("Participação oficial fora do universo lido.")
        snapshot = SnapshotAnalitico.objects.create(campanha=campanha, capturado_em=capturado_em)
        RegistroDoSnapshot.objects.bulk_create(
            (
                RegistroDoSnapshot(
                    snapshot=snapshot,
                    conclusao_id=pk,
                    elegivel_no_snapshot=elegivel,
                    participacao=participantes.get(pk),
                    origem_formacao=_origem(participantes.get(pk)),
                    **dict(zip(CAMPOS_DE_CONTEXTO, contexto, strict=True)),
                )
                for pk, (elegivel, contexto) in universo.items()
            ),
            batch_size=_LOTE,
        )
        _verificar(campanha, snapshot)
    return snapshot


def _exigir_captura_permitida(campanha: Campanha, capturado_em) -> None:
    """Só Campanha que entrou em coleta e já não está em coleta, pelos fatos da 004
    (`aberta_em` diz se houve coleta; 004 FR-040). Nunca aberta vem primeiro, para que a
    expirada sem abertura receba o motivo certo (spec FR-010 a FR-013; research R10)."""
    if campanha.aberta_em is None:
        raise SnapshotRecusado(Motivo.CAMPANHA_NUNCA_ABERTA, campanha.pk)
    if estado(campanha, agora=capturado_em) is not EstadoCampanha.ENCERRADA:
        raise SnapshotRecusado(Motivo.COLETA_NAO_ENCERRADA, campanha.pk)


def _elegiveis(campanha: Campanha):
    """A população da Campanha segundo a 004, com o contexto lido."""
    return populacao_no_momento(campanha).order_by().values_list("pk", *CAMPOS_DE_CONTEXTO)


def _participantes(campanha: Campanha) -> set:
    """As Conclusões com Participação na Campanha, só pelo `pk`."""
    return set(
        participacoes_oficiais()
        .filter(campanha=campanha)
        .values_list("conclusao_efetiva_id", flat=True)
    )


def _universo(campanha: Campanha) -> dict:
    """`pk da Conclusão → (elegível no snapshot, contexto)`. Elegíveis primeiro (`True`); as
    Conclusões com Participação que não estão entre elas entram como não elegíveis
    (`False`), e só delas o contexto é lido de novo. Deduplicado por Conclusão, nunca por
    Pessoa (spec FR-030 a FR-033)."""
    universo = {pk: (True, tuple(contexto)) for pk, *contexto in _elegiveis(campanha)}
    fora_da_populacao = _participantes(campanha) - universo.keys()
    if fora_da_populacao:
        lidas = ConclusaoAcademica.objects.filter(pk__in=fora_da_populacao).order_by()
        for pk, *contexto in lidas.values_list("pk", *CAMPOS_DE_CONTEXTO):
            universo[pk] = (False, tuple(contexto))
    return universo


def _verificar(campanha: Campanha, snapshot: SnapshotAnalitico) -> None:
    """Verificação de integridade na mesma transação (spec FR-053 d): toda Participação da
    Campanha tem registro. Detecta a escrita concorrente iniciada antes do encerramento e
    confirmada depois da leitura do universo. O total de registros (FR-053 c) não precisa de
    verificação: o `bulk_create` grava todos ou levanta, e o `UNIQUE (snapshot, conclusao)`
    impede duplicata."""
    # Só os registros com Participação: um `participacao_id` NULL dentro do `NOT IN` tornaria
    # a comparação desconhecida para todas as linhas e a verificação nunca contaria nada.
    congeladas = RegistroDoSnapshot.objects.filter(
        snapshot=snapshot, participacao__isnull=False
    ).values("participacao_id")
    sem_registro = (
        participacoes_oficiais().filter(campanha=campanha).exclude(pk__in=congeladas).count()
    )
    if sem_registro:
        raise CapturaInconsistente(
            f"snapshot {snapshot.pk}: {sem_registro} Participação(ões) da Campanha "
            f"{campanha.pk} sem registro"
        )


def _participantes_por_conclusao(campanha: Campanha) -> dict:
    """`Conclusão efetiva → Participação oficial`. Duas oficiais com a mesma Conclusão efetiva
    na Campanha violam 019 FR-093; a captura recusa em vez de congelar só uma delas."""
    participantes = {}
    oficiais = (
        participacoes_oficiais()
        .filter(campanha=campanha)
        .select_related("formacao_declarada__validacao__conclusao")
    )
    for p in oficiais:
        if p.conclusao_efetiva_id in participantes:
            raise CapturaInconsistente(
                f"Campanha {campanha.pk}: mais de uma Participação oficial para a Conclusão "
                f"{p.conclusao_efetiva_id}"
            )
        participantes[p.conclusao_efetiva_id] = p
    return participantes


def _origem(participacao):
    if participacao is None:
        return None
    if participacao.conclusao_id:
        return "institucional"
    if participacao.formacao_declarada.validacao.conclusao.fonte == ACERVO_HISTORICO:
        return "declarada_validada_acervo"
    return "declarada_validada_fonte_digital"

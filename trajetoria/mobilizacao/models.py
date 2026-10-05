"""Lote de Mobilização e seus membros (Feature 020; data-model §§2–3).

O Lote é uma onda operacional de abordagem dentro de uma Campanha. **Não é população**,
não altera a abrangência e não participa da admissão (ADR 0004). Nasce congelado (E3):
filtros, escopo e membros nunca mudam depois de gravados. Não tem estado próprio — a
situação é derivada dos membros (FR-031).

`MembroDoLote.campanha` repete a Campanha do Lote só para a restrição
`membro_uma_abordagem_por_campanha` (research R6): no máximo uma abordagem por Pessoa e
Campanha, garantida pelo banco (FR-024, FR-025).
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Q

from trajetoria.academico.models import Pessoa
from trajetoria.campanha.models import Campanha
from trajetoria.contato.models import ContatoDaPessoa


class LoteDeMobilizacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campanha = models.ForeignKey(Campanha, on_delete=models.PROTECT, related_name="+")
    nome = models.CharField(max_length=120)
    # Filtros; NULL significa "sem filtro".
    unidades = ArrayField(models.TextField(), null=True)
    nivel = models.TextField(null=True)
    ano_minimo = models.PositiveSmallIntegerField(null=True)
    ano_maximo = models.PositiveSmallIntegerField(null=True)
    curso = models.TextField(null=True)
    # Escopo do operador na confirmação.
    escopo_institucional = models.BooleanField()
    escopo_unidades = ArrayField(models.TextField(), default=list)
    excluidas_por_mobilizacao = models.PositiveIntegerField(default=0)
    confirmado_em = models.DateTimeField()
    operador = models.TextField()

    class Meta:
        ordering = ["-confirmado_em", "pk"]
        constraints = [
            models.CheckConstraint(condition=~Q(nome=""), name="lote_nome_nao_vazio"),
            models.CheckConstraint(condition=~Q(operador=""), name="lote_operador_nao_vazio"),
            models.CheckConstraint(
                condition=Q(unidades__isnull=True) | ~Q(unidades=[]),
                name="lote_unidades_nulo_ou_nao_vazio",
            ),
            models.CheckConstraint(condition=~Q(nivel=""), name="lote_nivel_nao_vazio"),
            models.CheckConstraint(condition=~Q(curso=""), name="lote_curso_nao_vazio"),
            models.CheckConstraint(
                condition=Q(ano_minimo__isnull=True)
                | Q(ano_maximo__isnull=True)
                | Q(ano_minimo__lte=F("ano_maximo")),
                name="lote_anos_coerentes",
            ),
            models.CheckConstraint(
                condition=Q(escopo_institucional=True, escopo_unidades=[])
                | (
                    Q(escopo_institucional=False, unidades__isnull=False)
                    & ~Q(escopo_unidades=[])
                ),
                name="lote_escopo_coerente",
            ),
        ]

    def __str__(self) -> str:
        return f"Lote {self.pk}"


class SituacaoDoMembro(models.TextChoices):
    SEM_CONTATO = "SEM_CONTATO", "Sem contato"
    NAO_TENTADO = "NAO_TENTADO", "Não tentado"
    EM_TENTATIVA = "EM_TENTATIVA", "Em tentativa"  # sobrevivendo à ação: resultado incerto
    SUBMETIDO_AO_TRANSPORTE = "SUBMETIDO_AO_TRANSPORTE", "Submetido ao transporte"
    FALHA_DE_TRANSPORTE = "FALHA_DE_TRANSPORTE", "Falha de transporte"


_S = SituacaoDoMembro
_FINAIS = [_S.SUBMETIDO_AO_TRANSPORTE, _S.FALHA_DE_TRANSPORTE]


class MembroDoLote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lote = models.ForeignKey(LoteDeMobilizacao, on_delete=models.PROTECT, related_name="membros")
    campanha = models.ForeignKey(Campanha, on_delete=models.PROTECT, related_name="+")
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="+")
    contato = models.ForeignKey(
        ContatoDaPessoa, on_delete=models.PROTECT, null=True, related_name="+"
    )
    situacao = models.TextField(choices=SituacaoDoMembro.choices)
    tentativa_iniciada_em = models.DateTimeField(null=True)
    resultado_em = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lote", "pessoa"], name="membro_unico_no_lote"),
            models.UniqueConstraint(
                fields=["campanha", "pessoa"],
                condition=~Q(situacao=_S.SEM_CONTATO),
                name="membro_uma_abordagem_por_campanha",
            ),
            models.CheckConstraint(
                condition=Q(situacao__in=[s.value for s in SituacaoDoMembro]),
                name="membro_situacao_conhecida",
            ),
            models.CheckConstraint(
                condition=Q(situacao=_S.SEM_CONTATO, contato__isnull=True)
                | (~Q(situacao=_S.SEM_CONTATO) & Q(contato__isnull=False)),
                name="membro_sem_contato_coerente",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        situacao__in=[_S.SEM_CONTATO, _S.NAO_TENTADO],
                        tentativa_iniciada_em__isnull=True,
                        resultado_em__isnull=True,
                    )
                    | Q(
                        situacao=_S.EM_TENTATIVA,
                        tentativa_iniciada_em__isnull=False,
                        resultado_em__isnull=True,
                    )
                    | Q(
                        situacao__in=_FINAIS,
                        tentativa_iniciada_em__isnull=False,
                        resultado_em__isnull=False,
                        resultado_em__gte=F("tentativa_iniciada_em"),
                    )
                ),
                name="membro_instantes_coerentes",
            ),
        ]

    def __str__(self) -> str:
        return f"Membro {self.pk} ({self.situacao})"

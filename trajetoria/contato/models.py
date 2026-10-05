"""Contato da Pessoa (Feature 020; data-model §1).

App próprio: nenhum app da 001, 018, 019, 021 ou 022 o importa (research R9, C5). O registro
é imutável — nenhuma operação o altera ou remove (FR-002; retenção é DP-2006). Uma
"observação" da fonte é o conjunto dos registros de mesma Pessoa, fonte e `obtido_em`
(research R2).

`valor` é legível **somente na demonstração** (E2). Antes do uso real, a proteção em
repouso é revista e registrada (DP-2010, Gate B); o ponto de troca é este campo e as duas
operações que o leem (research R9, C1).
"""

import uuid

from django.db import models
from django.db.models import Q

from trajetoria.academico.models import Pessoa


class Canal(models.TextChoices):
    EMAIL = "EMAIL", "E-mail"  # único canal da 020 (E1; DP-2009)


class Origem(models.TextChoices):
    FONTE_ACADEMICA = "FONTE_ACADEMICA", "Fonte acadêmica"  # dado institucional
    EGRESSO = "EGRESSO", "Informado pelo egresso"  # dado declarado


class ContatoDaPessoa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="+")
    canal = models.TextField(choices=Canal.choices, default=Canal.EMAIL)
    valor = models.CharField(max_length=254)
    origem = models.TextField(choices=Origem.choices)
    fonte = models.TextField(null=True)
    posicao = models.PositiveSmallIntegerField(null=True)
    obtido_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(canal=Canal.EMAIL), name="contato_canal_email"
            ),
            models.CheckConstraint(
                condition=Q(origem__in=[Origem.FONTE_ACADEMICA, Origem.EGRESSO]),
                name="contato_origem_conhecida",
            ),
            models.CheckConstraint(
                condition=(
                    Q(origem=Origem.FONTE_ACADEMICA, fonte__isnull=False, posicao__isnull=False)
                    | Q(origem=Origem.EGRESSO, fonte__isnull=True, posicao__isnull=True)
                ),
                name="contato_proveniencia_coerente",
            ),
            models.CheckConstraint(condition=~Q(valor=""), name="contato_valor_nao_vazio"),
            models.CheckConstraint(condition=~Q(fonte=""), name="contato_fonte_nao_vazia"),
            models.UniqueConstraint(
                fields=["pessoa", "fonte", "obtido_em", "posicao"],
                condition=Q(origem=Origem.FONTE_ACADEMICA),
                name="contato_observacao_unica",
            ),
        ]
        indexes = [
            models.Index(fields=["pessoa", "origem", "obtido_em"], name="contato_politica_idx"),
        ]

    def __str__(self) -> str:
        # Nunca o endereço (Observabilidade; research R9, C3).
        return f"Contato {self.origem} {self.pk}"

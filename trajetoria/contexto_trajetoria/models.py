"""Complemento da Conclusão e contexto institucional agregado (Feature 021, P2;
data-model §2).

App próprio: nenhum app da 001, 018 ou 019 o importa (FR-071). Os dois registros vêm só
da capacidade de contexto da trajetória, nunca são calculados da base local (FR-055) e
nunca são atualizados nem removidos: uma divergência é sinalizada, e uma nova apuração é um
registro novo (FR-048, FR-056).
"""

import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import ExtractYear

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.fonte_academica.contexto_da_trajetoria import MetricaAgregada


def _nao_vazio(campo: str, nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


class ComplementoDaConclusao(models.Model):
    """Ingresso na matrícula que resultou na Conclusão. A fonte é a da própria Conclusão.
    Fora do contexto fundamental: não entra em snapshot, exportação nem critérios (FR-047)."""

    conclusao = models.OneToOneField(
        ConclusaoAcademica, on_delete=models.PROTECT, primary_key=True,
        related_name="complemento",
    )
    ano_ingresso = models.PositiveSmallIntegerField()
    data_ingresso = models.DateField(null=True)
    obtido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(data_ingresso__isnull=True)
                | Q(ano_ingresso=ExtractYear("data_ingresso")),
                name="complemento_ano_coerente_com_data",
            ),
        ]


class MetricaDoAgregado(models.TextChoices):
    CONCLUSOES_CURSO_UNIDADE_ANO = (
        MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO.value, "Conclusões do curso na unidade no ano"
    )
    CONCLUSOES_UNIDADE_ANO = (
        MetricaAgregada.CONCLUSOES_UNIDADE_ANO.value, "Conclusões da unidade no ano"
    )


class ContextoInstitucionalAgregado(models.Model):
    """Fato sobre um grupo: não pertence a nenhuma Pessoa nem Conclusão (FR-052). Um
    registro por fonte, métrica, recorte e apuração, compartilhado pelas narrativas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fonte = models.TextField()
    metrica = models.TextField(choices=MetricaDoAgregado.choices)
    curso = models.TextField(null=True)
    unidade = models.TextField()
    ano = models.PositiveSmallIntegerField()
    valor = models.PositiveIntegerField()
    apurado_em = models.DateField()
    obtido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fonte", "metrica", "curso", "unidade", "ano", "apurado_em"],
                nulls_distinct=False,
                name="agregado_chave_unica",
            ),
            models.CheckConstraint(
                condition=(
                    Q(metrica=MetricaDoAgregado.CONCLUSOES_CURSO_UNIDADE_ANO, curso__isnull=False)
                    | Q(metrica=MetricaDoAgregado.CONCLUSOES_UNIDADE_ANO, curso__isnull=True)
                ),
                name="agregado_curso_conforme_metrica",
            ),
            _nao_vazio("fonte", "agregado_fonte_nao_vazio"),
            _nao_vazio("curso", "agregado_curso_nao_vazio"),
            _nao_vazio("unidade", "agregado_unidade_nao_vazio"),
        ]

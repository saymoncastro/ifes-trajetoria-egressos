"""Declaração imutável, decisão administrativa e dados separáveis para consulta."""

import uuid

from django.db import models
from django.db.models import F, Q
from django.db.models.functions import ExtractYear


def nao_vazio(campo, nome):
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


class FormacaoDeclarada(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.TextField()
    unidade = models.TextField()
    nivel = models.TextField()
    curso = models.TextField()
    ano_conclusao = models.PositiveSmallIntegerField()
    identificador_cpf = models.CharField(max_length=64, db_index=True)
    verificador = models.CharField(max_length=64, db_index=True)
    chave_de_criacao = models.UUIDField(unique=True)
    declarada_em = models.DateTimeField()

    class Meta:
        ordering = ["declarada_em", "id"]
        constraints = [
            nao_vazio(c, f"declaracao_{c}_nao_vazio") for c in ("nome", "unidade", "nivel", "curso")
        ] + [
            models.CheckConstraint(
                condition=Q(identificador_cpf__regex=r"^[0-9a-f]{64}$"), name="declaracao_cpf_hex"
            ),
            models.CheckConstraint(
                condition=Q(verificador__regex=r"^[0-9a-f]{64}$"), name="declaracao_par_hex"
            ),
        ]

    def __str__(self):
        return f"Declaração {self.pk}"


class DadosConsultaAcervo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formacao = models.OneToOneField(
        FormacaoDeclarada, on_delete=models.PROTECT, related_name="dados_consulta"
    )
    selado = models.TextField()

    def __str__(self):
        return f"Dados de consulta {self.pk}"


class ValidacaoDaFormacao(models.Model):
    class Resultado(models.TextChoices):
        CONFIRMADA = "CONFIRMADA", "Formação confirmada"
        NAO_CONFIRMADA = "NAO_CONFIRMADA", "Formação não confirmada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formacao = models.OneToOneField(
        FormacaoDeclarada, on_delete=models.PROTECT, related_name="validacao"
    )
    resultado = models.CharField(max_length=14, choices=Resultado.choices)
    conclusao = models.ForeignKey(
        "academico.ConclusaoAcademica", null=True, on_delete=models.PROTECT, related_name="+"
    )
    fora_da_abrangencia_na_validacao = models.BooleanField()
    conflito_detectado_na_validacao = models.BooleanField()
    registrada_em = models.DateTimeField()
    operador = models.TextField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(resultado="CONFIRMADA", conclusao__isnull=False)
                    | Q(resultado="NAO_CONFIRMADA", conclusao__isnull=True)
                ),
                name="validacao_conclusao_confirmada",
            ),
            models.CheckConstraint(
                condition=(
                    Q(resultado="CONFIRMADA")
                    | Q(
                        fora_da_abrangencia_na_validacao=False,
                        conflito_detectado_na_validacao=False,
                    )
                ),
                name="validacao_nao_confirmada_sem_fatos",
            ),
            models.CheckConstraint(
                condition=(
                    Q(conflito_detectado_na_validacao=False)
                    | Q(fora_da_abrangencia_na_validacao=False)
                ),
                name="validacao_conflito_compativel",
            ),
        ]

    def __str__(self):
        return f"Validação {self.pk}"


class AcessoAosDadosDeConsulta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formacao = models.ForeignKey(FormacaoDeclarada, on_delete=models.PROTECT, related_name="+")
    operador = models.TextField()
    acessado_em = models.DateTimeField()

    def __str__(self):
        return f"Acesso aos dados {self.pk}"


class ReferenciaDeAcervo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unidade = models.TextField()
    referencia = models.TextField()
    nivel = models.TextField()
    curso = models.TextField()
    ano_conclusao = models.PositiveSmallIntegerField()
    modalidade = models.TextField(null=True)
    forma_oferta = models.TextField(null=True)
    data_conclusao = models.DateField(null=True)
    registrada_em = models.DateTimeField()
    operador = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["unidade", "referencia"], name="acervo_referencia_unica"
            ),
            models.CheckConstraint(
                condition=(
                    Q(data_conclusao__isnull=True)
                    | Q(ano_conclusao=ExtractYear(F("data_conclusao")))
                ),
                name="acervo_ano_coerente",
            ),
        ] + [
            nao_vazio(c, f"acervo_{c}_nao_vazio")
            for c in ("unidade", "referencia", "nivel", "curso", "modalidade", "forma_oferta")
        ]

    def __str__(self):
        return f"Referência de acervo {self.pk}"

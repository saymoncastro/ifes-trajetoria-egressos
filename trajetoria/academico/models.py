"""Pessoa e Conclusão Acadêmica (specs/001-nucleo-academico-fonte-simulada/data-model.md).

Atributo `NULL` significa "não informado pela fonte". Todo atributo acadêmico é
institucional: não há campo declarado nem derivado.
"""

import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import ExtractYear


def _nao_vazio(campo: str, nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


class Pessoa(models.Model):
    """Indivíduo único no NIAE. Não tem atributos acadêmicos (FR-003); nome é só
    apresentação e não participa de identidade nem de deduplicação (FR-005)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fonte = models.TextField()
    id_externo = models.TextField()
    nome = models.TextField(null=True)
    incorporado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["fonte", "id_externo"], name="pessoa_origem_unica"),
            _nao_vazio("fonte", "pessoa_fonte_nao_vazio"),
            _nao_vazio("id_externo", "pessoa_id_externo_nao_vazio"),
            _nao_vazio("nome", "pessoa_nome_nao_vazio"),
        ]

    def __str__(self) -> str:
        return f"Pessoa {self.fonte}:{self.id_externo}"


class ConclusaoAcademica(models.Model):
    """Fato institucional: a Pessoa concluiu uma formação em dado contexto e período."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="conclusoes")
    fonte = models.TextField()
    id_externo = models.TextField()
    curso = models.TextField(null=True)
    unidade = models.TextField(null=True)
    nivel = models.TextField(null=True)
    modalidade = models.TextField(null=True)
    forma_oferta = models.TextField(null=True)
    ano_conclusao = models.PositiveSmallIntegerField(null=True)
    data_conclusao = models.DateField(null=True)
    incorporado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordem só de apresentação, sem significado de domínio (FR-017).
        ordering = ["ano_conclusao", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["fonte", "id_externo"], name="conclusao_origem_unica"
            ),
            *(
                _nao_vazio(campo, f"conclusao_{campo}_nao_vazio")
                for campo in (
                    "fonte",
                    "id_externo",
                    "curso",
                    "unidade",
                    "nivel",
                    "modalidade",
                    "forma_oferta",
                )
            ),
            # Com data, o ano é obrigatório e é o ano da data (FR-011). O IS NOT NULL é
            # explícito: sem ele, ano NULL daria UNKNOWN, que o CHECK aceita.
            models.CheckConstraint(
                condition=Q(data_conclusao__isnull=True)
                | (
                    Q(ano_conclusao__isnull=False)
                    & Q(ano_conclusao=ExtractYear("data_conclusao"))
                ),
                name="conclusao_ano_coerente_com_data",
            ),
        ]

    def __str__(self) -> str:
        return f"Conclusão {self.fonte}:{self.id_externo}"

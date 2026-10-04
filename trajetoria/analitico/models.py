"""Snapshot analítico e seus registros (specs/012-dataset-analitico-reprodutivel/data-model.md).

Só o que deriva é persistido (research R1): o pertencimento ao universo (a existência do
registro), a elegibilidade no momento da captura e o contexto acadêmico da Conclusão naquele
momento. Campanha, Versão, Participação e Respostas são referenciadas na leitura.

O contexto é **institucional, no momento da captura** (spec FR-044); `NULL` = não informado.
Os sete campos são `CAMPOS_DE_CONTEXTO` da 001, com os mesmos tipos. Ano e data são
atributos independentes (a fonte pode dar só o ano; research R4). Nenhum CHECK da 001 é
repetido: a cópia não rejeita nem reinterpreta o que a origem guarda (research R5).

`on_delete` (research R6):

- Conclusão `PROTECT`: preserva a rastreabilidade e a associação com os fatos transacionais.
  Uma eliminação futura de Conclusão referenciada falha até decisão explícita de retenção
  (DP-1202); nenhuma operação sobre a origem destrói snapshot em silêncio (spec FR-048).
- Campanha `PROTECT`: só Campanha nunca aberta é removível, e ela nunca tem snapshot.
- Snapshot → registros `CASCADE`: o registro é parte do snapshot; se um dia um snapshot for
  removido por decisão de retenção, sai inteiro, sem órfãos.

Escrita só por `operacoes.py`; nenhuma operação altera ou remove (spec FR-050; ADR 0002).
"""

import uuid

from django.db import models
from django.db.models import Q


class SnapshotAnalitico(models.Model):
    """Fotografia imutável de uma Campanha encerrada que entrou em coleta. Vários por
    Campanha, sem status (spec FR-060, FR-061)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campanha = models.ForeignKey("campanha.Campanha", on_delete=models.PROTECT, related_name="+")
    # Momento técnico da captura, gravado só pela operação; sem `default` nem
    # `auto_now_add`, para que nenhuma criação fora da operação passe despercebida.
    capturado_em = models.DateTimeField()

    class Meta:
        # Só determinismo, sem significado de autoridade (spec FR-063).
        ordering = ["capturado_em", "id"]

    def __str__(self) -> str:
        return f"Snapshot {self.id}"


class RegistroDoSnapshot(models.Model):
    """Uma Conclusão Acadêmica no universo de um snapshot (spec FR-030, FR-031)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot = models.ForeignKey(
        SnapshotAnalitico, on_delete=models.CASCADE, related_name="registros"
    )
    # Referência técnica interna; não é identificador exportável (spec FR-047).
    conclusao = models.ForeignKey(
        "academico.ConclusaoAcademica", on_delete=models.PROTECT, related_name="+"
    )
    class OrigemFormacao(models.TextChoices):
        INSTITUCIONAL = "institucional"
        FONTE_DIGITAL = "declarada_validada_fonte_digital"
        ACERVO = "declarada_validada_acervo"

    participacao = models.ForeignKey(
        "participacao.Participacao", null=True, on_delete=models.PROTECT, related_name="+"
    )
    origem_formacao = models.CharField(max_length=40, null=True, choices=OrigemFormacao.choices)
    # Resultado congelado da 004 no momento da captura; sem default (spec FR-021).
    elegivel_no_snapshot = models.BooleanField()
    curso = models.TextField(null=True)
    unidade = models.TextField(null=True)
    nivel = models.TextField(null=True)
    modalidade = models.TextField(null=True)
    forma_oferta = models.TextField(null=True)
    ano_conclusao = models.PositiveSmallIntegerField(null=True)
    data_conclusao = models.DateField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(participacao__isnull=True, origem_formacao__isnull=True)
                    | Q(participacao__isnull=False, origem_formacao__in=[
                        "institucional", "declarada_validada_fonte_digital",
                        "declarada_validada_acervo"])),
                name="registro_origem_com_participacao",
            ),
            models.UniqueConstraint(
                fields=["snapshot", "conclusao"], name="registro_conclusao_unica_no_snapshot"
            ),
        ]

    def __str__(self) -> str:
        return f"Registro {self.id}"

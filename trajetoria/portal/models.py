"""Oportunidade (Feature 025; data-model.md; research R1).

Primeiro fato persistente da camada de relacionamento (Constituição 2.1.0, "Camada de
relacionamento"; ADR 0008). Não tem chave estrangeira para o núcleo: a ligação com a Pessoa
só existe na consulta, pela regra de pertinência (FR-012).

Não há coluna de estado: ele é derivado de `publicada_em`, `retirada_em` e das datas
(`oportunidades.regras.estado`; FR-009). `NULL` nas listas de público = critério ausente;
`[]` e `""` são inválidos e nunca gravados. Regras que dependem de tempo ou escopo ficam em
`oportunidades/operacoes.py`, único caminho de escrita.
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Length
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

TITULO_MAXIMO = 120
RESUMO_MAXIMO = 300
CRITERIOS_DE_PUBLICO = ("publico_unidades", "publico_niveis", "publico_cursos")


class Categoria(models.TextChoices):
    """Lista fechada e provisória (FR-003; DP-2505). Só apresentação."""

    CURSOS = "cursos", "Cursos e formação continuada"
    EVENTOS = "eventos", "Eventos"
    PESQUISA_EXTENSAO = "pesquisa_extensao", "Pesquisa e extensão"
    CARREIRA = "carreira", "Carreira e empregabilidade"
    EMPREENDEDORISMO = "empreendedorismo", "Empreendedorismo"
    OUTRAS = "outras", "Outras iniciativas"


def _conjunto_valido(campo: str) -> list[models.CheckConstraint]:
    return [
        models.CheckConstraint(
            condition=Q(**{f"{campo}__isnull": True}) | Q(**{f"{campo}__len__gte": 1}),
            name=f"oportunidade_{campo}_nao_vazio",
        ),
        models.CheckConstraint(
            condition=~Q(**{f"{campo}__contains": [""]}),
            name=f"oportunidade_{campo}_sem_cadeia_vazia",
        ),
    ]


def _tamanho(campo: str, maximo: int) -> models.CheckConstraint:
    return models.CheckConstraint(
        condition=Q(GreaterThanOrEqual(Length(campo), 1))
        & Q(LessThanOrEqual(Length(campo), maximo)),
        name=f"oportunidade_{campo}_tamanho",
    )


class Oportunidade(models.Model):
    """Conteúdo institucional curado que aponta para uma página oficial (FR-001)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.TextField()
    resumo = models.TextField()
    categoria = models.TextField(choices=Categoria.choices)
    # "" = Ifes (institucional); senão, a designação textual da unidade (DP-1005).
    unidade_responsavel = models.TextField(default="", blank=True)
    endereco = models.TextField()
    inicio = models.DateField()
    fim = models.DateField()
    publico_unidades = ArrayField(models.TextField(), null=True)
    publico_niveis = ArrayField(models.TextField(), null=True)
    publico_cursos = ArrayField(models.TextField(), null=True)
    publicada_em = models.DateTimeField(null=True)
    publicada_por = models.TextField(null=True)
    retirada_em = models.DateTimeField(null=True)
    retirada_por = models.TextField(null=True)

    class Meta:
        # Só determinismo; a ordem do egresso é a da pertinência (research R7).
        ordering = ["-inicio", "titulo", "id"]
        constraints = [
            *(_tamanho(campo, maximo) for campo, maximo in (
                ("titulo", TITULO_MAXIMO), ("resumo", RESUMO_MAXIMO),
            )),
            models.CheckConstraint(
                condition=Q(categoria__in=Categoria.values),
                name="oportunidade_categoria_valida",
            ),
            models.CheckConstraint(
                condition=~Q(endereco=""), name="oportunidade_endereco_nao_vazio"
            ),
            models.CheckConstraint(
                condition=Q(inicio__lte=F("fim")), name="oportunidade_periodo_coerente"
            ),
            *(c for campo in CRITERIOS_DE_PUBLICO for c in _conjunto_valido(campo)),
            # Os IS NOT NULL são explícitos: comparação com NULL dá UNKNOWN, que o CHECK
            # aceita.
            models.CheckConstraint(
                condition=Q(publicada_em__isnull=True, publicada_por__isnull=True)
                | Q(publicada_em__isnull=False, publicada_por__isnull=False),
                name="oportunidade_publicacao_com_operador",
            ),
            models.CheckConstraint(
                condition=Q(retirada_em__isnull=True, retirada_por__isnull=True)
                | Q(retirada_em__isnull=False, retirada_por__isnull=False),
                name="oportunidade_retirada_com_operador",
            ),
            models.CheckConstraint(
                condition=Q(publicada_em__isnull=True)
                | Q(retirada_em__isnull=True)
                | Q(retirada_em__gte=F("publicada_em")),
                name="oportunidade_retirada_depois_da_publicacao",
            ),
        ]

    @property
    def institucional(self) -> bool:
        return self.unidade_responsavel == ""

    @property
    def tem_publico(self) -> bool:
        return any(getattr(self, campo) is not None for campo in CRITERIOS_DE_PUBLICO)

    def __str__(self) -> str:
        return f"Oportunidade {self.titulo}"

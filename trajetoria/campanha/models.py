"""Campanha (specs/004-campanhas-populacao-elegivel/data-model.md).

`NULL` significa "ausente". Nos critérios multivalorados, `NULL` = critério não definido;
`[]` é inválido e nunca é gravado. Não há coluna de estado: o estado é derivado
(`consultas.estado`). Regras que dependem de outra linha ou do tempo ficam em
`operacoes.py`, único caminho de escrita (research R10).
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Q

CRITERIOS_DE_CONJUNTO = ("unidades", "niveis", "modalidades", "formas_oferta")
CRITERIOS = ("ano_minimo", "ano_maximo", *CRITERIOS_DE_CONJUNTO)


def _nao_vazio(campo: str, nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


def _conjunto_valido(campo: str) -> list[models.CheckConstraint]:
    # `__len` devolve 0 para array vazio (não NULL), então `[]` é rejeitado.
    return [
        models.CheckConstraint(
            condition=Q(**{f"{campo}__isnull": True}) | Q(**{f"{campo}__len__gte": 1}),
            name=f"campanha_{campo}_nao_vazio",
        ),
        models.CheckConstraint(
            condition=~Q(**{f"{campo}__contains": [""]}),
            name=f"campanha_{campo}_sem_cadeia_vazia",
        ),
    ]


class Campanha(models.Model):
    """Rodada institucional de aplicação de uma Versão a uma população definida por
    critérios sobre a Conclusão Acadêmica."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.TextField()
    # Sem relação reversa: a Versão não conhece a Campanha; a dependência vai só do
    # conceito novo para o antigo (research R1).
    versao = models.ForeignKey("instrumento.Versao", on_delete=models.PROTECT, related_name="+")
    inicio = models.DateField(null=True)
    fim = models.DateField(null=True)
    ano_minimo = models.PositiveSmallIntegerField(null=True)
    ano_maximo = models.PositiveSmallIntegerField(null=True)
    unidades = ArrayField(models.TextField(), null=True)
    niveis = ArrayField(models.TextField(), null=True)
    modalidades = ArrayField(models.TextField(), null=True)
    formas_oferta = ArrayField(models.TextField(), null=True)
    aberta_em = models.DateTimeField(null=True)
    encerrada_em = models.DateTimeField(null=True)

    class Meta:
        # Só determinismo; sem significado de preferência (FR-052).
        ordering = ["inicio", "id"]
        constraints = [
            _nao_vazio("nome", "campanha_nome_nao_vazio"),
            # Os IS NOT NULL são explícitos: comparação com NULL dá UNKNOWN, que o CHECK
            # aceita.
            models.CheckConstraint(
                condition=Q(inicio__isnull=True, fim__isnull=True)
                | Q(inicio__isnull=False, fim__isnull=False, inicio__lte=F("fim")),
                name="campanha_periodo_coerente",
            ),
            models.CheckConstraint(
                condition=Q(ano_minimo__isnull=True)
                | Q(ano_maximo__isnull=True)
                | Q(ano_minimo__lte=F("ano_maximo")),
                name="campanha_anos_ordenados",
            ),
            *(c for campo in CRITERIOS_DE_CONJUNTO for c in _conjunto_valido(campo)),
            models.CheckConstraint(
                condition=Q(aberta_em__isnull=True)
                | Q(inicio__isnull=False, fim__isnull=False),
                name="campanha_aberta_tem_periodo",
            ),
            models.CheckConstraint(
                condition=Q(encerrada_em__isnull=True) | Q(aberta_em__isnull=False),
                name="campanha_encerrada_foi_aberta",
            ),
            models.CheckConstraint(
                condition=Q(encerrada_em__isnull=True)
                | Q(aberta_em__isnull=False, encerrada_em__gte=F("aberta_em")),
                name="campanha_encerrada_depois_de_aberta",
            ),
        ]

    @property
    def pesquisa(self):
        """A Pesquisa é a da Versão; não há coluna própria (FR-003)."""
        return self.versao.pesquisa

    @property
    def populacao_ampla(self) -> bool:
        """Sem nenhum critério definido: todas as Conclusões Acadêmicas (FR-019)."""
        return all(getattr(self, campo) is None for campo in CRITERIOS)

    def __str__(self) -> str:
        return f"Campanha {self.nome}"

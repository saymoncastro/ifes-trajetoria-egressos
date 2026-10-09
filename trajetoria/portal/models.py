"""Fatos da camada de relacionamento (Constituição 2.1.0, "Camada de relacionamento"; ADR
0008): a Oportunidade (025) e a Manifestação de interesse (026). Nenhum tem chave estrangeira
para o núcleo: o núcleo não depende da camada, e desligá-la não exige migração nele.

Oportunidade (Feature 025; data-model.md; research R1). A ligação com a Pessoa só existe na
consulta, pela regra de pertinência (FR-012). Não há coluna de estado: ele é derivado de
`publicada_em`, `retirada_em` e das datas (`oportunidades.regras.estado`; FR-009). `NULL` nas
listas de público = critério ausente; `[]` e `""` são inválidos e nunca gravados. Regras que
dependem de tempo ou escopo ficam em `oportunidades/operacoes.py`, único caminho de escrita.

Manifestação (Feature 026; plan, "Modelo de dados"; R2 a R6): ver a classe.
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


# --- Manifestação de interesse (026) --------------------------------------------------------

MENSAGEM_MAXIMA = 500
EMAIL_MAXIMO = 254


class Forma(models.TextChoices):
    """Lista fechada e provisória (026 FR-002; DP-801). Só apresentação."""

    MENTORIA = "mentoria", "Mentoria"
    EXPERIENCIA = "experiencia", "Compartilhar experiência"
    OPORTUNIDADE = "oportunidade", "Oferecer oportunidade"
    PESQUISA_EXTENSAO = "pesquisa_extensao", "Pesquisa e extensão"
    PARCERIA = "parceria", "Parceria"
    HISTORIA = "historia", "Contar sua história"


class Manifestacao(models.Model):
    """O egresso se oferece para contribuir (026 FR-001). Ato declarado da Pessoa (III, IV).

    Sem chave estrangeira (R2): `pessoa_id` e `conclusao_id` são identificadores, e a posse da
    Conclusão é verificada em `contribuicao/operacoes.py`, único caminho de escrita. A unidade
    é copiada da Conclusão no registro e define quem recebe. O e-mail é o da contribuição,
    com finalidade própria (D-2602), separado do `ContatoDaPessoa` da 020.

    Sem coluna de estado: a situação deriva de `retirada_em` e `contato_registrado_em`
    (`contribuicao.regras.situacao`). Nada é apagado: retirada e contato só acrescentam o
    momento (VIII).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa_id = models.UUIDField()
    conclusao_id = models.UUIDField()
    # "" = Conclusão sem unidade registrada: só a atuação institucional a recebe.
    unidade = models.TextField(blank=True)
    forma = models.TextField(choices=Forma.choices)
    mensagem = models.TextField(default="", blank=True)
    email = models.TextField()
    versao_da_ciencia = models.TextField()
    registrada_em = models.DateTimeField()
    contato_registrado_em = models.DateTimeField(null=True)
    contato_registrado_por = models.TextField(null=True)
    retirada_em = models.DateTimeField(null=True)

    class Meta:
        ordering = ["-registrada_em", "id"]
        indexes = [models.Index(fields=["pessoa_id"], name="manifestacao_pessoa")]
        constraints = [
            models.CheckConstraint(
                condition=Q(forma__in=Forma.values), name="manifestacao_forma_valida"
            ),
            models.CheckConstraint(
                condition=Q(LessThanOrEqual(Length("mensagem"), MENSAGEM_MAXIMA)),
                name="manifestacao_mensagem_tamanho",
            ),
            models.CheckConstraint(
                condition=Q(GreaterThanOrEqual(Length("email"), 3))
                & Q(LessThanOrEqual(Length("email"), EMAIL_MAXIMO)),
                name="manifestacao_email_tamanho",
            ),
            models.CheckConstraint(
                condition=~Q(versao_da_ciencia=""), name="manifestacao_versao_nao_vazia"
            ),
            # Os IS NOT NULL são explícitos, como na Oportunidade.
            models.CheckConstraint(
                condition=Q(contato_registrado_em__isnull=True, contato_registrado_por__isnull=True)
                | Q(contato_registrado_em__isnull=False, contato_registrado_por__isnull=False),
                name="manifestacao_contato_com_operador",
            ),
            models.CheckConstraint(
                condition=Q(contato_registrado_em__isnull=True)
                | Q(contato_registrado_em__gte=F("registrada_em")),
                name="manifestacao_contato_depois_do_registro",
            ),
            models.CheckConstraint(
                condition=Q(retirada_em__isnull=True) | Q(retirada_em__gte=F("registrada_em")),
                name="manifestacao_retirada_depois_do_registro",
            ),
            # FR-006 no banco, inclusive em corrida de dois envios (R6).
            models.UniqueConstraint(
                fields=["pessoa_id", "conclusao_id", "forma"],
                condition=Q(retirada_em__isnull=True),
                name="manifestacao_uma_ativa_por_forma_e_formacao",
            ),
        ]

    @property
    def ativa(self) -> bool:
        return self.retirada_em is None

    def __str__(self) -> str:
        return f"Manifestação {self.forma}"

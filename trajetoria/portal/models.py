"""Fatos da camada de relacionamento (Constituição 2.1.0, "Camada de relacionamento"; ADR
0008): a Oportunidade (025) e a Manifestação de interesse (026). Nenhum tem chave estrangeira
para o núcleo: o núcleo não depende da camada, e desligá-la não exige migração nele.

Oportunidade (Feature 025; data-model.md; research R1). A ligação com a Pessoa só existe na
consulta, pela regra de pertinência (FR-012). Não há coluna de estado: ele é derivado de
`publicada_em`, `retirada_em` e das datas (`oportunidades.regras.estado`; FR-009). `NULL` nas
listas de público = critério ausente; `[]` e `""` são inválidos e nunca gravados. Regras que
dependem de tempo ou escopo ficam em `oportunidades/operacoes.py`, único caminho de escrita.

Manifestação (Feature 026; plan, "Modelo de dados"; R2 a R6): ver a classe.

Encontro e Confirmação (Feature 031, incremento 1; data-model.md; research R2, R3, R5): ver as
classes. A Confirmação tem chave estrangeira para o Encontro, interna à camada; nenhuma aponta
para o núcleo.
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



# --- Encontro proposto por egresso e Confirmação (031, incremento 1) --------------------------

ENCONTRO_TITULO_MAXIMO = 90
ENCONTRO_DESCRICAO_MAXIMA = 400
NOME_APRESENTACAO_MAXIMO = 40
COMPLEMENTO_MAXIMO = 300


class MotivoDeModeracao(models.TextChoices):
    """Lista provisória de recusa e retirada (031 FR-017; H-3104; D8)."""

    FINALIDADE = "finalidade", "Fora da finalidade dos encontros entre egressos"
    COMERCIAL = "comercial", "Divulgação comercial ou venda"
    LINK = "link", "Link da reunião inadequado"
    CONFUSAO = "confusao", (
        "Informação incompleta ou que pode ser confundida com evento oficial do Ifes"
    )
    RESPEITO = "respeito", "Desrespeito a pessoas ou à lei"
    OUTRO = "outro", "Outro motivo"


def _tamanho_entre(campo: str, minimo: int, maximo: int, prefixo: str) -> models.CheckConstraint:
    return models.CheckConstraint(
        condition=Q(GreaterThanOrEqual(Length(campo), minimo))
        & Q(LessThanOrEqual(Length(campo), maximo)),
        name=f"{prefixo}_{campo}_tamanho",
    )


def _par(prefixo: str, *campos: str) -> models.CheckConstraint:
    """Os campos são todos nulos ou todos preenchidos (momento e operador)."""
    return models.CheckConstraint(
        condition=Q(**{f"{c}__isnull": True for c in campos})
        | Q(**{f"{c}__isnull": False for c in campos}),
        name=f"{prefixo}_{campos[0]}_em_par",
    )


class Encontro(models.Model):
    """Encontro virtual proposto por um egresso (031 FR-001 a FR-024a; data-model.md).

    Sem chave estrangeira para o núcleo (R2): `pessoa_id` e `conclusao_origem_id` são
    identificadores, e a posse da Conclusão é verificada em `encontros/operacoes.py`, único
    caminho de escrita. A origem é copiada da Conclusão no envio (R3): a moderação aprova o
    que vê. Sem coluna de estado: a situação deriva dos momentos e do relógio
    (`encontros.regras.situacao`; R5). O público usa os critérios da Oportunidade (R6).

    Incremento 1: correção depois da publicação, nova análise e denúncia ficam para o
    incremento 2 (roadmap, revisão 16) e não têm campos aqui (XXII).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa_id = models.UUIDField()
    conclusao_origem_id = models.UUIDField()
    origem_curso = models.TextField(default="", blank=True)
    origem_unidade = models.TextField(default="", blank=True)
    origem_ano = models.PositiveSmallIntegerField(null=True)
    nome_apresentacao = models.TextField()
    titulo = models.TextField()
    descricao = models.TextField()
    inicio = models.DateTimeField()
    termino = models.DateTimeField()
    publico_unidades = ArrayField(models.TextField(), null=True)
    publico_niveis = ArrayField(models.TextField(), null=True)
    publico_cursos = ArrayField(models.TextField(), null=True)
    link = models.TextField()
    versao_do_termo = models.TextField()
    enviado_em = models.DateTimeField()
    publicado_em = models.DateTimeField(null=True)
    publicado_por = models.TextField(null=True)
    # "institucional" (CPAEG) ou a unidade da CSAEG que publicou (FR-024; analyze F1).
    publicado_por_escopo = models.TextField(null=True)
    recusado_em = models.DateTimeField(null=True)
    recusado_por = models.TextField(null=True)
    retirado_em = models.DateTimeField(null=True)
    retirado_por = models.TextField(null=True)
    motivo = models.TextField(choices=MotivoDeModeracao.choices, null=True)
    complemento = models.TextField(default="", blank=True)
    cancelado_em = models.DateTimeField(null=True)

    class Meta:
        ordering = ["inicio", "titulo", "id"]
        indexes = [models.Index(fields=["pessoa_id"], name="encontro_pessoa")]
        constraints = [
            _tamanho_entre("titulo", 1, ENCONTRO_TITULO_MAXIMO, "encontro"),
            _tamanho_entre("descricao", 1, ENCONTRO_DESCRICAO_MAXIMA, "encontro"),
            _tamanho_entre("nome_apresentacao", 1, NOME_APRESENTACAO_MAXIMO, "encontro"),
            models.CheckConstraint(
                condition=Q(LessThanOrEqual(Length("complemento"), COMPLEMENTO_MAXIMO)),
                name="encontro_complemento_tamanho",
            ),
            models.CheckConstraint(condition=~Q(link=""), name="encontro_link_nao_vazio"),
            models.CheckConstraint(
                condition=~Q(versao_do_termo=""), name="encontro_termo_nao_vazio"
            ),
            models.CheckConstraint(
                condition=Q(inicio__lt=F("termino")), name="encontro_termino_depois_do_inicio"
            ),
            *(
                c
                for campo in CRITERIOS_DE_PUBLICO
                for c in (
                    models.CheckConstraint(
                        condition=Q(**{f"{campo}__isnull": True})
                        | Q(**{f"{campo}__len__gte": 1}),
                        name=f"encontro_{campo}_nao_vazio",
                    ),
                    models.CheckConstraint(
                        condition=~Q(**{f"{campo}__contains": [""]}),
                        name=f"encontro_{campo}_sem_cadeia_vazia",
                    ),
                )
            ),
            _par("encontro", "publicado_em", "publicado_por", "publicado_por_escopo"),
            _par("encontro", "recusado_em", "recusado_por"),
            _par("encontro", "retirado_em", "retirado_por"),
            # Recusa só antes da publicação; retirada só depois dela; nunca as duas.
            models.CheckConstraint(
                condition=Q(recusado_em__isnull=True) | Q(publicado_em__isnull=True),
                name="encontro_recusa_sem_publicacao",
            ),
            models.CheckConstraint(
                condition=Q(retirado_em__isnull=True)
                | Q(publicado_em__isnull=False, retirado_em__gte=F("publicado_em")),
                name="encontro_retirada_depois_da_publicacao",
            ),
            # O motivo existe se, e só se, houve recusa ou retirada (FR-017).
            models.CheckConstraint(
                condition=Q(motivo__isnull=True, recusado_em__isnull=True,
                            retirado_em__isnull=True)
                | (Q(motivo__in=MotivoDeModeracao.values)
                   & (Q(recusado_em__isnull=False) | Q(retirado_em__isnull=False))),
                name="encontro_motivo_com_decisao",
            ),
            models.CheckConstraint(
                condition=~Q(motivo=MotivoDeModeracao.OUTRO) | ~Q(complemento=""),
                name="encontro_outro_motivo_com_complemento",
            ),
        ]

    @property
    def tem_publico(self) -> bool:
        return any(getattr(self, campo) is not None for campo in CRITERIOS_DE_PUBLICO)

    def __str__(self) -> str:
        return f"Encontro {self.titulo}"


class Confirmacao(models.Model):
    """"Vou participar" (031 FR-020, FR-023). Não é inscrição nem registro de presença.

    Mostra o link a quem confirmou e dá ao organizador só a quantidade (FR-025). Nunca é
    exportada nem entra no dado analítico (FR-032). Cancelar não apaga: grava o momento, e
    confirmar de novo cria outra.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encontro = models.ForeignKey(Encontro, on_delete=models.PROTECT, related_name="confirmacoes")
    pessoa_id = models.UUIDField()
    versao_da_ciencia = models.TextField()
    confirmada_em = models.DateTimeField()
    cancelada_em = models.DateTimeField(null=True)

    class Meta:
        ordering = ["confirmada_em", "id"]
        indexes = [models.Index(fields=["pessoa_id"], name="confirmacao_pessoa")]
        constraints = [
            models.CheckConstraint(
                condition=~Q(versao_da_ciencia=""), name="confirmacao_versao_nao_vazia"
            ),
            models.CheckConstraint(
                condition=Q(cancelada_em__isnull=True) | Q(cancelada_em__gte=F("confirmada_em")),
                name="confirmacao_cancelada_depois",
            ),
            models.UniqueConstraint(
                fields=["encontro", "pessoa_id"],
                condition=Q(cancelada_em__isnull=True),
                name="confirmacao_uma_ativa_por_pessoa",
            ),
        ]

    @property
    def ativa(self) -> bool:
        return self.cancelada_em is None

"""Pesquisa, Versão, Seção, Pergunta e Opção (specs/002-pesquisa-versao-instrumento/data-model.md).

`NULL` significa "ausente"; cadeia vazia é proibida. Restrições que dependem de outra
linha (estado da Versão, mesma Versão, tipo da Pergunta) ficam em `operacoes.py`, único
caminho de escrita (research R8, R9).
"""

import uuid

from django.db import models
from django.db.models import F, Q


def _nao_vazio(campo: str, nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


def _posicao_positiva(nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=Q(posicao__gt=0), name=nome)


def _posicao_unica(campo: str, nome: str) -> models.UniqueConstraint:
    # Adiada para o fim da transação: reordenar troca posições sem estado intermediário
    # inválido (R4).
    return models.UniqueConstraint(
        fields=[campo, "posicao"], name=nome, deferrable=models.Deferrable.DEFERRED
    )


class EstadoVersao(models.TextChoices):
    RASCUNHO = "RASCUNHO"
    PUBLICADA = "PUBLICADA"


class TipoPergunta(models.TextChoices):
    ESCOLHA_UNICA = "ESCOLHA_UNICA"
    ESCOLHA_MULTIPLA = "ESCOLHA_MULTIPLA"
    TEXTO_CURTO = "TEXTO_CURTO"
    ESCALA = "ESCALA"


class Pesquisa(models.Model):
    """Instrumento lógico ao longo do tempo. Não contém conteúdo: ele pertence à Versão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.TextField()

    class Meta:
        constraints = [_nao_vazio("nome", "pesquisa_nome_nao_vazio")]

    def __str__(self) -> str:
        return f"Pesquisa {self.nome}"


class Versao(models.Model):
    """Configuração historicamente identificável de uma Pesquisa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pesquisa = models.ForeignKey(Pesquisa, on_delete=models.PROTECT, related_name="versoes")
    designacao = models.TextField()
    estado = models.TextField(choices=EstadoVersao.choices, default=EstadoVersao.RASCUNHO)
    publicada_em = models.DateTimeField(null=True)
    origem = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, related_name="derivadas"
    )
    titulo = models.TextField(null=True)
    texto_abertura = models.TextField(null=True)
    texto_encerramento = models.TextField(null=True)

    class Meta:
        # Só determinismo; sem significado de domínio (FR-008).
        ordering = ["designacao"]
        constraints = [
            models.UniqueConstraint(
                fields=["pesquisa", "designacao"], name="versao_designacao_unica"
            ),
            models.CheckConstraint(
                condition=Q(estado__in=EstadoVersao.values), name="versao_estado_valido"
            ),
            models.CheckConstraint(
                condition=Q(estado=EstadoVersao.PUBLICADA, publicada_em__isnull=False)
                | Q(estado=EstadoVersao.RASCUNHO, publicada_em__isnull=True),
                name="versao_publicada_em_coerente",
            ),
            models.CheckConstraint(condition=~Q(origem=F("id")), name="versao_origem_outra"),
            *(
                _nao_vazio(campo, f"versao_{campo}_nao_vazio")
                for campo in ("designacao", "titulo", "texto_abertura", "texto_encerramento")
            ),
        ]

    @property
    def publicada(self) -> bool:
        return self.estado == EstadoVersao.PUBLICADA

    def __str__(self) -> str:
        return f"Versão {self.designacao}"


class Secao(models.Model):
    """Unidade de organização e de navegação. `encaminhamento` ausente = fluxo padrão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    versao = models.ForeignKey(Versao, on_delete=models.PROTECT, related_name="secoes")
    posicao = models.PositiveIntegerField()
    titulo = models.TextField(null=True)
    texto = models.TextField(null=True)
    encaminhamento = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, related_name="encaminhadas"
    )

    class Meta:
        ordering = ["posicao"]
        constraints = [
            _posicao_unica("versao", "secao_posicao_unica"),
            _posicao_positiva("secao_posicao_positiva"),
            _nao_vazio("titulo", "secao_titulo_nao_vazio"),
            _nao_vazio("texto", "secao_texto_nao_vazio"),
        ]

    def __str__(self) -> str:
        return f"Seção {self.posicao}"


class Pergunta(models.Model):
    """Item do instrumento. O tipo é definido na criação e não muda (FR-062)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    secao = models.ForeignKey(Secao, on_delete=models.PROTECT, related_name="perguntas")
    posicao = models.PositiveIntegerField()
    tipo = models.TextField(choices=TipoPergunta.choices)
    texto = models.TextField()
    texto_explicativo = models.TextField(null=True)
    obrigatoria = models.BooleanField()
    escala_inicio = models.IntegerField(null=True)
    escala_fim = models.IntegerField(null=True)
    escala_rotulo_inicio = models.TextField(null=True)
    escala_rotulo_fim = models.TextField(null=True)

    class Meta:
        ordering = ["posicao"]
        constraints = [
            _posicao_unica("secao", "pergunta_posicao_unica"),
            _posicao_positiva("pergunta_posicao_positiva"),
            models.CheckConstraint(
                condition=Q(tipo__in=TipoPergunta.values), name="pergunta_tipo_valido"
            ),
            # Os IS NOT NULL são explícitos: comparação com NULL dá UNKNOWN, que o CHECK
            # aceita.
            models.CheckConstraint(
                condition=(
                    Q(
                        tipo=TipoPergunta.ESCALA,
                        escala_inicio__isnull=False,
                        escala_fim__isnull=False,
                        escala_inicio__lt=F("escala_fim"),
                    )
                    | (
                        ~Q(tipo=TipoPergunta.ESCALA)
                        & Q(
                            escala_inicio__isnull=True,
                            escala_fim__isnull=True,
                            escala_rotulo_inicio__isnull=True,
                            escala_rotulo_fim__isnull=True,
                        )
                    )
                ),
                name="pergunta_escala_coerente",
            ),
            *(
                _nao_vazio(campo, f"pergunta_{campo}_nao_vazio")
                for campo in (
                    "texto",
                    "texto_explicativo",
                    "escala_rotulo_inicio",
                    "escala_rotulo_fim",
                )
            ),
        ]

    def __str__(self) -> str:
        return f"Pergunta {self.posicao} ({self.tipo})"


class Opcao(models.Model):
    """Alternativa de uma pergunta de escolha. A regra de navegação condicional fica na
    própria Opção: `regra_destino` ("ir para a Seção") ou `regra_finaliza`, nunca os dois
    (R6)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name="opcoes")
    posicao = models.PositiveIntegerField()
    texto = models.TextField()
    complemento_textual = models.BooleanField(default=False)
    regra_destino = models.ForeignKey(
        Secao, on_delete=models.PROTECT, null=True, related_name="regras_que_apontam"
    )
    regra_finaliza = models.BooleanField(default=False)

    class Meta:
        ordering = ["posicao"]
        constraints = [
            _posicao_unica("pergunta", "opcao_posicao_unica"),
            _posicao_positiva("opcao_posicao_positiva"),
            models.UniqueConstraint(fields=["pergunta", "texto"], name="opcao_texto_unico"),
            models.UniqueConstraint(
                fields=["pergunta"],
                condition=Q(complemento_textual=True),
                name="opcao_complemento_unico",
            ),
            models.CheckConstraint(
                condition=~Q(regra_destino__isnull=False, regra_finaliza=True),
                name="opcao_uma_regra",
            ),
            _nao_vazio("texto", "opcao_texto_nao_vazio"),
        ]

    @property
    def tem_regra(self) -> bool:
        return self.regra_destino_id is not None or self.regra_finaliza

    def __str__(self) -> str:
        return f"Opção {self.posicao}"

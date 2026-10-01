"""Participação e Resposta (specs/005-participacao-respostas-rascunho/data-model.md).

`NULL` significa "ausente". Os CHECKs protegem só invariantes das colunas da própria linha;
regras entre tabelas (tipo da Pergunta, pertença à Versão e à Pergunta, limites da escala,
≥ 1 seleção, complemento × Opção, coleta da Campanha) ficam em `operacoes.py`, único
caminho de escrita (research R4, R9).

Toda FK para modelo de feature anterior usa `related_name="+"`: Campanha, Conclusão,
Pergunta e Opção não ganham acessor reverso (research R2).
"""

import uuid

from django.db import models
from django.db.models import Q


def _nao_vazio(campo: str, nome: str) -> models.CheckConstraint:
    return models.CheckConstraint(condition=~Q(**{campo: ""}), name=nome)


def _ambos(a: str, b: str) -> Q:
    return Q(**{f"{a}__isnull": False, f"{b}__isnull": False})


class Participacao(models.Model):
    """Ocorrência de acompanhamento de uma Conclusão Acadêmica numa Campanha. Em rascunho
    ou concluída, derivado de `concluida_em`; sem enum de estado (006 FR-002)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campanha = models.ForeignKey("campanha.Campanha", on_delete=models.PROTECT, related_name="+")
    conclusao = models.ForeignKey(
        "academico.ConclusaoAcademica", on_delete=models.PROTECT, related_name="+"
    )
    # Momento de referência da criação, não `auto_now_add`: os testes controlam o tempo.
    iniciada_em = models.DateTimeField()
    # Momento de referência da conclusão aceita; `NULL` = em rascunho (006 FR-001). Gravado
    # só por `concluir`, uma única vez (006 FR-003).
    concluida_em = models.DateTimeField(null=True)

    class Meta:
        # Só determinismo; sem significado de preferência ou de "atual" (FR-049).
        ordering = ["iniciada_em", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["campanha", "conclusao"], name="participacao_par_unico"
            ),
        ]

    @property
    def pessoa(self):
        """Pela Conclusão; não há coluna própria (FR-004)."""
        return self.conclusao.pessoa

    @property
    def versao(self):
        """A Versão aplicada pela Campanha; não há coluna própria (FR-004)."""
        return self.campanha.versao

    @property
    def pesquisa(self):
        return self.campanha.versao.pesquisa

    def __str__(self) -> str:
        return f"Participação {self.id}"


class Resposta(models.Model):
    """Valor declarado atual de uma Pergunta numa Participação. Uma linha por Pergunta,
    atualizada no lugar a cada edição do rascunho (FR-018, FR-033).

    Forma do valor por tipo da Pergunta: `opcao` (escolha única), `opcoes` (escolha
    múltipla), `texto` (texto curto), `escala` (escala); `complemento` acompanha a Opção
    que o admite, em escolha."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participacao = models.ForeignKey(
        Participacao, on_delete=models.PROTECT, related_name="respostas"
    )
    pergunta = models.ForeignKey("instrumento.Pergunta", on_delete=models.PROTECT, related_name="+")
    opcao = models.ForeignKey(
        "instrumento.Opcao", on_delete=models.PROTECT, null=True, related_name="+"
    )
    texto = models.TextField(null=True)
    escala = models.IntegerField(null=True)
    complemento = models.TextField(null=True)
    opcoes = models.ManyToManyField("instrumento.Opcao", through="RespostaOpcao", related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participacao", "pergunta"], name="resposta_pergunta_unica"
            ),
            models.CheckConstraint(
                condition=~(
                    _ambos("opcao", "texto") | _ambos("opcao", "escala") | _ambos("texto", "escala")
                ),
                name="resposta_um_valor_direto",
            ),
            _nao_vazio("texto", "resposta_texto_nao_vazio"),
            _nao_vazio("complemento", "resposta_complemento_nao_vazio"),
        ]

    def __str__(self) -> str:
        return f"Resposta {self.id}"


class RespostaOpcao(models.Model):
    """Tabela técnica do conjunto da escolha múltipla; sem significado de domínio, operação
    ou consulta próprios. Sem posição nem timestamp: a ordem de seleção não é informação
    (research R5)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # O conjunto é parte do valor: remover a Resposta remove as seleções.
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE, related_name="+")
    opcao = models.ForeignKey("instrumento.Opcao", on_delete=models.PROTECT, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["resposta", "opcao"], name="resposta_opcao_unica"),
        ]

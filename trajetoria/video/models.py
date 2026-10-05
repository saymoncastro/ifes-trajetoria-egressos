"""Estado técnico da geração do vídeo (Feature 022; data-model §3; research R5, R6).

Não é entidade de domínio (FR-028): existe só para o egresso consultar um processamento que
não cabe numa requisição. Não tem FK: a `chave` é o SHA-256 da composição visual, e o vídeo
de uma composição é o conteúdo que a própria Pessoa já pode gerar. A `composicao` (que pode
ter o nome) vive só até o processamento; o vídeo, só até `expira_em`, que toda transição
define (FR-029; analyze P1).
"""

from django.db import models
from django.db.models import Q


class GeracaoDeVideo(models.Model):
    SOLICITADO, PROCESSANDO, PRONTO, FALHOU = "SOLICITADO", "PROCESSANDO", "PRONTO", "FALHOU"
    ESTADOS = [(e, e.capitalize()) for e in (SOLICITADO, PROCESSANDO, PRONTO, FALHOU)]

    id = models.BigAutoField(primary_key=True)
    chave = models.CharField(max_length=64)
    template = models.CharField(max_length=40)
    estado = models.CharField(max_length=12, choices=ESTADOS)
    composicao = models.JSONField(null=True)
    video = models.BinaryField(null=True)
    tamanho = models.PositiveIntegerField(null=True)
    motivo = models.CharField(max_length=40, blank=True)
    solicitado_em = models.DateTimeField()
    iniciado_em = models.DateTimeField(null=True)
    concluido_em = models.DateTimeField(null=True)
    # Sempre definido: momento da transição + TRAJETORIA_VIDEO_RETENCAO.
    expira_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chave"], name="video_chave_unica"),
            models.CheckConstraint(
                condition=~Q(estado="PRONTO") | Q(video__isnull=False),
                name="video_pronto_tem_video",
            ),
            models.CheckConstraint(
                condition=~Q(estado="FALHOU") | ~Q(motivo=""),
                name="video_falha_tem_motivo",
            ),
            models.CheckConstraint(
                condition=~Q(estado="SOLICITADO") | Q(composicao__isnull=False),
                name="video_solicitado_tem_composicao",
            ),
        ]
        indexes = [
            models.Index(fields=["estado", "solicitado_em"], name="video_fila"),
            models.Index(fields=["expira_em"], name="video_expiracao"),
        ]

    def __str__(self):
        # Sem a chave nem o conteúdo (FR-027).
        return f"GeracaoDeVideo({self.pk}, {self.estado})"

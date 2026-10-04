"""Material pseudonimizado de acesso, sem dados acadêmicos ou valores em claro."""

from uuid import uuid4

from django.db import models


class MaterialDeVerificacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    pessoa = models.OneToOneField("academico.Pessoa", on_delete=models.PROTECT, related_name="+")
    identificador_cpf = models.TextField(db_index=True)
    verificador = models.TextField(null=True)
    atualizado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(identificador_cpf__regex=r"^[0-9a-f]{64}$"),
                name="acesso_identificador_hex",
            ),
            models.CheckConstraint(
                condition=models.Q(verificador__isnull=True)
                | models.Q(verificador__regex=r"^[0-9a-f]{64}$"),
                name="acesso_verificador_hex",
            ),
        ]

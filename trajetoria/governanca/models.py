"""Vínculo de governança (specs/010-governanca-papeis-escopos/data-model.md).

Registro administrativo de que um operador atua pela CPAEG ou por uma CSAEG. Ele **reflete**
uma designação feita fora do sistema (portaria — PAEG Art. 17, Art. 18, III, Art. 24) e não a
verifica (spec FR-065; DP-1002). Não é dado sobre o egresso.

O escopo não é gravado: decorre do papel. CPAEG atua no âmbito institucional, sem unidade
(`unidade == ""`); CSAEG atua numa unidade explícita (`unidade` não vazia). A unidade é a
mesma designação textual da fonte acadêmica e da Campanha, sem catálogo (DP-1005).

`ativo` responde só "este vínculo concede autorização agora?": não há histórico, vigência,
portaria nem autor (spec FR-026).
"""

import uuid

from django.db import models
from django.db.models import Q


class Papel(models.TextChoices):
    """As duas atuações da PAEG (Art. 16; Art. 18, III). Lista fechada (spec FR-010)."""

    CPAEG = "CPAEG", "Comissão Própria de Acompanhamento do Egresso (CPAEG)"
    CSAEG = "CSAEG", "Comissão Setorial de Acompanhamento de Egressos (CSAEG)"


class VinculoDeGovernanca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identificador_operador = models.TextField()
    papel = models.TextField(choices=Papel.choices)
    unidade = models.TextField(default="")
    ativo = models.BooleanField(default=True)

    class Meta:
        # Só determinismo; sem significado de domínio.
        ordering = ["identificador_operador", "papel", "unidade"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(identificador_operador=""), name="vinculo_identificador_nao_vazio"
            ),
            models.CheckConstraint(
                condition=Q(papel__in=["CPAEG", "CSAEG"]), name="vinculo_papel_valido"
            ),
            models.CheckConstraint(
                condition=Q(papel="CPAEG", unidade="") | (Q(papel="CSAEG") & ~Q(unidade="")),
                name="vinculo_unidade_conforme_papel",
            ),
            models.UniqueConstraint(
                fields=["identificador_operador", "papel", "unidade"], name="vinculo_unico"
            ),
        ]

    @property
    def rotulo_de_atuacao(self) -> str:
        if self.papel == Papel.CPAEG:
            return f"{Papel.CPAEG.label} — atuação institucional"
        return f"{Papel.CSAEG.label} — unidade {self.unidade}"

    def __str__(self) -> str:
        return self.rotulo_de_atuacao

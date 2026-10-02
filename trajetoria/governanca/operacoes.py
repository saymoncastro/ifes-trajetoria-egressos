"""Registro e desativação de vínculos (contracts/governanca.md, "Operações").

**Mecanismo técnico administrativo** (spec FR-062): usado por testes, pelo preparo da
demonstração e por quem opera o servidor (`manage.py shell`). **Não** é processo oficial de
designação: o registro reflete uma designação feita fora do sistema (portaria) e não a
verifica (spec FR-065; DP-1002). Registrar ou operar este módulo não confere, por si,
nenhuma capacidade (FR-066).

Não há exclusão, troca de papel ou de unidade: corrigir um vínculo é desativá-lo e
registrar outro. Toda rejeição é tudo-ou-nada.
"""

from enum import Enum

from django.db import IntegrityError, transaction

from trajetoria.governanca.models import Papel, VinculoDeGovernanca


class Motivo(Enum):
    IDENTIFICADOR_INVALIDO = "identificador_invalido"
    PAPEL_INVALIDO = "papel_invalido"
    UNIDADE_PROIBIDA = "unidade_proibida"
    UNIDADE_EXIGIDA = "unidade_exigida"
    UNIDADE_INVALIDA = "unidade_invalida"
    JA_ATIVO = "ja_ativo"
    JA_INATIVO = "ja_inativo"


class VinculoRejeitado(Exception):
    def __init__(self, motivo: Motivo):
        super().__init__(motivo.value)
        self.motivo = motivo


def _sem_espacos_nas_pontas(texto) -> bool:
    return isinstance(texto, str) and texto == texto.strip()


def _validar(identificador, papel, unidade) -> None:
    if not (_sem_espacos_nas_pontas(identificador) and identificador):
        raise VinculoRejeitado(Motivo.IDENTIFICADOR_INVALIDO)
    if papel not in Papel.values:
        raise VinculoRejeitado(Motivo.PAPEL_INVALIDO)
    if not isinstance(unidade, str):
        raise VinculoRejeitado(Motivo.UNIDADE_INVALIDA)
    if papel == Papel.CPAEG and unidade != "":
        raise VinculoRejeitado(Motivo.UNIDADE_PROIBIDA)
    if papel == Papel.CSAEG and not unidade.strip():
        raise VinculoRejeitado(Motivo.UNIDADE_EXIGIDA)
    if not _sem_espacos_nas_pontas(unidade):
        raise VinculoRejeitado(Motivo.UNIDADE_INVALIDA)


def registrar_vinculo(identificador: str, papel: Papel, unidade: str = "") -> VinculoDeGovernanca:
    """Registra o vínculo ativo. A mesma combinação inativa é **reativada** (mesma linha); a
    mesma combinação ativa é recusada (`JA_ATIVO`). A unidade é gravada como informada."""
    _validar(identificador, papel, unidade)
    try:
        with transaction.atomic():
            vinculo = (
                VinculoDeGovernanca.objects.select_for_update()
                .filter(identificador_operador=identificador, papel=papel, unidade=unidade)
                .first()
            )
            if vinculo is None:
                return VinculoDeGovernanca.objects.create(
                    identificador_operador=identificador, papel=papel, unidade=unidade
                )
            if vinculo.ativo:
                raise VinculoRejeitado(Motivo.JA_ATIVO)
            vinculo.ativo = True
            vinculo.save(update_fields=["ativo"])
            return vinculo
    except IntegrityError:
        # Corrida: outra transação criou a mesma combinação entre a busca e a criação.
        raise VinculoRejeitado(Motivo.JA_ATIVO) from None


def desativar_vinculo(vinculo: VinculoDeGovernanca) -> None:
    """Marca o vínculo como inativo, sem apagar. Já inativo → `JA_INATIVO`."""
    with transaction.atomic():
        atual = VinculoDeGovernanca.objects.select_for_update().get(pk=vinculo.pk)
        if not atual.ativo:
            raise VinculoRejeitado(Motivo.JA_INATIVO)
        atual.ativo = False
        atual.save(update_fields=["ativo"])
    vinculo.ativo = False

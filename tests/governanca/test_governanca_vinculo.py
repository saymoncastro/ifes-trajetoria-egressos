"""Vínculo de governança: restrições de banco e operações (Feature 010; data-model §3–§4;
contracts/governanca.md).

As restrições são verificadas gravando direto no modelo **só aqui**: fora dos testes, toda
escrita passa por `operacoes`.
"""

import pytest
from django.db import IntegrityError, transaction

from trajetoria.governanca import operacoes
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.governanca.operacoes import (
    Motivo,
    VinculoRejeitado,
    desativar_vinculo,
    registrar_vinculo,
)

pytestmark = pytest.mark.django_db

A = "demonstracao:operador-a"
B = "demonstracao:operador-b"


def _gravar(identificador=A, papel="CPAEG", unidade="", ativo=True):
    return VinculoDeGovernanca.objects.create(
        identificador_operador=identificador, papel=papel, unidade=unidade, ativo=ativo
    )


def _deve_violar(nome, **campos):
    with pytest.raises(IntegrityError, match=nome), transaction.atomic():
        _gravar(**campos)


# --- Restrições de banco --------------------------------------------------------------------


def test_identificador_vazio_e_papel_invalido_sao_recusados():
    _deve_violar("vinculo_identificador_nao_vazio", identificador="")
    _deve_violar("vinculo_papel_valido", papel="ADMIN")


def test_unidade_conforme_o_papel():
    _deve_violar("vinculo_unidade_conforme_papel", papel="CPAEG", unidade="Vitória")
    _deve_violar("vinculo_unidade_conforme_papel", papel="CSAEG", unidade="")


def test_unidade_nao_informada_e_vazia_e_nao_nula():
    vinculo = VinculoDeGovernanca.objects.create(identificador_operador=A, papel="CPAEG")
    vinculo.refresh_from_db()
    assert vinculo.unidade == "" and vinculo.ativo is True


def test_unicidade_inclusive_cpaeg_e_inclusive_inativa():
    _gravar(ativo=False)
    _deve_violar("vinculo_unico")
    _gravar(B, "CSAEG", "Vitória")
    _deve_violar("vinculo_unico", identificador=B, papel="CSAEG", unidade="Vitória")


def test_combinacoes_distintas_coexistem():
    _gravar(B, "CSAEG", "Vitória")
    _gravar(B, "CSAEG", "Serra")
    _gravar(B, "CPAEG")
    _gravar(A, "CPAEG")
    assert VinculoDeGovernanca.objects.count() == 4


# --- Operações -------------------------------------------------------------------------------


def _recusa(motivo, funcao, *args):
    antes = list(VinculoDeGovernanca.objects.values_list("pk", "ativo"))
    with pytest.raises(VinculoRejeitado) as erro:
        funcao(*args)
    assert erro.value.motivo is motivo
    assert list(VinculoDeGovernanca.objects.values_list("pk", "ativo")) == antes


def test_registrar_cria_ativo():
    cpaeg = registrar_vinculo(A, Papel.CPAEG)
    csaeg = registrar_vinculo(B, Papel.CSAEG, "Vitória")
    assert (cpaeg.papel, cpaeg.unidade, cpaeg.ativo) == ("CPAEG", "", True)
    assert (csaeg.papel, csaeg.unidade, csaeg.ativo) == ("CSAEG", "Vitória", True)


@pytest.mark.parametrize(
    ("motivo", "argumentos"),
    [
        (Motivo.IDENTIFICADOR_INVALIDO, ("", Papel.CPAEG)),
        (Motivo.IDENTIFICADOR_INVALIDO, ("  ", Papel.CPAEG)),
        (Motivo.IDENTIFICADOR_INVALIDO, (" " + A, Papel.CPAEG)),
        (Motivo.IDENTIFICADOR_INVALIDO, (None, Papel.CPAEG)),
        (Motivo.PAPEL_INVALIDO, (A, "ADMIN")),
        (Motivo.UNIDADE_PROIBIDA, (A, Papel.CPAEG, "Vitória")),
        (Motivo.UNIDADE_EXIGIDA, (B, Papel.CSAEG, "")),
        (Motivo.UNIDADE_EXIGIDA, (B, Papel.CSAEG, "  ")),
        (Motivo.UNIDADE_INVALIDA, (B, Papel.CSAEG, " Vitória")),
        (Motivo.UNIDADE_INVALIDA, (B, Papel.CSAEG, None)),
    ],
)
def test_registro_invalido_e_recusado_sem_gravar(motivo, argumentos):
    _recusa(motivo, registrar_vinculo, *argumentos)
    assert not VinculoDeGovernanca.objects.exists()


def test_registrar_ativo_de_novo_e_recusado():
    registrar_vinculo(A, Papel.CPAEG)
    _recusa(Motivo.JA_ATIVO, registrar_vinculo, A, Papel.CPAEG)


def test_desativar_nao_apaga_e_reativar_usa_a_mesma_linha():
    vinculo = registrar_vinculo(B, Papel.CSAEG, "Vitória")
    desativar_vinculo(vinculo)
    vinculo.refresh_from_db()
    assert vinculo.ativo is False and VinculoDeGovernanca.objects.count() == 1
    _recusa(Motivo.JA_INATIVO, desativar_vinculo, vinculo)
    reativado = registrar_vinculo(B, Papel.CSAEG, "Vitória")
    assert reativado.pk == vinculo.pk and reativado.ativo is True
    assert VinculoDeGovernanca.objects.count() == 1


def test_varios_operadores_e_varios_vinculos_por_operador():
    registrar_vinculo(A, Papel.CPAEG)
    registrar_vinculo(B, Papel.CPAEG)
    registrar_vinculo(A, Papel.CSAEG, "Vitória")
    assert VinculoDeGovernanca.objects.filter(ativo=True).count() == 3


def test_unidade_gravada_como_informada():
    assert registrar_vinculo(B, Papel.CSAEG, "Campus VITÓRIA").unidade == "Campus VITÓRIA"


def test_sem_exclusao_nem_edicao_de_vinculo():
    publicos = {n for n in vars(operacoes) if not n.startswith("_")}
    assert {"registrar_vinculo", "desativar_vinculo"} <= publicos
    assert not [
        n for n in publicos if n.startswith(("excluir", "apagar", "remover", "alterar", "trocar"))
    ]

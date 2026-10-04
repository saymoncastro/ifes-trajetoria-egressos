from dataclasses import replace
from datetime import date, timedelta

import pytest

from tests.acesso.construcao import AGORA, ANA, BRUNO
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contrato import FonteAcademicaIndisponivel
from trajetoria.fonte_academica.simulada import FonteSimulada

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.django_db
def test_atualizacoes_e_ausencias(caplog):
    from trajetoria.acesso.chaves import chaves_de_acesso, identificador_cpf, verificador
    from trajetoria.acesso.material import incorporar_com_material, registrar_material
    from trajetoria.acesso.models import MaterialDeVerificacao

    r = incorporar_com_material(FonteSimulada(), "SIM-P-0001")
    p = r.pessoa
    c = chaves_de_acesso()
    m = MaterialDeVerificacao.objects.get(pessoa=p)
    assert m.identificador_cpf == identificador_cpf(ANA.cpf11, c)
    assert m.verificador == verificador(ANA.cpf11, ANA.data, c)
    original = m.atualizado_em
    for cpf, data in ((ANA.cpf11, ANA.data), (None, None), (ANA.cpf11, None)):
        registrar_material(p, cpf, data, c, AGORA)
        m.refresh_from_db()
        assert m.atualizado_em == original
    nova = date(1998, 4, 13)
    sinais = registrar_material(p, ANA.cpf11, nova, c, AGORA)
    m.refresh_from_db()
    assert m.verificador == verificador(ANA.cpf11, nova, c) and m.atualizado_em == AGORA
    assert any(s.campos == ("data_nascimento",) for s in sinais)
    registrar_material(p, BRUNO.cpf11, None, c, AGORA + timedelta(seconds=1))
    m.refresh_from_db()
    assert m.identificador_cpf == identificador_cpf(BRUNO.cpf11, c) and m.verificador is None
    registrar_material(p, BRUNO.cpf11, BRUNO.data, c, AGORA + timedelta(seconds=2))
    m.refresh_from_db()
    assert m.verificador == verificador(BRUNO.cpf11, BRUNO.data, c)
    for valor in (ANA.cpf, ANA.cpf11, ANA.data.isoformat(), m.identificador_cpf, m.verificador):
        assert valor not in caplog.text


@pytest.mark.parametrize("cpf", [None, "11111111111", "00000000192"])
def test_material_ausente_ou_inutilizavel(cpf, caplog):
    from trajetoria.acesso.material import incorporar_com_material
    from trajetoria.acesso.models import MaterialDeVerificacao

    fonte = FonteSimulada(pessoas=(replace(cenarios.PESSOAS[0], cpf=cpf),))
    incorporar_com_material(fonte, "SIM-P-0001")
    assert not MaterialDeVerificacao.objects.exists()
    if cpf:
        assert "CPF_INUTILIZAVEL" in caplog.text and cpf not in caplog.text


def test_incompleto_colisao_e_sem_conclusao(caplog):
    from trajetoria.acesso.material import incorporar_com_material
    from trajetoria.acesso.models import MaterialDeVerificacao

    for i in (9, 10, 11, 6):
        incorporar_com_material(FonteSimulada(), f"SIM-P-{i:04}")
    assert MaterialDeVerificacao.objects.count() == 3
    assert MaterialDeVerificacao.objects.filter(verificador__isnull=True).count() == 1
    assert "COLISAO" in caplog.text


def test_chaves_antes_da_fonte(settings, monkeypatch):
    from trajetoria.acesso.chaves import ChavesInvalidas
    from trajetoria.acesso.material import incorporar_com_material

    settings.TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = ""
    fonte = FonteSimulada()
    monkeypatch.setattr(fonte, "obter_pessoa", lambda _: pytest.fail("fonte consultada"))
    with pytest.raises(ChavesInvalidas):
        incorporar_com_material(fonte, "SIM-P-0001")


def test_erros_e_fidelidade():
    from django.db import transaction

    from trajetoria.academico.incorporacao import incorporar_pessoa
    from trajetoria.academico.models import ConclusaoAcademica, Pessoa
    from trajetoria.acesso.material import incorporar_com_material

    with pytest.raises(FonteAcademicaIndisponivel):
        incorporar_com_material(FonteSimulada(indisponivel=True), "SIM-P-0001")
    assert incorporar_com_material(FonteSimulada(), "SIM-P-9999").pessoa is None
    with transaction.atomic():
        incorporar_com_material(FonteSimulada(), "SIM-P-0001")
        p = Pessoa.objects.get()
        cs = list(ConclusaoAcademica.objects.values_list("id_externo", "curso"))
        nome = p.nome
        transaction.set_rollback(True)
    incorporar_pessoa(FonteSimulada(), "SIM-P-0001")
    assert Pessoa.objects.get().nome == nome
    assert list(ConclusaoAcademica.objects.values_list("id_externo", "curso")) == cs


def test_material_sem_data_nao_sinaliza_ausencia_a_cada_carga(caplog):
    """Revisão 018: só é ausência o que já esteve presente."""
    from trajetoria.acesso.material import incorporar_com_material

    incorporar_com_material(FonteSimulada(), "SIM-P-0009")
    caplog.clear()
    incorporar_com_material(FonteSimulada(), "SIM-P-0009")
    assert "AUSENTE_NA_FONTE" not in caplog.text

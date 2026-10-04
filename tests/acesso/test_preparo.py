import pytest
from django.apps import apps

from tests.acesso.construcao import DADOS, linhas_de_dominio
from trajetoria.demonstracao.cenario import PreparoRecusado, preparar

pytestmark = pytest.mark.django_db


def test_preparo_sem_chaves(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True
    settings.TRAJETORIA_CHAVE_ACESSO_VERIFICACAO = ""
    antes = linhas_de_dominio()
    with pytest.raises(PreparoRecusado, match="As chaves de acesso não estão configuradas"):
        preparar()
    assert linhas_de_dominio() == antes


def test_preparo_idempotente_e_sem_claro(settings):
    from trajetoria.acesso.models import MaterialDeVerificacao

    settings.TRAJETORIA_DEMONSTRACAO = True
    preparar()
    assert MaterialDeVerificacao.objects.count() == 8
    assert MaterialDeVerificacao.objects.filter(verificador__isnull=False).count() == 7
    antes = linhas_de_dominio()
    preparar()
    assert antes == linhas_de_dominio()
    valores = []
    for m in apps.get_models():
        valores.extend(str(row) for row in m.objects.values())
    texto = " ".join(valores)
    for d in DADOS:
        if d.cpf:
            assert d.cpf not in texto and d.cpf11 not in texto
        if d.data:
            assert d.data.isoformat() not in texto and d.nascimento not in texto

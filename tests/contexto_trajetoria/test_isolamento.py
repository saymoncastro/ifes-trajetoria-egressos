"""Isolamento da capacidade de contexto (021 FR-071; SC-014): identidade, incorporação,
resposta e narrativa P1 não dependem do enriquecimento."""

from urllib.parse import urlsplit

import pytest

from tests.interface import construcao_interface as ci
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.incorporacao import incorporar_pessoa
from trajetoria.acesso.material import incorporar_com_material
from trajetoria.campanha.models import Campanha
from trajetoria.contexto_trajetoria.models import (
    ComplementoDaConclusao,
    ContextoInstitucionalAgregado,
)
from trajetoria.demonstracao.cenario import preparar
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def modo_demonstracao(settings):
    settings.TRAJETORIA_DEMONSTRACAO = True


def test_preparo_com_contexto_indisponivel(client):
    preparar(ContextoSimulado(indisponivel=True))
    assert not ComplementoDaConclusao.objects.exists()
    assert not ContextoInstitucionalAgregado.objects.exists()

    maria = ce.pessoa_da_fonte("SIM-P-0003")
    tads = maria.conclusoes.first()
    resposta = ci.iniciar(client, maria, tads)
    participacao = Participacao.objects.get(pk=ci.participacao_de(resposta))
    versao = Campanha.objects.get(pk=participacao.campanha_id).versao
    _, url = ci.percorrer_pela_interface(client, participacao.pk, versao, {})
    assert client.post(urlsplit(url).path).status_code == 302
    participacao.refresh_from_db()
    assert participacao.concluida_em is not None

    texto = ci.texto_visivel(client.get("/minha-trajetoria/"))
    assert "O Ifes registra 2 formações concluídas por você." in texto
    assert "começou em" not in texto and "Naquele ano no Ifes" not in texto


def test_preparo_padrao_carrega_o_contexto_simulado():
    preparar()
    assert ComplementoDaConclusao.objects.get().conclusao.id_externo == "SIM-C-0001"
    assert ContextoInstitucionalAgregado.objects.count() == 2


def test_preparo_sobrevive_a_erro_inesperado_da_fonte_de_contexto():
    class Quebrada:
        codigo = "simulada"

        def obter_contexto(self, ids):
            raise RuntimeError("falha inesperada")

    preparar(Quebrada())
    assert ce.pessoa_da_fonte("SIM-P-0003").conclusoes.count() == 2
    assert not ContextoInstitucionalAgregado.objects.exists()


def test_incorporacao_e_material_nao_consultam_o_contexto(monkeypatch):
    def proibido(*_):
        raise AssertionError("a incorporação não conhece a capacidade de contexto")

    monkeypatch.setattr(ContextoSimulado, "obter_contexto", proibido)
    incorporar_pessoa(FonteSimulada(), "SIM-P-0001")
    incorporar_com_material(FonteSimulada(), "SIM-P-0003")
    assert ce.pessoa_da_fonte("SIM-P-0003").conclusoes.count() == 2

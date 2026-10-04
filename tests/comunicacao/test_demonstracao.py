from datetime import timedelta

import pytest
from django.core import mail
from django.test import Client
from django.urls import URLPattern
from django.utils import timezone

from tests.editor.construcao_editor import A, B, C
from trajetoria.academico.models import Pessoa
from trajetoria.acompanhamento import urls
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.comunicacao.acesso import RecusaComunicacao, autorizar_operador
from trajetoria.comunicacao.operacoes import simular_comunicacao
from trajetoria.demonstracao.entrada import usar as usar_pessoa
from trajetoria.governanca.models import VinculoDeGovernanca
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def test_inventario_protegido(campanha, clientes):
    rotas = [p for p in urls.urlpatterns if isinstance(p, URLPattern)]
    assert len(rotas) == 4
    comunicacao = [p for p in rotas if "/comunicacao/" in str(p.pattern)]
    assert len(comunicacao) == 2
    assert all(getattr(p.callback, "comunicacao", False) for p in comunicacao)
    assert not any(getattr(p.callback, "acompanhamento", False) for p in comunicacao)
    raiz = f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/"
    for caminho, metodo in [(raiz, "get"), (raiz + "simular/", "post")]:
        assert getattr(clientes[C], metodo)(caminho).status_code == 403
        assert getattr(Client(), metodo)(caminho).status_code == 302


def test_vinculo_misto_revogacao_e_multiplas_unidades(campanha, clientes):
    VinculoDeGovernanca.objects.create(identificador_operador=B, papel="CSAEG", unidade="Serra")
    assert autorizar_operador(B).escopo.unidades == frozenset({"Serra", "Vitória"})
    assert simular_comunicacao(campanha.pk, B).totais["pessoas"] == 5
    VinculoDeGovernanca.objects.create(identificador_operador=A, papel="CSAEG", unidade="Vitória")
    assert autorizar_operador(A).escopo.institucional
    pagina = f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/"
    assert clientes[A].get(pagina).context["totais"]["pessoas"] == 9
    VinculoDeGovernanca.objects.filter(identificador_operador=A, papel="CPAEG").update(ativo=False)
    assert clientes[A].post(pagina + "simular/").context["totais"]["pessoas"] == 2


def test_cta_com_pessoa_nao_abre_campanha(campanha, snapshot):
    antes = snapshot()
    pessoa = Pessoa.objects.get(id_externo="SIM-P-0002")
    cliente = Client()
    from django.http import HttpResponse

    resposta = HttpResponse()
    usar_pessoa(resposta, pessoa)
    cliente.cookies.update(resposta.cookies)
    assert cliente.get("/demonstracao/").status_code == 200
    pagina = f"/acompanhamento/campanhas/{campanha.pk}/comunicacao/"
    assert cliente.get(pagina).status_code == 302
    assert estado(campanha) == EstadoCampanha.EM_PREPARACAO
    assert not Participacao.objects.exists()
    assert snapshot() == antes


def test_coleta_e_encerramento_por_data(campanha):
    ampla = campanha.__class__.objects.get(nome="Demonstração — coleta ampla")
    assert estado(ampla) == EstadoCampanha.EM_COLETA
    resultado = simular_comunicacao(ampla.pk, A)
    assert resultado.totais["aceitas"] > 0
    sem_nome = next(msg for msg in mail.outbox if msg.to == ["sim-p-0009@example.invalid"])
    assert sem_nome.body.startswith("Olá!")
    ampla.fim = timezone.localdate() - timedelta(days=1)
    ampla.inicio = ampla.fim - timedelta(days=180)
    ampla.save()
    with pytest.raises(RecusaComunicacao) as erro:
        simular_comunicacao(ampla.pk, A)
    assert erro.value.status == 409

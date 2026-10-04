import pytest
from django.http import Http404, HttpResponse
from django.test import RequestFactory

from trajetoria.acompanhamento import acesso


def test_gate_direto_modo_desligado(settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    view = acesso.gestao(lambda request: HttpResponse("ok"))
    assert view.gestao
    with pytest.raises(Http404):
        view(RequestFactory().get("/"))


def test_gate_sem_operador():
    view = acesso.gestao(lambda request: HttpResponse("ok"))
    assert view(RequestFactory().get("/")).url == acesso.ESCOLHA_DE_OPERADOR


def test_atuacao(cliente_cpaeg, cliente_csaeg_vitoria):
    assert cliente_cpaeg.get("/acompanhamento/").context["atuacao"].gerir_campanha
    assert not cliente_csaeg_vitoria.get("/acompanhamento/").context["atuacao"].gerir_campanha


def rotas(c):
    from trajetoria.acompanhamento.urls import urlpatterns

    return [
        f"/acompanhamento/{str(p.pattern).replace('<uuid:campanha>', str(c.pk))}"
        for p in urlpatterns
        if getattr(p.callback, "gestao", False)
    ]


@pytest.mark.parametrize("operador", ["cliente_csaeg_vitoria", "cliente_sem_vinculo"])
def test_todas_rotas_recusam_sem_gravar(inst, request, operador):
    from tests.acompanhamento import construcao as k
    from tests.editor.construcao_editor import texto_visivel
    from trajetoria.campanha.models import Campanha

    c = k.campanha(inst.versao, estado="pronta", nome="Campanha sigilosa 017")
    cliente = request.getfixturevalue(operador)
    antes = list(Campanha.objects.values().order_by("id"))
    for endereco in rotas(c):
        for metodo in ("get", "post"):
            r = getattr(cliente, metodo)(endereco)
            assert r.status_code == 403
            assert "Acesso não permitido" in texto_visivel(r)
            assert c.nome not in texto_visivel(r)
    assert list(Campanha.objects.values().order_by("id")) == antes


def test_rotas_sem_operador_modo_metodos(inst, cliente_cpaeg, settings):
    from django.test import Client

    from tests.acompanhamento import construcao as k

    c = k.campanha(inst.versao, estado="pronta")
    for endereco in rotas(c):
        for metodo in ("get", "post"):
            r = getattr(Client(), metodo)(endereco)
            assert r.status_code == 302 and r.url == acesso.ESCOLHA_DE_OPERADOR
        for metodo in ("put", "patch", "delete", "head"):
            assert getattr(cliente_cpaeg, metodo)(endereco).status_code == 405
    settings.TRAJETORIA_DEMONSTRACAO = False
    for endereco in rotas(c):
        for metodo in ("get", "post"):
            assert getattr(cliente_cpaeg, metodo)(endereco).status_code == 404


def test_revogacao_entre_get_post(inst, cliente_cpaeg):
    from tests.acompanhamento import construcao as k
    from trajetoria.campanha.models import Campanha
    from trajetoria.governanca.models import VinculoDeGovernanca

    c = k.campanha(inst.versao, estado="pronta")
    for endereco in rotas(c):
        VinculoDeGovernanca.objects.filter(identificador_operador=k.A).update(ativo=True)
        assert cliente_cpaeg.get(endereco).status_code in (200, 409)
        VinculoDeGovernanca.objects.filter(identificador_operador=k.A).update(ativo=False)
        antes = list(Campanha.objects.values().order_by("id"))
        assert cliente_cpaeg.post(endereco).status_code == 403
        assert list(Campanha.objects.values().order_by("id")) == antes


def test_gate_sintetico_reconsulta(cliente_cpaeg, cliente_csaeg_vitoria):
    from tests.acompanhamento import construcao as k
    from trajetoria.governanca.models import VinculoDeGovernanca

    view = acesso.gestao(lambda r: HttpResponse(str(r.atuacao.gerir_campanha)))
    fabrica = RequestFactory()
    request = fabrica.get("/")
    request.COOKIES.update({n: v.value for n, v in cliente_cpaeg.cookies.items()})
    assert view(request).content == b"True"
    VinculoDeGovernanca.objects.filter(identificador_operador=k.A).update(ativo=False)
    assert view(request).status_code == 403
    request.COOKIES.clear()
    request.COOKIES.update({n: v.value for n, v in cliente_csaeg_vitoria.cookies.items()})
    assert view(request).status_code == 403

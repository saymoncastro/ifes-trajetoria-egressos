from datetime import timedelta

import pytest

from tests.acompanhamento import construcao as k
from tests.editor.construcao_editor import texto_visivel
from trajetoria.campanha.models import Campanha

NOVA = "/acompanhamento/campanhas/nova/"


def dados(inst, **extra):
    return {
        "nome": "Rodada institucional",
        "versao": str(inst.versao.pk),
        "inicio": "",
        "fim": "",
        **extra,
    }


def test_criar_minima(inst, cliente_cpaeg):
    r = cliente_cpaeg.get(NOVA)
    assert r.status_code == 200
    for campo in ("nome", "versao", "inicio", "fim"):
        assert f'name="{campo}"' in r.content.decode()
    assert cliente_cpaeg.post(NOVA, dados(inst)).status_code == 302
    c = Campanha.objects.get(nome="Rodada institucional")
    assert c.inicio is c.fim is c.aberta_em is None
    assert all(
        getattr(c, f) is None
        for f in ("ano_minimo", "ano_maximo", "unidades", "niveis", "modalidades", "formas_oferta")
    )


@pytest.mark.parametrize(
    "extra,campo",
    [
        ({"nome": "  "}, "nome"),
        ({"inicio": "2027-01-01"}, "fim"),
        ({"inicio": "2027-02-01", "fim": "2027-01-01"}, "inicio"),
        ({"inicio": "inválida"}, "inicio"),
        ({"versao": "inexistente"}, "versao"),
    ],
)
def test_criacao_atomica_com_erros(inst, cliente_cpaeg, extra, campo):
    antes = Campanha.objects.count()
    r = cliente_cpaeg.post(NOVA, dados(inst, **extra))
    assert r.status_code == 422
    assert campo in r.context["formulario"].errors
    assert Campanha.objects.count() == antes
    assert "NOME_VAZIO" not in texto_visivel(r)


def test_criar_com_periodo(inst, cliente_cpaeg):
    r = cliente_cpaeg.post(NOVA, dados(inst, inicio="2027-01-01", fim="2027-02-01"))
    assert r.status_code == 302
    assert r.url.endswith("?aviso=campanha-criada")
    assert Campanha.objects.get(nome="Rodada institucional").inicio.isoformat() == "2027-01-01"


def test_sem_publicada(cliente_cpaeg):
    from tests.campanha.construcao import versao_rascunho

    versao_rascunho("Sem publicada")
    r = cliente_cpaeg.get(NOVA)
    assert r.status_code == 200
    assert "<form" not in r.content.decode()
    assert "publicação não é feita aqui" in texto_visivel(r)


def test_so_publicadas(inst, cliente_cpaeg):
    v = k.versao_em_rascunho(inst)
    r = cliente_cpaeg.get(NOVA)
    assert str(inst.versao.pk) in r.content.decode()
    assert str(v.pk) not in r.content.decode()
    assert " — " in texto_visivel(r)


def test_nova_ausente_para_csaeg(cliente_csaeg_vitoria):
    assert "Nova Campanha" not in texto_visivel(cliente_csaeg_vitoria.get("/acompanhamento/"))


def editar_url(c):
    return f"/acompanhamento/campanhas/{c.pk}/editar/"


def test_editar_rascunho_e_completar(inst, cliente_cpaeg):
    v = k.versao_em_rascunho(inst)
    c = k.campanha(v, estado="sem_periodo")
    outra = k.versao_em_rascunho(inst)
    r = cliente_cpaeg.get(editar_url(c))
    assert r.status_code == 200
    assert "não publicada — impede a abertura" in texto_visivel(r)
    assert f'value="{v.pk}" selected' in r.content.decode()
    assert str(outra.pk) not in r.content.decode()
    r = cliente_cpaeg.post(
        editar_url(c),
        dados(inst, inicio=k.hoje().isoformat(), fim=(k.hoje() + timedelta(days=5)).isoformat()),
    )
    assert r.status_code == 302
    c.refresh_from_db()
    assert c.nome == "Rodada institucional" and c.versao_id == inst.versao.pk
    assert c.inicio == k.hoje()


def test_edicao_atomica_e_remocao_periodo(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    antes = Campanha.objects.filter(pk=c.pk).values().get()
    for extra in (
        {"inicio": "", "fim": ""},
        {"inicio": "2027-02-01", "fim": "2027-01-01"},
        {"inicio": "2027-01-01", "fim": ""},
    ):
        r = cliente_cpaeg.post(editar_url(c), dados(inst, **extra))
        assert r.status_code == 422
        assert Campanha.objects.filter(pk=c.pk).values().get() == antes
    assert "pode ser corrigido, mas não removido" in texto_visivel(
        cliente_cpaeg.post(editar_url(c), dados(inst))
    )


def test_editar_sem_periodo_e_criterios_preservados(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="sem_periodo", unidades=["Vitória"], niveis=["Técnico"])
    assert "abrangência restrita" in texto_visivel(cliente_cpaeg.get(editar_url(c)))
    assert cliente_cpaeg.post(editar_url(c), dados(inst)).status_code == 302
    c.refresh_from_db()
    assert c.unidades == ["Vitória"] and c.niveis == ["Técnico"] and c.inicio is None


def test_corrigir_expirada(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="expirada_sem_abertura")
    assert (
        cliente_cpaeg.post(
            editar_url(c), dados(inst, inicio=k.hoje().isoformat(), fim=k.hoje().isoformat())
        ).status_code
        == 302
    )
    assert "Abrir coleta" in texto_visivel(k.detalhe(cliente_cpaeg, c))


@pytest.mark.parametrize("estado", ["em_coleta", "encerrada_explicita", "encerrada_por_periodo"])
def test_editar_aberta_conflito(inst, cliente_cpaeg, estado):
    c = k.campanha(inst.versao, estado=estado)
    antes = Campanha.objects.filter(pk=c.pk).values().get()
    for metodo in ("get", "post"):
        assert getattr(cliente_cpaeg, metodo)(editar_url(c), dados(inst)).status_code == 409
    assert Campanha.objects.filter(pk=c.pk).values().get() == antes


def test_editar_inexistente(cliente_cpaeg):
    import uuid

    assert cliente_cpaeg.get(f"/acompanhamento/campanhas/{uuid.uuid4()}/editar/").status_code == 404


def test_criacao_mostra_todos_os_problemas_numa_submissao(inst, cliente_cpaeg):
    """Nome inválido não esconde o erro do período (FR-014; code review da 017)."""
    r = cliente_cpaeg.post(NOVA, dados(inst, nome=" ", inicio="2027-01-01"))
    assert r.status_code == 422
    assert {"nome", "fim"} <= set(r.context["formulario"].errors)
    r = cliente_cpaeg.post(NOVA, dados(inst, nome=" ", inicio="2027-02-01", fim="2027-01-01"))
    assert {"nome", "inicio"} <= set(r.context["formulario"].errors)
    assert not Campanha.objects.filter(nome=" ").exists()


def test_edicao_rejeitada_mostra_o_que_esta_gravado(inst, cliente_cpaeg):
    """Rejeição do período desfaz a troca de nome; a página não exibe o nome não gravado."""
    c = k.campanha(inst.versao, estado="em_preparacao", nome="Nome gravado")
    url = f"/acompanhamento/campanhas/{c.pk}/editar/"
    r = cliente_cpaeg.post(
        url, dados(inst, nome="Nome não gravado", inicio="2027-02-01", fim="2027-01-01")
    )
    assert r.status_code == 422
    assert r.context["campanha"].nome == "Nome gravado"
    assert "Nome não gravado" not in [rotulo for rotulo, _ in r.context["trilha"]]
    c.refresh_from_db()
    assert c.nome == "Nome gravado"

import pytest

from tests.acompanhamento import construcao as k
from tests.acompanhamento.gestao import acoes
from tests.editor.construcao_editor import texto_visivel


@pytest.mark.parametrize(
    "estado,esperadas",
    [
        ("pronta", ("Editar configuração", "Abrir coleta")),
        ("sem_periodo", ("Editar configuração",)),
        ("em_preparacao", ("Editar configuração",)),
        ("expirada_sem_abertura", ("Editar configuração",)),
        ("em_coleta", ("Encerrar coleta",)),
        ("encerrada_explicita", ()),
        ("encerrada_por_periodo", ()),
    ],
)
def test_matriz_painel(inst, cliente_cpaeg, estado, esperadas):
    c = k.campanha(inst.versao, estado=estado)
    r = k.detalhe(cliente_cpaeg, c)
    assert acoes(r) == esperadas
    texto = texto_visivel(r)
    assert "Comunicação simulada" in texto
    if estado == "em_coleta":
        assert "Encerramento previsto" in texto
    if estado == "expirada_sem_abertura":
        assert "Período encerrado — Campanha nunca aberta" in texto
    if estado == "em_preparacao":
        assert c.inicio.strftime("%d/%m/%Y") in texto


def test_impedimentos_simultaneos(inst, cliente_cpaeg):
    c = k.campanha(k.versao_em_rascunho(inst), estado="sem_periodo")
    texto = texto_visivel(k.detalhe(cliente_cpaeg, c))
    assert "A Versão escolhida ainda não foi publicada" in texto
    assert "O período de coleta não foi definido" in texto
    assert "A publicação não é feita aqui" in texto


def test_abrangencia(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, unidades=["Vitória"], niveis=["Técnico"])
    texto = texto_visivel(k.detalhe(cliente_cpaeg, c))
    assert "abrangência restrita" in texto
    assert "Unidades: Vitória" in texto and "Níveis: Técnico" in texto


def test_csaeg_sem_painel(inst, cliente_csaeg_vitoria):
    c = k.campanha(inst.versao, estado="pronta", unidades=["Vitória"])
    r = k.detalhe(cliente_csaeg_vitoria, c)
    assert acoes(r) == ()
    texto = texto_visivel(r)
    for t in ("Gestão da Campanha", "abrangência restrita", "Nova Campanha"):
        assert t not in texto
    for t in ("Resumo", "Recortes", "Comunicação simulada", "Elegíveis"):
        assert t in texto


def test_rotulo_expirada_para_todos(inst, cliente_cpaeg, cliente_csaeg_vitoria):
    c = k.campanha(inst.versao, estado="expirada_sem_abertura")
    for cliente in (cliente_cpaeg, cliente_csaeg_vitoria):
        assert "Período encerrado — Campanha nunca aberta" in texto_visivel(k.detalhe(cliente, c))
        assert "Período encerrado — Campanha nunca aberta" in texto_visivel(
            cliente.get("/acompanhamento/")
        )


def test_aviso_desconhecido(inst, cliente_cpaeg):
    c = k.campanha(inst.versao, estado="pronta")
    r = cliente_cpaeg.get(f"/acompanhamento/campanhas/{c.pk}/?aviso=nao-exibir-017")
    assert "nao-exibir-017" not in texto_visivel(r)


def test_misto_cpaeg_inativo_preserva_acompanhamento(inst, cliente_cpaeg_e_csaeg):
    from trajetoria.governanca.models import VinculoDeGovernanca

    c = k.campanha(inst.versao, estado="pronta", unidades=["Serra"])
    VinculoDeGovernanca.objects.filter(identificador_operador=k.A, papel="CPAEG").update(
        ativo=False
    )
    for r in (k.detalhe(cliente_cpaeg_e_csaeg, c), cliente_cpaeg_e_csaeg.get("/acompanhamento/")):
        assert r.status_code == 200
        texto = texto_visivel(r)
        for acao in (
            "Nova Campanha",
            "Editar configuração",
            "Abrir coleta",
            "Encerrar coleta",
            "Gestão da Campanha",
            "abrangência restrita",
        ):
            assert acao not in texto
    texto = texto_visivel(k.detalhe(cliente_cpaeg_e_csaeg, c))
    for elemento in ("Resumo", "Recortes", "Comunicação simulada", "Elegíveis"):
        assert elemento in texto


def test_misto_cpaeg_ativo_concede_gestao(inst, cliente_cpaeg_e_csaeg):
    c = k.campanha(inst.versao, estado="pronta")
    assert acoes(k.detalhe(cliente_cpaeg_e_csaeg, c)) == ("Editar configuração", "Abrir coleta")

"""Estado técnico da geração (022 US1; data-model §3; FR-028 a FR-032; analyze P1)."""

from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction

from tests.video.construcao import NOME, composicao
from trajetoria.narrativa.composicao import chave_da_composicao
from trajetoria.video import operacoes
from trajetoria.video.models import GeracaoDeVideo as G

pytestmark = pytest.mark.django_db
RETENCAO = timedelta(hours=2)


@pytest.fixture(autouse=True)
def retencao(settings):
    settings.TRAJETORIA_VIDEO_RETENCAO = RETENCAO


def _linha(c):
    return G.objects.get(chave=chave_da_composicao(c))


def _forcar(c, **campos):
    G.objects.filter(chave=chave_da_composicao(c)).update(**campos)


def test_pedido_novo(relogio):
    c = composicao("maria", NOME)
    operacoes.solicitar(c)
    linha = _linha(c)
    assert linha.estado == G.SOLICITADO
    assert linha.composicao == c
    assert linha.template == "trajetoria-v1"
    assert linha.solicitado_em == relogio.agora
    assert linha.expira_em == relogio.agora + RETENCAO


@pytest.mark.parametrize("estado", [G.SOLICITADO, G.PROCESSANDO, G.PRONTO])
def test_sem_duplicata(estado, relogio):
    c = composicao("ana")
    operacoes.solicitar(c)
    extras = {"video": b"x", "composicao": None} if estado == G.PRONTO else {}
    _forcar(c, estado=estado, **extras)
    antes = _linha(c)
    relogio.agora += timedelta(minutes=1)
    operacoes.solicitar(c)
    depois = _linha(c)
    assert G.objects.count() == 1
    assert (depois.estado, depois.solicitado_em, depois.expira_em) == (
        antes.estado, antes.solicitado_em, antes.expira_em
    )


def test_tentar_de_novo_depois_de_falha(relogio):
    c = composicao("ana")
    operacoes.solicitar(c)
    _forcar(c, estado=G.FALHOU, motivo="codigo_1", composicao=None,
            concluido_em=relogio.agora, iniciado_em=relogio.agora)
    relogio.agora += timedelta(minutes=3)
    operacoes.solicitar(c)
    linha = _linha(c)
    assert linha.estado == G.SOLICITADO and linha.motivo == ""
    assert linha.composicao == c and linha.video is None
    assert linha.iniciado_em is None and linha.concluido_em is None
    assert linha.solicitado_em == relogio.agora
    assert linha.expira_em == relogio.agora + RETENCAO


def test_estado_para(relogio):
    c = composicao("ana")
    chave = chave_da_composicao(c)
    assert operacoes.estado_para(chave) == "nenhum"
    operacoes.solicitar(c)
    assert operacoes.estado_para(chave) == "preparando"
    _forcar(c, estado=G.PROCESSANDO, iniciado_em=relogio.agora)
    assert operacoes.estado_para(chave) == "preparando"
    _forcar(c, estado=G.PRONTO, video=b"x", composicao=None, concluido_em=relogio.agora)
    assert operacoes.estado_para(chave) == "pronto"
    _forcar(c, estado=G.FALHOU, video=None, motivo="codigo_1")
    assert operacoes.estado_para(chave) == "falhou"


def test_limpar_apaga_vencidas_em_qualquer_estado(relogio):
    for caso, estado in (("ana", G.SOLICITADO), ("maria", G.FALHOU), ("diego", G.PRONTO)):
        c = composicao(caso)
        operacoes.solicitar(c)
        extras = {"video": b"x", "composicao": None} if estado == G.PRONTO else {}
        if estado == G.FALHOU:
            extras = {"motivo": "codigo_1", "composicao": None}
        _forcar(c, estado=estado, expira_em=relogio.agora - timedelta(seconds=1), **extras)
    operacoes.limpar()
    assert G.objects.count() == 0


def test_limpar_processando_travado(relogio):
    c = composicao("ana")
    operacoes.solicitar(c)
    _forcar(c, estado=G.PROCESSANDO, iniciado_em=relogio.agora - timedelta(minutes=6))
    operacoes.limpar()
    linha = _linha(c)
    assert linha.estado == G.FALHOU and linha.motivo == "tempo_esgotado"
    assert linha.composicao is None
    assert linha.expira_em == relogio.agora + RETENCAO


def test_sem_processador_o_nome_vive_no_maximo_dez_minutos(relogio):
    c = composicao("maria", NOME)
    chave = chave_da_composicao(c)
    operacoes.solicitar(c)
    relogio.agora += timedelta(minutes=11)
    assert operacoes.estado_para(chave) == "falhou"
    linha = _linha(c)
    assert linha.motivo == "sem_processador" and linha.composicao is None
    relogio.agora += RETENCAO + timedelta(minutes=1)
    assert operacoes.estado_para(chave) == "nenhum"
    assert not G.objects.exists()


def test_video_pronto_respeita_a_retencao(relogio):
    c = composicao("ana")
    chave = chave_da_composicao(c)
    operacoes.solicitar(c)
    _forcar(c, estado=G.PRONTO, video=b"mp4", composicao=None, concluido_em=relogio.agora,
            expira_em=relogio.agora + RETENCAO)
    assert operacoes.video_pronto(chave) == b"mp4"
    relogio.agora += RETENCAO + timedelta(seconds=1)
    assert operacoes.video_pronto(chave) is None
    assert not G.objects.exists()


def _inserir(**campos):
    base = {"chave": "a" * 64, "template": "trajetoria-v1", "estado": G.SOLICITADO,
            "composicao": {"x": 1}, "solicitado_em": "2027-05-01T12:00:00Z",
            "expira_em": "2027-05-01T14:00:00Z"}
    base.update(campos)
    with transaction.atomic():
        G.objects.create(**base)


@pytest.mark.parametrize("campos", [
    {"estado": G.PRONTO, "composicao": None, "video": None},
    {"estado": G.FALHOU, "composicao": None, "motivo": ""},
    {"estado": G.SOLICITADO, "composicao": None},
    {"expira_em": None},
])
def test_restricoes_no_banco(campos):
    with pytest.raises(IntegrityError):
        _inserir(**campos)


def test_chave_unica():
    _inserir()
    with pytest.raises(IntegrityError):
        _inserir()


def test_sem_vinculo_com_dominio():
    assert not [f for f in G._meta.get_fields() if f.is_relation]


def test_render_longo_nao_e_dado_como_travado(relogio, settings):
    """O prazo de 'travado' acompanha o tempo máximo de render (code review)."""
    settings.TRAJETORIA_VIDEO_TEMPO_MAXIMO = 600
    c = composicao("ana")
    operacoes.solicitar(c)
    _forcar(c, estado=G.PROCESSANDO, iniciado_em=relogio.agora)
    relogio.agora += timedelta(minutes=6)
    operacoes.limpar()
    assert _linha(c).estado == G.PROCESSANDO
    relogio.agora += timedelta(minutes=6)
    operacoes.limpar()
    assert _linha(c).motivo == "tempo_esgotado"


def test_retencao_curta_nao_apaga_pedido_nem_render_em_curso(relogio, settings):
    settings.TRAJETORIA_VIDEO_RETENCAO = timedelta(minutes=1)
    c = composicao("ana")
    chave = chave_da_composicao(c)
    operacoes.solicitar(c)
    relogio.agora += timedelta(minutes=2)
    operacoes.limpar()
    assert operacoes.estado_para(chave) == "preparando"
    relogio.agora += timedelta(minutes=9)
    operacoes.limpar()
    assert operacoes.estado_para(chave) == "falhou"
    assert _linha(c).motivo == "sem_processador"


def test_leituras_limpam_no_maximo_a_cada_30_segundos(relogio):
    c = composicao("ana")
    chave = chave_da_composicao(c)
    operacoes.limpar()
    operacoes.solicitar(c)
    _forcar(c, expira_em=relogio.agora - timedelta(seconds=1))
    relogio.agora += timedelta(seconds=10)
    assert operacoes.estado_para(chave) == "preparando"  # sem nova limpeza ainda
    relogio.agora += timedelta(seconds=25)
    assert operacoes.estado_para(chave) == "nenhum"
    assert not G.objects.exists()

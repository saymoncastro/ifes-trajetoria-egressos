"""Os quatro tipos de resposta (US3–US6) e o complemento de "Outro" (US8).

Em toda rejeição, nada é gravado: `retrato` idêntico antes e depois.
"""

from datetime import date

import pytest

from tests.participacao import construcao as c
from tests.participacao.construcao import NO_PERIODO
from trajetoria.participacao.models import Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import (
    iniciar_participacao,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

pytestmark = pytest.mark.django_db


def rejeita_sem_gravar(participacao, motivo, operacao, *args, campo=None, **kwargs):
    antes = c.retrato(participacao)
    (violacao,) = c.rejeita([motivo], operacao, participacao, *args, agora=NO_PERIODO, **kwargs)
    if campo is not None:
        assert violacao.campo == campo
    assert c.retrato(participacao) == antes
    return violacao


def resposta(participacao, pergunta) -> Resposta:
    return Resposta.objects.get(participacao=participacao, pergunta=pergunta)


# --- US3: escolha única -------------------------------------------------------------------


def test_escolha_unica_valida(participacao, inst):
    sim = inst.opcao(inst.unica, "Sim")
    gravada = responder_escolha_unica(participacao, inst.unica, sim, agora=NO_PERIODO)

    r = resposta(participacao, inst.unica)
    assert r.id == gravada.id
    assert (r.opcao_id, r.texto, r.escala, r.complemento) == (sim.id, None, None, None)
    assert not RespostaOpcao.objects.filter(resposta=r).exists()


def test_escolha_unica_com_opcao_de_outra_pergunta_de_mesmo_texto(participacao, inst):
    # "A" de `multipla` respondida em `unica_outro`, que também tem "A" (US3.3, FR-028).
    a_de_outra = inst.opcao(inst.multipla, "A")
    rejeita_sem_gravar(
        participacao,
        Motivo.OPCAO_DE_OUTRA_PERGUNTA,
        responder_escolha_unica,
        inst.unica_outro,
        a_de_outra,
    )
    rejeita_sem_gravar(
        participacao,
        Motivo.OPCAO_DE_OUTRA_PERGUNTA,
        responder_escolha_unica,
        inst.unica,
        inst.opcao(inst.campus, "Campus Serra"),
    )


def test_escolha_unica_sem_opcao(participacao, inst):
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_VAZIO, responder_escolha_unica, inst.unica, None, campo="opcao"
    )


@pytest.mark.parametrize("valor", ["Sim", 1, "lista"])
def test_escolha_unica_com_valor_de_forma_errada(participacao, inst, valor):
    if valor == "lista":
        valor = [inst.opcao(inst.unica, "Sim")]
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_INCOMPATIVEL, responder_escolha_unica, inst.unica, valor
    )


def test_escolha_unica_em_pergunta_de_outro_tipo(participacao, inst):
    rejeita_sem_gravar(
        participacao,
        Motivo.VALOR_INCOMPATIVEL,
        responder_escolha_unica,
        inst.texto,
        inst.opcao(inst.unica, "Sim"),
    )


def test_opcao_com_regra_nao_aplica_navegacao(participacao, inst):
    responder_texto(participacao, inst.posterior, "comentário", agora=NO_PERIODO)
    antes = resposta(participacao, inst.posterior)

    responder_escolha_unica(
        participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=NO_PERIODO
    )

    depois = resposta(participacao, inst.posterior)
    assert (depois.id, depois.texto) == (antes.id, antes.texto)
    assert Resposta.objects.filter(participacao=participacao).count() == 2


def test_uma_resposta_por_pergunta_e_mesmo_valor_aceito(participacao, inst):
    sim = inst.opcao(inst.unica, "Sim")
    primeira = responder_escolha_unica(participacao, inst.unica, sim, agora=NO_PERIODO)
    antes = c.retrato(participacao)

    segunda = responder_escolha_unica(participacao, inst.unica, sim, agora=NO_PERIODO)

    assert segunda.id == primeira.id
    assert c.retrato(participacao) == antes
    assert Resposta.objects.filter(participacao=participacao).count() == 1


@pytest.mark.parametrize("errado", ["participacao", "pergunta", "agora_ingenuo", "agora_data"])
def test_argumento_estrutural_de_tipo_errado(participacao, inst, errado):
    args = {
        "participacao": participacao,
        "pergunta": inst.unica,
        "agora": NO_PERIODO,
    }
    args |= {
        "participacao": {"participacao": "x"},
        "pergunta": {"pergunta": "x"},
        "agora_ingenuo": {"agora": NO_PERIODO.replace(tzinfo=None)},
        "agora_data": {"agora": date(2027, 5, 1)},
    }[errado]
    antes = c.retrato(participacao)
    with pytest.raises(TypeError):
        responder_escolha_unica(
            args["participacao"],
            args["pergunta"],
            inst.opcao(inst.unica, "Sim"),
            agora=args["agora"],
        )
    assert c.retrato(participacao) == antes


# --- US4: escolha múltipla ----------------------------------------------------------------


def _opcoes(inst, *textos):
    return [inst.opcao(inst.multipla, t) for t in textos]


def _conjunto(r: Resposta) -> list[str]:
    return [o.texto for o in r.opcoes.all()]


def test_escolha_multipla_valida(participacao, inst):
    r = responder_escolha_multipla(
        participacao, inst.multipla, _opcoes(inst, "A", "C"), agora=NO_PERIODO
    )

    assert (r.opcao_id, r.texto, r.escala) == (None, None, None)
    assert _conjunto(resposta(participacao, inst.multipla)) == ["A", "C"]
    assert RespostaOpcao.objects.filter(resposta=r).count() == 2


def test_ordem_de_selecao_nao_tem_significado(campanha, inst):
    p1 = iniciar_participacao(campanha, c.conclusao(), agora=NO_PERIODO).participacao
    p2 = iniciar_participacao(campanha, c.conclusao(), agora=NO_PERIODO).participacao
    responder_escolha_multipla(p1, inst.multipla, _opcoes(inst, "A", "C"), agora=NO_PERIODO)
    responder_escolha_multipla(p2, inst.multipla, _opcoes(inst, "C", "A"), agora=NO_PERIODO)

    # Lida na ordem do instrumento, não na de seleção.
    assert (
        _conjunto(resposta(p1, inst.multipla))
        == _conjunto(resposta(p2, inst.multipla))
        == [
            "A",
            "C",
        ]
    )


def test_selecao_repetida_conta_uma_vez(participacao, inst):
    r = responder_escolha_multipla(
        participacao, inst.multipla, _opcoes(inst, "A", "A"), agora=NO_PERIODO
    )
    assert _conjunto(r) == ["A"]
    assert RespostaOpcao.objects.filter(resposta=r).count() == 1


@pytest.mark.parametrize("vazio", [[], set(), (), None])
def test_selecao_vazia_ou_ausente(participacao, inst, vazio):
    rejeita_sem_gravar(
        participacao,
        Motivo.VALOR_VAZIO,
        responder_escolha_multipla,
        inst.multipla,
        vazio,
        campo="opcoes",
    )


def test_opcao_estranha_rejeita_o_conjunto_inteiro(participacao, inst):
    x = inst.opcao(inst.unica, "Sim")
    rejeita_sem_gravar(
        participacao,
        Motivo.OPCAO_DE_OUTRA_PERGUNTA,
        responder_escolha_multipla,
        inst.multipla,
        [*_opcoes(inst, "A"), x],
    )
    assert not Resposta.objects.filter(participacao=participacao).exists()


def test_todas_as_opcoes_sem_maximo_nem_exclusividade(participacao, inst):
    r = responder_escolha_multipla(
        participacao, inst.multipla, _opcoes(inst, "A", "B", "C", "Outro:"), agora=NO_PERIODO
    )
    assert _conjunto(r) == ["A", "B", "C", "Outro:"]


@pytest.mark.parametrize("valor", ["A", "opcao_isolada"])
def test_escolha_multipla_com_valor_de_forma_errada(participacao, inst, valor):
    if valor == "opcao_isolada":
        valor = inst.opcao(inst.multipla, "A")
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_INCOMPATIVEL, responder_escolha_multipla, inst.multipla, valor
    )


def test_escolha_multipla_em_pergunta_de_outro_tipo(participacao, inst):
    rejeita_sem_gravar(
        participacao,
        Motivo.VALOR_INCOMPATIVEL,
        responder_escolha_multipla,
        inst.unica,
        [inst.opcao(inst.unica, "Sim")],
    )


# --- US5: texto curto ---------------------------------------------------------------------


def test_texto_preservado_exatamente(participacao, inst):
    responder_texto(participacao, inst.texto, "  27 anos ", agora=NO_PERIODO)
    r = resposta(participacao, inst.texto)
    assert (r.texto, r.opcao_id, r.escala, r.complemento) == ("  27 anos ", None, None, None)


def test_texto_sem_validacao_de_formato(participacao, inst):
    responder_texto(participacao, inst.texto, "2020/2", agora=NO_PERIODO)
    assert resposta(participacao, inst.texto).texto == "2020/2"


@pytest.mark.parametrize("vazio", [None, "", "   "])
def test_texto_vazio_ou_ausente(participacao, inst, vazio):
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_VAZIO, responder_texto, inst.texto, vazio, campo="texto"
    )


@pytest.mark.parametrize("valor", [3, "opcao"])
def test_texto_com_valor_de_forma_errada(participacao, inst, valor):
    if valor == "opcao":
        valor = inst.opcao(inst.unica, "Sim")
    rejeita_sem_gravar(participacao, Motivo.VALOR_INCOMPATIVEL, responder_texto, inst.texto, valor)


def test_texto_em_pergunta_de_outro_tipo(participacao, inst):
    rejeita_sem_gravar(participacao, Motivo.VALOR_INCOMPATIVEL, responder_texto, inst.escala, "3")


# --- US6: escala --------------------------------------------------------------------------


@pytest.mark.parametrize("valor", [1, 3, 5])
def test_escala_dentro_dos_limites(participacao, inst, valor):
    responder_escala(participacao, inst.escala, valor, agora=NO_PERIODO)
    r = resposta(participacao, inst.escala)
    assert (r.escala, r.texto, r.opcao_id, r.complemento) == (valor, None, None, None)


@pytest.mark.parametrize("valor", [0, 6, -1])
def test_escala_fora_dos_limites(participacao, inst, valor):
    rejeita_sem_gravar(
        participacao, Motivo.ESCALA_FORA_DOS_LIMITES, responder_escala, inst.escala, valor
    )


@pytest.mark.parametrize("valor", [2.5, "3", True])
def test_escala_com_valor_de_forma_errada(participacao, inst, valor):
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_INCOMPATIVEL, responder_escala, inst.escala, valor
    )


def test_escala_ausente(participacao, inst):
    rejeita_sem_gravar(
        participacao, Motivo.VALOR_VAZIO, responder_escala, inst.escala, None, campo="escala"
    )


def test_escala_em_pergunta_de_outro_tipo(participacao, inst):
    rejeita_sem_gravar(participacao, Motivo.VALOR_INCOMPATIVEL, responder_escala, inst.texto, 3)


# --- US8: complemento de "Outro" ------------------------------------------------------------


def test_complemento_em_escolha_unica(participacao, inst):
    outro = inst.opcao(inst.unica_outro, "Outro:")
    responder_escolha_unica(
        participacao, inst.unica_outro, outro, complemento="Cuidando de familiar", agora=NO_PERIODO
    )
    r = resposta(participacao, inst.unica_outro)
    assert (r.opcao_id, r.complemento) == (outro.id, "Cuidando de familiar")


def test_complemento_em_escolha_multipla(participacao, inst):
    responder_escolha_multipla(
        participacao,
        inst.multipla,
        _opcoes(inst, "A", "Outro:"),
        complemento="  Bolsa de extensão ",
        agora=NO_PERIODO,
    )
    r = resposta(participacao, inst.multipla)
    assert (_conjunto(r), r.complemento) == (["A", "Outro:"], "  Bolsa de extensão ")


def test_complemento_sem_a_opcao_que_o_admite(participacao, inst):
    rejeita_sem_gravar(
        participacao,
        Motivo.COMPLEMENTO_NAO_ADMITIDO,
        responder_escolha_unica,
        inst.unica_outro,
        inst.opcao(inst.unica_outro, "A"),
        complemento="x",
    )
    rejeita_sem_gravar(
        participacao,
        Motivo.COMPLEMENTO_NAO_ADMITIDO,
        responder_escolha_multipla,
        inst.multipla,
        _opcoes(inst, "A", "B"),
        complemento="x",
    )


@pytest.mark.parametrize("vazio", ["", "  "])
def test_complemento_vazio(participacao, inst, vazio):
    rejeita_sem_gravar(
        participacao,
        Motivo.VALOR_VAZIO,
        responder_escolha_unica,
        inst.unica_outro,
        inst.opcao(inst.unica_outro, "Outro:"),
        complemento=vazio,
        campo="complemento",
    )


def test_complemento_de_forma_errada(participacao, inst):
    rejeita_sem_gravar(
        participacao,
        Motivo.VALOR_INCOMPATIVEL,
        responder_escolha_unica,
        inst.unica_outro,
        inst.opcao(inst.unica_outro, "Outro:"),
        complemento=3,
    )


def test_outro_sem_complemento_e_aceito(participacao, inst):
    responder_escolha_unica(
        participacao, inst.unica_outro, inst.opcao(inst.unica_outro, "Outro:"), agora=NO_PERIODO
    )
    assert resposta(participacao, inst.unica_outro).complemento is None


def test_substituir_outro_apaga_o_complemento(participacao, inst):
    responder_escolha_unica(
        participacao,
        inst.unica_outro,
        inst.opcao(inst.unica_outro, "Outro:"),
        complemento="x",
        agora=NO_PERIODO,
    )
    responder_escolha_unica(
        participacao, inst.unica_outro, inst.opcao(inst.unica_outro, "A"), agora=NO_PERIODO
    )
    r = resposta(participacao, inst.unica_outro)
    assert (r.opcao.texto, r.complemento) == ("A", None)


def test_texto_e_escala_nao_aceitam_complemento(participacao, inst):
    # FR-030 b pela assinatura: o parâmetro não existe nesses tipos.
    with pytest.raises(TypeError):
        responder_texto(participacao, inst.texto, "x", complemento="y", agora=NO_PERIODO)
    with pytest.raises(TypeError):
        responder_escala(participacao, inst.escala, 3, complemento="y", agora=NO_PERIODO)
    assert not Resposta.objects.filter(participacao=participacao).exists()


def test_mensagens_nao_contem_valor_declarado(participacao, inst):
    with pytest.raises(ParticipacaoRejeitada) as erro:
        responder_escala(participacao, inst.escala, 99, agora=NO_PERIODO)
    assert "99" not in str(erro.value)


# --- Regressão do code review --------------------------------------------------------------


def test_escritas_fora_da_multipla_nao_tocam_selecoes(participacao, inst):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as consultas:
        responder_texto(participacao, inst.texto, "27", agora=NO_PERIODO)
        responder_escala(participacao, inst.escala, 3, agora=NO_PERIODO)
        responder_escolha_unica(
            participacao, inst.unica, inst.opcao(inst.unica, "Sim"), agora=NO_PERIODO
        )
    tabela = RespostaOpcao._meta.db_table
    assert not [q["sql"] for q in consultas.captured_queries if tabela in q["sql"]]

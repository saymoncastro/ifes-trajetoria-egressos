"""Publicação e imutabilidade da Versão publicada: US5 (FR-011–FR-018, FR-059, SC-002).

A imutabilidade é garantida pelas operações (research R9): cada operação de escrita é
tentada numa Versão publicada, e o conteúdo lido depois tem de ser igual ao de antes.
"""

import inspect

import pytest

from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import EstadoVersao, Opcao, Pergunta, Secao, Versao
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada

pytestmark = pytest.mark.django_db



def _versao_completa(pesquisa, designacao="2024"):
    versao = op.criar_versao(pesquisa, designacao)
    op.alterar_versao(versao, titulo="Egresso Ifes", texto_abertura="Prezado(a) egresso(a)")
    termos = op.adicionar_secao(versao, 1, titulo="Termos", texto="Termos e condições.")
    q1 = op.adicionar_pergunta(termos, 1, "ESCOLHA_UNICA", "Concorda?", obrigatoria=True)
    op.adicionar_opcao(q1, 1, "Sim")
    op.adicionar_opcao(q1, 2, "Não")
    avaliacao = op.adicionar_secao(versao, 2, titulo="Avaliação")
    op.adicionar_pergunta(
        avaliacao, 1, "ESCALA", "Corcordo?", obrigatoria=True,
        escala=Escala(1, 5, "Disc", "Corcordo totalmente"),
    )
    q3 = op.adicionar_pergunta(avaliacao, 2, "ESCOLHA_MULTIPLA", "Bolsas?", obrigatoria=True)
    op.adicionar_opcao(q3, 1, "Ensino")
    op.adicionar_opcao(q3, 2, "Outro", complemento_textual=True)
    op.adicionar_pergunta(avaliacao, 3, "TEXTO_CURTO", "Ano?", obrigatoria=False)
    return versao


@pytest.fixture
def publicada(pesquisa):
    versao = _versao_completa(pesquisa)
    assert op.publicar(versao) == op.SituacaoPublicacao.PUBLICADA
    return Versao.objects.get(pk=versao.pk)


# --- Publicação ---------------------------------------------------------------------


def test_publicar_versao_completa(publicada):
    assert publicada.estado == EstadoVersao.PUBLICADA
    assert publicada.publicada_em is not None


def test_publicar_de_novo_nao_muda_nada(publicada):
    antes = conteudo_da_versao(publicada)
    assert op.publicar(publicada) == op.SituacaoPublicacao.JA_PUBLICADA
    assert conteudo_da_versao(publicada) == antes


def _pendencias(versao):
    with pytest.raises(OperacaoRejeitada) as erro:
        op.publicar(versao)
    return erro.value.violacoes


def test_versao_sem_secoes_nao_e_publicada(pesquisa):
    versao = op.criar_versao(pesquisa, "vazia")
    violacoes = _pendencias(versao)
    assert [(v.motivo, v.elemento) for v in violacoes] == [(Motivo.SEM_SECOES, versao.id)]
    assert conteudo_da_versao(versao).estado == EstadoVersao.RASCUNHO


def test_publicacao_informa_todas_as_pendencias(pesquisa):
    versao = op.criar_versao(pesquisa, "incompleta")
    vazia = op.adicionar_secao(versao, 1)
    secao = op.adicionar_secao(versao, 2)
    unica = op.adicionar_pergunta(secao, 1, "ESCOLHA_UNICA", "Uma opção?", obrigatoria=True)
    op.adicionar_opcao(unica, 1, "Só esta")
    multipla = op.adicionar_pergunta(secao, 2, "ESCOLHA_MULTIPLA", "Nenhuma?", obrigatoria=True)
    antes = conteudo_da_versao(versao)
    violacoes = _pendencias(versao)
    assert [(v.motivo, v.elemento) for v in violacoes] == [
        (Motivo.SECAO_SEM_PERGUNTAS, vazia.id),
        (Motivo.OPCOES_INSUFICIENTES, unica.id),
        (Motivo.OPCOES_INSUFICIENTES, multipla.id),
    ]
    assert conteudo_da_versao(versao) == antes


def test_destino_nao_posterior_impede_a_publicacao(pesquisa):
    versao = _versao_completa(pesquisa, "destinos")
    termos, avaliacao = Secao.objects.filter(versao=versao).order_by("posicao")
    op.definir_encaminhamento(avaliacao, termos)  # Seção anterior
    q1 = termos.perguntas.get()
    op.definir_regra(q1, q1.opcoes.get(texto="Não"), termos)  # a própria Seção
    violacoes = _pendencias(versao)
    assert [(v.motivo, v.elemento) for v in violacoes] == [
        (Motivo.DESTINO_NAO_POSTERIOR, q1.opcoes.get(texto="Não").id),
        (Motivo.DESTINO_NAO_POSTERIOR, avaliacao.id),
    ]


# --- SC-002: nada muda numa Versão publicada ----------------------------------------


@pytest.fixture
def elementos(publicada):
    termos, avaliacao = Secao.objects.filter(versao=publicada).order_by("posicao")
    q1 = Pergunta.objects.get(secao=termos)
    escala = Pergunta.objects.get(secao=avaliacao, tipo="ESCALA")
    return {
        "versao": publicada,
        "termos": termos,
        "avaliacao": avaliacao,
        "q1": q1,
        "escala": escala,
        "multipla": Pergunta.objects.get(secao=avaliacao, tipo="ESCOLHA_MULTIPLA"),
        "sim": Opcao.objects.get(pergunta=q1, texto="Sim"),
        "nao": Opcao.objects.get(pergunta=q1, texto="Não"),
    }


def _nada_muda(versao, tentativa):
    antes = conteudo_da_versao(versao)
    with pytest.raises(OperacaoRejeitada) as erro:
        tentativa()
    assert erro.value.motivos == (Motivo.VERSAO_PUBLICADA,)
    assert conteudo_da_versao(versao) == antes


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("designacao", "2024-b"),
        ("titulo", "Outro título"),
        ("texto_abertura", None),
        ("texto_encerramento", "Fim."),
    ],
)
def test_versao_publicada_nao_e_editada(elementos, campo, valor):
    versao = elementos["versao"]
    _nada_muda(versao, lambda: op.alterar_versao(versao, **{campo: valor}))


def test_versao_publicada_nao_volta_a_rascunho(elementos):
    versao = elementos["versao"]
    for nome in op.__all__:
        funcao = getattr(op, nome)
        if callable(funcao) and not isinstance(funcao, type):
            assert "estado" not in inspect.signature(funcao).parameters, nome
    antes = conteudo_da_versao(versao)
    assert op.publicar(versao) == op.SituacaoPublicacao.JA_PUBLICADA
    assert conteudo_da_versao(versao) == antes
    assert antes.estado == EstadoVersao.PUBLICADA


TENTATIVAS_DE_SECAO = {
    "adicionar": lambda e: op.adicionar_secao(e["versao"], 9, titulo="Nova"),
    "alterar titulo": lambda e: op.alterar_secao(e["termos"], titulo="Outro"),
    "alterar texto": lambda e: op.alterar_secao(e["termos"], texto=None),
    "remover": lambda e: op.remover_secao(e["avaliacao"]),
    "reordenar": lambda e: op.reordenar_secoes(e["versao"], [e["avaliacao"], e["termos"]]),
}


@pytest.mark.parametrize("tentativa", TENTATIVAS_DE_SECAO.values(), ids=TENTATIVAS_DE_SECAO)
def test_secao_de_versao_publicada_nao_muda(elementos, tentativa):
    _nada_muda(elementos["versao"], lambda: tentativa(elementos))


def test_encaminhamento_de_versao_publicada_nao_muda(elementos):
    _nada_muda(
        elementos["versao"],
        lambda: op.definir_encaminhamento(elementos["termos"], elementos["avaliacao"]),
    )


TENTATIVAS_DE_PERGUNTA = {
    "adicionar": lambda e: op.adicionar_pergunta(
        e["avaliacao"], 9, "TEXTO_CURTO", "Nova?", obrigatoria=True
    ),
    "alterar texto": lambda e: op.alterar_pergunta(e["q1"], texto="Concorda com os termos?"),
    "alterar texto explicativo": lambda e: op.alterar_pergunta(e["q1"], texto_explicativo="x"),
    "alterar obrigatoriedade": lambda e: op.alterar_pergunta(e["q1"], obrigatoria=False),
    "alterar escala": lambda e: op.alterar_pergunta(e["escala"], escala=Escala(0, 10)),
    "corrigir grafia do rótulo": lambda e: op.alterar_pergunta(
        e["escala"], escala=Escala(1, 5, "Disc", "Concordo totalmente")
    ),
    "mover": lambda e: op.mover_pergunta(e["q1"], e["avaliacao"], 9),
    "remover": lambda e: op.remover_pergunta(e["multipla"]),
    "reordenar": lambda e: op.reordenar_perguntas(
        e["avaliacao"], list(e["avaliacao"].perguntas.order_by("-posicao"))
    ),
}


@pytest.mark.parametrize("tentativa", TENTATIVAS_DE_PERGUNTA.values(), ids=TENTATIVAS_DE_PERGUNTA)
def test_pergunta_de_versao_publicada_nao_muda(elementos, tentativa):
    _nada_muda(elementos["versao"], lambda: tentativa(elementos))


TENTATIVAS_DE_OPCAO = {
    "adicionar": lambda e: op.adicionar_opcao(e["q1"], 9, "Talvez"),
    "alterar texto": lambda e: op.alterar_opcao(e["sim"], texto="Sim, concordo"),
    "alterar complemento": lambda e: op.alterar_opcao(e["sim"], complemento_textual=True),
    "remover": lambda e: op.remover_opcao(e["nao"]),
    "reordenar": lambda e: op.reordenar_opcoes(e["q1"], [e["nao"], e["sim"]]),
}


@pytest.mark.parametrize("tentativa", TENTATIVAS_DE_OPCAO.values(), ids=TENTATIVAS_DE_OPCAO)
def test_opcao_de_versao_publicada_nao_muda(elementos, tentativa):
    _nada_muda(elementos["versao"], lambda: tentativa(elementos))


def test_regra_de_versao_publicada_nao_muda(elementos):
    e = elementos
    _nada_muda(e["versao"], lambda: op.definir_regra(e["q1"], e["nao"], op.FINALIZAR))
    _nada_muda(e["versao"], lambda: op.remover_regra(e["q1"], e["nao"]))


def test_renomear_pesquisa_nao_altera_versao_publicada(pesquisa, publicada):
    antes = conteudo_da_versao(publicada)
    op.renomear_pesquisa(pesquisa, "Pesquisa de Egressos do Ifes")
    assert conteudo_da_versao(publicada) == antes


def test_referencia_a_outra_versao_gravada_fora_das_operacoes_impede_a_publicacao(pesquisa):
    # Sem gatilhos (ADR 0002), uma escrita direta pode criar a referência; a publicação a
    # rejeita explicitamente em vez de falhar.
    versao = _versao_completa(pesquisa)
    estranha = op.adicionar_secao(op.criar_versao(pesquisa, "2026"), 1)
    nao = Opcao.objects.get(pergunta__secao__versao=versao, texto="Não")
    termos = Secao.objects.get(versao=versao, posicao=1)
    Opcao.objects.filter(pk=nao.pk).update(regra_destino=estranha)
    Secao.objects.filter(pk=termos.pk).update(encaminhamento=estranha)
    violacoes = _pendencias(versao)
    assert [(v.motivo, v.elemento) for v in violacoes] == [
        (Motivo.REFERENCIA_OUTRA_VERSAO, termos.id),
        (Motivo.REFERENCIA_OUTRA_VERSAO, nao.id),
    ]

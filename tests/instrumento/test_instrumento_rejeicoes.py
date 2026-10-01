"""Rejeição explícita de estruturas inválidas: US9 (FR-058–FR-062, SC-004).

Um caso por `Motivo`: a operação é rejeitada com o motivo e o elemento esperados, e o
estado depois da rejeição é idêntico ao de antes.
"""

import pytest

from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta, Pesquisa, Secao, Versao
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada

pytestmark = pytest.mark.django_db


class Cenario:
    """Uma Versão em rascunho com duas Seções e uma pergunta de cada tipo de escolha, e
    uma segunda Versão da mesma Pesquisa (para referências entre Versões)."""

    def __init__(self):
        self.pesquisa = op.criar_pesquisa("Pesquisa")
        self.versao = op.criar_versao(self.pesquisa, "2024")
        self.s1 = op.adicionar_secao(self.versao, 1, titulo="S1")
        self.s2 = op.adicionar_secao(self.versao, 2, titulo="S2")
        self.unica = op.adicionar_pergunta(self.s1, 1, "ESCOLHA_UNICA", "Única?", obrigatoria=True)
        self.sim = op.adicionar_opcao(self.unica, 1, "Sim")
        self.nao = op.adicionar_opcao(self.unica, 2, "Não")
        self.multipla = op.adicionar_pergunta(
            self.s2, 1, "ESCOLHA_MULTIPLA", "Várias?", obrigatoria=True
        )
        self.ensino = op.adicionar_opcao(self.multipla, 1, "Ensino")
        self.outro = op.adicionar_opcao(self.multipla, 2, "Outro", complemento_textual=True)
        self.texto = op.adicionar_pergunta(self.s2, 2, "TEXTO_CURTO", "Ano?", obrigatoria=True)
        self.outra_versao = op.criar_versao(self.pesquisa, "2026")
        self.estranha = op.adicionar_secao(self.outra_versao, 1, titulo="De outra Versão")


def _vazia(c):
    return op.adicionar_secao(c.versao, 3, titulo="Vazia")


def _publicada(c):
    s3 = op.adicionar_secao(c.versao, 3)
    op.remover_pergunta(c.texto)
    op.adicionar_pergunta(s3, 1, "TEXTO_CURTO", "Fim?", obrigatoria=True)
    op.publicar(c.versao)
    return c.versao.id


def _encaminhada(c):
    s3 = op.adicionar_secao(c.versao, 3, titulo="Destino")
    op.definir_encaminhamento(c.s2, s3)
    return s3


def _encaminhamento_para_tras(c):
    op.definir_encaminhamento(c.s2, c.s1)
    return c.s2.id


# motivo → (preparação que devolve o elemento esperado, operação)
CASOS = {
    Motivo.VERSAO_PUBLICADA: (
        _publicada,
        lambda c: op.alterar_versao(c.versao, titulo="Corrigido"),
    ),
    Motivo.REFERENCIA_OUTRA_VERSAO: (
        lambda c: c.estranha.id,
        lambda c: op.definir_regra(c.unica, c.nao, c.estranha),
    ),
    Motivo.OPCAO_EM_TIPO_SEM_OPCOES: (
        lambda c: c.texto.id,
        lambda c: op.adicionar_opcao(c.texto, 1, "Sim"),
    ),
    Motivo.ESCALA_EM_TIPO_NAO_ESCALA: (
        lambda c: c.s2.id,
        lambda c: op.adicionar_pergunta(
            c.s2, 3, "TEXTO_CURTO", "P?", obrigatoria=True, escala=Escala(1, 5)
        ),
    ),
    Motivo.ESCALA_INVALIDA: (
        lambda c: c.s2.id,
        lambda c: op.adicionar_pergunta(
            c.s2, 3, "ESCALA", "P?", obrigatoria=True, escala=Escala(5, 1)
        ),
    ),
    Motivo.REGRA_EM_TIPO_INCOMPATIVEL: (
        lambda c: c.multipla.id,
        lambda c: op.definir_regra(c.multipla, c.ensino, c.s2),
    ),
    Motivo.OPCAO_DE_OUTRA_PERGUNTA: (
        lambda c: c.ensino.id,
        lambda c: op.definir_regra(c.unica, c.ensino, c.s2),
    ),
    Motivo.REGRA_JA_DEFINIDA: (
        lambda c: op.definir_regra(c.unica, c.nao, op.FINALIZAR).id,
        lambda c: op.definir_regra(c.unica, c.nao, c.s2),
    ),
    Motivo.POSICAO_OCUPADA: (
        lambda c: c.versao.id,
        lambda c: op.adicionar_secao(c.versao, 2),
    ),
    Motivo.ORDEM_INCOMPLETA: (
        lambda c: c.versao.id,
        lambda c: op.reordenar_secoes(c.versao, [c.s2]),
    ),
    Motivo.POSICAO_INVALIDA: (
        lambda c: c.versao.id,
        lambda c: op.adicionar_secao(c.versao, 0),
    ),
    Motivo.TIPO_NAO_SUPORTADO: (
        lambda c: c.s2.id,
        lambda c: op.adicionar_pergunta(c.s2, 3, "DATA", "Quando?", obrigatoria=True),
    ),
    Motivo.TEXTO_VAZIO: (
        lambda c: c.unica.id,
        lambda c: op.adicionar_opcao(c.unica, 3, "  "),
    ),
    Motivo.DESIGNACAO_REPETIDA: (
        lambda c: c.versao.id,
        lambda c: op.alterar_versao(c.versao, designacao="2026"),
    ),
    Motivo.OPCAO_REPETIDA: (
        lambda c: c.unica.id,
        lambda c: op.adicionar_opcao(c.unica, 3, "Sim"),
    ),
    Motivo.COMPLEMENTO_REPETIDO: (
        lambda c: c.multipla.id,
        lambda c: op.adicionar_opcao(c.multipla, 3, "Mais um", complemento_textual=True),
    ),
    Motivo.SECAO_COM_PERGUNTAS: (
        lambda c: c.s1.id,
        lambda c: op.remover_secao(c.s1),
    ),
    Motivo.SECAO_REFERENCIADA: (
        lambda c: _encaminhada(c).id,
        lambda c: op.remover_secao(Secao.objects.get(versao=c.versao, posicao=3)),
    ),
    Motivo.SEM_SECOES: (
        lambda c: (op.remover_secao(c.estranha), c.outra_versao.id)[1],
        lambda c: op.publicar(c.outra_versao),
    ),
    Motivo.SECAO_SEM_PERGUNTAS: (
        lambda c: _vazia(c).id,
        lambda c: op.publicar(c.versao),
    ),
    Motivo.OPCOES_INSUFICIENTES: (
        lambda c: (op.remover_opcao(c.nao), c.unica.id)[1],
        lambda c: op.publicar(c.versao),
    ),
    Motivo.DESTINO_NAO_POSTERIOR: (
        _encaminhamento_para_tras,
        lambda c: op.publicar(c.versao),
    ),
}


def test_todos_os_motivos_tem_caso():
    assert set(CASOS) == set(Motivo)


def _estado():
    return (
        tuple(conteudo_da_versao(v) for v in Versao.objects.order_by("id")),
        tuple(m.objects.count() for m in (Pesquisa, Versao, Secao, Pergunta, Opcao)),
    )


@pytest.mark.parametrize(
    "motivo", [pytest.param(m, id=m.name) for m in CASOS]
)
def test_rejeicao_explicita_sem_alteracao(motivo):
    preparar, operacao = CASOS[motivo]
    cenario = Cenario()
    elemento = preparar(cenario)
    antes = _estado()
    with pytest.raises(OperacaoRejeitada) as erro:
        operacao(cenario)
    violacao = erro.value.violacoes[0]
    assert (violacao.motivo, violacao.elemento) == (motivo, elemento)
    assert _estado() == antes

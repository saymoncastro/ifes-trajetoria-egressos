"""Nova Versão a partir de existente: US6 (FR-019–FR-023, SC-003)."""

import pytest

from tests.instrumento.construcao import sem_identidades
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import EstadoVersao, Opcao, Pergunta, Secao, Versao
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada

pytestmark = pytest.mark.django_db



def _origem(pesquisa, com_navegacao=False):
    versao = op.criar_versao(pesquisa, "2024")
    op.alterar_versao(versao, titulo="Egresso Ifes", texto_encerramento="Fim.")
    termos = op.adicionar_secao(versao, 1, titulo="Termos", texto="Termos.")
    q1 = op.adicionar_pergunta(termos, 1, "ESCOLHA_UNICA", "Concorda?", obrigatoria=True)
    op.adicionar_opcao(q1, 1, "Sim")
    nao = op.adicionar_opcao(q1, 2, "Não")
    trabalho = op.adicionar_secao(versao, 2, titulo="Trabalho")
    q2 = op.adicionar_pergunta(trabalho, 1, "ESCOLHA_MULTIPLA", "Bolsas?", obrigatoria=True,
                               texto_explicativo="Não considerar auxílio.")
    op.adicionar_opcao(q2, 1, "Ensino")
    op.adicionar_opcao(q2, 2, "Outro", complemento_textual=True)
    op.adicionar_pergunta(trabalho, 2, "ESCALA", "Na área?", obrigatoria=False,
                          escala=Escala(1, 5, "Disc", "Concordo totalmente"))
    op.adicionar_pergunta(trabalho, 3, "TEXTO_CURTO", "Ano?", obrigatoria=True)
    estudo = op.adicionar_secao(versao, 3, titulo="Estudo")
    op.adicionar_pergunta(estudo, 1, "TEXTO_CURTO", "Curso?", obrigatoria=False)
    if com_navegacao:
        op.definir_regra(q1, nao, op.FINALIZAR)
        op.definir_regra(q1, Opcao.objects.get(pergunta=q1, texto="Sim"), estudo)
        op.definir_encaminhamento(termos, trabalho)
    return versao


def _ids(conteudo):
    ids = set()
    for secao in conteudo.secoes:
        ids.add(secao.id)
        for pergunta in secao.perguntas:
            ids.add(pergunta.id)
            ids.update(opcao.id for opcao in pergunta.opcoes)
    return ids


def _referencias(conteudo):
    refs = {s.encaminhamento_id for s in conteudo.secoes}
    refs |= {
        o.regra.destino_secao_id
        for s in conteudo.secoes
        for p in s.perguntas
        for o in p.opcoes
        if o.regra
    }
    return refs - {None}


def _copia_de_publicada(pesquisa, com_navegacao=False):
    origem = _origem(pesquisa, com_navegacao)
    op.publicar(origem)
    antes = conteudo_da_versao(origem)
    nova = op.criar_versao_a_partir_de(origem, "2026")
    return origem, antes, nova


def test_nova_versao_em_rascunho_na_mesma_pesquisa(pesquisa):
    origem, _, nova = _copia_de_publicada(pesquisa)
    nova = Versao.objects.get(pk=nova.pk)
    assert (nova.pesquisa_id, nova.estado, nova.origem_id, nova.publicada_em) == (
        pesquisa.id,
        EstadoVersao.RASCUNHO,
        origem.id,
        None,
    )


def test_conteudo_equivalente_com_identidades_proprias(pesquisa):
    origem, antes, nova = _copia_de_publicada(pesquisa)
    copia = conteudo_da_versao(nova)
    assert _ids(copia).isdisjoint(_ids(antes))
    assert sem_identidades(copia) == sem_identidades(antes)


def test_referencias_internas_apontam_para_a_nova_versao(pesquisa):
    origem, antes, nova = _copia_de_publicada(pesquisa, com_navegacao=True)
    copia = conteudo_da_versao(nova)
    assert _referencias(copia) <= {s.id for s in copia.secoes}
    assert _referencias(copia).isdisjoint(_ids(antes))
    assert sem_identidades(copia) == sem_identidades(antes)


def test_alterar_a_copia_nao_altera_a_origem(pesquisa):
    origem, antes, nova = _copia_de_publicada(pesquisa)
    secao = Secao.objects.get(versao=nova, posicao=2)
    op.alterar_pergunta(Pergunta.objects.get(secao=secao, posicao=1), texto="Recebeu bolsa?")
    op.alterar_pergunta(Pergunta.objects.get(secao=secao, posicao=2), escala=Escala(0, 10))
    op.alterar_opcao(Opcao.objects.get(pergunta__secao=secao, texto="Ensino"), texto="Monitoria")
    op.alterar_versao(nova, titulo="Egresso Ifes 2026")
    op.remover_pergunta(Pergunta.objects.get(secao=secao, posicao=3))
    assert conteudo_da_versao(origem) == antes


def test_alterar_regra_da_copia_nao_altera_a_origem(pesquisa):
    origem, antes, nova = _copia_de_publicada(pesquisa, com_navegacao=True)
    q1 = Pergunta.objects.get(secao__versao=nova, secao__posicao=1)
    nao = Opcao.objects.get(pergunta=q1, texto="Não")
    op.remover_regra(q1, nao)
    op.definir_encaminhamento(Secao.objects.get(versao=nova, posicao=1), None)
    assert conteudo_da_versao(origem) == antes


def test_copia_de_rascunho_e_independente_da_origem(pesquisa):
    origem = _origem(pesquisa)
    nova = op.criar_versao_a_partir_de(origem, "2026")
    copia = conteudo_da_versao(nova)
    op.alterar_versao(origem, titulo="Mudou na origem")
    op.alterar_opcao(Opcao.objects.get(pergunta__secao__versao=origem, texto="Sim"), texto="S")
    assert conteudo_da_versao(nova) == copia


def test_designacao_repetida_nao_cria_nada(pesquisa):
    origem = _origem(pesquisa)
    linhas = (Versao.objects.count(), Secao.objects.count(), Opcao.objects.count())
    with pytest.raises(OperacaoRejeitada) as erro:
        op.criar_versao_a_partir_de(origem, "2024")
    assert erro.value.motivos == (Motivo.DESIGNACAO_REPETIDA,)
    assert (Versao.objects.count(), Secao.objects.count(), Opcao.objects.count()) == linhas


def test_copia_usa_numero_fixo_de_consultas(pesquisa, django_assert_max_num_queries):
    # A cópia não faz uma consulta por Pergunta ou Opção: bulk_create e bulk_update.
    origem = _origem(pesquisa, com_navegacao=True)
    secao = op.adicionar_secao(origem, 9, titulo="Muitas")
    for n in range(1, 41):
        pergunta = op.adicionar_pergunta(secao, n, "ESCOLHA_UNICA", f"P{n}?", obrigatoria=True)
        for m in range(1, 6):
            op.adicionar_opcao(pergunta, m, f"Opção {m}")
    with django_assert_max_num_queries(15):
        nova = op.criar_versao_a_partir_de(origem, "2026")
    assert sem_identidades(conteudo_da_versao(nova)) == sem_identidades(
        conteudo_da_versao(origem)
    )

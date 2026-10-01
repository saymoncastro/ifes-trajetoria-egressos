"""Estrutura do instrumento em rascunho: US1–US4 (specs/002-pesquisa-versao-instrumento)."""

import inspect

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.instrumento.construcao import rejeita
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import EstadoVersao, Opcao, TipoPergunta, Versao
from trajetoria.instrumento.regras import Motivo

pytestmark = pytest.mark.django_db


# --- US1: Pesquisa e Versão em rascunho ---------------------------------------------


def test_pesquisa_nasce_sem_versoes(pesquisa):
    assert pesquisa.nome == "Pesquisa Institucional de Egressos"
    assert pesquisa.versoes.count() == 0


def test_versao_nasce_em_rascunho_e_pertence_a_pesquisa(pesquisa):
    versao = op.criar_versao(pesquisa, "2024")
    assert versao.estado == EstadoVersao.RASCUNHO
    assert versao.publicada_em is None
    assert versao.origem is None
    assert versao.pesquisa_id == pesquisa.id


def test_pesquisa_com_varias_versoes_distintas(pesquisa):
    v2024 = op.criar_versao(pesquisa, "2024")
    v2026 = op.criar_versao(pesquisa, "2026")
    assert v2024.id != v2026.id
    assert list(pesquisa.versoes.values_list("designacao", flat=True)) == ["2024", "2026"]


def test_designacao_repetida_na_mesma_pesquisa_e_rejeitada(pesquisa, versao):
    rejeita(Motivo.DESIGNACAO_REPETIDA, op.criar_versao, pesquisa, "2024")
    assert Versao.objects.count() == 1


def test_mesma_designacao_em_outra_pesquisa_e_aceita(versao):
    outra = op.criar_pesquisa("Outra pesquisa")
    assert op.criar_versao(outra, "2024").designacao == "2024"


def test_renomear_pesquisa_altera_so_o_nome(pesquisa, versao):
    op.renomear_pesquisa(pesquisa, "Pesquisa de Egressos")
    pesquisa.refresh_from_db()
    assert pesquisa.nome == "Pesquisa de Egressos"
    assert conteudo_da_versao(versao).designacao == "2024"


def test_textos_da_versao_sao_alteraveis_e_removiveis(versao):
    op.alterar_versao(
        versao,
        titulo="Egresso Ifes",
        texto_abertura="Prezado(a) egresso(a)",
        texto_encerramento="Agradecemos a participação.",
    )
    conteudo = conteudo_da_versao(versao)
    assert (conteudo.titulo, conteudo.texto_abertura, conteudo.texto_encerramento) == (
        "Egresso Ifes",
        "Prezado(a) egresso(a)",
        "Agradecemos a participação.",
    )
    op.alterar_versao(versao, texto_abertura=None)
    conteudo = conteudo_da_versao(versao)
    assert conteudo.texto_abertura is None
    assert conteudo.titulo == "Egresso Ifes"


def test_textos_ausentes_aparecem_como_none(versao):
    conteudo = conteudo_da_versao(versao)
    assert (conteudo.titulo, conteudo.texto_abertura, conteudo.texto_encerramento) == (
        None,
        None,
        None,
    )


def test_alterar_designacao_em_rascunho(pesquisa, versao):
    op.criar_versao(pesquisa, "2026")
    op.alterar_versao(versao, designacao="2024-b")
    assert conteudo_da_versao(versao).designacao == "2024-b"
    rejeita(Motivo.DESIGNACAO_REPETIDA, op.alterar_versao, versao, designacao="2026")


@pytest.mark.parametrize("texto", ["", "   "])
def test_textos_vazios_sao_rejeitados(pesquisa, versao, texto):
    rejeita(Motivo.TEXTO_VAZIO, op.criar_pesquisa, texto)
    rejeita(Motivo.TEXTO_VAZIO, op.criar_versao, pesquisa, texto)
    rejeita(Motivo.TEXTO_VAZIO, op.renomear_pesquisa, pesquisa, texto)
    rejeita(Motivo.TEXTO_VAZIO, op.alterar_versao, versao, titulo=texto)


def test_texto_e_gravado_sem_alteracao(pesquisa):
    versao = op.criar_versao(pesquisa, "  2024 ")
    assert conteudo_da_versao(versao).designacao == "  2024 "


def test_nada_depende_de_pessoa_ou_conclusao(pesquisa, versao):
    # FR-065: o instrumento existe sem nenhuma Pessoa ou Conclusão Acadêmica.
    assert Pessoa.objects.count() == 0
    assert ConclusaoAcademica.objects.count() == 0


# --- US2: Seções e Perguntas ordenadas ----------------------------------------------


def _texto_curto(secao, posicao, texto="Pergunta?", **kwargs):
    kwargs.setdefault("obrigatoria", True)
    return op.adicionar_pergunta(secao, posicao, "TEXTO_CURTO", texto, **kwargs)


def test_secoes_seguem_as_posicoes_e_nao_a_criacao(versao):
    for posicao in (3, 1, 2):
        op.adicionar_secao(versao, posicao, titulo=f"S{posicao}")
    conteudo = conteudo_da_versao(versao)
    assert [s.titulo for s in conteudo.secoes] == ["S1", "S2", "S3"]
    assert conteudo_da_versao(versao) == conteudo


def test_perguntas_seguem_as_posicoes_e_nao_a_criacao(versao):
    secao = op.adicionar_secao(versao, 1)
    for posicao in (2, 3, 1):
        _texto_curto(secao, posicao, f"P{posicao}")
    perguntas = conteudo_da_versao(versao).secoes[0].perguntas
    assert [p.texto for p in perguntas] == ["P1", "P2", "P3"]


def test_secao_sem_titulo_aparece_sem_titulo(versao):
    op.adicionar_secao(versao, 1)
    secao = conteudo_da_versao(versao).secoes[0]
    assert (secao.titulo, secao.texto, secao.encaminhamento_id) == (None, None, None)


def test_textos_da_secao_sao_alteraveis(versao):
    secao = op.adicionar_secao(versao, 1, titulo="Termos e condições", texto="Termos.")
    op.alterar_secao(secao, texto=None)
    lida = conteudo_da_versao(versao).secoes[0]
    assert (lida.titulo, lida.texto) == ("Termos e condições", None)


def test_reordenar_secoes_renumera_na_ordem_dada(versao):
    a, b, c = (op.adicionar_secao(versao, n, titulo=t) for n, t in ((1, "A"), (2, "B"), (5, "C")))
    op.reordenar_secoes(versao, [c, a, b])
    secoes = conteudo_da_versao(versao).secoes
    assert [(s.titulo, s.posicao) for s in secoes] == [("C", 1), ("A", 2), ("B", 3)]


def test_reordenar_perguntas_renumera_na_ordem_dada(versao):
    secao = op.adicionar_secao(versao, 1)
    p1, p2 = _texto_curto(secao, 1, "P1"), _texto_curto(secao, 2, "P2")
    op.reordenar_perguntas(secao, [p2, p1])
    perguntas = conteudo_da_versao(versao).secoes[0].perguntas
    assert [(p.texto, p.posicao) for p in perguntas] == [("P2", 1), ("P1", 2)]


def test_reordenacao_incompleta_ou_com_repeticao_e_rejeitada(pesquisa, versao):
    a, b = op.adicionar_secao(versao, 1), op.adicionar_secao(versao, 2)
    estranha = op.adicionar_secao(op.criar_versao(pesquisa, "2026"), 1)
    for ordem in ([a], [a, a], [a, b, estranha], [a, estranha]):
        rejeita(Motivo.ORDEM_INCOMPLETA, op.reordenar_secoes, versao, ordem)
    p1 = _texto_curto(a, 1)
    rejeita(Motivo.ORDEM_INCOMPLETA, op.reordenar_perguntas, a, [])
    rejeita(Motivo.ORDEM_INCOMPLETA, op.reordenar_perguntas, a, [p1, p1])


@pytest.mark.parametrize("posicao", [0, -1, True, 1.5, "1"])
def test_posicao_invalida(versao, posicao):
    rejeita(Motivo.POSICAO_INVALIDA, op.adicionar_secao, versao, posicao)
    secao = op.adicionar_secao(versao, 1)
    rejeita(Motivo.POSICAO_INVALIDA, _texto_curto, secao, posicao)


def test_posicao_ocupada(versao):
    secao = op.adicionar_secao(versao, 1)
    rejeita(Motivo.POSICAO_OCUPADA, op.adicionar_secao, versao, 1)
    _texto_curto(secao, 1)
    rejeita(Motivo.POSICAO_OCUPADA, _texto_curto, secao, 1)


def test_mover_pergunta_para_outra_secao_mantem_identidade(versao):
    origem, destino = op.adicionar_secao(versao, 1), op.adicionar_secao(versao, 2)
    pergunta = _texto_curto(origem, 1)
    _texto_curto(destino, 1, "Já está lá")
    rejeita(Motivo.POSICAO_OCUPADA, op.mover_pergunta, pergunta, destino, 1)
    op.mover_pergunta(pergunta, destino, 2)
    secoes = conteudo_da_versao(versao).secoes
    assert secoes[0].perguntas == ()
    assert [p.id for p in secoes[1].perguntas][1] == pergunta.id


def test_mover_pergunta_na_mesma_secao(versao):
    secao = op.adicionar_secao(versao, 1)
    pergunta = _texto_curto(secao, 1)
    op.mover_pergunta(pergunta, secao, 4)
    assert conteudo_da_versao(versao).secoes[0].perguntas[0].posicao == 4


def test_mover_pergunta_para_outra_versao_e_rejeitado(pesquisa, versao):
    pergunta = _texto_curto(op.adicionar_secao(versao, 1), 1)
    estranha = op.adicionar_secao(op.criar_versao(pesquisa, "2026"), 1)
    rejeita(Motivo.REFERENCIA_OUTRA_VERSAO, op.mover_pergunta, pergunta, estranha, 1)


def test_remover_pergunta_e_secao(versao):
    secao = op.adicionar_secao(versao, 1)
    pergunta = _texto_curto(secao, 1)
    rejeita(Motivo.SECAO_COM_PERGUNTAS, op.remover_secao, secao)
    op.remover_pergunta(pergunta)
    op.remover_secao(secao)
    assert conteudo_da_versao(versao).secoes == ()


def test_alterar_pergunta_mantem_identidade(versao):
    pergunta = _texto_curto(op.adicionar_secao(versao, 1), 1, "Quantos anos você tem?")
    op.alterar_pergunta(
        pergunta, texto="Idade?", texto_explicativo="Exemplo: 30", obrigatoria=False
    )
    lida = conteudo_da_versao(versao).secoes[0].perguntas[0]
    assert (lida.id, lida.texto, lida.texto_explicativo, lida.obrigatoria) == (
        pergunta.id,
        "Idade?",
        "Exemplo: 30",
        False,
    )


# --- US3: os quatro tipos -----------------------------------------------------------

ESCALA_1_5 = Escala(1, 5, "Discordo totalmente", "Concordo totalmente")


@pytest.fixture
def secao(versao):
    return op.adicionar_secao(versao, 1)


def test_uma_pergunta_de_cada_tipo(versao, secao):
    op.adicionar_pergunta(secao, 1, "ESCOLHA_UNICA", "Você é PcD?", obrigatoria=True)
    op.adicionar_pergunta(
        secao, 2, TipoPergunta.ESCOLHA_MULTIPLA, "Publicações?", obrigatoria=True
    )
    op.adicionar_pergunta(secao, 3, "TEXTO_CURTO", "Ano de conclusão?", obrigatoria=True)
    op.adicionar_pergunta(
        secao, 4, "ESCALA", "Gosto por cultura aumentou.", obrigatoria=False, escala=ESCALA_1_5
    )
    perguntas = conteudo_da_versao(versao).secoes[0].perguntas
    assert [p.tipo for p in perguntas] == list(TipoPergunta)
    assert [p.escala for p in perguntas] == [None, None, None, ESCALA_1_5]


@pytest.mark.parametrize("tipo", ["DATA", "MATRIZ", "UPLOAD", "escala", None])
def test_tipo_fora_dos_quatro_e_rejeitado(secao, tipo):
    rejeita(Motivo.TIPO_NAO_SUPORTADO, op.adicionar_pergunta, secao, 1, tipo, "P?",
             obrigatoria=True)


@pytest.mark.parametrize(
    "escala", [None, Escala(5, 1), Escala(3, 3), Escala(1.0, 5), Escala(True, 5), "1-5"]
)
def test_escala_invalida(secao, escala):
    rejeita(Motivo.ESCALA_INVALIDA, op.adicionar_pergunta, secao, 1, "ESCALA", "P?",
             obrigatoria=True, escala=escala)


def test_rotulo_de_escala_vazio(secao):
    rejeita(Motivo.TEXTO_VAZIO, op.adicionar_pergunta, secao, 1, "ESCALA", "P?",
             obrigatoria=True, escala=Escala(1, 5, ""))


def test_escala_sem_rotulos(versao, secao):
    op.adicionar_pergunta(secao, 1, "ESCALA", "P?", obrigatoria=True, escala=Escala(0, 10))
    escala = conteudo_da_versao(versao).secoes[0].perguntas[0].escala
    assert (escala.rotulo_inicio, escala.rotulo_fim) == (None, None)


@pytest.mark.parametrize("tipo", ["ESCOLHA_UNICA", "ESCOLHA_MULTIPLA", "TEXTO_CURTO"])
def test_escala_em_tipo_nao_escala(secao, tipo):
    rejeita(Motivo.ESCALA_EM_TIPO_NAO_ESCALA, op.adicionar_pergunta, secao, 1, tipo, "P?",
             obrigatoria=True, escala=ESCALA_1_5)


@pytest.mark.parametrize("tipo", list(TipoPergunta))
def test_obrigatoriedade_e_texto_explicativo_em_todos_os_tipos(versao, secao, tipo):
    escala = ESCALA_1_5 if tipo == TipoPergunta.ESCALA else None
    op.adicionar_pergunta(secao, 1, tipo, "P?", obrigatoria=False,
                          texto_explicativo="Obs: explicação.", escala=escala)
    lida = conteudo_da_versao(versao).secoes[0].perguntas[0]
    assert (lida.obrigatoria, lida.texto_explicativo) == (False, "Obs: explicação.")


def test_tipo_e_imutavel(secao):
    # FR-062: para mudar o tipo, remove-se a Pergunta e cria-se outra.
    assert "tipo" not in inspect.signature(op.alterar_pergunta).parameters
    pergunta = op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", "P?", obrigatoria=True)
    with pytest.raises(TypeError):
        op.alterar_pergunta(pergunta, tipo="ESCALA")


def test_alterar_escala(versao, secao):
    pergunta = op.adicionar_pergunta(secao, 1, "ESCALA", "P?", obrigatoria=True,
                                     escala=ESCALA_1_5)
    op.alterar_pergunta(pergunta, escala=Escala(0, 10))
    assert conteudo_da_versao(versao).secoes[0].perguntas[0].escala == Escala(0, 10)
    rejeita(Motivo.ESCALA_INVALIDA, op.alterar_pergunta, pergunta, escala=None)
    texto = op.adicionar_pergunta(secao, 2, "TEXTO_CURTO", "P?", obrigatoria=True)
    rejeita(Motivo.ESCALA_EM_TIPO_NAO_ESCALA, op.alterar_pergunta, texto, escala=ESCALA_1_5)


# --- US4: Opções e escalas ----------------------------------------------------------


def _escolha(secao, posicao=1, tipo="ESCOLHA_UNICA", texto="P?"):
    return op.adicionar_pergunta(secao, posicao, tipo, texto, obrigatoria=True)


def _opcoes(versao, secao_idx=0, pergunta_idx=0):
    return conteudo_da_versao(versao).secoes[secao_idx].perguntas[pergunta_idx].opcoes


def test_opcoes_seguem_as_posicoes_com_identidade_propria(versao, secao):
    pergunta = _escolha(secao)
    nao = op.adicionar_opcao(pergunta, 2, "Não")
    sim = op.adicionar_opcao(pergunta, 1, "Sim")
    opcoes = _opcoes(versao)
    assert [(o.texto, o.id) for o in opcoes] == [("Sim", sim.id), ("Não", nao.id)]
    assert all(o.regra is None and not o.complemento_textual for o in opcoes)


def test_alterar_texto_da_opcao_mantem_identidade(versao, secao):
    opcao = op.adicionar_opcao(_escolha(secao), 1, "Branco")
    op.alterar_opcao(opcao, texto="Branco(a)")
    assert [(o.id, o.texto) for o in _opcoes(versao)] == [(opcao.id, "Branco(a)")]


@pytest.mark.parametrize("tipo", ["ESCOLHA_UNICA", "ESCOLHA_MULTIPLA"])
def test_complemento_textual(versao, secao, tipo):
    pergunta = _escolha(secao, tipo=tipo)
    op.adicionar_opcao(pergunta, 1, "Livro")
    op.adicionar_opcao(pergunta, 2, "Outro", complemento_textual=True)
    assert [o.complemento_textual for o in _opcoes(versao)] == [False, True]
    rejeita(Motivo.COMPLEMENTO_REPETIDO, op.adicionar_opcao, pergunta, 3, "Mais um",
             complemento_textual=True)
    livro = Opcao.objects.get(texto="Livro")
    rejeita(Motivo.COMPLEMENTO_REPETIDO, op.alterar_opcao, livro, complemento_textual=True)


@pytest.mark.parametrize("tipo", ["TEXTO_CURTO", "ESCALA"])
def test_opcao_em_tipo_sem_opcoes(secao, tipo):
    escala = ESCALA_1_5 if tipo == "ESCALA" else None
    pergunta = op.adicionar_pergunta(secao, 1, tipo, "P?", obrigatoria=True, escala=escala)
    rejeita(Motivo.OPCAO_EM_TIPO_SEM_OPCOES, op.adicionar_opcao, pergunta, 1, "Sim")


def test_texto_repetido_na_mesma_pergunta(secao):
    pergunta = _escolha(secao)
    op.adicionar_opcao(pergunta, 1, "Sim")
    nao = op.adicionar_opcao(pergunta, 2, "Não")
    rejeita(Motivo.OPCAO_REPETIDA, op.adicionar_opcao, pergunta, 3, "Sim")
    rejeita(Motivo.OPCAO_REPETIDA, op.alterar_opcao, nao, texto="Sim")
    rejeita(Motivo.TEXTO_VAZIO, op.adicionar_opcao, pergunta, 3, " ")


def test_listas_iguais_em_perguntas_diferentes_sao_independentes(versao, secao):
    # Lista E de Q8 e Q9: cada pergunta tem suas próprias Opções (FR-043).
    pai, mae = _escolha(secao, 1, texto="Pai?"), _escolha(secao, 2, texto="Mãe?")
    for pergunta in (pai, mae):
        op.adicionar_opcao(pergunta, 1, "Sem instrução")
        op.adicionar_opcao(pergunta, 2, "Não sei dizer")
    op.alterar_opcao(pai.opcoes.get(posicao=1), texto="Sem escolaridade")
    assert [o.texto for o in _opcoes(versao, 0, 1)] == ["Sem instrução", "Não sei dizer"]
    assert {o.id for o in _opcoes(versao, 0, 0)}.isdisjoint(o.id for o in _opcoes(versao, 0, 1))


def test_textos_preservados_exatamente(versao, secao):
    op.adicionar_pergunta(secao, 1, "ESCALA", "P?", obrigatoria=True,
                          escala=Escala(1, 5, "Disc", "Corcordo totalmente"))
    pergunta = _escolha(secao, 2)
    op.adicionar_opcao(pergunta, 1, "Outros: transferência, remoção,  etc. ")
    perguntas = conteudo_da_versao(versao).secoes[0].perguntas
    assert perguntas[0].escala.rotulo_fim == "Corcordo totalmente"
    assert perguntas[1].opcoes[0].texto == "Outros: transferência, remoção,  etc. "


def test_reordenar_e_remover_opcoes(versao, secao):
    pergunta = _escolha(secao)
    a, b, c = (op.adicionar_opcao(pergunta, n, t) for n, t in ((1, "A"), (2, "B"), (3, "C")))
    op.reordenar_opcoes(pergunta, [c, a, b])
    assert [o.texto for o in _opcoes(versao)] == ["C", "A", "B"]
    rejeita(Motivo.ORDEM_INCOMPLETA, op.reordenar_opcoes, pergunta, [c, a])
    op.remover_opcao(a)
    assert [o.texto for o in _opcoes(versao)] == ["C", "B"]
    rejeita(Motivo.POSICAO_OCUPADA, op.adicionar_opcao, pergunta, 1, "D")


def test_remover_pergunta_remove_opcoes(secao):
    pergunta = _escolha(secao)
    op.adicionar_opcao(pergunta, 1, "Sim")
    op.remover_pergunta(pergunta)
    assert not Opcao.objects.filter(pergunta_id=pergunta.id).exists()


def test_lista_extensa_de_opcoes(versao, secao):
    pergunta = _escolha(secao)
    for n in range(1, 81):
        op.adicionar_opcao(pergunta, n, f"Curso {n:02d}")
    assert len(_opcoes(versao)) == 80


# --- Tipos de argumento e concorrência (code review) --------------------------------


def test_tipo_errado_de_argumento_e_typeerror_sem_escrita(pesquisa, versao, secao):
    # Erro de programação, não valor de domínio: TypeError antes de qualquer escrita.
    with pytest.raises(TypeError):
        op.criar_versao(pesquisa, 2024)
    with pytest.raises(TypeError):
        op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", "P?", obrigatoria=None)
    with pytest.raises(TypeError):
        op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", "P?", obrigatoria="sim")
    pergunta = op.adicionar_pergunta(secao, 1, "ESCOLHA_UNICA", "P?", obrigatoria=True)
    with pytest.raises(TypeError):
        op.alterar_pergunta(pergunta, obrigatoria=1)
    with pytest.raises(TypeError):
        op.adicionar_opcao(pergunta, 1, "Sim", complemento_textual="x")
    opcao = op.adicionar_opcao(pergunta, 1, "Sim")
    with pytest.raises(TypeError):
        op.alterar_opcao(opcao, complemento_textual=None)
    with pytest.raises(TypeError):
        op.definir_encaminhamento(secao, secao.id)
    assert Versao.objects.filter(pesquisa=pesquisa).count() == 1
    assert [p.obrigatoria for p in conteudo_da_versao(versao).secoes[0].perguntas] == [True]
    assert conteudo_da_versao(versao).secoes[0].perguntas[0].opcoes[0].complemento_textual is False


@pytest.mark.parametrize(
    "operacao",
    [
        lambda p, v: op.criar_versao(p, "2026"),
        lambda p, v: op.alterar_versao(v, designacao="2024-b"),
        lambda p, v: op.criar_versao_a_partir_de(v, "2026"),
    ],
    ids=["criar_versao", "alterar_versao", "criar_versao_a_partir_de"],
)
def test_toda_gravacao_de_designacao_bloqueia_a_pesquisa(pesquisa, versao, operacao):
    # A verificação de designação repetida só é segura sob concorrência se todas as
    # operações que gravam designação serializarem na Pesquisa.
    with CaptureQueriesContext(connection) as consultas:
        operacao(pesquisa, versao)
    assert any(
        "instrumento_pesquisa" in c["sql"] and "FOR UPDATE" in c["sql"]
        for c in consultas.captured_queries
    )

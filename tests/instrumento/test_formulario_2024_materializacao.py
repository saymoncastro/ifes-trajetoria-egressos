"""Materialização da baseline do Formulário Egresso Ifes 2024 (specs/003, US1, US8;
contracts/materializacao.md)."""

import ast
from pathlib import Path

import pytest
from django.apps import apps

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.formulario_2024 import (
    BaselineDivergente,
    MaterializacaoRecusada,
    PesquisaAmbigua,
    forma_da_versao,
    forma_esperada,
    materializar,
)
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta, Pesquisa, Secao, Versao

pytestmark = pytest.mark.django_db

NOME = "Pesquisa Institucional de Egressos"
DESIGNACAO = "Formulário Egresso Ifes 2024 — referência migrada"
RAIZ = Path(__file__).resolve().parents[2]


def contagens():
    return tuple(m.objects.count() for m in (Pesquisa, Versao, Secao, Pergunta, Opcao))


# --- US1: criação ---------------------------------------------------------------------


def test_cria_a_baseline_em_rascunho():
    resultado = materializar()

    assert resultado.criada is True
    assert Pesquisa.objects.filter(nome=NOME).count() == 1
    versao = Versao.objects.get(pk=resultado.versao.pk)
    assert versao.pesquisa.nome == NOME
    assert versao.designacao == DESIGNACAO
    assert versao.estado == "RASCUNHO"
    assert versao.publicada_em is None
    assert versao.origem_id is None
    assert Versao.objects.count() == 1


def test_baseline_criada_equivale_a_declaracao():
    assert forma_da_versao(materializar().versao) == forma_esperada()


def test_usa_a_pesquisa_homonima_existente():
    pesquisa = op.criar_pesquisa(NOME)

    resultado = materializar()

    assert resultado.criada is True
    assert resultado.versao.pesquisa_id == pesquisa.id
    assert Pesquisa.objects.filter(nome=NOME).count() == 1


def test_nao_toca_a_feature_001():
    assert (Pessoa.objects.count(), ConclusaoAcademica.objects.count()) == (0, 0)
    materializar()
    assert (Pessoa.objects.count(), ConclusaoAcademica.objects.count()) == (0, 0)


def test_atomicidade_falha_na_ultima_etapa_nao_deixa_nada(monkeypatch):
    def falha(*args, **kwargs):
        raise RuntimeError("falha provocada")

    # definir_regra é a última etapa da construção: tudo o mais já foi gravado.
    monkeypatch.setattr(op, "definir_regra", falha)

    with pytest.raises(RuntimeError, match="falha provocada"):
        materializar()
    assert contagens() == (0, 0, 0, 0, 0)


@pytest.mark.django_db(transaction=True)
def test_materializa_com_commit_real():
    # A unicidade de posições da 002 é adiada até o COMMIT (002, R4).
    resultado = materializar()
    assert Versao.objects.get(pk=resultado.versao.pk).estado == "RASCUNHO"


# --- US8: idempotência e divergência ---------------------------------------------------


def identidades():
    return tuple(
        frozenset(m.objects.values_list("id", flat=True))
        for m in (Pesquisa, Versao, Secao, Pergunta, Opcao)
    )


def test_reexecucao_equivalente_nao_altera_nada():
    primeira = materializar()
    antes = (identidades(), conteudo_da_versao(primeira.versao))

    segunda = materializar()

    assert segunda.criada is False
    assert segunda.versao.pk == primeira.versao.pk
    assert (identidades(), conteudo_da_versao(segunda.versao)) == antes


def _pergunta(versao, secao, posicao):
    return Pergunta.objects.get(secao__versao=versao, secao__posicao=secao, posicao=posicao)


def _opcao(versao, secao, posicao, opcao):
    return Opcao.objects.get(pergunta=_pergunta(versao, secao, posicao), posicao=opcao)


def _secao(versao, posicao):
    return Secao.objects.get(versao=versao, posicao=posicao)


ALTERACOES = {
    "texto de Opção de Q11": (
        lambda v: op.alterar_opcao(_opcao(v, 3, 2, 1), texto="Alegre (campus)"),
        "S3·2·1: texto difere",
    ),
    "Q54 removida": (
        lambda v: op.remover_pergunta(_pergunta(v, 13, 3)),
        "S13: 2 Perguntas, esperadas 3",
    ),
    "regra acrescentada em Q51": (
        lambda v: op.definir_regra(_pergunta(v, 12, 3), _opcao(v, 12, 3, 1), _secao(v, 13)),
        "S12·3·1: regra difere",
    ),
    "texto de abertura": (
        lambda v: op.alterar_versao(v, texto_abertura="Outro convite."),
        "Versão: texto de abertura difere",
    ),
    "obrigatoriedade de Q6": (
        lambda v: op.alterar_pergunta(_pergunta(v, 2, 5), obrigatoria=True),
        "S2·5: obrigatoriedade difere",
    ),
}


@pytest.mark.parametrize("alteracao", ALTERACOES)
def test_divergencia_falha_sem_escrever(alteracao):
    alterar, local = ALTERACOES[alteracao]
    versao = materializar().versao
    alterar(versao)
    antes = (identidades(), conteudo_da_versao(versao))

    with pytest.raises(BaselineDivergente) as erro:
        materializar()

    assert erro.value.divergencia == local
    assert (identidades(), conteudo_da_versao(versao)) == antes


# Destino fora da Versão só é possível por escrita fora das operações da 002; não pode se
# confundir com "sem encaminhamento" ou "sem regra" (code review, achado 1).


def test_encaminhamento_fora_da_versao_e_divergencia():
    versao = materializar().versao
    estranha = op.adicionar_secao(op.criar_versao(versao.pesquisa, "outra"), 1)
    Secao.objects.filter(pk=_secao(versao, 2).pk).update(encaminhamento=estranha)

    with pytest.raises(BaselineDivergente) as erro:
        materializar()
    assert erro.value.divergencia == "S2: encaminhamento difere"


def test_regra_fora_da_versao_e_divergencia():
    versao = materializar().versao
    estranha = op.adicionar_secao(op.criar_versao(versao.pesquisa, "outra"), 1)
    Opcao.objects.filter(pk=_opcao(versao, 12, 3, 1).pk).update(regra_destino=estranha)

    with pytest.raises(BaselineDivergente) as erro:
        materializar()
    assert erro.value.divergencia == "S12·3·1: regra difere"


def test_diagnostico_aponta_a_primeira_diferenca():
    # Conteúdo alterado em S2 e uma 14ª Seção ao fim: a primeira diferença é a de S2, não
    # a quantidade de Seções (code review, achado 2).
    versao = materializar().versao
    op.alterar_pergunta(_pergunta(versao, 2, 1), texto="Outro texto?")
    op.adicionar_secao(versao, 14)

    with pytest.raises(BaselineDivergente) as erro:
        materializar()
    assert erro.value.divergencia == "S2·1: texto difere"


def test_diagnostico_de_quantidade_quando_o_resto_e_igual():
    versao = materializar().versao
    op.adicionar_opcao(_pergunta(versao, 12, 3), 4, "Outra")

    with pytest.raises(BaselineDivergente) as erro:
        materializar()
    assert erro.value.divergencia == "S12·3: 4 Opções, esperadas 3"


def test_pesquisa_ambigua():
    op.criar_pesquisa(NOME)
    op.criar_pesquisa(NOME)

    with pytest.raises(PesquisaAmbigua):
        materializar()
    assert Versao.objects.count() == 0


def test_baseline_publicada_equivalente_e_no_op():
    versao = materializar().versao
    op.publicar(versao)  # só neste teste; a materialização nunca publica
    publicada = Versao.objects.get(pk=versao.pk)

    resultado = materializar()

    assert resultado.criada is False
    depois = Versao.objects.get(pk=versao.pk)
    assert (depois.estado, depois.publicada_em) == ("PUBLICADA", publicada.publicada_em)


def test_recusas_sao_materializacao_recusada():
    assert issubclass(BaselineDivergente, MaterializacaoRecusada)
    assert issubclass(PesquisaAmbigua, MaterializacaoRecusada)


# --- Limites: nada de modelo, migração, app ou dependência novos (FR-040, FR-041) ----


def test_formulario_2024_nao_e_app_django():
    assert "trajetoria.formulario_2024" not in {c.name for c in apps.get_app_configs()}


def test_modelos_e_migracoes_das_features_001_e_002_inalterados():
    assert {m.__name__ for m in apps.get_app_config("instrumento").get_models()} == {
        "Pesquisa", "Versao", "Secao", "Pergunta", "Opcao"
    }
    for app in ("instrumento", "academico"):
        arquivos = {p.name for p in (RAIZ / "trajetoria" / app / "migrations").glob("*.py")}
        assert arquivos == {"__init__.py", "0001_initial.py"}, app


def test_pacote_nao_importa_001_nem_publica():
    for arquivo in (RAIZ / "trajetoria" / "formulario_2024").glob("*.py"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                modulos = [no.module or ""]
            elif isinstance(no, ast.Import):
                modulos = [a.name for a in no.names]
            else:
                modulos = []
            for modulo in modulos:
                assert not modulo.startswith(
                    ("trajetoria.academico", "trajetoria.fonte_academica")
                ), arquivo.name
            assert not (isinstance(no, ast.Attribute) and no.attr == "publicar"), arquivo.name
            assert not (isinstance(no, ast.Name) and no.id == "publicar"), arquivo.name

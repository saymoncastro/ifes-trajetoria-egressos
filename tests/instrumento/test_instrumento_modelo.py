"""Restrições do modelo (data-model.md), por escrita direta no ORM.

A imutabilidade da Versão publicada não é protegida aqui: ela é garantida pelas operações
(research R9; ADR 0002 rejeitado nesta fase).
"""

import pytest
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.utils import timezone

from trajetoria.instrumento.models import Opcao, Pergunta, Pesquisa, Secao, Versao

pytestmark = pytest.mark.django_db


def _deve_violar(criar):
    with pytest.raises(IntegrityError), transaction.atomic():
        criar()


def _deve_violar_no_fim_da_transacao(acao):
    # Unicidade adiada: só é verificada ao confirmar a transação. Nos testes a transação
    # externa nunca é confirmada, então a verificação é antecipada explicitamente.
    with pytest.raises(IntegrityError), transaction.atomic():
        acao()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


@pytest.fixture
def pesquisa():
    return Pesquisa.objects.create(nome="P")


@pytest.fixture
def versao(pesquisa):
    return Versao.objects.create(pesquisa=pesquisa, designacao="2024")


@pytest.fixture
def secao(versao):
    return Secao.objects.create(versao=versao, posicao=1)


def _pergunta(secao, **campos):
    return Pergunta.objects.create(
        **{
            "secao": secao,
            "posicao": 1,
            "tipo": "ESCOLHA_UNICA",
            "texto": "Pergunta?",
            "obrigatoria": True,
            **campos,
        }
    )


# --- Pesquisa e Versão (US1) --------------------------------------------------------


def test_cadeia_vazia_proibida_em_pesquisa():
    _deve_violar(lambda: Pesquisa.objects.create(nome=""))


@pytest.mark.parametrize(
    "campo", ["designacao", "titulo", "texto_abertura", "texto_encerramento"]
)
def test_cadeia_vazia_proibida_em_versao(pesquisa, campo):
    _deve_violar(
        lambda: Versao.objects.create(**{"pesquisa": pesquisa, "designacao": "v", campo: ""})
    )


def test_designacao_unica_na_pesquisa(pesquisa, versao):
    _deve_violar(lambda: Versao.objects.create(pesquisa=pesquisa, designacao="2024"))


def test_estado_e_publicada_em_coerentes(pesquisa):
    _deve_violar(
        lambda: Versao.objects.create(pesquisa=pesquisa, designacao="a", estado="PUBLICADA")
    )
    _deve_violar(
        lambda: Versao.objects.create(
            pesquisa=pesquisa, designacao="b", publicada_em=timezone.now()
        )
    )


def test_estado_fora_dos_dois_valores(pesquisa):
    _deve_violar(
        lambda: Versao.objects.create(pesquisa=pesquisa, designacao="a", estado="ARQUIVADA")
    )


def test_pesquisa_com_versao_nao_pode_ser_excluida(pesquisa, versao):
    with pytest.raises(ProtectedError):
        pesquisa.delete()


def test_campos_de_pesquisa_e_versao():
    def nomes(modelo):
        return {campo.name for campo in modelo._meta.get_fields() if campo.concrete}

    assert nomes(Pesquisa) == {"id", "nome"}
    assert nomes(Versao) == {
        "id",
        "pesquisa",
        "designacao",
        "estado",
        "publicada_em",
        "origem",
        "titulo",
        "texto_abertura",
        "texto_encerramento",
    }


# --- Ordem (US2) --------------------------------------------------------------------


def test_posicao_zero_proibida(versao, secao):
    _deve_violar(lambda: Secao.objects.create(versao=versao, posicao=0))
    _deve_violar(lambda: _pergunta(secao, posicao=0))


def test_posicao_repetida_viola_no_fim_da_transacao(versao, secao):
    _deve_violar_no_fim_da_transacao(lambda: Secao.objects.create(versao=versao, posicao=1))
    _pergunta(secao)
    _deve_violar_no_fim_da_transacao(lambda: _pergunta(secao, texto="Outra?"))


def test_troca_de_posicoes_na_mesma_transacao_e_aceita(versao, secao):
    outra = Secao.objects.create(versao=versao, posicao=2)
    with transaction.atomic():
        Secao.objects.filter(pk=secao.pk).update(posicao=2)
        Secao.objects.filter(pk=outra.pk).update(posicao=1)
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
    assert list(Secao.objects.values_list("pk", flat=True)) == [outra.pk, secao.pk]


def test_secao_com_pergunta_nao_pode_ser_excluida(secao):
    _pergunta(secao)
    with pytest.raises(ProtectedError):
        secao.delete()


# --- Tipos e escala (US3) -----------------------------------------------------------


def test_tipo_fora_dos_quatro(secao):
    _deve_violar(lambda: _pergunta(secao, tipo="DATA"))


def test_escala_incoerente(secao):
    _deve_violar(lambda: _pergunta(secao, tipo="ESCALA", escala_fim=5))
    _deve_violar(lambda: _pergunta(secao, tipo="ESCALA", escala_inicio=1))
    _deve_violar(lambda: _pergunta(secao, tipo="ESCALA", escala_inicio=5, escala_fim=5))
    _deve_violar(lambda: _pergunta(secao, tipo="ESCALA", escala_inicio=5, escala_fim=1))


@pytest.mark.parametrize(
    "campos",
    [
        {"escala_inicio": 1},
        {"escala_fim": 5},
        {"escala_rotulo_inicio": "Discordo"},
        {"escala_rotulo_fim": "Concordo"},
    ],
)
def test_colunas_de_escala_so_em_escala(secao, campos):
    _deve_violar(lambda: _pergunta(secao, **campos))


def test_rotulo_de_escala_vazio(secao):
    _deve_violar(
        lambda: _pergunta(
            secao, tipo="ESCALA", escala_inicio=1, escala_fim=5, escala_rotulo_fim=""
        )
    )


# --- Opções (US4) -------------------------------------------------------------------


def _opcao(pergunta, **campos):
    return Opcao.objects.create(**{"pergunta": pergunta, "posicao": 1, "texto": "Sim", **campos})


def test_texto_de_opcao_unico_na_pergunta(secao):
    pergunta = _pergunta(secao)
    _opcao(pergunta)
    _deve_violar(lambda: _opcao(pergunta, posicao=2))


def test_um_complemento_textual_por_pergunta(secao):
    pergunta = _pergunta(secao)
    _opcao(pergunta, complemento_textual=True)
    _deve_violar(lambda: _opcao(pergunta, posicao=2, texto="Outro", complemento_textual=True))


def test_no_maximo_uma_regra_por_opcao(secao):
    pergunta = _pergunta(secao)
    _deve_violar(lambda: _opcao(pergunta, regra_destino=secao, regra_finaliza=True))


def test_texto_de_opcao_nao_vazio(secao):
    _deve_violar(lambda: _opcao(_pergunta(secao), texto=""))

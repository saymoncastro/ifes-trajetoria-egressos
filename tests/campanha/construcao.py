"""Auxiliares dos testes de Campanha (não são testes).

Todo teste temporal passa `agora` explícito, construído por `momento`: nenhum teste depende
do relógio real (research R6).
"""

from datetime import datetime
from itertools import count

import pytest
from django.utils import timezone

from trajetoria.academico.incorporacao import incorporar_pessoa
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.regras import CampanhaRejeitada
from trajetoria.fonte_academica import cenarios
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.models import Versao

_sequencia = count(1)


def momento(ano: int, mes: int, dia: int, hora: int = 12) -> datetime:
    """Data e hora na timezone configurada do projeto, sem fuso nominal."""
    return timezone.make_aware(datetime(ano, mes, dia, hora))


def _versao(designacao: str) -> Versao:
    """Instrumento mínimo pelas operações da 002: uma Seção, uma pergunta de texto curto."""
    pesquisa = op.criar_pesquisa(f"Pesquisa de teste {next(_sequencia)}")
    versao = op.criar_versao(pesquisa, designacao)
    secao = op.adicionar_secao(versao, 1)
    op.adicionar_pergunta(secao, 1, "TEXTO_CURTO", "Pergunta de teste", obrigatoria=True)
    return versao


def versao_publicada(designacao: str = "teste") -> Versao:
    versao = _versao(designacao)
    op.publicar(versao)
    versao.refresh_from_db()
    return versao


def versao_rascunho(designacao: str = "rascunho") -> Versao:
    return _versao(designacao)


def conclusao(
    *,
    ano=None,
    unidade=None,
    nivel=None,
    modalidade=None,
    forma_oferta=None,
    pessoa: Pessoa | None = None,
) -> ConclusaoAcademica:
    """Conclusão criada por ORM, com atributos ausentes escolhidos, fora dos cenários da 001
    (research R14)."""
    n = next(_sequencia)
    if pessoa is None:
        pessoa = Pessoa.objects.create(fonte="teste-campanha", id_externo=f"TC-P-{n}")
    return ConclusaoAcademica.objects.create(
        pessoa=pessoa,
        fonte="teste-campanha",
        id_externo=f"TC-C-{n}",
        unidade=unidade,
        nivel=nivel,
        modalidade=modalidade,
        forma_oferta=forma_oferta,
        ano_conclusao=ano,
    )


def incorporar_cenarios(fonte, ids=None) -> None:
    """Incorpora as Pessoas dos cenários da 001 (todas, ou só `ids`) pelo caminho real."""
    for pessoa in cenarios.PESSOAS:
        if ids is None or pessoa.id_externo in ids:
            incorporar_pessoa(fonte, pessoa.id_externo)


def conclusao_da_fonte(id_externo: str) -> ConclusaoAcademica:
    return ConclusaoAcademica.objects.get(fonte="simulada", id_externo=id_externo)


def rejeita(motivos, operacao, *args, **kwargs):
    """Executa a operação, exige rejeição com exatamente `motivos` e devolve as violações."""
    with pytest.raises(CampanhaRejeitada) as erro:
        operacao(*args, **kwargs)
    assert erro.value.motivos == tuple(motivos)
    return erro.value.violacoes


def linha(campanha: Campanha) -> dict:
    """A linha gravada, para comparar antes e depois."""
    return Campanha.objects.filter(pk=campanha.pk).values().get()

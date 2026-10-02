"""Medição de volume (spec SC-012, hipótese; research R15). Fora da suíte padrão:
`uv run pytest -m volume tests/exportacao`.

Preparação de volume por escrita direta **só neste teste**: uma Participação-molde é
preenchida e concluída pelas operações da 005/006; as demais copiam suas Respostas por
`bulk_create`. Só a exportação é medida.
"""

import time

import pytest

from tests.analitico import construcao as c
from tests.participacao.construcao import (
    baseline_publicada,
    escolhas_baseline,
    preencher,
    secoes_esperadas,
)
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao.formatos import exportar_csv, exportar_xlsx
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import concluir

pytestmark = [pytest.mark.volume, pytest.mark.django_db]

REGISTROS = 20_000
COM_PARTICIPACAO = REGISTROS // 5
LIMITE_EM_SEGUNDOS = 60


def _conclusoes(n: int) -> list[ConclusaoAcademica]:
    pessoas = Pessoa.objects.bulk_create(
        Pessoa(fonte="teste-volume", id_externo=f"TV-P-{i}", nome=f"Pessoa Ficticia {i}")
        for i in range(n)
    )
    return ConclusaoAcademica.objects.bulk_create(
        ConclusaoAcademica(
            pessoa=p,
            fonte="teste-volume",
            id_externo=f"TV-C-{i}",
            unidade="Serra",
            ano_conclusao=2022,
        )
        for i, p in enumerate(pessoas)
    )


def test_exportacao_de_20_mil_registros():
    base = baseline_publicada()
    campanha = c.campanha_aberta_no_passado(base.versao, unidades=["Serra"])
    conclusoes = _conclusoes(REGISTROS)

    molde = c.iniciada(campanha, conclusoes[0])
    escolhas = escolhas_baseline("Sim", "Graduação", "Sim", "Sim")
    preencher(
        molde,
        base,
        secoes_esperadas("Sim", "Graduação", "Sim", "Sim"),
        escolhas,
        agora=c.na_coleta(),
    )
    molde = concluir(molde, agora=c.na_coleta()).participacao

    # preparação de volume; só a exportação é medida
    copias = Participacao.objects.bulk_create(
        Participacao(
            campanha=campanha,
            conclusao=conclusao,
            iniciada_em=molde.iniciada_em,
            concluida_em=molde.concluida_em,
        )
        for conclusao in conclusoes[1:COM_PARTICIPACAO]
    )
    respostas = list(Resposta.objects.filter(participacao=molde).prefetch_related("opcoes"))
    novas = Resposta.objects.bulk_create(
        Resposta(
            participacao=copia,
            pergunta_id=r.pergunta_id,
            opcao_id=r.opcao_id,
            texto=r.texto,
            escala=r.escala,
            complemento=r.complemento,
        )
        for copia in copias
        for r in respostas
    )
    selecoes = {r.pergunta_id: [o.pk for o in r.opcoes.all()] for r in respostas}
    RespostaOpcao.objects.bulk_create(
        RespostaOpcao(resposta=nova, opcao_id=opcao)
        for nova in novas
        for opcao in selecoes[nova.pergunta_id]
    )
    snapshot = capturar_snapshot(campanha)

    for exportar in (exportar_csv, exportar_xlsx):
        inicio = time.perf_counter()
        conteudo = exportar(snapshot)
        duracao = time.perf_counter() - inicio
        print(f"{exportar.__name__}: {duracao:.1f} s, {len(conteudo) / 1e6:.1f} MB")
        assert duracao < LIMITE_EM_SEGUNDOS, exportar.__name__

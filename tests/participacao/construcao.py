"""Auxiliares dos testes de Participação e Resposta (não são testes).

Todo teste temporal passa `agora` explícito, construído por `momento`: nenhum teste depende
do relógio real (research R13). Instrumentos são montados e publicados pelas operações da
002; a baseline da 003 nunca é publicada. Somente dados fictícios (DP-504).

Imports de `trajetoria.participacao.models` ficam dentro das funções, para que este módulo
importe antes de os modelos existirem (tasks, F1).
"""

from dataclasses import dataclass
from datetime import date, datetime
from itertools import count

import pytest
from django.utils import timezone

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.models import Campanha
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import Opcao, Pergunta, Versao
from trajetoria.participacao.regras import ParticipacaoRejeitada

_sequencia = count(1)


def momento(ano: int, mes: int, dia: int, hora: int = 12) -> datetime:
    """Data e hora na timezone configurada do projeto, sem fuso nominal."""
    return timezone.make_aware(datetime(ano, mes, dia, hora))


INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)
NO_PERIODO = momento(2027, 5, 1)
ULTIMO_DIA = momento(2027, 6, 30, 23)
DEPOIS_DO_FIM = momento(2027, 7, 1)


# --- Instrumento de teste ------------------------------------------------------------------


@dataclass
class Instrumento:
    versao: Versao
    unica: Pergunta
    unica_outro: Pergunta
    multipla: Pergunta
    texto: Pergunta
    escala: Pergunta
    campus: Pergunta
    posterior: Pergunta

    def opcao(self, pergunta: Pergunta, texto: str) -> Opcao:
        return Opcao.objects.get(pergunta=pergunta, texto=texto)


def _escolha(secao, posicao, tipo, texto, opcoes, *, obrigatoria=True, outro=False):
    pergunta = op.adicionar_pergunta(secao, posicao, tipo, texto, obrigatoria=obrigatoria)
    for i, texto_opcao in enumerate(opcoes, start=1):
        op.adicionar_opcao(pergunta, i, texto_opcao)
    if outro:
        op.adicionar_opcao(pergunta, len(opcoes) + 1, "Outro:", complemento_textual=True)
    return pergunta


def _carregar(versao: Versao) -> Instrumento:
    """As Perguntas da Versão, pela posição (Seção 1: 1–6; Seção 2: 1)."""

    def pergunta(secao: int, posicao: int) -> Pergunta:
        return Pergunta.objects.get(secao__versao=versao, secao__posicao=secao, posicao=posicao)

    return Instrumento(
        versao=versao,
        unica=pergunta(1, 1),
        unica_outro=pergunta(1, 2),
        multipla=pergunta(1, 3),
        texto=pergunta(1, 4),
        escala=pergunta(1, 5),
        campus=pergunta(1, 6),
        posterior=pergunta(2, 1),
    )


def instrumento(designacao: str = "2027") -> Instrumento:
    """Versão publicada com uma pergunta de cada tipo, "Outro:" com complemento, uma regra
    de finalização e uma Seção posterior."""
    pesquisa = op.criar_pesquisa(f"Pesquisa de teste {next(_sequencia)}")
    versao = op.criar_versao(pesquisa, designacao)
    s1 = op.adicionar_secao(versao, 1)
    s2 = op.adicionar_secao(versao, 2)
    unica = _escolha(s1, 1, "ESCOLHA_UNICA", "Atualmente você trabalha?", ["Sim", "Não"])
    op.definir_regra(unica, Opcao.objects.get(pergunta=unica, texto="Não"), op.FINALIZAR)
    _escolha(s1, 2, "ESCOLHA_UNICA", "Motivo", ["A", "B"], outro=True)
    _escolha(
        s1, 3, "ESCOLHA_MULTIPLA", "Atividades", ["A", "B", "C"], obrigatoria=False, outro=True
    )
    op.adicionar_pergunta(s1, 4, "TEXTO_CURTO", "Quantos anos você tem?", obrigatoria=True)
    op.adicionar_pergunta(
        s1,
        5,
        "ESCALA",
        "Grau de concordância",
        obrigatoria=True,
        escala=Escala(inicio=1, fim=5, rotulo_fim="Concordo totalmente"),
    )
    _escolha(
        s1,
        6,
        "ESCOLHA_UNICA",
        "Em qual campus você concluiu seu curso?",
        ["Campus Serra", "Campus Vitória"],
    )
    op.adicionar_pergunta(s2, 1, "TEXTO_CURTO", "Comentário", obrigatoria=False)
    op.publicar(versao)
    versao.refresh_from_db()
    return _carregar(versao)


def instrumento_derivado(origem: Instrumento, designacao: str = "2028") -> Instrumento:
    """Nova Versão da mesma Pesquisa, criada da origem: textos idênticos, elementos novos."""
    versao = op.criar_versao_a_partir_de(origem.versao, designacao)
    op.publicar(versao)
    versao.refresh_from_db()
    return _carregar(versao)


# --- Conclusões e Campanhas ----------------------------------------------------------------


def conclusao(*, ano=2022, unidade="Serra", pessoa: Pessoa | None = None) -> ConclusaoAcademica:
    """Conclusão fictícia por ORM, fora dos cenários da 001."""
    n = next(_sequencia)
    if pessoa is None:
        pessoa = Pessoa.objects.create(fonte="teste-participacao", id_externo=f"TP-P-{n}")
    return ConclusaoAcademica.objects.create(
        pessoa=pessoa,
        fonte="teste-participacao",
        id_externo=f"TP-C-{n}",
        unidade=unidade,
        ano_conclusao=ano,
    )


def campanha_em_preparacao(versao: Versao, *, inicio=INICIO, fim=FIM, **criterios) -> Campanha:
    campanha = op_campanha.criar_campanha(f"Campanha {next(_sequencia)}", versao)
    op_campanha.definir_periodo(campanha, inicio, fim)
    if criterios:
        op_campanha.definir_criterios(campanha, **criterios)
    return campanha


def campanha_aberta(
    versao: Versao, *, inicio=INICIO, fim=FIM, abrir_em=None, **criterios
) -> Campanha:
    """Campanha aberta pelas operações da 004; por padrão, no primeiro dia do período."""
    campanha = campanha_em_preparacao(versao, inicio=inicio, fim=fim, **criterios)
    if abrir_em is None:
        abrir_em = momento(inicio.year, inicio.month, inicio.day)
    op_campanha.abrir(campanha, agora=abrir_em)
    return campanha


# --- Verificação ---------------------------------------------------------------------------


def rejeita(motivos, operacao, *args, **kwargs):
    """Executa a operação, exige rejeição com exatamente `motivos` e devolve as violações."""
    with pytest.raises(ParticipacaoRejeitada) as erro:
        operacao(*args, **kwargs)
    assert erro.value.motivos == tuple(motivos)
    return erro.value.violacoes


def retrato(participacao) -> dict:
    """Linhas gravadas da Participação, das suas Respostas e das suas seleções, para comparar
    antes e depois."""
    from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao

    respostas = Resposta.objects.filter(participacao_id=participacao.pk)
    return {
        "participacao": list(Participacao.objects.filter(pk=participacao.pk).values()),
        "respostas": list(respostas.order_by("id").values()),
        "selecoes": list(
            RespostaOpcao.objects.filter(resposta__in=respostas).order_by("id").values()
        ),
    }

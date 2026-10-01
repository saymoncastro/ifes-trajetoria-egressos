"""Gravação de uma Seção pelas operações da 005 (008 contracts/formulario-secao.md; R7).

Para cada Pergunta da Seção, no máximo **uma** operação da 005 — registrar/substituir
(`responder_*`) ou remover — e nenhuma quando nada mudou (FR-040). Nenhuma Resposta é
gravada por outro meio: a interface não toca os modelos.

A submissão é **atômica** (FR-045): todas as operações rodam numa transação; cada rejeição
da 005 é capturada por Pergunta, fora do bloco atômico da própria operação, para reunir
todos os erros de uma vez (FR-049); havendo qualquer erro, a transação inteira é desfeita.
O bloqueio da Participação, tomado pela primeira operação, vale até o fim da transação: a
submissão é serializada com uma conclusão concorrente (006 FR-043). As operações leem o
próprio relógio — a interface não passa `agora` nem avalia período (FR-065).
"""

from dataclasses import dataclass, field

from django.db import transaction

from trajetoria.instrumento.conteudo import ConteudoSecao
from trajetoria.instrumento.models import Pergunta, TipoPergunta
from trajetoria.interface import mensagens
from trajetoria.interface.formularios import Valor, valor_gravado
from trajetoria.participacao.operacoes import (
    remover_resposta,
    responder_escala,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada

# Rejeições que não são de uma Pergunta: a submissão inteira vira uma tela de estado.
GLOBAIS = (
    Motivo.COLETA_NAO_ADMITIDA,
    Motivo.PARTICIPACAO_CONCLUIDA,
    Motivo.PARTICIPACAO_INEXISTENTE,
)


@dataclass
class ResultadoDaGravacao:
    erros_por_pergunta: dict[int, list[str]] = field(default_factory=dict)
    motivo_global: Motivo | None = None
    operacoes: int = 0  # aplicadas e mantidas; 0 sempre que houve erro

    @property
    def aceito(self) -> bool:
        return not self.erros_por_pergunta and self.motivo_global is None


class _Desfazer(Exception):
    pass


class _OpcaoDesconhecida(Exception):
    """Posição de Opção que não existe na Pergunta (o formulário já a recusa; só chega aqui
    com valores forjados). Vira erro da Pergunta, sem chamar a 005."""


def salvar_secao(participacao, secao: ConteudoSecao, limpos: dict[int, Valor], respostas):
    """Aplica `limpos` (posição da Pergunta → `Valor`) às Respostas da Seção, comparando com
    `respostas` (as atuais da 005, indexadas pelo `id` da Pergunta)."""
    perguntas = {
        p.posicao: p
        for p in Pergunta.objects.filter(secao_id=secao.id).prefetch_related("opcoes")
    }
    resultado = ResultadoDaGravacao()
    try:
        with transaction.atomic():
            for conteudo in secao.perguntas:
                valor = limpos.get(conteudo.posicao)
                if valor is None:
                    continue
                try:
                    operacao = _operacao(
                        participacao, perguntas[conteudo.posicao], conteudo, valor, respostas
                    )
                except _OpcaoDesconhecida:
                    resultado.erros_por_pergunta[conteudo.posicao] = [mensagens.ESCOLHA_INVALIDA]
                    continue
                if operacao is None:
                    continue
                try:
                    operacao()
                except ParticipacaoRejeitada as erro:
                    globais = [m for m in erro.motivos if m in GLOBAIS]
                    if globais:
                        resultado.motivo_global = globais[0]
                        break
                    resultado.erros_por_pergunta[conteudo.posicao] = _mensagens(erro)
                    continue
                resultado.operacoes += 1
            if not resultado.aceito:
                raise _Desfazer
    except _Desfazer:
        resultado.operacoes = 0
    return resultado


def _operacao(participacao, pergunta: Pergunta, conteudo, valor: Valor, respostas):
    """A única operação da 005 para esta Pergunta, ou `None` se nada muda."""
    gravada = respostas.get(pergunta.id)
    if valor.ausente:
        if gravada is None:
            return None
        return lambda: remover_resposta(participacao, pergunta)
    if gravada is not None and valor_gravado(conteudo, gravada) == valor:
        return None
    opcoes = {o.posicao: o for o in pergunta.opcoes.all()}

    def opcao(posicao):
        if posicao not in opcoes:
            raise _OpcaoDesconhecida
        return opcoes[posicao]

    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        escolhida = opcao(valor.opcao)
        return lambda: responder_escolha_unica(
            participacao, pergunta, escolhida, complemento=valor.complemento
        )
    if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
        escolhidas = [opcao(p) for p in sorted(valor.opcoes)]
        return lambda: responder_escolha_multipla(
            participacao, pergunta, escolhidas, complemento=valor.complemento
        )
    if pergunta.tipo == TipoPergunta.TEXTO_CURTO:
        return lambda: responder_texto(participacao, pergunta, valor.texto)
    return lambda: responder_escala(participacao, pergunta, valor.escala)


def _mensagens(erro: ParticipacaoRejeitada) -> list[str]:
    textos = []
    for motivo in erro.motivos:
        texto = mensagens.POR_MOTIVO.get(motivo, mensagens.NAO_SALVA)
        if texto not in textos:
            textos.append(texto)
    return textos

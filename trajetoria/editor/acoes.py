"""Auxiliares de ação do editor (research R6, R7; contracts/diagnostico.md §3).

Três funções pequenas, cada uma com consumidor concreto nas views. Toda escrita continua
sendo das operações da 002: aqui só se calcula posição e ordem, e se compõe a troca de
desvio numa única transação.
"""

from django.db import transaction
from django.db.models import Max

from trajetoria.instrumento import operacoes as op


def proxima_posicao(conjunto) -> int:
    """A posição logo após a última do conjunto (Seções, Perguntas ou Opções). Só lê."""
    return (conjunto.aggregate(maior=Max("posicao"))["maior"] or 0) + 1


def mover(em_ordem: list, elemento, direcao: str) -> list | None:
    """A ordem com `elemento` trocado com o vizinho; `None` na ponta."""
    i = em_ordem.index(elemento)
    j = i - 1 if direcao == "cima" else i + 1
    if not 0 <= j < len(em_ordem):
        return None
    nova = list(em_ordem)
    nova[i], nova[j] = nova[j], nova[i]
    return nova


def definir_desvio(pergunta, opcao, destino) -> None:
    """Deixa a Opção com exatamente o desvio `destino` (Seção, `op.FINALIZAR` ou `None`).

    A 002 recusa definir regra sobre Opção que já tem uma (FR-052), então a troca é
    `remover_regra` + `definir_regra` numa única transação: se a segunda falhar, a primeira
    é desfeita e a Opção mantém o desvio anterior (009 FR-052)."""
    opcao.refresh_from_db()
    if destino is None:
        atual_igual = not opcao.tem_regra
    elif destino is op.FINALIZAR:
        atual_igual = opcao.regra_finaliza
    else:
        atual_igual = opcao.regra_destino_id == destino.pk
    if atual_igual:
        return
    with transaction.atomic():
        if opcao.tem_regra:
            op.remover_regra(pergunta, opcao)
        if destino is not None:
            op.definir_regra(pergunta, opcao, destino)

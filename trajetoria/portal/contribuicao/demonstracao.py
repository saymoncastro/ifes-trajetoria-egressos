"""Manifestações fictícias da demonstração (026 plan R13).

Carregadas pelo sinal `cenario_preparado`, dentro da transação do preparo, só pelas operações
(único caminho de escrita), como o catálogo da 025. Idempotente: identificadores `uuid5`
fixos; o que já existe não é tocado. Os e-mails usam o domínio reservado `example.invalid`.

Duas manifestações, para a lista da unidade ter conteúdo: a do Diego (Vila Velha), que só a
CPAEG (operador A) vê, e a do Bruno (Vitória), que a CSAEG de Vitória (operador B) também vê.
"""

import uuid
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.demonstracao.sinais import CargaRecusada
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.mensagens import VERSAO_DA_CIENCIA
from trajetoria.portal.contribuicao.regras import ManifestacaoRejeitada
from trajetoria.portal.models import Forma, Manifestacao

_NAMESPACE = uuid.UUID("0a1b2c3d-0260-4026-8026-000000000026")

# (chave, Pessoa, Conclusão, forma, mensagem, dias a partir de D)
MANIFESTACOES = (
    ("M1", "SIM-P-0004", "SIM-C-0007", Forma.EXPERIENCIA,
     "Trabalho com controle de qualidade em uma indústria química e posso conversar com as "
     "turmas da licenciatura sobre a carreira.", -2),
    ("M2", "SIM-P-0002", "SIM-C-0002", Forma.MENTORIA, "", -5),
)


def identificador(chave: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, chave)


def carregar_manifestacoes(sender, data: date, **kwargs) -> None:
    """Receptor de `cenario_preparado`. Uma recusa vira `CargaRecusada`: o preparo desfaz tudo
    e orienta, em vez de terminar com um traceback."""
    try:
        _carregar(data)
    except ManifestacaoRejeitada as erro:
        raise CargaRecusada(f"manifestações fictícias: {erro}") from erro


def _carregar(data: date) -> None:
    for chave, pessoa_externa, conclusao_externa, forma, mensagem, dias in MANIFESTACOES:
        pk = identificador(chave)
        if Manifestacao.objects.filter(pk=pk).exists():
            continue
        pessoa = Pessoa.objects.filter(
            fonte=FonteSimulada.codigo, id_externo=pessoa_externa
        ).first()
        conclusao = ConclusaoAcademica.objects.filter(
            fonte=FonteSimulada.codigo, id_externo=conclusao_externa
        ).first()
        if pessoa is None or conclusao is None:
            continue  # Pessoa fora do preparo: nada a carregar para ela
        operacoes.registrar(
            pessoa, conclusao_id=conclusao.pk, forma=forma, mensagem=mensagem,
            email=f"{pessoa_externa.lower()}.contribuicao@example.invalid",
            versao_da_ciencia=VERSAO_DA_CIENCIA,
            agora=timezone.make_aware(datetime.combine(data + timedelta(days=dias), time(10, 0))),
            id=pk,
        )

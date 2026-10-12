"""Encontros fictícios da demonstração (031, incremento 1; research R15).

Carregados pelo sinal `cenario_preparado`, dentro da transação do preparo, só pelas operações
(único caminho de escrita), como o catálogo da 025 e as manifestações da 026. Idempotente:
identificadores `uuid5` fixos; o que já existe não é tocado. Os textos são os do protótipo.

- **E1**, de Maria, publicado pela CPAEG: público por cursos de duas unidades; Diego (Licenciatura
  em Química) o vê na lista e já confirmou; Ana também, pelo endereço.
- **E2**, de Bruno, publicado pela CPAEG, aberto a todos.
- **E3**, de Bruno, em análise, só para a unidade Vitória: a CSAEG de Vitória (operador B)
  o vê; a demonstração não tem CSAEG de outra unidade (analyze F3).
- **E4**, de Maria, recusado pela CPAEG, com motivo.
- **E5**, de Maria, publicado e já encerrado, com a confirmação de Diego.
"""

import uuid
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.demonstracao.sinais import CargaRecusada
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.portal.encontros import operacoes
from trajetoria.portal.encontros.mensagens import VERSAO_DA_CIENCIA, VERSAO_DO_TERMO
from trajetoria.portal.encontros.operacoes import Proposta
from trajetoria.portal.encontros.regras import EncontroRejeitado
from trajetoria.portal.models import Confirmacao, Encontro, MotivoDeModeracao

_NAMESPACE = uuid.UUID("0a1b2c3d-0310-4031-8031-000000000031")
OPERADOR_A = "demonstracao:operador-a"  # CPAEG
INSTITUCIONAL = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())

LINK = "https://meet.exemplo.org/{chave}"  # domínio fictício; nada é acessado

# (chave, Pessoa, Conclusão de origem, nome, título, descrição, dias até o encontro, hora de
#  início, duração em minutos, público, dias do envio, decisão)
ENCONTROS = (
    ("E1", "SIM-P-0003", "SIM-C-0005", "Maria E.",
     "Tecnologia na sala de aula: o que funciona de verdade",
     "Conversa entre egressos que dão aula ou trabalham com formação. Cada pessoa traz uma "
     "experiência com tecnologia em sala, que deu certo ou não. Sem apresentação de slides.",
     18, 19, 90, {"publico_cursos": ["Especialização em Informática na Educação",
                                     "Licenciatura em Química"]}, -3, "publicar"),
    ("E2", "SIM-P-0002", "SIM-C-0003", "Bruno E.",
     "Voltar a estudar depois de anos longe da sala de aula",
     "Para quem pensa em fazer outra graduação, uma especialização ou um mestrado depois de "
     "um tempo no trabalho. Conversa aberta, sem palestra.",
     25, 18, 60, {}, -4, "publicar"),
    ("E3", "SIM-P-0002", "SIM-C-0002", "Bruno E.",
     "Engenharia e edificações: dez anos depois do técnico",
     "Egressos do técnico e da engenharia contam como foi a entrada no mercado e o que "
     "mudou na profissão.",
     30, 19, 60, {"publico_unidades": ["Vitória"]}, -1, None),
    ("E4", "SIM-P-0003", "SIM-C-0004", "Maria E.",
     "Mentoria para concursos públicos",
     "Encontro para apresentar o meu curso preparatório para concursos, com desconto para "
     "egressos.",
     10, 10, 60, {}, -5, "recusar"),
)
# Encerrado: enviado, publicado e confirmado no passado.
ENCERRADO = ("E5", "SIM-P-0003", "SIM-C-0004", "Maria E.",
             "Roda de conversa: primeiros anos de docência",
             "Egressos que começaram a dar aula contam o que aprenderam no primeiro ano.",
             -9, 19, 60, {"publico_cursos": ["Licenciatura em Química",
                                             "Tecnologia em Análise e Desenvolvimento de "
                                             "Sistemas"]}, -20)
CONFIRMACOES = (("C1", "E1", "SIM-P-0004"), ("C2", "E1", "SIM-P-0001"),
                ("C3", "E5", "SIM-P-0004"))


def identificador(chave: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, chave)


def carregar_encontros(sender, data: date, **kwargs) -> None:
    """Receptor de `cenario_preparado`. Uma recusa vira `CargaRecusada`."""
    try:
        _carregar(data)
    except EncontroRejeitado as erro:
        raise CargaRecusada(f"encontros fictícios: {erro}") from erro


def _pessoa(id_externo):
    return Pessoa.objects.filter(fonte=FonteSimulada.codigo, id_externo=id_externo).first()


def _conclusao(id_externo):
    return ConclusaoAcademica.objects.filter(
        fonte=FonteSimulada.codigo, id_externo=id_externo
    ).first()


def _momento(dia: date, hora: int, minuto: int = 0) -> datetime:
    return timezone.make_aware(datetime.combine(dia, time(hora, minuto)))


def _propor(chave, pessoa_externa, conclusao_externa, nome, titulo, descricao, dias, hora,
            minutos, publico, dias_envio, data: date):
    pessoa, conclusao = _pessoa(pessoa_externa), _conclusao(conclusao_externa)
    if pessoa is None or conclusao is None:
        return None
    inicio = _momento(data + timedelta(days=dias), hora)
    proposta = Proposta(
        titulo=titulo, descricao=descricao, nome_apresentacao=nome,
        inicio=inicio, termino=inicio + timedelta(minutes=minutos),
        publico_unidades=publico.get("publico_unidades"),
        publico_niveis=publico.get("publico_niveis"),
        publico_cursos=publico.get("publico_cursos"),
        link=LINK.format(chave=chave.lower()), conclusao_origem_id=conclusao.pk,
    )
    return operacoes.propor(pessoa, proposta, versao_do_termo=VERSAO_DO_TERMO,
                            agora=_momento(data + timedelta(days=dias_envio), 10),
                            id=identificador(chave))


def _carregar(data: date) -> None:
    for chave, *campos, dias_envio, decisao in ENCONTROS:
        if Encontro.objects.filter(pk=identificador(chave)).exists():
            continue
        encontro = _propor(chave, *campos, dias_envio, data)
        if encontro is None:
            continue
        decidido_em = _momento(data + timedelta(days=dias_envio + 1), 9)
        if decisao == "publicar":
            operacoes.publicar(encontro.pk, operador=OPERADOR_A, escopo=INSTITUCIONAL,
                               agora=decidido_em)
        elif decisao == "recusar":
            operacoes.recusar(
                encontro.pk, operador=OPERADOR_A, escopo=INSTITUCIONAL,
                motivo=MotivoDeModeracao.COMERCIAL,
                complemento="A descrição oferece um curso pago. Encontros entre egressos não "
                            "divulgam venda de produtos ou serviços.",
                agora=decidido_em,
            )
    chave, *campos, dias_envio = ENCERRADO
    if not Encontro.objects.filter(pk=identificador(chave)).exists():
        encontro = _propor(chave, *campos, dias_envio, data)
        if encontro is not None:
            operacoes.publicar(encontro.pk, operador=OPERADOR_A, escopo=INSTITUCIONAL,
                               agora=_momento(data + timedelta(days=dias_envio + 1), 9))
    for chave, encontro_chave, pessoa_externa in CONFIRMACOES:
        encontro = Encontro.objects.filter(pk=identificador(encontro_chave)).first()
        pessoa = _pessoa(pessoa_externa)
        if (encontro is None or pessoa is None
                or Confirmacao.objects.filter(pk=identificador(chave)).exists()):
            continue
        quando = encontro.publicado_em + timedelta(hours=2)
        operacoes.confirmar(pessoa, encontro.pk, versao_da_ciencia=VERSAO_DA_CIENCIA,
                            agora=quando, id=identificador(chave))

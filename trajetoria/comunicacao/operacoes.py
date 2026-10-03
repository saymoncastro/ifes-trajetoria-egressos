"""Simulação síncrona: cada chamada é independente; sem transação, retry ou persistência."""

from dataclasses import dataclass
from smtplib import SMTPException
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.comunicacao.acesso import (
    RecusaComunicacao,
    autorizar_operador,
    campanha_autorizada,
)
from trajetoria.comunicacao.consultas import publico_atual
from trajetoria.comunicacao.convite import renderizar_convite
from trajetoria.comunicacao.seguranca import transporte_local, validar_mensagem


@dataclass(frozen=True)
class SituacaoIndividual:
    pessoa_id: UUID
    situacao: str


@dataclass(frozen=True)
class Resultado:
    campanha: object
    momento: object
    escopo: object
    totais: dict
    individuais: tuple[SituacaoIndividual, ...]
    interrompida: bool = False


def simular_comunicacao(campanha_id, operador_id):
    contexto = autorizar_operador(operador_id)
    campanha = campanha_autorizada(campanha_id, contexto)
    agora = timezone.now()
    if estado(campanha, agora=agora) == EstadoCampanha.ENCERRADA:
        raise RecusaComunicacao("campanha_encerrada", 409)
    try:
        # Todo contato/render é validado antes mesmo de construir uma conexão:
        # `Convite.mensagem` aplica `validar_mensagem` a cada mensagem construída.
        publico = publico_atual(campanha, contexto.escopo)
        transporte = transporte_local()
        mensagens = {
            i.pessoa.pk: renderizar_convite(
                i.pessoa.nome,
                campanha.nome,
                settings.TRAJETORIA_URL_ENTRADA_DEMONSTRACAO,
            ).mensagem(i.contato)
            for i in publico.itens
            if i.contato is not None
        }
    except RecusaComunicacao:
        raise
    except Exception:
        raise RecusaComunicacao("falha_preparacao", 422) from None

    individuais = []
    interrompida = False
    for item in publico.itens:
        if item.contato is None:
            situacao = "sem_contato"
        elif interrompida:
            situacao = "nao_tentada"
        else:
            msg = mensagens[item.pessoa.pk]
            conexao = None
            # Só é tentativa de transporte (submetida/falha) a partir do send; um erro antes
            # dele interrompe a execução sem que a mensagem tenha saído.
            situacao = "nao_tentada"
            try:
                # Segunda barreira no destinatário final, não delegada ao host/Mailpit.
                validar_mensagem(msg)
                conexao = transporte.conexao()
                msg.connection = conexao
                situacao = "falha"
                if msg.send(fail_silently=False) == 1:
                    situacao = "submetida"
            except (SMTPException, OSError):
                pass  # falta de confirmação; nunca incluir o texto da exceção no resultado/log
            except Exception:
                interrompida = True
            finally:
                if conexao is not None:
                    try:
                        conexao.close()
                    except (SMTPException, OSError):
                        pass  # o retorno confirmado do envio não é desfeito por erro no fechamento
                    except Exception:
                        interrompida = True
        individuais.append(SituacaoIndividual(item.pessoa.pk, situacao))

    aceitas = sum(i.situacao == "submetida" for i in individuais)
    falhas = sum(i.situacao == "falha" for i in individuais)
    totais = {
        **publico.totais,
        "submetidas": aceitas + falhas,
        "aceitas": aceitas,
        "falhas": falhas,
        "nao_tentadas": sum(i.situacao == "nao_tentada" for i in individuais),
    }
    return Resultado(campanha, agora, contexto.escopo, totais, tuple(individuais), interrompida)

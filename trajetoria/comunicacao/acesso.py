"""Capacidade local explícita; identificação e escopo da 010/011, sem autenticação nova."""

from dataclasses import dataclass
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect

from trajetoria.acompanhamento.acesso import Atuacao, recusa
from trajetoria.acompanhamento.consultas import campanhas_visiveis
from trajetoria.campanha.models import Campanha
from trajetoria.demonstracao.operador import (
    operador_em_uso,
    operador_ficticio,
    vinculos_do_operador_em_uso,
)
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.regras import (
    escopo_de_acompanhamento,
    pode_consultar_rascunho,
    pode_simular_comunicacao,
)


class RecusaComunicacao(Exception):
    """Somente categoria fixa e status, nunca dados de uma exceção externa."""

    def __init__(self, categoria="sem_autorizacao", status=403):
        self.categoria = categoria
        self.status = status
        super().__init__(categoria)


@dataclass(frozen=True)
class Contexto:
    operador: str
    escopo: object
    atuacao: Atuacao


def _contexto(operador, vinculos):
    if not pode_simular_comunicacao(vinculos):
        raise RecusaComunicacao()
    return Contexto(
        operador,
        escopo_de_acompanhamento(vinculos),
        Atuacao(tuple(v.rotulo_de_atuacao for v in vinculos), pode_consultar_rascunho(vinculos)),
    )


def autorizar_operador(operador):
    if not settings.TRAJETORIA_DEMONSTRACAO:
        raise RecusaComunicacao("modo_desligado", 404)
    if operador_ficticio(operador) is None:
        raise RecusaComunicacao()
    return _contexto(operador, vinculos_ativos(operador))


def campanha_autorizada(campanha_id, contexto):
    campanha = campanhas_visiveis(contexto.escopo).filter(pk=campanha_id).first()
    if campanha is None:
        if not Campanha.objects.filter(pk=campanha_id).exists():
            raise RecusaComunicacao("inexistente", 404)
        raise RecusaComunicacao("fora_do_escopo", 403)
    return campanha


def comunicacao(view):
    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise RecusaComunicacao("modo_desligado", 404)
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect("/demonstracao/operador/?destino=acompanhamento")
        try:
            contexto = _contexto(operador_em_uso(request), vinculos)
        except RecusaComunicacao:
            return recusa(request, "Sem vínculo institucional ativo para comunicação simulada.")
        request.comunicacao = contexto
        request.atuacao = contexto.atuacao
        return view(request, *args, **kwargs)

    # Compatibilidade com o inventário de rotas institucionais da 011; a capacidade é própria.
    envolvida.acompanhamento = True
    return envolvida

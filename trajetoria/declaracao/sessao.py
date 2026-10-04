"""Sujeito declarante na sessão (019 FR-040 a FR-042; research R7).

Guarda só os UUIDs das declarações do par e os instantes; nunca HMAC, CPF, data, Pessoa,
formação ou Campanha. É exclusivo com a sessão de Pessoa da 018 (`cycle_key` + `clear` em
ambos) e segue as mesmas expirações. A 018 não conhece este módulo.
"""

from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from trajetoria.acesso.sessao import post_de_entrada
from trajetoria.declaracao.models import FormacaoDeclarada

_FORMACOES = "declaracao.formacoes"
_CONFIRMADA_EM = "declaracao.confirmada_em"
_ULTIMO_USO = "declaracao.ultimo_uso"
# Cache por requisição: as leituras de uma mesma requisição (contexto, posse, tela) revalidam
# a sessão uma vez. A 018 zera este atributo ao estabelecer ou encerrar a sessão de Pessoa.
_CACHE = "_declaracoes_de_acesso"


def estabelecer_declarante(request, uuids, agora):
    request.session.cycle_key()
    request.session.clear()
    request.session.update(
        {
            _FORMACOES: [str(id) for id in uuids],
            _CONFIRMADA_EM: agora.isoformat(),
            _ULTIMO_USO: agora.isoformat(),
        }
    )
    request._pessoa_de_acesso = None
    setattr(request, _CACHE, tuple(uuids))


def declaracoes_em_uso(request):
    """Os UUIDs das declarações em uso, ou `None`. Revalida prazo e existência uma vez por
    requisição; sessão inválida é descartada, salvo no POST de entrada da 018."""
    if hasattr(request, _CACHE):
        return getattr(request, _CACHE)
    uuids = _revalidar(request)
    setattr(request, _CACHE, uuids)
    return uuids


def _revalidar(request):
    sessao = getattr(request, "session", None)
    if sessao is None or _FORMACOES not in sessao:
        return None
    try:
        inicio = datetime.fromisoformat(sessao[_CONFIRMADA_EM])
        ultimo = datetime.fromisoformat(sessao[_ULTIMO_USO])
        agora = timezone.now()
        uuids = tuple(UUID(id) for id in sessao[_FORMACOES])
        if (
            not timezone.is_aware(inicio)
            or not timezone.is_aware(ultimo)
            or not inicio <= ultimo <= agora
            or agora - ultimo > settings.TRAJETORIA_SESSAO_INATIVIDADE
            or agora - inicio > settings.TRAJETORIA_SESSAO_DURACAO_MAXIMA
        ):
            raise ValueError
        existentes = set(
            FormacaoDeclarada.objects.filter(pk__in=uuids).values_list("pk", flat=True)
        )
        if existentes != set(uuids):
            raise ValueError
        if agora - ultimo >= timedelta(minutes=1) and not post_de_entrada(request):
            sessao[_ULTIMO_USO] = agora.isoformat()
        return uuids
    except (ValueError, TypeError, KeyError, ValidationError):
        if not post_de_entrada(request):
            sessao.flush()
        return None


def acrescentar_declaracao(request, uuid):
    uuids = declaracoes_em_uso(request)
    if uuids is None:
        estabelecer_declarante(request, [uuid], timezone.now())
    elif uuid not in uuids:
        novos = (*uuids, uuid)
        request.session[_FORMACOES] = [str(id) for id in novos]
        setattr(request, _CACHE, novos)

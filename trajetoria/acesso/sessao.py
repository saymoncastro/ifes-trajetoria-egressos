"""Sessão do egresso: só UUID e instantes; separada do operador fictício."""

from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from trajetoria.academico.models import Pessoa
from trajetoria.acesso import pendente
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.fonte_academica.simulada import FonteSimulada

# Barreira da demonstração (008 FR-008), não regra da sessão: a entrada só confirma numa
# base exclusivamente simulada (FR-005), e esta revalidação recusa qualquer Pessoa de outra
# fonte que apareça depois. Sai junto com o modo de demonstração.
_FONTE_ADMITIDA = FonteSimulada.codigo


def dados_de_sessao(pessoa, versao_material, agora):
    return {
        "acesso.pessoa": str(pessoa.pk),
        "acesso.confirmada_em": agora.isoformat(),
        "acesso.ultimo_uso": agora.isoformat(),
        "acesso.versao_material": versao_material.isoformat() if versao_material else None,
    }


def estabelecer(request, confirmada, agora):
    request.session.cycle_key()
    limpar_preservando_envio(request.session)
    request.session.update(dados_de_sessao(confirmada.pessoa, confirmada.versao_material, agora))
    request._pessoa_de_acesso = confirmada.pessoa
    request._declaracoes_de_acesso = None


def pessoa_em_uso(request):
    if hasattr(request, "_pessoa_de_acesso"):
        return request._pessoa_de_acesso
    pessoa = None
    sessao = getattr(request, "session", None)
    invalida = False
    if sessao and any(k.startswith("acesso.") for k in sessao.keys()):
        try:
            UUID(sessao["acesso.pessoa"])
            confirmada = datetime.fromisoformat(sessao["acesso.confirmada_em"])
            ultimo = datetime.fromisoformat(sessao["acesso.ultimo_uso"])
            agora = timezone.now()
            if (
                not timezone.is_aware(confirmada)
                or not timezone.is_aware(ultimo)
                or not confirmada <= ultimo <= agora
                or agora - ultimo > settings.TRAJETORIA_SESSAO_INATIVIDADE
                or agora - confirmada > settings.TRAJETORIA_SESSAO_DURACAO_MAXIMA
            ):
                invalida = True
            else:
                # Uma leitura para Pessoa e versão, também quando não há material.
                versao = MaterialDeVerificacao.objects.filter(pessoa_id=OuterRef("pk")).values(
                    "atualizado_em"
                )[:1]
                candidata = (
                    Pessoa.objects.filter(pk=sessao["acesso.pessoa"], fonte=_FONTE_ADMITIDA)
                    .annotate(_versao_material=Subquery(versao))
                    .first()
                )
                atual = (
                    candidata._versao_material.isoformat()
                    if candidata and candidata._versao_material
                    else None
                )
                if candidata is None or atual != sessao["acesso.versao_material"]:
                    invalida = True
                else:
                    pessoa = candidata
                    if agora - ultimo >= timedelta(minutes=1) and not post_de_entrada(request):
                        sessao["acesso.ultimo_uso"] = agora.isoformat()
        except (ValidationError, ValueError, TypeError, KeyError):
            invalida = True
    if invalida and not post_de_entrada(request):
        descartar_preservando_envio(sessao)
        request._sessao_expirada = True
    request._pessoa_de_acesso = pessoa
    return pessoa


def post_de_entrada(request):
    """POST de `/acesso/`: um resultado sem confirmação nunca modifica a sessão anterior,
    nem por renderizar a faixa. Público para o sujeito declarante da 019 (`declaracao.sessao`),
    que segue a mesma regra."""
    return request.method == "POST" and request.path == "/acesso/"


def encerrar(request):
    pendente.descartar(request)
    request.session.flush()
    request._pessoa_de_acesso = None
    request._declaracoes_de_acesso = None


# --- 023: sessão expirada e envio pendente ---------------------------------------------------


def limpar_preservando_envio(sessao):
    """`clear()` da sessão, mantendo só a chave opaca do envio pendente (023 FR-005): o
    registro do envio fica fora da sessão do sujeito e atravessa a nova confirmação."""
    chave = sessao.get(pendente.CHAVE)
    sessao.clear()
    if chave:
        sessao[pendente.CHAVE] = chave


def descartar_preservando_envio(sessao):
    """`flush()` da sessão descartada, mantendo a chave do envio pendente na sessão nova."""
    chave = sessao.get(pendente.CHAVE)
    sessao.flush()
    if chave:
        sessao[pendente.CHAVE] = chave


def destino_da_entrada(request):
    """Para onde mandar quem pede uma tela do egresso sem sujeito (023 FR-001): com aviso
    quando a sessão anterior acabou de ser descartada ou quando um envio foi guardado nesta
    requisição; sem aviso, como antes, quando nunca houve sessão. Nenhum dado no endereço."""
    if getattr(request, "_sessao_expirada", False) or pendente.guardado_nesta_requisicao(
        request
    ):
        return "/acesso/?aviso=sessao"
    return "/acesso/"

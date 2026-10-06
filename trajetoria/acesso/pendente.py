"""Envio pendente de uma Seção (023 FR-002 a FR-009; research R1 a R3).

Quando o envio de uma Seção chega sem sujeito válido (sessão expirada ou ausente), o que a
pessoa enviou é guardado aqui por pouco tempo, para voltar à Seção depois da nova
confirmação. O registro fica **fora** da sessão do sujeito: é outra chave do mesmo
armazenamento de sessões, com validade própria, e a sessão do navegador guarda só essa chave
opaca (`CHAVE`). Assim a sessão do sujeito nunca contém Participação nem valores (018
FR-040) e o registro some do banco na validade mais a limpeza diária de sessões.

O conteúdo é opaco para a 018: quem decide quais campos guardar e como restaurá-los é a
interface. Nada daqui vai a log, URL ou tela de confirmação de dados.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from importlib import import_module
from uuid import UUID

from django.conf import settings
from django.utils import timezone

CHAVE = "pendente.envio"
VALIDADE = timedelta(minutes=30)
# Limites do que se guarda (research R2): uma Seção real tem poucas dezenas de campos curtos.
# Acima disso o envio não é guardado, para que um POST sem sessão não vire depósito no banco.
LIMITE_VALOR = 2000
LIMITE_CAMPOS = 60
LIMITE_TOTAL = 20000


@dataclass(frozen=True)
class EnvioPendente:
    participacao: UUID
    posicao: int
    dados: dict[str, list[str]]
    em: datetime
    # Já levou a pessoa de volta à Seção uma vez: daí em diante a Seção continua restaurada,
    # mas nenhuma outra tela redireciona para ela (sem prender a pessoa num laço).
    apresentado: bool = False


def _armazenamento(chave=None):
    return import_module(settings.SESSION_ENGINE).SessionStore(session_key=chave)


def guardar(request, participacao, posicao: int, dados: dict[str, list[str]]) -> bool:
    """Substitui qualquer envio pendente anterior deste navegador pelo novo. Devolve `False`,
    sem guardar nada, quando o envio passa dos limites."""
    descartar(request)
    limpos = {
        campo: [str(v)[:LIMITE_VALOR] for v in valores]
        for campo, valores in list(dados.items())[:LIMITE_CAMPOS]
    }
    if sum(len(v) for valores in limpos.values() for v in valores) > LIMITE_TOTAL:
        return False
    registro = _armazenamento()
    registro.update(
        {
            "participacao": str(participacao),
            "posicao": int(posicao),
            "dados": limpos,
            "em": timezone.now().isoformat(),
        }
    )
    registro.set_expiry(int(VALIDADE.total_seconds()))
    registro.save()
    request.session[CHAVE] = registro.session_key
    request._envio_pendente_guardado = True
    return True


def ler(request) -> EnvioPendente | None:
    """O envio pendente válido deste navegador, ou `None`. Vencido, corrompido ou ausente,
    o ponteiro e o registro são apagados."""
    chave = request.session.get(CHAVE) if hasattr(request, "session") else None
    if not chave:
        return None
    registro = _armazenamento(chave)
    try:
        if not registro.exists(chave):
            raise ValueError
        em = datetime.fromisoformat(registro["em"])
        if not timezone.is_aware(em) or not em <= timezone.now() <= em + VALIDADE:
            raise ValueError
        envio = EnvioPendente(
            participacao=UUID(registro["participacao"]),
            posicao=int(registro["posicao"]),
            dados={str(k): [str(v) for v in vs] for k, vs in dict(registro["dados"]).items()},
            em=em,
            apresentado=bool(registro.get("apresentado", False)),
        )
    except (KeyError, ValueError, TypeError, AttributeError):
        descartar(request)
        return None
    return envio


def marcar_apresentado(request) -> None:
    chave = request.session.get(CHAVE)
    if not chave:
        return
    registro = _armazenamento(chave)
    if registro.get("em") is None:
        return
    registro["apresentado"] = True
    # A expiração no banco continua contada do envio, não desta gravação (FR-004).
    fim = datetime.fromisoformat(registro["em"]) + VALIDADE
    registro.set_expiry(max(1, int((fim - timezone.now()).total_seconds())))
    registro.save()


def descartar(request) -> None:
    sessao = getattr(request, "session", None)
    if sessao is None:
        return
    chave = sessao.get(CHAVE)
    if chave:
        _armazenamento(chave).delete(chave)
        del sessao[CHAVE]


def guardado_nesta_requisicao(request) -> bool:
    return getattr(request, "_envio_pendente_guardado", False)

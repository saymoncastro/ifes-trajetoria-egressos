"""Operador fictício em uso (Feature 010; contracts/demonstracao-operador.md; research R6).

**Adaptador temporário.** Faz as vezes da futura identificação de operadores institucionais
(DP-1001), como `entrada.py` faz para a Pessoa: entrega ao editor um identificador já
resolvido. Não autentica, não comprova identidade e não é mecanismo de produção. A escolha
só identifica; o que o operador pode fazer decorre exclusivamente dos vínculos de governança.

Só existem os três operadores fictícios abaixo, fixos no código: nenhum identificador vindo
do navegador é aceito se não estiver nesta lista, e nenhum vínculo registrado para pessoa
real é selecionável, mesmo com o modo ligado por engano. Com o modo desligado, nenhum
cookie é lido.
"""

from dataclasses import dataclass

from django.conf import settings

from trajetoria.governanca.consultas import vinculos_ativos


@dataclass(frozen=True)
class OperadorFicticio:
    identificador: str
    rotulo: str


OPERADORES_FICTICIOS = (
    OperadorFicticio("demonstracao:operador-a", "Operador fictício A"),
    OperadorFicticio("demonstracao:operador-b", "Operador fictício B"),
    OperadorFicticio("demonstracao:operador-c", "Operador fictício C"),
)

COOKIE = "trajetoria_demonstracao_operador"
SALT = "operador-de-demonstracao"


def operador_ficticio(identificador) -> OperadorFicticio | None:
    return next((o for o in OPERADORES_FICTICIOS if o.identificador == identificador), None)


_EM_USO = "_operador_de_demonstracao"


def operador_em_uso(request) -> str | None:
    """O identificador do operador fictício do cookie, revalidado contra a lista; `None` em
    qualquer outro caso e sempre com o modo desligado. Nunca grava e nunca levanta exceção
    por cookie ausente, inválido ou adulterado. Lido uma vez por requisição."""
    if not settings.TRAJETORIA_DEMONSTRACAO:
        return None
    if not hasattr(request, _EM_USO):
        valor = request.get_signed_cookie(COOKIE, default=None, salt=SALT)
        operador = operador_ficticio(valor)
        setattr(request, _EM_USO, operador.identificador if operador else None)
    return getattr(request, _EM_USO)


def vinculos_do_operador_em_uso(request) -> list | None:
    """Ponto único de identificação das superfícies institucionais (editor e acompanhamento):
    `None` sem operador identificado; senão os vínculos ativos dele (`[]` se nenhum). Não
    autoriza nada: cada superfície aplica a sua regra sobre esses vínculos."""
    identificador = operador_em_uso(request)
    return None if identificador is None else vinculos_ativos(identificador)


def usar_operador(response, operador: OperadorFicticio) -> None:
    if operador not in OPERADORES_FICTICIOS:
        raise ValueError("só operadores fictícios podem ser usados na demonstração")
    # Cookie de sessão do navegador (sem max_age): fechar o navegador encerra a escolha.
    response.set_signed_cookie(
        COOKIE, operador.identificador, salt=SALT, httponly=True, samesite="Lax"
    )


def esquecer_operador(response) -> None:
    response.delete_cookie(COOKIE, samesite="Lax")

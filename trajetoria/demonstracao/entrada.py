"""Pessoa de demonstração em uso (contracts/demonstracao.md; research R4).

**Adaptador temporário.** Faz as vezes da futura fronteira de identidade, entregando à
interface uma "Pessoa resolvida" (007 FR-001). Não é autenticação, não comprova
identidade e não é mecanismo de produção (FR-004). Quando a fronteira real existir, este
app sai e a interface troca a importação de `pessoa_em_uso` (FR-005).

O único estado entre requisições é um cookie assinado com o `pk` da Pessoa (FR-009). A
assinatura evita adulteração trivial; o controle que importa é a revalidação a cada
requisição: só Pessoas da **fonte simulada** são aceitas, de modo que nenhuma Pessoa
real seria listada ou aceita mesmo sobre um banco com dados reais (FR-008, FR-010).
"""

from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet

from trajetoria.academico.models import Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada

COOKIE = "trajetoria_demonstracao_pessoa"
SALT = "pessoa-de-demonstracao"


def pessoas_de_demonstracao() -> QuerySet:
    """Pessoas da fonte simulada, com as Conclusões, em ordem (nome, pk) — determinística,
    sem significado."""
    return (
        Pessoa.objects.filter(fonte=FonteSimulada.codigo)
        .prefetch_related("conclusoes")
        .order_by(F("nome").asc(nulls_last=True), "pk")
    )


def pessoa_de_demonstracao(pk) -> Pessoa | None:
    """A Pessoa da fonte simulada com esse `pk`, ou `None` (inexistente, de outra fonte ou
    identificador malformado)."""
    try:
        return Pessoa.objects.filter(pk=pk, fonte=FonteSimulada.codigo).first()
    except (ValidationError, ValueError, TypeError):
        return None


_EM_USO = "_pessoa_de_demonstracao"


def pessoa_em_uso(request) -> Pessoa | None:
    """A Pessoa do cookie, revalidada; `None` em qualquer outro caso. Nunca grava e nunca
    levanta exceção por cookie ausente, inválido ou adulterado. Lida uma vez por
    requisição: view e cabeçalho (processador de contexto) usam o mesmo resultado."""
    if not hasattr(request, _EM_USO):
        pk = request.get_signed_cookie(COOKIE, default=None, salt=SALT)
        setattr(request, _EM_USO, None if pk is None else pessoa_de_demonstracao(pk))
    return getattr(request, _EM_USO)


def usar(response, pessoa: Pessoa) -> None:
    if pessoa.fonte != FonteSimulada.codigo:
        raise ValueError("só Pessoas da fonte simulada podem ser usadas na demonstração")
    # Cookie de sessão do navegador (sem max_age): fechar o navegador encerra a escolha.
    response.set_signed_cookie(COOKIE, str(pessoa.pk), salt=SALT, httponly=True, samesite="Lax")


def esquecer(response) -> None:
    response.delete_cookie(COOKIE, samesite="Lax")

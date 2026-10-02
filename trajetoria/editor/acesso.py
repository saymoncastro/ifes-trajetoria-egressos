"""Autorização do editor (Feature 010; contracts/acesso-editor.md; research R8, R14).

Cada view declara, com `@exige(regra)`, uma das três regras de `governanca.regras`. A cada
requisição, **antes** de qualquer outra coisa da view (busca do elemento, formulário,
operação da 002):

1. identificação e vínculos ativos: `vinculos_do_operador_em_uso` — o adaptador de
   demonstração, único ponto a trocar quando houver identificação produtiva (DP-1001), o
   mesmo do acompanhamento da coleta (011). Sem operador → escolha de operador fictício
   (endereço fixo, sem retorno);
2. nenhum vínculo ativo → recusa;
3. a regra da rota; falsa → recusa.

Resolução do operador e autorização ficam separadas. Fora do modo de demonstração o
middleware da 008 já respondeu 404, e `operador_em_uso` devolve `None` de todo modo.
"""

from dataclasses import dataclass
from functools import wraps

from django.shortcuts import redirect, render

from trajetoria.demonstracao.operador import vinculos_do_operador_em_uso
from trajetoria.editor import mensagens
from trajetoria.governanca.regras import (
    pode_consultar_publicado,
    pode_consultar_rascunho,
    pode_elaborar_instrumento,
)

ESCOLHA_DE_OPERADOR = "/demonstracao/operador/"
_REGRAS = (pode_consultar_publicado, pode_consultar_rascunho, pode_elaborar_instrumento)


@dataclass(frozen=True)
class Atuacao:
    """O que as páginas sabem do operador: rótulos das atuações e o que ele pode fazer.
    Nunca o identificador."""

    rotulos: tuple[str, ...]
    consultar_rascunho: bool
    elaborar: bool


def recusa(request, texto: str):
    """Página 403 em linguagem operacional (contracts/acesso-editor.md)."""
    atuacao = getattr(request, "atuacao", None)
    return render(
        request,
        "editor/recusa.html",
        {
            "banner": mensagens.BANNER,
            "atuacao": atuacao,
            "titulo": mensagens.RECUSA_TITULO,
            "texto": texto,
        },
        status=403,
    )


def exige(regra):
    if regra not in _REGRAS:
        raise ValueError("o editor só conhece as três regras de governanca.regras")

    def decorador(view):
        @wraps(view)
        def envolvida(request, *args, **kwargs):
            vinculos = vinculos_do_operador_em_uso(request)
            if vinculos is None:
                return redirect(ESCOLHA_DE_OPERADOR)
            if not vinculos:
                return recusa(request, mensagens.RECUSA_SEM_ATUACAO)
            request.atuacao = Atuacao(
                rotulos=tuple(v.rotulo_de_atuacao for v in vinculos),
                consultar_rascunho=pode_consultar_rascunho(vinculos),
                elaborar=pode_elaborar_instrumento(vinculos),
            )
            if not regra(vinculos):
                elaboracao = regra is pode_elaborar_instrumento
                return recusa(
                    request,
                    mensagens.RECUSA_ELABORACAO if elaboracao else mensagens.RECUSA_RASCUNHO,
                )
            return view(request, *args, **kwargs)

        envolvida.exige = regra
        return envolvida

    return decorador

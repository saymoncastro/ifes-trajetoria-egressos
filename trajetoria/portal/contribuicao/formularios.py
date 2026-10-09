"""Leitura da escolha do egresso (026 FR-012; plan R11).

Sem estado em sessão: a escolha vai da primeira tela à confirmação em campos ocultos e é lida
de novo, do mesmo jeito, em cada POST. Só converte e aponta o erro de cada campo; quem grava e
revalida tudo é `operacoes.registrar`. Uma formação fora das Conclusões da Pessoa, mesmo num
POST forjado, é recusada aqui.
"""

from dataclasses import dataclass

from trajetoria.portal.contribuicao import mensagens as m
from trajetoria.portal.contribuicao.regras import normalizar_mensagem, violacoes_da_escolha
from trajetoria.portal.models import Forma


@dataclass(frozen=True)
class Escolha:
    forma: str
    conclusao: object | None
    mensagem: str


def ler_escolha(dados, conclusoes) -> tuple[Escolha, dict[str, str]]:
    """A escolha lida e os erros por campo, na ordem da tela (forma, formação, mensagem)."""
    forma = dados.get("forma") or ""
    formacao = dados.get("formacao") or ""
    conclusao = next((c for c in conclusoes if str(c.pk) == formacao), None)
    mensagem = normalizar_mensagem(dados.get("mensagem"))
    campos = {v.campo for v in violacoes_da_escolha(forma, mensagem)}
    erros = {}
    if "forma" in campos:
        erros["forma"] = m.ERROS["forma"]
    if conclusao is None:
        erros["formacao"] = m.ERROS["formacao"]
    if "mensagem" in campos:
        erros["mensagem"] = m.ERROS["mensagem"]
    return Escolha(forma if "forma" not in campos else "", conclusao, mensagem), erros


def formacao_em_texto(conclusao) -> str:
    if conclusao is None:
        return m.FORMACAO_NAO_ENCONTRADA
    partes = [conclusao.curso or "Formação", conclusao.unidade or m.SEM_UNIDADE]
    if conclusao.ano_conclusao:
        partes.append(str(conclusao.ano_conclusao))
    return " · ".join(partes)


def opcoes(escolha: Escolha | None, conclusoes) -> dict:
    """As opções das duas listas, com a marcada. Uma só formação já vem marcada (XXI)."""
    forma = escolha.forma if escolha else ""
    marcada = escolha.conclusao if escolha else None
    if marcada is None and len(conclusoes) == 1:
        marcada = conclusoes[0]
    return {
        "formas": [
            {"valor": f.value, "rotulo": f.label, "descricao": m.DESCRICOES[f],
             "marcada": f.value == forma}
            for f in Forma
        ],
        "formacoes": [
            {"valor": str(c.pk), "rotulo": formacao_em_texto(c),
             "marcada": marcada is not None and c.pk == marcada.pk}
            for c in conclusoes
        ],
    }

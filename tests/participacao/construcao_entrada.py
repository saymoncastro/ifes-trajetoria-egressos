"""Auxiliares dos testes de entrada (Feature 007; não são testes).

Não altera `construcao.py`: reutiliza seus auxiliares. Todo teste passa `agora` explícito.
Somente dados fictícios.
"""

from itertools import count

from tests.campanha.construcao import incorporar_cenarios
from tests.participacao import construcao as c
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha.models import Campanha
from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao
from trajetoria.participacao.operacoes import concluir, iniciar_participacao

_sequencia = count(1)


def pessoa() -> Pessoa:
    """Pessoa fictícia por ORM, sem Conclusões."""
    return Pessoa.objects.create(fonte="teste-entrada", id_externo=f"TE-P-{next(_sequencia)}")


def formacao(p: Pessoa, *, ano=2022, unidade="Serra") -> ConclusaoAcademica:
    return c.conclusao(pessoa=p, ano=ano, unidade=unidade)


def participacao_em_rascunho(campanha, conclusao, agora=c.NO_PERIODO) -> Participacao:
    return iniciar_participacao(campanha, conclusao, agora=agora).participacao


def participacao_concluida(campanha, conclusao, inst, agora=c.NO_PERIODO) -> Participacao:
    """Iniciada, preenchida e concluída pelas operações da 005/006."""
    participacao = participacao_em_rascunho(campanha, conclusao, agora)
    c.preencher_instrumento(participacao, inst, agora)
    return concluir(participacao, agora=agora).participacao


def linhas() -> dict:
    """Todas as linhas das tabelas que a entrada poderia tocar, para comparar."""
    modelos = (Pessoa, ConclusaoAcademica, Campanha, Participacao, Resposta, RespostaOpcao)
    return {m.__name__: list(m.objects.order_by("pk").values()) for m in modelos}


def incorporar(fonte, *ids) -> None:
    """Incorpora cenários da fonte simulada (001) pelo caminho real."""
    incorporar_cenarios(fonte, set(ids) or None)


def pessoa_da_fonte(id_externo: str) -> Pessoa:
    return Pessoa.objects.get(fonte="simulada", id_externo=id_externo)

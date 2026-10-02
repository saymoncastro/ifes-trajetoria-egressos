"""Auxiliares dos testes do acompanhamento da coleta (Feature 011; não são testes).

Somente dados fictícios. Conclusões por ORM (como nos testes da 004 e da 005), Campanhas e
Participações pelas operações da 004, 005 e 006. As views usam o relógio do sistema; por isso
as Campanhas têm período relativo a hoje e as operações recebem `agora=None` — inclusive
`preencher_instrumento`, cujo padrão é 2027.
"""

import re
from datetime import datetime, time, timedelta
from itertools import count

from django.utils import timezone

from tests.editor.construcao_editor import A, B, C, atuar_como
from tests.participacao.construcao import preencher_instrumento
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.participacao.operacoes import (
    concluir,
    iniciar_participacao,
    responder_escolha_unica,
    responder_texto,
)

__all__ = ["A", "B", "C", "atuar_como"]

_sequencia = count(1)


def hoje():
    return timezone.localdate()


def momento_em(dia) -> datetime:
    return timezone.make_aware(datetime.combine(dia, time(12)))


def conclusao(
    *,
    unidade=None,
    curso=None,
    nivel=None,
    modalidade=None,
    forma_oferta=None,
    ano=None,
    pessoa: Pessoa | None = None,
) -> ConclusaoAcademica:
    n = next(_sequencia)
    if pessoa is None:
        pessoa = Pessoa.objects.create(
            fonte="teste-acompanhamento", id_externo=f"TA-P-{n}", nome=f"Pessoa Ficticia {n}"
        )
    return ConclusaoAcademica.objects.create(
        pessoa=pessoa,
        fonte="teste-acompanhamento",
        id_externo=f"TA-C-{n}",
        unidade=unidade,
        curso=curso,
        nivel=nivel,
        modalidade=modalidade,
        forma_oferta=forma_oferta,
        ano_conclusao=ano,
    )


def campanha(versao, *, estado="em_coleta", nome=None, **criterios):
    """Campanha pelas operações da 004.

    - `em_coleta`: período de hoje−10 a hoje+30, aberta agora;
    - `em_preparacao`: período de hoje+10 a hoje+40, nunca aberta;
    - `sem_periodo`: nunca aberta, sem período;
    - `encerrada_explicita`: aberta e encerrada agora;
    - `encerrada_por_periodo`: período de hoje−40 a hoje−5, aberta em hoje−30;
    - `expirada_sem_abertura`: período de hoje−40 a hoje−5, nunca aberta.
    """
    c = op_campanha.criar_campanha(nome or f"Campanha fictícia {next(_sequencia)}", versao)
    if criterios:
        op_campanha.definir_criterios(c, **criterios)
    d = hoje()
    if estado == "em_coleta":
        op_campanha.definir_periodo(c, d - timedelta(days=10), d + timedelta(days=30))
        op_campanha.abrir(c)
    elif estado == "em_preparacao":
        op_campanha.definir_periodo(c, d + timedelta(days=10), d + timedelta(days=40))
    elif estado == "sem_periodo":
        pass
    elif estado == "encerrada_explicita":
        op_campanha.definir_periodo(c, d - timedelta(days=10), d + timedelta(days=30))
        op_campanha.abrir(c)
        op_campanha.encerrar(c)
    elif estado in ("encerrada_por_periodo", "expirada_sem_abertura"):
        op_campanha.definir_periodo(c, d - timedelta(days=40), d - timedelta(days=5))
        if estado == "encerrada_por_periodo":
            op_campanha.abrir(c, agora=momento_em(d - timedelta(days=30)))
    else:
        raise ValueError(estado)
    c.refresh_from_db()
    return c


def iniciada(campanha_, conclusao_):
    return iniciar_participacao(campanha_, conclusao_, agora=None).participacao


def concluida(campanha_, conclusao_, inst):
    participacao = iniciada(campanha_, conclusao_)
    preencher_instrumento(participacao, inst, agora=None)
    return concluir(participacao, agora=None).participacao


def concluida_por_recusa(campanha_, conclusao_, inst):
    """Q1 = "Não" finaliza a jornada depois da Seção atual (006 FR-022): no instrumento de
    teste da 005, as demais obrigatórias da Seção 1 continuam exigidas. Conta como
    concluída (011 FR-033)."""
    participacao = iniciada(campanha_, conclusao_)
    preencher_instrumento(participacao, inst, agora=None)
    responder_escolha_unica(participacao, inst.unica, inst.opcao(inst.unica, "Não"), agora=None)
    return concluir(participacao, agora=None).participacao


def com_texto_declarado(participacao, inst, texto):
    responder_texto(participacao, inst.texto, texto, agora=None)
    return participacao


# --- Leitura das páginas ------------------------------------------------------------------------


def detalhe(cliente, campanha, recorte=None):
    sufixo = f"?recorte={recorte}" if recorte else ""
    return cliente.get(f"/acompanhamento/campanhas/{campanha.pk}/{sufixo}")


def _limpar(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def resumo_em_numeros(resposta) -> dict[str, str]:
    """Rótulo do indicador → valor exibido, a partir da `<dl>` do resumo."""
    html = resposta.content.decode()
    html = html[html.index("<h2>Resumo</h2>") : html.index("<h2>Recortes</h2>")]
    pares = re.findall(r"<dt>(.*?) <span class=\"definicao\">.*?</dt><dd>(.*?)</dd>", html, re.S)
    return {rotulo: _limpar(valor) for rotulo, valor in pares}


def tabela_do_recorte(resposta) -> dict:
    """`{"cabecalhos": [...], "linhas": [[células]...], "total": [células]}` da tabela do
    recorte, com o texto visível de cada célula."""
    html = resposta.content.decode()
    html = html[html.index("<h2>Recortes</h2>") :]
    cabecalhos = [_limpar(c) for c in re.findall(r"<th scope=\"col\"[^>]*>(.*?)</th>", html, re.S)]

    def celulas(trecho):
        return [_limpar(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", trecho, re.S)]

    corpo = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    linhas = [celulas(tr) for tr in re.findall(r"<tr>(.*?)</tr>", corpo, re.S)]
    total = celulas(re.search(r"<tfoot>(.*?)</tfoot>", html, re.S).group(1))
    return {"cabecalhos": cabecalhos, "linhas": linhas, "total": total}

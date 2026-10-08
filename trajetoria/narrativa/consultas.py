"""Leitura dos fatos da narrativa (Feature 021; research R2, R14).

Só leitura: nada aqui grava (FR-008). A narrativa é da Pessoa e reúne todas as suas
Conclusões Acadêmicas (FR-001, FR-016). Desde a 024 (FR-009), o acesso não depende de
participação em pesquisa.
Nenhuma Resposta é lida (FR-044). Complemento e agregados vêm do que a carga do contexto da
trajetória gravou (P2); nada é calculado da base local como valor (FR-055).
"""

import logging

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.contexto_trajetoria.models import ContextoInstitucionalAgregado
from trajetoria.narrativa.contrato import (
    METRICA_CURSO_UNIDADE_ANO,
    METRICA_UNIDADE_ANO,
    ContextoSelecionado,
    EntradaDaNarrativa,
    FatoDaFormacao,
)

logger = logging.getLogger("trajetoria.narrativa")

_CONTEXTO = (
    "curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao", "data_conclusao",
)


def elegivel(pessoa) -> bool:
    """Regra positiva da 024 (FR-009; revisa 021 FR-001, FR-002 e E2, e 022 FR-001): a Pessoa
    identificada com ao menos uma Conclusão Acadêmica tem trajetória institucional,
    independentemente de participação em pesquisa. Formação Declarada (019) não é Conclusão
    e fica de fora por construção."""
    return pessoa.conclusoes.exists()


def _ingresso(conclusao) -> dict:
    """Ingresso do complemento, só se coerente: posterior ao ano de conclusão invalida o
    complemento para a narrativa, que o omite e sinaliza sem dado pessoal (FR-051)."""
    complemento = getattr(conclusao, "complemento", None)
    if complemento is None:
        return {}
    if conclusao.ano_conclusao is not None and complemento.ano_ingresso > conclusao.ano_conclusao:
        logger.warning(
            "Complemento incoerente em %s:%s (campos: ano_ingresso)",
            conclusao.fonte, conclusao.id_externo,
        )
        return {}
    return {"ingresso_ano": complemento.ano_ingresso, "ingresso_data": complemento.data_ingresso}


def _selecionado(conclusao, indice, metrica) -> ContextoSelecionado | None:
    """Exatamente uma apuração conhecida da mesma fonte e do recorte exato (FR-058, FR-059);
    senão, nada: nenhuma escolha por data. A base local é só trava: se já há mais Conclusões
    incorporadas no recorte do que o valor diz, o agregado é incoerente (FR-060)."""
    por_curso = metrica == METRICA_CURSO_UNIDADE_ANO
    recorte = {"unidade": conclusao.unidade, "ano": conclusao.ano_conclusao}
    registros = list(
        ContextoInstitucionalAgregado.objects.filter(
            fonte=conclusao.fonte,
            metrica=metrica,
            **recorte,
            **({"curso": conclusao.curso} if por_curso else {"curso__isnull": True}),
        )[:2]
    )
    if len(registros) != 1:
        return None
    agregado = registros[0]
    locais = ConclusaoAcademica.objects.filter(
        fonte=conclusao.fonte,
        unidade=conclusao.unidade,
        ano_conclusao=conclusao.ano_conclusao,
        **({"curso": conclusao.curso} if por_curso else {}),
    ).count()
    if locais > agregado.valor:
        logger.warning(
            "Agregado incoerente em %s: %s",
            conclusao.fonte,
            " · ".join(
                str(v) for v in (metrica, agregado.curso, agregado.unidade, agregado.ano) if v
            ),
        )
        return None
    return ContextoSelecionado(
        metrica=metrica,
        unidade=agregado.unidade,
        ano=agregado.ano,
        valor=agregado.valor,
        apurado_em=agregado.apurado_em,
        formacao=indice,
        curso=agregado.curso,
    )


def _agregados(conclusoes) -> tuple[ContextoSelecionado, ...]:
    """Pela ordem das formações; métrica por curso antes da por unidade; a por unidade uma
    vez por (unidade, ano)."""
    selecionados, unidades = [], set()
    for indice, conclusao in enumerate(conclusoes):
        if conclusao.unidade is None or conclusao.ano_conclusao is None:
            continue
        if conclusao.curso is not None:
            if escolhido := _selecionado(conclusao, indice, METRICA_CURSO_UNIDADE_ANO):
                selecionados.append(escolhido)
        chave = (conclusao.unidade, conclusao.ano_conclusao)
        if chave not in unidades:
            if escolhido := _selecionado(conclusao, indice, METRICA_UNIDADE_ANO):
                selecionados.append(escolhido)
                unidades.add(chave)
    return tuple(selecionados)


def entrada_da_pessoa(pessoa, referencia, demonstracao) -> EntradaDaNarrativa:
    # Ordem do model (ano_conclusao, id), a mesma da 007; atributos como valores (FR-013).
    conclusoes = list(pessoa.conclusoes.select_related("complemento"))
    formacoes = tuple(
        FatoDaFormacao(
            **{campo: getattr(conclusao, campo) for campo in _CONTEXTO}, **_ingresso(conclusao)
        )
        for conclusao in conclusoes
    )
    return EntradaDaNarrativa(
        nome=pessoa.nome,
        formacoes=formacoes,
        agregados=_agregados(conclusoes),
        referencia=referencia,
        demonstracao=demonstracao,
    )

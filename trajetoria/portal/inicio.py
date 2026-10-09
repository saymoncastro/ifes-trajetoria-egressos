"""Composição do Início do Portal (024 FR-016 a FR-021; contracts/inicio.md; research R6).

Só leitura e uma única fonte de fatos: a mesma montagem da narrativa da 021, sem o nome
(FR-019), e a situação da entrada da 007, para o convite. Não lê Resposta nem contato. A
origem de cada frase vem do próprio contrato da narrativa (institucional ou derivado), e
vira texto visível (FR-018).
"""

import dataclasses
import logging

from django.db import DatabaseError

from trajetoria.interface import mensagens as estados
from trajetoria.narrativa import card, rasterizacao
from trajetoria.narrativa.consultas import elegivel, entrada_da_pessoa
from trajetoria.narrativa.contrato import DERIVADO, INSTITUCIONAL
from trajetoria.narrativa.montagem import montar
from trajetoria.participacao.entrada import (
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    situacao_de_entrada,
)
from trajetoria.portal import mensagens
from trajetoria.portal.oportunidades import mensagens as m_oportunidades
from trajetoria.portal.oportunidades.consultas import itens_da_pessoa
from trajetoria.video import renderizador

logger = logging.getLogger("trajetoria.portal")

_ORIGEM = {INSTITUCIONAL: mensagens.REGISTRO_DO_IFES, DERIVADO: mensagens.DERIVADO}

# Compactação do destaque de Oportunidades (025 research R9; T026, T046): 0 = padrão; 1 a 3
# aplicam as etapas em ordem. Nenhuma etapa remove título, explicação, unidade responsável,
# origem do site nem domínio (FR-004, FR-013). Decidida pela medida da T046.
COMPACTACAO_DO_DESTAQUE = 3  # T046: variante 3 medida (Diego: 290 → 253 px)


def _reconhecimento(pessoa, referencia, demonstracao) -> dict | None:
    """Síntese e formações, cada frase com a sua origem. `None` se a montagem falhar: o
    Início omite o bloco e segue (spec, Edge Cases)."""
    try:
        entrada = dataclasses.replace(
            entrada_da_pessoa(pessoa, referencia, demonstracao), nome=None
        )
        narrativa = montar(entrada)
    except Exception:
        logger.exception("portal: falha ao montar o reconhecimento")  # só o fato técnico
        return None
    registro = narrativa.secao("o_que_o_ifes_registra")
    trajetoria = narrativa.secao("trajetoria_academica")
    frases = trajetoria.frases if trajetoria else ()
    formacoes = []
    for indice in sorted({f.formacao for f in frases if f.formacao is not None}):
        formacoes.append([
            # A linha de atributos ("Graduação · Presencial") detalha o fato anterior e herda
            # a sua origem: não repete o selo.
            {
                "texto": f.texto,
                "origem": None if f.tipo != "frase" else _ORIGEM.get(f.origem),
                "atributos": f.tipo != "frase",
                "ano": narrativa.formacoes[indice].ano_conclusao,
            }
            for f in frases
            if f.formacao == indice
        ])
    naquele_ano = narrativa.secao("naquele_ano")
    agregadas = [f for f in naquele_ano.frases if f.formacao is not None] if naquele_ano else []
    return {
        "sintese": [f.texto for f in registro.frases] if registro else [],
        "formacoes": formacoes,
        "numeros": [
            {"numero": card.numero_formatado(c.valor), "texto": f.texto}
            for c, f in zip(narrativa.contextos_agregados, agregadas, strict=True)
        ],
        "apuracoes": [f.texto for f in naquele_ano.frases if f.formacao is None]
        if naquele_ano else [],
        "card_alt": card.descricao(narrativa.compartilhavel, None, demonstracao),
        # O mesmo formato da prévia da Minha trajetória (021): PNG com as fontes embutidas
        # quando há rasterização; SVG só sem ela.
        "card_arquivo": (
            f"/minha-trajetoria/card.{'png' if rasterizacao.rasterizacao_disponivel() else 'svg'}"
        ),
    }


def _convite(situacao) -> dict | None:
    """Um único bloco, pela resolução da 007 (FR-020). A ação sempre leva à escolha de
    formações, que decide e conduz como hoje (e mostra o "onde parou" da 023).

    Para a formação a retomar, o texto diz que a pessoa já começou (revisão de 2026-10-08,
    A7). A Seção exata não aparece aqui: ela sai das Respostas, que o Início não lê (FR-017)."""
    resolucao = situacao.resolucao
    if resolucao == ResolucaoDaEntrada.SEM_FORMACAO:
        return None
    if resolucao == ResolucaoDaEntrada.SEM_PESQUISA:
        return {"texto": estados.SEM_PESQUISA, "acao": None}
    if resolucao == ResolucaoDaEntrada.SEM_ENTRADA_PENDENTE:
        return {"texto": estados.SEM_ENTRADA_PENDENTE, "acao": None}
    if resolucao == ResolucaoDaEntrada.SELECAO_NECESSARIA:
        n = len(situacao.pendentes)
        return {"texto": mensagens.CONVITE_VARIAS.format(n=n), "acao": mensagens.ACAO_ESCOLHER}
    formacao = situacao.pendentes[0]  # ENTRADA_RESOLVIDA
    curso = formacao.conclusao.curso
    retomar = formacao.situacao == SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR
    if retomar:
        texto = (
            mensagens.CONVITE_RETOMAR.format(curso=curso) if curso
            else mensagens.CONVITE_RETOMAR_SEM_CURSO
        )
        return {"texto": texto, "acao": mensagens.ACAO_CONTINUAR}
    texto = mensagens.CONVITE_UMA.format(curso=curso) if curso else mensagens.CONVITE_UMA_SEM_CURSO
    return {"texto": texto, "acao": mensagens.ACAO_RESPONDER}


ACAO_CARD = {"rotulo": mensagens.ACAO_CARD, "endereco": "/minha-trajetoria/#card"}


def _acoes(com_trajetoria: bool, com_previa: bool = False) -> list[dict]:
    """Com a prévia do card no Início (028), a ação do card fica junto dela e sai da lista,
    para não repetir o mesmo link."""
    acoes = []
    if com_trajetoria:
        acoes.append({"rotulo": mensagens.ACAO_TRAJETORIA, "endereco": "/minha-trajetoria/"})
        if not com_previa:
            acoes.append(ACAO_CARD)
        if renderizador.disponivel():
            acoes.append({"rotulo": mensagens.ACAO_VIDEO, "endereco": "/minha-trajetoria/#video"})
    acoes.append({"rotulo": mensagens.ACAO_EMAIL, "endereco": "/meu-email/"})
    return acoes


def _oportunidades(pessoa, hoje) -> dict | None:
    """Um destaque e o total (025 FR-021). `None` sem itens: o bloco não existe. Uma falha do
    banco omite só o bloco, como no reconhecimento; erro de programação não é engolido (code
    review do PR #49): sem isso, uma regressão na pertinência sumiria com o bloco em silêncio."""
    try:
        itens = itens_da_pessoa(pessoa, hoje)
    except DatabaseError:
        logger.exception("portal: falha ao montar as oportunidades")
        return None
    if not itens:
        return None
    total = len(itens)
    return {
        "titulo": m_oportunidades.TITULO,
        "destaque": itens[0],
        "ver": (
            m_oportunidades.VER_TODAS.format(n=total) if total > 1 else m_oportunidades.VER_PAGINA
        ),
        "compacto": COMPACTACAO_DO_DESTAQUE,
    }


def montar_inicio(pessoa, referencia, demonstracao) -> dict:
    com_trajetoria = elegivel(pessoa)
    reconhecimento = (
        _reconhecimento(pessoa, referencia, demonstracao) if com_trajetoria else None
    )
    return {
        "titulo": mensagens.TITULO,
        "reconhecimento": reconhecimento,
        "sem_formacao": None if com_trajetoria else estados.SEM_FORMACAO,
        "proveniencia": mensagens.PROVENIENCIA if com_trajetoria else None,
        "titulo_acoes": mensagens.TITULO_ACOES,
        "acoes": _acoes(com_trajetoria, com_previa=reconhecimento is not None),
        "acao_card": ACAO_CARD,
        "oportunidades": _oportunidades(pessoa, referencia) if com_trajetoria else None,
        "titulo_convite": mensagens.TITULO_CONVITE,
        "convite": _convite(situacao_de_entrada(pessoa)),
    }

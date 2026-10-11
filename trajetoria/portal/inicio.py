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
from trajetoria.narrativa.views import nome_do_card
from trajetoria.participacao.entrada import (
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    situacao_de_entrada,
)
from trajetoria.portal import mensagens
from trajetoria.portal.contribuicao import mensagens as m_contribuicao
from trajetoria.portal.contribuicao.consultas import resumo_da_pessoa
from trajetoria.portal.models import Categoria
from trajetoria.portal.oportunidades import mensagens as m_oportunidades
from trajetoria.portal.oportunidades.consultas import itens_da_pessoa
from trajetoria.video import renderizador

logger = logging.getLogger("trajetoria.portal")

_ORIGEM = {INSTITUCIONAL: mensagens.REGISTRO_DO_IFES, DERIVADO: mensagens.DERIVADO}

# Compactação do destaque de Oportunidades (025 research R9; T026, T046): 0 = padrão; 1 a 3
# aplicam as etapas em ordem. Nenhuma etapa remove título, explicação, unidade responsável,
# origem do site nem domínio (FR-004, FR-013). Decidida pela medida da T046.
COMPACTACAO_DO_DESTAQUE = 3  # T046: variante 3 medida (Diego: 290 → 253 px)


def formacoes_com_origem(narrativa) -> list[list[dict]]:
    """As frases de cada formação, com a origem visível (FR-018). Também serve à
    demonstração da página pública (029 FR-009), no mesmo formato do Início."""
    trajetoria = narrativa.secao("trajetoria_academica")
    frases = trajetoria.frases if trajetoria else ()
    return [
        [
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
        ]
        for indice in sorted({f.formacao for f in frases if f.formacao is not None})
    ]


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
    png = rasterizacao.rasterizacao_disponivel()
    registro = narrativa.secao("o_que_o_ifes_registra")
    formacoes = formacoes_com_origem(narrativa)
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
        # quando há rasterização; SVG só sem ela. O nome do download é o da 021.
        "card_arquivo": f"/minha-trajetoria/card.{'png' if png else 'svg'}",
        "card_nome": nome_do_card(png),
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


def _acoes(com_trajetoria: bool, reconhecimento: dict | None) -> list[dict]:
    """Ações da trajetória junto do card (032, convergência C): baixar o card, quando há prévia,
    ver a trajetória e o vídeo, quando há renderizador. O e-mail fica na participação."""
    acoes = []
    if com_trajetoria:
        if reconhecimento:
            acoes.append({"rotulo": mensagens.ACAO_CARD,
                          "endereco": reconhecimento["card_arquivo"],
                          "baixar": reconhecimento["card_nome"]})
        acoes.append({"rotulo": mensagens.ACAO_TRAJETORIA, "endereco": "/minha-trajetoria/"})
        if renderizador.disponivel():
            acoes.append({"rotulo": mensagens.ACAO_VIDEO, "endereco": "/minha-trajetoria/#video"})
    return acoes


def _itens(pessoa, hoje):
    """As oportunidades pertinentes, ou `None` se o banco falhar: nesse caso só os blocos que
    dependem delas somem, como no reconhecimento. Erro de programação não é engolido (code
    review do PR #49): sem isso, uma regressão na pertinência sumiria com o bloco em silêncio."""
    try:
        return itens_da_pessoa(pessoa, hoje)
    except DatabaseError:
        logger.exception("portal: falha ao montar as oportunidades")
        return None


def _encontro(itens):
    """Encontros de egressos (comunidade, alternativa A): o primeiro item pertinente da
    categoria Eventos (025). Nenhuma inferência além da pertinência (032 FR-012)."""
    return next((i for i in itens or () if i.oportunidade.categoria == Categoria.EVENTOS), None)


def _oportunidades(itens, encontro) -> dict | None:
    """Um destaque e o total (025 FR-021). `None` sem itens: a seção não existe. O destaque não
    repete o encontro mostrado acima (032 FR-008)."""
    if not itens:
        return None
    destaque = next((i for i in itens if i is not encontro), None)
    if destaque is None:
        return None
    total = len(itens)
    return {
        "titulo": mensagens.TITULO_OPORTUNIDADES_INICIO,
        "destaque": destaque,
        "ver": (
            m_oportunidades.VER_TODAS.format(n=total) if total > 1 else m_oportunidades.VER_PAGINA
        ),
        "compacto": COMPACTACAO_DO_DESTAQUE,
    }


def _hoje(itens, com_secao: bool) -> dict | None:
    """"Hoje" na linha (032 FR-009): quantas oportunidades há, com link, ou que não há. O link
    vai à seção do Início quando ela existe; se o único item é o encontro mostrado à parte, vai
    à página de Oportunidades, que lista todos."""
    if itens is None:
        return None
    if not itens:
        return {"texto": mensagens.HOJE_NENHUMA, "endereco": None}
    texto = mensagens.HOJE_UMA if len(itens) == 1 else mensagens.HOJE_VARIAS.format(n=len(itens))
    return {"texto": texto, "endereco": "#oportunidades" if com_secao else "/oportunidades/"}


def _adiante(quantas: int) -> dict:
    """"Adiante" na linha (032 FR-009): contribuições enviadas e ativas, ou o convite. Sem
    estados de atendimento (D-2601)."""
    if not quantas:
        return {"texto": m_contribuicao.INICIO_TITULO, "endereco": "/contribuir/"}
    texto = (m_contribuicao.ADIANTE_UMA if quantas == 1
             else m_contribuicao.ADIANTE_VARIAS.format(n=quantas))
    return {"texto": texto, "endereco": "/contribuicoes/"}


def montar_participacao(pessoa, com_trajetoria: bool | None = None, resumo=None) -> dict:
    """Os blocos de participação (032 FR-008, FR-011), no Início e em `/participacao/`:
    contribuição (026), e-mail (020, só convite: o Início não lê contato) e, por último, o
    convite da pesquisa (007; ADR 0009, decisão 8)."""
    if com_trajetoria is None:
        com_trajetoria = elegivel(pessoa)
    if com_trajetoria and resumo is None:
        resumo = resumo_da_pessoa(pessoa)
    return {
        "com_trajetoria": com_trajetoria,
        "contribuicao": resumo.ultima if com_trajetoria else None,
        "suas": com_trajetoria and resumo.existe,
        "titulo_convite": mensagens.TITULO_CONVITE,
        "convite": _convite(situacao_de_entrada(pessoa)),
    }


def montar_inicio(pessoa, referencia, demonstracao) -> dict:
    com_trajetoria = elegivel(pessoa)
    reconhecimento = (
        _reconhecimento(pessoa, referencia, demonstracao) if com_trajetoria else None
    )
    itens = _itens(pessoa, referencia) if com_trajetoria else None
    encontro = _encontro(itens)
    oportunidades = _oportunidades(itens, encontro)
    resumo = resumo_da_pessoa(pessoa) if com_trajetoria else None
    participacao = montar_participacao(pessoa, com_trajetoria, resumo)
    return {
        "titulo": mensagens.TITULO,
        "reconhecimento": reconhecimento,
        "sem_formacao": None if com_trajetoria else estados.SEM_FORMACAO,
        "proveniencia": mensagens.PROVENIENCIA if com_trajetoria else None,
        "titulo_acoes": mensagens.TITULO_ACOES,
        "acoes": _acoes(com_trajetoria, reconhecimento),
        "hoje": _hoje(itens, oportunidades is not None) if reconhecimento else None,
        "adiante": _adiante(resumo.enviadas) if reconhecimento else None,
        "encontro": encontro,
        "oportunidades": oportunidades,
        **participacao,
    }

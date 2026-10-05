"""Montagem da narrativa (Feature 021; research R5 a R7).

Função pura: mesma entrada, mesma narrativa (FR-011). Não lê banco, relógio nem log. Toda
frase vem do catálogo, preenchida só com valores presentes; nada é estimado (FR-021).
"""

from datetime import date

from trajetoria.narrativa import card, catalogo
from trajetoria.narrativa.contrato import (
    AGREGADO,
    DERIVADO,
    INSTITUCIONAL,
    METRICA_CURSO_UNIDADE_ANO,
    Compartilhavel,
    ContextoAgregado,
    ContextoCompartilhavel,
    ContextoSelecionado,
    Derivado,
    EntradaDaNarrativa,
    FatoDaFormacao,
    Formacao,
    FormacaoCompartilhavel,
    Frase,
    Relacao,
    Secao,
    TrajetoriaNarrativa,
)

MAXIMO_NO_CARD = 4
_SEPARADOR = " · "


def _anos_completos(desde: date, ate: date) -> int:
    return ate.year - desde.year - ((ate.month, ate.day) < (desde.month, desde.day))


def _data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _relacoes(fatos) -> list[Relacao | None]:
    """"Depois de" só entre anos conhecidos e distintos, e só quando o grupo de ano
    imediatamente anterior tem exatamente uma formação (R5)."""
    anos = sorted({f.ano_conclusao for f in fatos if f.ano_conclusao is not None})
    relacoes = []
    for f in fatos:
        anteriores = [a for a in anos if f.ano_conclusao is not None and a < f.ano_conclusao]
        grupo = (
            [i for i, g in enumerate(fatos) if g.ano_conclusao == anteriores[-1]]
            if anteriores
            else []
        )
        relacoes.append(Relacao("depois_de", grupo[0]) if len(grupo) == 1 else None)
    return relacoes


def _primeira(fatos) -> int | None:
    anos = [f.ano_conclusao for f in fatos if f.ano_conclusao is not None]
    if not anos:
        return None
    menores = [i for i, f in enumerate(fatos) if f.ano_conclusao == min(anos)]
    return menores[0] if len(menores) == 1 else None


def _frase_de_conclusao(f: FatoDaFormacao) -> str | None:
    if f.curso is None:
        return None
    if f.ano_conclusao is not None and f.unidade is not None:
        return catalogo.CONCLUIU_COMPLETO.format(
            ano=f.ano_conclusao, curso=f.curso, unidade=f.unidade
        )
    if f.ano_conclusao is not None:
        return catalogo.CONCLUIU_SEM_UNIDADE.format(ano=f.ano_conclusao, curso=f.curso)
    if f.unidade is not None:
        return catalogo.CONCLUIU_SEM_ANO.format(curso=f.curso, unidade=f.unidade)
    return catalogo.CONCLUIU_SO_CURSO.format(curso=f.curso)


def _atributos(f: FatoDaFormacao) -> str:
    """Atributos informados que a frase de conclusão não disse (sem curso, a unidade vai
    aqui)."""
    partes = (None if f.curso else f.unidade, f.nivel, f.modalidade, f.forma_oferta)
    return _SEPARADOR.join(p for p in partes if p)


def _tempo(f: FatoDaFormacao, referencia: date) -> int | None:
    if f.data_conclusao is None or f.data_conclusao > referencia:
        return None
    anos = _anos_completos(f.data_conclusao, referencia)
    return anos if anos >= 1 else None


def _inicio(fatos) -> int | None:
    """Formação de menor ano de ingresso, só se esse ano for único e houver curso (FR-050)."""
    anos = [f.ingresso_ano for f in fatos if f.ingresso_ano is not None]
    if not anos:
        return None
    menores = [i for i, f in enumerate(fatos) if f.ingresso_ano == min(anos)]
    if len(menores) != 1 or fatos[menores[0]].curso is None:
        return None
    return menores[0]


def _frase_de_agregado(a: ContextoSelecionado) -> str:
    if a.metrica == METRICA_CURSO_UNIDADE_ANO:
        return catalogo.plural(catalogo.AGREGADO_CURSO, a.valor).format(
            ano=a.ano, n=a.valor, curso=a.curso, unidade=a.unidade
        )
    return catalogo.plural(catalogo.AGREGADO_UNIDADE, a.valor).format(
        ano=a.ano, n=a.valor, unidade=a.unidade
    )


def _apuracoes(agregados) -> list[str]:
    datas = sorted({a.apurado_em for a in agregados})
    return [catalogo.APURACAO.format(apuracao=_data(d)) for d in datas]


def _secao(chave, frases) -> Secao | None:
    return Secao(chave, catalogo.TITULOS_DAS_SECOES[chave], tuple(frases)) if frases else None


def _compartilhavel(e: EntradaDaNarrativa) -> Compartilhavel:
    formacoes = []
    for f in e.formacoes[:MAXIMO_NO_CARD]:
        ano = f.ano_conclusao
        atributos = [a for a in (f.unidade, f.nivel, f.modalidade) if a]
        if ano is not None:
            atributos.append(str(ano))
        formacoes.append(
            FormacaoCompartilhavel(
                curso=f.curso,
                unidade=f.unidade,
                nivel=f.nivel,
                modalidade=f.modalidade,
                ano_conclusao=ano,
                linhas_curso=(
                    card.quebrar_linhas(f.curso, card.TAMANHO_CURSO, True) if f.curso else ()
                ),
                linhas_detalhe=card.quebrar_atributos(atributos, card.TAMANHO_TEXTO),
            )
        )
    # No máximo um par: o da primeira formação, na ordem de exibição, com agregado (FR-033).
    primeira = min((a.formacao for a in e.agregados), default=None)
    par = [a for a in e.agregados if a.formacao == primeira]
    textos = [_frase_de_agregado(a) for a in par] + _apuracoes(par)
    return Compartilhavel(
        formacoes=tuple(formacoes),
        formacoes_omitidas=max(0, len(e.formacoes) - MAXIMO_NO_CARD),
        formacoes_registradas=len(e.formacoes),
        contextos_agregados=tuple(
            ContextoCompartilhavel(t, card.quebrar_linhas(t, card.TAMANHO_TEXTO))
            for t in textos
        ),
        nome_disponivel=e.nome is not None,
    )


def montar(e: EntradaDaNarrativa) -> TrajetoriaNarrativa:
    fatos = e.formacoes
    relacoes = _relacoes(fatos)
    primeira = _primeira(fatos)
    inicio = _inicio(fatos)
    tempos = [_tempo(f, e.referencia) for f in fatos]
    n = len(fatos)

    registro = []
    if n:
        if e.nome:
            registro.append(
                Frase(catalogo.NOME_REGISTROS.format(nome=e.nome), INSTITUCIONAL)
            )
        registro.append(Frase(catalogo.plural(catalogo.REGISTRADAS, n).format(n=n), DERIVADO))

    trajetoria = []
    if inicio is not None:
        f = fatos[inicio]
        trajetoria.append(
            Frase(
                catalogo.INICIO.format(ano=f.ingresso_ano, curso=f.curso), INSTITUCIONAL
            )
        )
    for i, f in enumerate(fatos):
        conclusao = _frase_de_conclusao(f)
        if conclusao:
            trajetoria.append(Frase(conclusao, INSTITUCIONAL, i))
        elif f.ano_conclusao is not None:
            trajetoria.append(
                Frase(catalogo.CONCLUIDA_EM.format(ano=f.ano_conclusao), INSTITUCIONAL, i)
            )
        if atributos := _atributos(f):
            trajetoria.append(Frase(atributos, INSTITUCIONAL, i, "atributos"))
        if tempos[i] is not None:
            trajetoria.append(
                Frase(
                    catalogo.plural(catalogo.HA_ANOS, tempos[i]).format(n=tempos[i]),
                    DERIVADO,
                    i,
                )
            )

    outras = [
        Frase(catalogo.DEPOIS.format(curso=fatos[i].curso), DERIVADO, i)
        for i, r in enumerate(relacoes)
        if r is not None and fatos[i].curso is not None
    ]

    naquele_ano = [Frase(_frase_de_agregado(a), AGREGADO, a.formacao) for a in e.agregados]
    naquele_ano += [Frase(t, AGREGADO) for t in _apuracoes(e.agregados)]

    derivados = [Derivado("formacoes_registradas", n, "contagem das Conclusões Acadêmicas")]
    derivados += [
        Derivado("tempo_desde_conclusao", t, "anos completos entre a data de conclusão e a "
                 "data de referência", formacao=i)
        for i, t in enumerate(tempos)
        if t is not None
    ]
    if primeira is not None and n > 1:
        derivados.append(
            Derivado("primeira_formacao", primeira, "menor ano de conclusão, quando único")
        )

    secoes = tuple(
        s
        for s in (
            _secao("o_que_o_ifes_registra", registro),
            _secao("trajetoria_academica", trajetoria),
            _secao("outras_formacoes", outras),
            _secao("naquele_ano", naquele_ano),
        )
        if s is not None
    )
    return TrajetoriaNarrativa(
        referencia=e.referencia,
        nome=e.nome,
        formacoes=tuple(
            Formacao(
                curso=f.curso,
                unidade=f.unidade,
                nivel=f.nivel,
                modalidade=f.modalidade,
                forma_oferta=f.forma_oferta,
                ano_conclusao=f.ano_conclusao,
                data_conclusao=f.data_conclusao,
                relacao=relacoes[i],
                ingresso_ano=f.ingresso_ano,
                ingresso_data=f.ingresso_data,
            )
            for i, f in enumerate(fatos)
        ),
        derivados=tuple(derivados),
        contextos_agregados=tuple(
            ContextoAgregado(a.metrica, a.unidade, a.ano, a.valor, a.apurado_em, a.curso)
            for a in e.agregados
        ),
        secoes=secoes,
        compartilhavel=_compartilhavel(e),
    )

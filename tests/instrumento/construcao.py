"""Auxiliares dos testes do instrumento (não são testes)."""

from dataclasses import replace

import pytest

from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import ConteudoVersao, Escala
from trajetoria.instrumento.models import Versao
from trajetoria.instrumento.regras import OperacaoRejeitada


def rejeita(motivo, operacao, *args, **kwargs):
    """Executa a operação, exige rejeição só com `motivo` e devolve a Violação."""
    with pytest.raises(OperacaoRejeitada) as erro:
        operacao(*args, **kwargs)
    assert erro.value.motivos == (motivo,)
    return erro.value.violacoes[0]


def sem_identidades(conteudo: ConteudoVersao) -> ConteudoVersao:
    """A árvore com identidades, estado, publicação, origem e designação neutralizados,
    para comparar conteúdos de Versões diferentes. Referências viram a posição da Seção
    de destino."""
    posicao = {s.id: s.posicao for s in conteudo.secoes}

    def regra(r):
        return r and replace(r, destino_secao_id=posicao.get(r.destino_secao_id))

    secoes = tuple(
        replace(
            s,
            id=None,
            encaminhamento_id=posicao.get(s.encaminhamento_id),
            perguntas=tuple(
                replace(
                    p,
                    id=None,
                    opcoes=tuple(replace(o, id=None, regra=regra(o.regra)) for o in p.opcoes),
                )
                for p in s.perguntas
            ),
        )
        for s in conteudo.secoes
    )
    return replace(
        conteudo,
        id=None,
        estado=None,
        publicada_em=None,
        origem_id=None,
        designacao=None,
        secoes=secoes,
    )


def percursos_de_secoes(conteudo: ConteudoVersao) -> set[tuple[str, ...]]:
    """Percursos de Seções possíveis, pela semântica de destino de
    contracts/conteudo.md#percurso-de-seções. Cada percurso é uma tupla de rótulos (título
    da Seção ou "#posição") terminada em "FIM".

    O momento de aplicação da regra dentro da Seção está fora do escopo (FR-053); por isso
    uma Seção com mais de uma pergunta com regras é recusada, assim como destino que não
    seja posterior (proteção contra ciclo)."""
    secoes = conteudo.secoes
    indice = {s.id: i for i, s in enumerate(secoes)}

    def rotulo(secao):
        return secao.titulo or f"#{secao.posicao}"

    def padrao(i):
        secao = secoes[i]
        if secao.encaminhamento_id:
            return indice[secao.encaminhamento_id]
        return i + 1 if i + 1 < len(secoes) else None

    def destinos(i):
        secao = secoes[i]
        com_regras = [p for p in secao.perguntas if any(o.regra for o in p.opcoes)]
        if len(com_regras) > 1:
            raise ValueError(f"Seção {rotulo(secao)} tem mais de uma pergunta com regras")
        if not com_regras:
            return {padrao(i)}
        pergunta = com_regras[0]
        saidas = set()
        for opcao in pergunta.opcoes:
            if opcao.regra is None:
                saidas.add(padrao(i))
            elif opcao.regra.finaliza:
                saidas.add(None)
            else:
                saidas.add(indice[opcao.regra.destino_secao_id])
        if not pergunta.obrigatoria:
            saidas.add(padrao(i))  # pergunta opcional sem resposta
        return saidas

    def percorrer(i):
        for destino in destinos(i):
            if destino is not None and destino <= i:
                raise ValueError(f"destino não posterior a partir de {rotulo(secoes[i])}")
            if destino is None:
                yield (rotulo(secoes[i]), "FIM")
            else:
                for resto in percorrer(destino):
                    yield (rotulo(secoes[i]), *resto)

    return set(percorrer(0)) if secoes else {("FIM",)}


RAMOS = ("Integrado", "Concomitante", "Graduação", "Pós-graduação")


def versao_de_demonstracao() -> Versao:
    """Versão fictícia e reduzida, construída só pelas operações públicas, que cobre cada
    característica de "intenção" da tabela de cobertura da spec. Não é o Formulário 2024:
    representá-lo é a Feature 003."""
    pesquisa = op.criar_pesquisa("Pesquisa de demonstração")
    versao = op.criar_versao(pesquisa, "demonstração")
    op.alterar_versao(
        versao,
        titulo="Instrumento de demonstração",
        texto_abertura="Convite fictício para responder.",
        texto_encerramento="Fim do instrumento de demonstração.",
    )
    posicoes = iter(range(1, 100))

    def secao(titulo=None, texto=None):
        return op.adicionar_secao(versao, next(posicoes), titulo=titulo, texto=texto)

    def escolha(s, posicao, texto, opcoes, tipo="ESCOLHA_UNICA", obrigatoria=True, outro=None):
        pergunta = op.adicionar_pergunta(s, posicao, tipo, texto, obrigatoria=obrigatoria)
        criadas = {t: op.adicionar_opcao(pergunta, n, t) for n, t in enumerate(opcoes, 1)}
        if outro:
            criadas[outro] = op.adicionar_opcao(
                pergunta, len(opcoes) + 1, outro, complemento_textual=True
            )
        return pergunta, criadas

    termos = secao("Termos", "Termos fictícios de participação.")
    aceite, respostas = escolha(termos, 1, "Concorda com os termos?", ("Sim", "Não"))

    pessoais = secao("Pessoais")
    escolha(pessoais, 1, "Possui alguma condição X?", ("Sim", "Não"))
    escolaridade = ("Fundamental", "Médio", "Superior", "Não sei dizer")
    escolha(pessoais, 2, "Escolaridade do responsável A?", escolaridade)
    escolha(pessoais, 3, "Escolaridade do responsável B?", escolaridade)
    op.adicionar_pergunta(pessoais, 4, "TEXTO_CURTO", "Ano de referência?", obrigatoria=True,
                          texto_explicativo="Exemplo: 2020.")

    curso = secao("Curso")
    nivel, niveis = escolha(curso, 1, "Qual nível?", RAMOS)
    ramos = {}
    for ramo in RAMOS:
        ramos[ramo] = secao(ramo)
        escolha(ramos[ramo], 1, f"Qual curso de {ramo}?", ("Curso A", "Curso B"))

    avaliacao = secao("Avaliação")
    op.adicionar_pergunta(
        avaliacao, 1, "ESCALA", "Afirmação fictícia.", obrigatoria=False,
        escala=Escala(1, 5, "Discordo totalmente", "Concordo totalmente"),
    )
    escolha(avaliacao, 2, "Recebeu algum apoio?", ("Ensino", "Pesquisa", "Nenhum"),
            tipo="ESCOLHA_MULTIPLA", outro="Outro")
    trabalha, situacao = escolha(avaliacao, 3, "Atualmente trabalha?", ("Sim", "Não"))

    trabalho = secao("Trabalha")
    op.adicionar_pergunta(trabalho, 1, "TEXTO_CURTO", "Cargo?", obrigatoria=False)
    nao_trabalha = secao("Não trabalha")
    escolha(nao_trabalha, 1, "Por qual motivo?", ("Procurando", "Não procurando"), outro="Outro")
    impactos = secao()  # sem título
    op.adicionar_pergunta(
        impactos, 1, "ESCALA", "Outra afirmação.", obrigatoria=True, escala=Escala(1, 5)
    )

    op.definir_regra(aceite, respostas["Não"], op.FINALIZAR)
    for ramo in RAMOS:
        op.definir_regra(nivel, niveis[ramo], ramos[ramo])
        op.definir_encaminhamento(ramos[ramo], avaliacao)
    op.definir_regra(trabalha, situacao["Sim"], trabalho)
    op.definir_regra(trabalha, situacao["Não"], nao_trabalha)
    op.definir_encaminhamento(trabalho, impactos)
    return versao

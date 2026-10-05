"""Auxiliares dos testes da Feature 021 (não são testes). Somente dados fictícios.

`entradas_dos_cenarios()` reproduz, sem banco, as formações reconhecidas da fonte simulada
(001), para varrer a narrativa de todas as Pessoas fictícias.
"""

from dataclasses import dataclass
from datetime import date

from tests.interface import construcao_interface as ci
from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.narrativa.contrato import EntradaDaNarrativa, FatoDaFormacao

REFERENCIA = date(2026, 10, 4)
CAMPOS = ("curso", "unidade", "nivel", "modalidade", "forma_oferta", "ano_conclusao",
          "data_conclusao")


def fato(**atributos) -> FatoDaFormacao:
    return FatoDaFormacao(**atributos)


def entrada(formacoes, nome=None, agregados=(), referencia=REFERENCIA, demonstracao=True):
    return EntradaDaNarrativa(
        nome=nome,
        formacoes=tuple(formacoes),
        agregados=tuple(agregados),
        referencia=referencia,
        demonstracao=demonstracao,
    )


def _chave(registro):
    # Ordem do model (ano_conclusao, id): ano ausente por último, como no PostgreSQL.
    return (registro.ano_conclusao is None, registro.ano_conclusao or 0, registro.id_externo)


def entradas_dos_cenarios() -> dict[str, EntradaDaNarrativa]:
    """Uma entrada por Pessoa simulada com ao menos uma conclusão reconhecida."""
    entradas = {}
    for pessoa in cenarios.PESSOAS:
        registros = sorted(
            (
                r for r in cenarios.REGISTROS
                if r.id_pessoa == pessoa.id_externo and r.situacao == cenarios.CONCLUIDA
            ),
            key=_chave,
        )
        if registros:
            entradas[pessoa.id_externo] = entrada(
                [fato(**{campo: getattr(r, campo) for campo in CAMPOS}) for r in registros],
                nome=pessoa.nome,
            )
    return entradas


@dataclass
class CenarioNarrativa:
    inst: c.Instrumento
    campanha: object

    def pessoa(self, id_externo):
        return ce.pessoa_da_fonte(id_externo)

    def concluir(self, conclusao):
        """Participação iniciada, preenchida e concluída pelas operações da 005/006."""
        return ce.participacao_concluida(self.campanha, conclusao, self.inst)


def cenario_narrativa(*ids) -> CenarioNarrativa:
    inst = c.instrumento()
    campanha = c.campanha_aberta(inst.versao)
    padrao = ("SIM-P-0001", "SIM-P-0002", "SIM-P-0003", "SIM-P-0004", "SIM-P-0009")
    ce.incorporar(FonteSimulada(), *(ids or padrao))
    return CenarioNarrativa(inst, campanha)


def entrar(client, pessoa) -> None:
    ci.entrar_como(client, pessoa)


# --- Card montado à mão (Fase 3: antes da montagem existir) -------------------------------

UNIDADE_LONGA = "Cachoeiro de Itapemirim"
NOME_LONGO = "Maria Aparecida dos Santos Albuquerque de Oliveira Figueiredo"
CURSOS_LONGOS = (
    "Especialização em Práticas Pedagógicas para Professores da Educação Profissional",
    "Tecnologia em Análise e Desenvolvimento de Sistemas",
    "Mestrado Profissional em Educação Profissional e Tecnológica",
    "Especialização em Educação Profissional e Tecnológica Inclusiva",
)


def formacao_card(curso, unidade, nivel, modalidade, ano):
    from trajetoria.narrativa import card
    from trajetoria.narrativa.contrato import FormacaoCompartilhavel

    atributos = [a for a in (unidade, nivel, modalidade) if a]
    return FormacaoCompartilhavel(
        curso, unidade, nivel, modalidade, ano,
        card.quebrar_linhas(curso, card.TAMANHO_CURSO, True, card.LIMITE_ITEM) if curso else (),
        card.quebrar_atributos(atributos, card.TAMANHO_DETALHE, limite=card.LIMITE_ITEM),
    )


def destaque_card(numero, unidade, ano, por_curso=True):
    from trajetoria.narrativa import catalogo
    from trajetoria.narrativa.contrato import (
        METRICA_CURSO_UNIDADE_ANO,
        METRICA_UNIDADE_ANO,
        ContextoCompartilhavel,
    )

    par = catalogo.DESTAQUE_CURSO if por_curso else catalogo.DESTAQUE_UNIDADE
    return ContextoCompartilhavel(
        METRICA_CURSO_UNIDADE_ANO if por_curso else METRICA_UNIDADE_ANO,
        numero,
        tuple(linha.format(unidade=unidade, ano=ano) for linha in catalogo.plural(par, numero)),
    )


APURACAO = "Dados institucionais apurados em 31/01/2026."


def compartilhavel(formacoes, omitidas=0, agregados=(), nome_disponivel=True):
    from trajetoria.narrativa.contrato import Compartilhavel

    return Compartilhavel(
        formacoes=tuple(formacoes),
        formacoes_omitidas=omitidas,
        formacoes_registradas=len(formacoes) + omitidas,
        contextos_agregados=tuple(agregados),
        nome_disponivel=nome_disponivel,
        apuracao=APURACAO if agregados else None,
        unidade_da_imagem=formacoes[0].unidade if formacoes else None,
    )


def par_de_destaques(unidade, ano):
    return [destaque_card(27, unidade, ano), destaque_card(812, unidade, ano, por_curso=False)]


def pior_caso():
    """Nome longo, 4 cursos longos numa unidade longa, "e mais 3" e um par de destaques."""
    formacoes = [
        formacao_card(curso, UNIDADE_LONGA, "Pós-graduação", "A distância", 2012 + 3 * i)
        for i, curso in enumerate(CURSOS_LONGOS)
    ]
    return compartilhavel(formacoes, omitidas=3, agregados=par_de_destaques(UNIDADE_LONGA, 2012))


TADS_SERRA = (cenarios.TADS, "Serra", "Graduação", "Presencial", 2022)
ESPECIALIZACAO_CEFOR = (
    "Especialização em Informática na Educação", "Cefor", "Pós-graduação", "A distância", 2025,
)


def caso_maria():
    return compartilhavel(
        [formacao_card(*TADS_SERRA), formacao_card(*ESPECIALIZACAO_CEFOR)],
        agregados=par_de_destaques("Serra", 2022),
    )


def caso_ana():
    return compartilhavel([formacao_card(*TADS_SERRA)], agregados=par_de_destaques("Serra", 2022))


def caso_diego():
    return compartilhavel([
        formacao_card("Técnico em Química", "Vila Velha", "Técnico", "Presencial", 2012),
        formacao_card("Licenciatura em Química", "Vila Velha", "Graduação", "Presencial", 2017),
        formacao_card("Mestrado Profissional em Química", "Vila Velha", "Pós-graduação",
                      "Presencial", 2020),
    ])


def caso_quatro():
    return compartilhavel([
        formacao_card("Técnico em Informática", "Serra", "Técnico", "Presencial", 2014),
        formacao_card(*TADS_SERRA),
        formacao_card(*ESPECIALIZACAO_CEFOR),
        formacao_card("Mestrado Profissional em Educação Profissional e Tecnológica", "Vitória",
                      "Pós-graduação", "Presencial", 2026),
    ])


def caso_sem_imagem_propria():
    """Unidade sem entrada no catálogo de imagens: cai na genérica, com a legenda da
    unidade da formação."""
    return compartilhavel(
        [formacao_card("Engenharia de Controle e Automação", "Linhares", "Graduação",
                       "Presencial", 2019)],
        agregados=[destaque_card(41, "Linhares", 2019)],
    )


def caso_sem_unidade():
    return compartilhavel([formacao_card("Técnico em Mecânica", None, "Técnico", None, None)])

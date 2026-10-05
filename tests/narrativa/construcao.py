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

    atributos = [a for a in (unidade, nivel, modalidade, None if ano is None else str(ano)) if a]
    return FormacaoCompartilhavel(
        curso, unidade, nivel, modalidade, ano,
        card.quebrar_linhas(curso, card.TAMANHO_CURSO, True) if curso else (),
        card.quebrar_atributos(atributos, card.TAMANHO_TEXTO),
    )


def agregado_card(texto):
    from trajetoria.narrativa import card
    from trajetoria.narrativa.contrato import ContextoCompartilhavel

    return ContextoCompartilhavel(texto, card.quebrar_linhas(texto, card.TAMANHO_TEXTO))


def compartilhavel(formacoes, omitidas=0, agregados=(), nome_disponivel=True):
    from trajetoria.narrativa.contrato import Compartilhavel

    return Compartilhavel(
        formacoes=tuple(formacoes),
        formacoes_omitidas=omitidas,
        formacoes_registradas=len(formacoes) + omitidas,
        contextos_agregados=tuple(agregados),
        nome_disponivel=nome_disponivel,
    )


def pior_caso():
    """Nome longo, 4 cursos longos numa unidade longa, "e mais 3" e um par de agregados."""
    formacoes = [
        formacao_card(curso, UNIDADE_LONGA, "Pós-graduação", "A distância", 2012 + 3 * i)
        for i, curso in enumerate(CURSOS_LONGOS)
    ]
    agregados = [
        agregado_card(
            f"Em 2012, 27 conclusões de {CURSOS_LONGOS[0]} foram registradas na unidade "
            f"{UNIDADE_LONGA}, incluindo a sua."
        ),
        agregado_card(f"Em 2012, 812 conclusões foram registradas na unidade {UNIDADE_LONGA}."),
        agregado_card("Dados institucionais apurados em 31/01/2026."),
    ]
    return compartilhavel(formacoes, omitidas=3, agregados=agregados)


def caso_maria():
    return compartilhavel(
        [
            formacao_card(cenarios.TADS, "Serra", "Graduação", "Presencial", 2022),
            formacao_card(
                "Especialização em Informática na Educação", "Cefor", "Pós-graduação",
                "A distância", 2025,
            ),
        ],
        agregados=[
            agregado_card(
                f"Em 2022, 27 conclusões de {cenarios.TADS} foram registradas na unidade "
                "Serra, incluindo a sua."
            ),
            agregado_card("Em 2022, 812 conclusões foram registradas na unidade Serra."),
            agregado_card("Dados institucionais apurados em 31/01/2026."),
        ],
    )

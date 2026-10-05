"""Casos da matriz da 022 (não são testes). Reusam os cards montados à mão da 021."""

from tests.narrativa import construcao as cn


def caso_quatro_curtos():
    """Quatro formações de nome curto: o único jeito de o card exibir 4 nós (o caso
    `quatro` da 021 exibe 3 e "e mais 1")."""
    return cn.compartilhavel([
        cn.formacao_card("Técnico em Química", "Serra", "Técnico", None, 2010),
        cn.formacao_card("Química", "Serra", "Graduação", None, 2015),
        cn.formacao_card("Ensino de Química", "Serra", "Pós-graduação", None, 2018),
        cn.formacao_card("Mestrado em Química", "Serra", "Pós-graduação", None, 2022),
    ])


CASOS = {
    "maria": cn.caso_maria,
    "ana": cn.caso_ana,
    "diego": cn.caso_diego,
    "quatro": cn.caso_quatro,
    "quatro_curtos": caso_quatro_curtos,
    "pior": cn.pior_caso,
    "sem_imagem": cn.caso_sem_imagem_propria,
    "sem_unidade": cn.caso_sem_unidade,
}
NOME = "Maria Exemplo"
NOME_LONGO = "Maria Aparecida dos Santos Albuquerque de Oliveira"


def composicao(caso: str, nome: str | None = None, demonstracao: bool = True) -> dict:
    from trajetoria.narrativa.composicao import composicao_visual

    return composicao_visual(CASOS[caso](), nome, demonstracao)


def zona(composicao: dict, chave: str) -> dict | None:
    return next((z for z in composicao["zonas"] if z["chave"] == chave), None)

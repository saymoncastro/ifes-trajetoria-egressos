"""Oráculo dos testes da baseline do Formulário Egresso Ifes 2024 (não são testes).

O manifesto abaixo é transcrito da Matriz de Migração e das tabelas da spec da Feature
003, e não da declaração: é a expectativa independente exigida por FR-039. O inventário
é lido só como texto bruto, para verificar que um texto está documentado; nada é
extraído dele (research R10).
"""

import re
from pathlib import Path

import pytest
from django.db import transaction

from trajetoria.formulario_2024 import materializar
from trajetoria.instrumento.conteudo import ConteudoPergunta, ConteudoVersao, conteudo_da_versao

INVENTARIO = (
    Path(__file__).resolve().parents[2]
    / "docs/referencias/formulario-egresso-ifes-2024-inventario.md"
)


def normalizado(texto: str) -> str:
    """Espaços e quebras de linha colapsados (só para não depender da formatação)."""
    return " ".join(texto.split())


@pytest.fixture(scope="module")
def inventario_bruto() -> str:
    texto = INVENTARIO.read_text(encoding="utf-8")
    return normalizado(re.sub(r"(?m)^>\s?", "", texto))


@pytest.fixture(scope="module")
def baseline(django_db_setup, django_db_blocker) -> ConteudoVersao:
    """A baseline materializada uma vez por módulo, numa transação desfeita ao final.
    Devolve a árvore imutável; nada fica no banco."""
    with django_db_blocker.unblock(), transaction.atomic():
        conteudo = conteudo_da_versao(materializar().versao)
        transaction.set_rollback(True)
    return conteudo


def perguntas_por_chave(conteudo: ConteudoVersao) -> dict[str, ConteudoPergunta]:
    """A n-ésima Pergunta, na ordem (Seção, posição), corresponde a Qn (FR-009)."""
    perguntas = [p for s in conteudo.secoes for p in s.perguntas]
    return {f"Q{n}": p for n, p in enumerate(perguntas, 1)}


def secao_da_pergunta(conteudo: ConteudoVersao) -> dict[str, str]:
    """Qn → Sn."""
    resultado, n = {}, 0
    for i, secao in enumerate(conteudo.secoes, 1):
        for _ in secao.perguntas:
            n += 1
            resultado[f"Q{n}"] = f"S{i}"
    return resultado


def textos(conteudo: ConteudoVersao) -> list[str]:
    """Todos os textos não nulos da baseline."""
    resultado = [conteudo.titulo, conteudo.texto_abertura, conteudo.texto_encerramento]
    for secao in conteudo.secoes:
        resultado += [secao.titulo, secao.texto]
        for pergunta in secao.perguntas:
            resultado += [pergunta.texto, pergunta.texto_explicativo]
            if pergunta.escala:
                resultado += [pergunta.escala.rotulo_inicio, pergunta.escala.rotulo_fim]
            resultado += [opcao.texto for opcao in pergunta.opcoes]
    return [t for t in resultado if t is not None]


# --- Manifesto (transcrito da spec, não da declaração) -----------------------------------

EU, EM, TC, ESC = "ESCOLHA_UNICA", "ESCOLHA_MULTIPLA", "TEXTO_CURTO", "ESCALA"
SIM_NAO = ("Sim", "Não")

# "Seções da baseline": (chave, título, tem texto introdutório, quantidade de Perguntas).
SECOES_ESPERADAS = (
    ("S1", "Termos e condições", True, 1),
    ("S2", "Informações Pessoais", False, 8),
    ("S3", "Informações do curso", False, 5),
    ("S4", "Ensino Médio/Técnico Integrado", False, 1),
    ("S5", "Técnico Concomitante / Subsequente /EJA - PROEJA", False, 2),
    ("S6", "Graduação", False, 1),
    ("S7", "Pós-Graduação", False, 1),  # E-05: sem a nota interna
    ("S8", "Avaliação", False, 14),
    ("S9", "Egresso que trabalha", False, 11),
    ("S10", "Egresso que não trabalha", False, 1),
    ("S11", "Estudo", False, 3),
    ("S12", "Egresso que estuda", False, 3),
    ("S13", None, False, 3),
)

# Matriz de Migração: Qn → (Seção, posição, tipo, obrigatória, trecho distintivo do texto,
# Opções em ordem | nome da lista extensa | ()). O trecho não é o texto inteiro: o texto
# completo é conferido contra o inventário (C1).
ESPERADO = {
    "Q1": ("S1", 1, EU, True, "concorda com os termos", SIM_NAO),
    "Q2": ("S2", 1, EU, True, "sexo/identidade de gênero", (
        "Masculino", "Feminino", "Mulher trans/travesti", "Homem trans",
        "Pessoa não binária", "Prefiro não responder")),
    "Q3": ("S2", 2, TC, True, "Quantos anos", ()),
    "Q4": ("S2", 3, EU, True, "se autodeclara", (
        "Branco(a)", "Preto(a)", "Pardo(a)", "Amarelo(a)", "Indígena")),
    "Q5": ("S2", 4, EU, True, "Você é PcD", SIM_NAO),
    "Q6": ("S2", 5, EU, False, "qual a deficiência", (
        "Deficiência física", "Deficiência visual", "Deficiência intelectual",
        "Deficiência auditiva")),
    "Q7": ("S2", 6, EU, True, "estado civil", (
        "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Separado(a)", "Viúvo(a)")),
    "Q8": ("S2", 7, EU, True, "escolaridade do seu pai", "LISTA_E"),
    "Q9": ("S2", 8, EU, True, "escolaridade da sua mãe", "LISTA_E"),
    "Q10": ("S3", 1, TC, True, "Em que ano você concluiu", ()),
    "Q11": ("S3", 2, EU, True, "Em qual campus", "LISTA_C"),
    "Q12": ("S3", 3, EU, True, "qual modalidade", ("Presencial", "À distância")),
    "Q13": ("S3", 4, EU, True, "foi admitido(a)", (
        "Cotista (vagas de cotas, ações afirmativas)",
        "Não cotista (vagas de ampla concorrência)",
        "Outros: transferência, remoção, reopção, reingresso, novo curso, etc.")),
    "Q14": ("S3", 5, EU, True, "questionário que pretende preencher", (
        "Ensino Médio/Técnico Integrado", "Técnico Concomitante/Subsequente/EJA-PROEJA",
        "Graduação", "Pós-Graduação")),
    "Q15": ("S4", 1, EU, True, "de qual Curso?", "LISTA_15"),
    "Q16": ("S5", 1, EU, True, "qual forma de oferta", (
        "Concomitante", "Subsequente", "EJA-PROEJA")),
    "Q17": ("S5", 2, EU, True, "de qual Curso?", "LISTA_17"),
    "Q18": ("S6", 1, EU, True, "de qual Curso?", "LISTA_18"),
    "Q19": ("S7", 1, EU, True, "de qual Curso?", "LISTA_19"),
    "Q20": ("S8", 1, ESC, True, "gosto por cultura", ()),
    "Q21": ("S8", 2, ESC, True, "acesso à cultura", ()),
    "Q22": ("S8", 3, EU, True, "ações de extensão", SIM_NAO),
    "Q23": ("S8", 4, EU, True, "monitor(a) de disciplinas", SIM_NAO),
    "Q24": ("S8", 5, EU, True, "algum tipo de estágio", SIM_NAO),
    "Q25": ("S8", 6, EU, True, "atividades acadêmicas (seminários", SIM_NAO),
    "Q26": ("S8", 7, EM, True, "tipo de publicação", (
        "Artigos técnico científicos", "Anais de Congresso", "Livro", "Capítulos de livro",
        "Não houve", "Outro:")),
    "Q27": ("S8", 8, EU, True, "intercâmbio no exterior", SIM_NAO),
    "Q28": ("S8", 9, EU, True, "grupos de pesquisas e de estudos", SIM_NAO),
    "Q29": ("S8", 10, EU, True, "mantém algum vínculo", SIM_NAO),
    "Q30": ("S8", 11, EU, True, "empresa júnior", SIM_NAO),
    "Q31": ("S8", 12, EU, True, "iniciação científica", SIM_NAO),
    "Q32": ("S8", 13, EM, True, "algum tipo de bolsa", (
        "Ensino", "Pesquisa", "Extensão", "Não recebi", "Outro:")),
    "Q33": ("S8", 14, EU, True, "Atualmente você trabalha?", SIM_NAO),
    "Q34": ("S9", 1, EU, True, "trabalha no setor", (
        "Misto", "Público", "Privado", "Terceiro setor (cooperativas/sindicatos)",
        "Trabalho em mais de um setor")),
    "Q35": ("S9", 2, EU, True, "cargo/emprego exige", (
        "Nenhum nível de instrução", "Ensino fundamental", "Ensino médio/técnico",
        "Graduação", "Pós-graduação", "Não sei dizer")),
    "Q36": ("S9", 3, ESC, True, "na minha área de formação", ()),
    "Q37": ("S9", 4, EU, True, "cargo de chefia", SIM_NAO),
    "Q38": ("S9", 5, EU, True, "remuneração bruta mensal", (
        "Até 1 salário mínimo", "De 1 até 2,5 salários mínimos",
        "De 2,5 até 5,5 salários mínimos", "De 5,5 até 10 salários mínimos",
        "Acima de 10 salários mínimos")),
    "Q39": ("S9", 6, EU, True, "A organização na qual você trabalha", (
        "Micro empresa/organização (até 19 colaboradores)",
        "Pequena empresa/organização (de 20 a 99 colaboradores)",
        "Média empresa/organização (de 100 a 499 colaboradores)",
        "Grande empresa/organização (acima de 500 colaboradores)",
        "Não sei dizer")),
    "Q40": ("S9", 7, EU, True, "Você trabalha atualmente:", (
        "Na mesma cidade do campus do Ifes onde fiz o curso",
        "Em outra cidade, mas na mesma região do campus do Ifes onde fiz o curso",
        "Em outra cidade e em outra região do campus do Ifes onde fiz o curso, mas ainda no"
        " estado do Espírito Santo",
        "Em outro estado brasileiro",
        "Em outro país")),
    "Q41": ("S9", 8, EU, True, "oferta de vagas", (
        "Não existem vagas de trabalho", "Existem poucas vagas de trabalho",
        "Existem muitas vagas de trabalho", "Não sei dizer")),
    "Q42": ("S9", 9, ESC, False, "realização de curso no Ifes", ()),
    "Q43": ("S9", 10, ESC, True, "experiência profissional anterior", ()),
    "Q44": ("S9", 11, ESC, False, "redes de contato", ()),
    "Q45": ("S10", 1, EU, True, "não está trabalhando", (
        "Não encontrei vaga de trabalho, mas estou à procura",
        "Não estou à procura de vaga de trabalho no momento",
        "Outro:")),
    "Q46": ("S11", 1, EU, True, "Atualmente você estuda?", SIM_NAO),
    "Q47": ("S11", 2, EM, True, "Após o curso, você:", (
        "Não estudei mais", "Fiz cursos livres", "Fiz curso técnico",
        "Fiz curso de graduação", "Fiz especialização lato sensu", "Fiz mestrado",
        "Fiz doutorado", "Fiz pós-doutorado")),
    "Q48": ("S11", 3, ESC, False, "O curso que realizei", ()),
    "Q49": ("S12", 1, EU, True, "categoria de estudante", (
        "Sou estudante de curso técnico", "Sou estudante de curso de graduação",
        "Sou estudante de curso de especialização lato sensu", "Sou estudante de mestrado",
        "Sou estudante de doutorado", "Sou estudante de pós-doutorado")),
    "Q50": ("S12", 2, ESC, True, "O curso que estou realizando", ()),
    "Q51": ("S12", 3, EU, True, "instituição na qual você está cursando", (
        "Ifes", "Outra Instituição Pública", "Instituição Privada")),
    "Q52": ("S13", 1, ESC, True, "mudou a minha vida", ()),
    "Q53": ("S13", 2, ESC, True, "situação econômica", ()),
    "Q54": ("S13", 3, ESC, True, "exemplo e inspiração", ()),
}

# Listas extensas: quantidade, primeiro e último item. A sequência completa é conferida
# por ocorrência literal no texto bruto do inventário.
LISTAS = {
    "LISTA_C": (23, "Alegre", "Vitória"),
    "LISTA_E": (17, "Sem instrução", "Não se aplica"),
    "LISTA_15": (33, "Fiz apenas o Ensino Médio", "Técnico em Zootecnia"),
    "LISTA_17": (47, "Técnico em Administração", "Técnico em Treinamento e Instrução de Cães-Guia"),
    "LISTA_18": (
        50,
        "EaD - Complementação Pedagógica: Matemática, Física, Biologia e Química",
        "Tecnologia em Sistemas para Internet",
    ),
    "LISTA_19": (
        77,
        "Aperfeiçoamento em Educação para o Trânsito",
        "Mestrado Profissional em Tecnologias Sustentáveis",
    ),
}

# "Contagens verificáveis".
CONTAGENS = {
    "secoes": 13,
    "perguntas": 54,
    EU: 38,
    EM: 3,
    TC: 2,
    ESC: 11,
    "obrigatorias": 50,
    "opcionais": 4,
    "perguntas_com_opcoes": 41,
    "opcoes": 385,
    "opcoes_com_complemento": 3,
    "perguntas_com_texto_explicativo": 3,
    "secoes_com_texto": 1,
    "secoes_sem_titulo": 1,
}

TEXTOS_EXPLICATIVOS = {
    "Q10": "Exemplo: 2020, 2021, 2022, etc.",
    "Q32": "Obs: Não considerar auxilio estudantil como bolsa.",
    "Q48": "Caso não tenha estudado mais deixe essa resposta em branco.",
}

# Tabela "Escalas": rótulo final; o inicial é ausente em todas (DP-301).
ROTULOS_FINAIS = {
    **dict.fromkeys(
        ("Q20", "Q21", "Q36", "Q42", "Q43", "Q44", "Q50", "Q52", "Q53", "Q54"),
        "Concordo totalmente",
    ),
    "Q48": "concordo totalmente",
}

# "Navegação da baseline": (Qn, texto da Opção) → Sn | "FINALIZAR". Q51 não tem regra (E-07).
REGRAS = {
    ("Q1", "Sim"): "S2",
    ("Q1", "Não"): "FINALIZAR",
    ("Q14", "Ensino Médio/Técnico Integrado"): "S4",
    ("Q14", "Técnico Concomitante/Subsequente/EJA-PROEJA"): "S5",
    ("Q14", "Graduação"): "S6",
    ("Q14", "Pós-Graduação"): "S7",
    ("Q33", "Sim"): "S9",
    ("Q33", "Não"): "S10",
    ("Q46", "Sim"): "S12",
    ("Q46", "Não"): "S13",
}

ENCAMINHAMENTOS = {
    "S4": "S8",
    "S5": "S8",
    "S6": "S8",
    "S7": "S8",
    "S9": "S11",
    "S10": "S11",
    "S12": "S13",
}

# "Percursos esperados", no formato de `percursos_de_secoes` (título da Seção ou "#13").
_RAMOS_DE_CURSO = (
    "Ensino Médio/Técnico Integrado",
    "Técnico Concomitante / Subsequente /EJA - PROEJA",
    "Graduação",
    "Pós-Graduação",
)
_RAMOS_DE_TRABALHO = ("Egresso que trabalha", "Egresso que não trabalha")
_RAMOS_DE_ESTUDO = (("Egresso que estuda",), ())
PERCURSOS = (
    ("Termos e condições", "FIM"),
    *(
        ("Termos e condições", "Informações Pessoais", "Informações do curso", curso,
         "Avaliação", trabalho, "Estudo", *estudo, "#13", "FIM")
        for curso in _RAMOS_DE_CURSO
        for trabalho in _RAMOS_DE_TRABALHO
        for estudo in _RAMOS_DE_ESTUDO
    ),
)

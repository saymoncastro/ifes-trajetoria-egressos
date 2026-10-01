"""Declaração da baseline do Formulário Egresso Ifes 2024 (specs/003, data-model.md).

Única fonte executável da baseline. O conteúdo é transcrito à mão do inventário
(docs/referencias/formulario-egresso-ifes-2024-inventario.md) conforme a Matriz de
Migração da spec. As chaves `S1`…`S13` e `Q1`…`Q54` existem só aqui e nos testes, para
rastreabilidade; nunca são persistidas (FR-012).

Sem validação própria: a coerência é verificada pelos testes e pelas operações da 002.
"""

from dataclasses import dataclass

from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.instrumento.operacoes import FINALIZAR, Finalizar

__all__ = [
    "DESIGNACAO",
    "FINALIZAR",
    "NOME_PESQUISA",
    "SECOES",
    "TEXTO_ABERTURA",
    "TEXTO_ENCERRAMENTO",
    "TEXTO_TERMOS",
    "TITULO",
    "PerguntaDeclarada",
    "SecaoDeclarada",
]


@dataclass(frozen=True)
class PerguntaDeclarada:
    chave: str
    tipo: TipoPergunta
    texto: str
    obrigatoria: bool
    texto_explicativo: str | None = None
    opcoes: tuple[str, ...] = ()
    complemento: str | None = None  # texto da Opção que admite complemento textual
    escala: Escala | None = None
    regras: tuple[tuple[str, str | Finalizar], ...] = ()  # (texto da Opção, chave da Seção)


@dataclass(frozen=True)
class SecaoDeclarada:
    chave: str
    titulo: str | None
    texto: str | None
    perguntas: tuple[PerguntaDeclarada, ...]
    encaminhamento: str | None = None  # chave da Seção


NOME_PESQUISA = "Pesquisa Institucional de Egressos"
DESIGNACAO = "Formulário Egresso Ifes 2024 — referência migrada"

# --- Textos da Versão e dos termos (inventário, "Seção 1") ------------------------------

TITULO = "Egresso Ifes"

TEXTO_ABERTURA = "\n\n".join((
    "Prezado(a) egresso(a) do Ifes,",
    "É com muita satisfação que nós, do Instituto Federal do Espírito Santo (Ifes), nos "
    "dirigimos a você para convidá-lo(a) a participar da Pesquisa com Egressos(as). Nesta "
    "pesquisa, desejamos conhecer quais as oportunidades que o Ifes proporcionou para a sua "
    "vida pessoal e profissional.",
    "A sua participação na pesquisa é muito importante e contribuirá para compreendermos "
    "como a educação oferecida pelo Ifes colaborou no processo de sua formação "
    "profissional, de sua inserção no mundo do trabalho e na melhoria de vida. Basta que "
    "você responda a este questionário!",
    "Se você tiver alguma dúvida sobre esta pesquisa ou sobre sua participação, por favor, "
    "entre em contato pelo e-mail: egressos@ifes.edu.br ou pelo telefone (27) 99527-0027.",
))

TEXTO_TERMOS = "\n\n".join((
    "Para participar deste estudo, você não terá nenhum custo, nem receberá qualquer "
    "vantagem financeira e tem garantida plena liberdade de recusar-se a participar ou "
    "retirar seu consentimento, sem necessidade de comunicado prévio. A sua participação é "
    "voluntária e a recusa em participar não acarretará qualquer penalidade ou modificação "
    "na forma em que será atendido(a) pelo Ifes. Você não será identificado(a) em nenhuma "
    "publicação que possa resultar desta pesquisa.",
    "O Ifes tratará a sua identidade com padrões de sigilo e confidencialidade, atendendo à "
    "legislação brasileira, em especial, à Resolução 466/2012 do Conselho Nacional de "
    "Saúde, e utilizará as informações somente para fins de gestão educacional, além dos "
    "acadêmicos e científicos.",
))

# Seção 14 do original: não é Seção, é o encerramento da Versão (E-04).
TEXTO_ENCERRAMENTO = "\n\n".join((
    "Este formulário chegou ao fim!",
    "Agradecemos imensamente a atenção dispensada e a participação na pesquisa.",
))

# --- Listas extensas (um item por linha, na ordem do inventário) -------------------------

# Inventário, Lista C — campus (Q11), 23 opções.
LISTA_C = (
    "Alegre",
    "Aracruz",
    "Barra de São Francisco",
    "Cachoeiro de Itapemirim",
    "Cariacica",
    "Cefor",
    "Centro-Serrano",
    "Colatina",
    "Guarapari",
    "Ibatiba",
    "Itapina",
    "Linhares",
    "Montanha",
    "Nova Venécia",
    "Piúma",
    "Presidente Kennedy",
    "Santa Teresa",
    "São Mateus",
    "Serra",
    "Venda Nova do Imigrante",
    "Viana",
    "Vila Velha",
    "Vitória",
)

# Inventário, Lista E — escolaridade (Q8 e Q9), 17 opções.
LISTA_E = (
    "Sem instrução",
    "Ensino fundamental incompleto",
    "Ensino fundamental completo",
    "Ensino médio incompleto",
    "Ensino médio completo",
    "Ensino superior incompleto",
    "Ensino superior completo",
    "Especialização incompleta",
    "Especialização completa",
    "Mestrado incompleto",
    "Mestrado completo",
    "Doutorado incompleto",
    "Doutorado completo",
    "Pós-doutorado incompleto",
    "Pós-doutorado completo",
    "Não sei dizer",
    "Não se aplica",
)

# Inventário, Lista 15 — Ensino Médio/Técnico Integrado (Q15), 33 opções.
LISTA_15 = (
    "Fiz apenas o Ensino Médio",
    "Técnico em Administração",
    "Técnico em Agricultura",
    "Técnico em Agroindústria",
    "Técnico em Agropecuária",
    "Técnico em Alimentação Escolar",
    "Técnico em Alimentos",
    "Técnico em Aquicultura",
    "Técnico em Automação Industrial",
    "Técnico em Biotecnologia",
    "Técnico em Edificações",
    "Técnico em Eletromecânica",
    "Técnico em Eletrotécnica",
    "Técnico em Estradas",
    "Técnico em Florestas",
    "Técnico em Guia de Turismo",
    "Técnico em Hospedagem",
    "Técnico em Informática",
    "Técnico em Informática para Internet",
    "Técnico em Infraestrutura Escolar",
    "Técnico em Internet das Coisas",
    "Técnico em Logística",
    "Técnico em Manutenção de Sistemas Metroferroviários",
    "Técnico em Mecânica",
    "Técnico em Meio Ambiente",
    "Técnico em Metalurgia",
    "Técnico em Mineração",
    "Técnico em Pesca",
    "Técnico em Portos",
    "Técnico em Química",
    "Técnico em Secretaria Escolar",
    "Técnico em Segurança do Trabalho",
    "Técnico em Zootecnia",
)

# Inventário, Lista 17 — Técnico Concomitante/Subsequente/EJA-PROEJA (Q17), 47 opções.
LISTA_17 = (
    "Técnico em Administração",
    "Técnico em Agricultura",
    "Técnico em Agrimensura",
    "Técnico em Agroindústria",
    "Técnico em Agropecuária",
    "Técnico em Alimentação Escolar",
    "Técnico em Automação Industrial",
    "Técnico em Biotecnologia",
    "Técnico em Cadista para a Construção Civil",
    "Técnico em Cafeicultura",
    "Técnico em Comércio",
    "Técnico em Comércio Exterior",
    "Técnico em Controle Ambiental",
    "Técnico em Desenvolvimento de Sistemas Web com Metodologias Ágeis",
    "Técnico em Edificações",
    "Técnico em Eletricista Instalador Predial de Baixa Tensão",
    "Técnico em Eletromecânica",
    "Técnico em Eletrotécnica",
    "Técnico em Estradas",
    "Técnico em Eventos",
    "Técnico em Florestas",
    "Técnico em Gastronomia",
    "Técnico em Geoprocessamento",
    "Técnico em Gestão da Qualidade em Serviço",
    "Técnico em Gestão e Inovação de Processos Químicos e Biotecnológicos",
    "Técnico em Guia de Turismo",
    "Técnico em Hospedagem",
    "Técnico em Informática",
    "Técnico em Infraestrutura Escolar",
    "Técnico em Logística",
    "Técnico em Manutenção e Suporte em Informática",
    "Técnico em Mecânica",
    "Técnico em Meio Ambiente",
    "Técnico em Metalurgia",
    "Técnico em Mineração",
    "Técnico em Multimeios Didáticos",
    "Técnico em Operadores de Instrumentos Topográficos",
    "Técnico em Petroquímica",
    "Técnico em Portos",
    "Técnico em Processamento de Pescado",
    "Técnico em Química",
    "Técnico em Redes de Computadores",
    "Técnico em Saneamento",
    "Técnico em Secretaria Escolar",
    "Técnico em Segurança do Trabalho",
    "Técnico em Sustentabilidade Ambiental e Inovação",
    "Técnico em Treinamento e Instrução de Cães-Guia",
)

# Inventário, Lista 18 — Graduação (Q18), 50 opções.
LISTA_18 = (
    "EaD - Complementação Pedagógica: Matemática, Física, Biologia e Química",
    "EaD - Letras Inglês - Segunda Licenciatura",
    "EaD - Licenciatura em Informática",
    "EaD - Licenciatura em Letras - Português",
    "EaD - Licenciatura em Pedagogia",
    "EaD - Tecnologia em Gestão Pública",
    "EaD - Tecnologia em Sistemas para Internet",
    "Bacharelado em Administração",
    "Bacharelado em Agronomia",
    "Bacharelado em Arquitetura e Urbanismo",
    "Bacharelado em Biomedicina",
    "Bacharelado em Ciências Biológicas",
    "Bacharelado em Ciência da Computação",
    "Bacharelado em Ciências Econômicas",
    "Bacharelado em Ciência e Tecnologia de Alimentos",
    "Bacharelado em Engenharia Ambiental",
    "Bacharelado em Engenharia Civil",
    "Bacharelado em Engenharia de Aquicultura",
    "Bacharelado em Engenharia de Controle e Automação",
    "Bacharelado em Engenharia de Minas",
    "Bacharelado em Engenharia de Pesca",
    "Bacharelado em Engenharia de Produção",
    "Bacharelado em Engenharia Elétrica",
    "Bacharelado em Engenharia Mecânica",
    "Bacharelado em Engenharia Metalúrgica",
    "Bacharelado em Engenharia Química",
    "Bacharelado em Engenharia Sanitária e Ambiental",
    "Bacharelado em Física",
    "Bacharelado em Geologia",
    "Bacharelado em Química Industrial",
    "Bacharelado em Sistemas de Informação",
    "Bacharelado em Zootecnia",
    "Licenciatura em Ciências Agrícolas",
    "Licenciatura em Ciências Biológicas",
    "Licenciatura em Ciências da Natureza",
    "Licenciatura em Física",
    "Licenciatura em Geografia",
    "Licenciatura em História",
    "Licenciatura em Letras - Português",
    "Licenciatura em Letras - Português/Inglês",
    "Licenciatura em Matemática",
    "Licenciatura em Pedagogia",
    "Licenciatura em Química",
    "Tecnologia em Análise e Desenvolvimento de Sistemas",
    "Tecnologia em Cafeicultura",
    "Tecnologia em Gestão Ambiental",
    "Tecnologia em Logística",
    "Tecnologia em Redes de Computadores",
    "Tecnologia em Saneamento Ambiental",
    "Tecnologia em Sistemas para Internet",
)

# Inventário, Lista 19 — Pós-Graduação (Q19), 77 opções.
LISTA_19 = (
    "Aperfeiçoamento em Educação para o Trânsito",
    "Aperfeiçoamento em Estruturas de Aço",
    "Doutorado em Educação em Ciências e Matemática",
    "EaD - Aperfeiçoamento em Aspectos Técnicos da Mineração de Rochas Ornamentais",
    "EaD - Aperfeiçoamento em Design Educacional",
    "EaD - Aperfeiçoamento em Educação Especial Inclusiva",
    "EaD - Aperfeiçoamento em Formação Docente para Educação a Distância",
    "EaD - Aperfeiçoamento em Gestão Aplicada à Política",
    "EaD - Aperfeiçoamento em Internet das Coisas",
    "EaD - Aperfeiçoamento em Mentoria para a Educação Profissional e Tecnológica",
    "EaD - Aperfeiçoamento em Tecnologias Digitais Aplicadas à Educação",
    "EaD - Especialização em Agroecologia e Sustentabilidade",
    "EaD - Especialização em Ciências Policiais",
    "EaD - Especialização em Controle de Qualidade e Segurança de Alimentos",
    "EaD - Especialização em Docência para a Educação Profissional e Tecnológica (DocentEPT)",
    "EaD - Especialização em Educação a Distância",
    "EaD - Especialização em Educação em Humanidades",
    "EaD - Especialização em Educação Especial Inclusiva",
    "EaD - Especialização em Ensino Interdisciplinar em Saúde e Meio Ambiente",
    "EaD - Especialização em Gestão da Inovação",
    "EaD - Especialização em Gestão Escolar para profissionais da Educação",
    "EaD - Especialização em Informática na Educação",
    "EaD - Especialização em Práticas Pedagógicas",
    "EaD - Lato Sensu em Educação: Metodologias e Práticas para o Ensino Fundamental",
    "EaD - Lato Sensu em Finanças Corporativas",
    "EaD - Lato Sensu em Práticas Pedagógicas para Educação Profissional e Tecnológica",
    "Especialização em Agroecologia e Sustentabilidade",
    "Especialização em Currículo e Ensino na Educação Básica",
    "Especialização em Docência nos Anos Iniciais do Ensino Fundamental: Língua Portuguesa e "
    "Matemática",
    "Especialização em Educação e Divulgação em Ciências",
    "Especialização em Educação Profissional e Tecnológica",
    "Especialização em Eficiência Energética",
    "Especialização em Energias Renováveis e Eficiência Energética",
    "Especialização em Engenharia de Infraestrutura Urbana",
    "Especialização em Engenharia Elétrica com ênfase em Sistemas Inteligentes Aplicados à "
    "Automação",
    "Especialização em Engenharia Ferroviária com ênfase em Via Permanente",
    "Especialização em Ensino de Ciências Naturais com ênfase em Física ou Química",
    "Especialização em Georreferenciamento de Imóveis Rurais e Urbanos",
    "Especialização em Gestão Pública",
    "Especialização em Informática na Educação",
    "Especialização em Meio Ambiente",
    "Especialização em Prática Pedagógicas para Professores",
    "Especialização em Recursos Hídricos",
    "Especialização no Ensino de Ciências, Saúde e Ambiente",
    "Lato Sensu em Administração/Gestão Pública",
    "Lato Sensu em Agricultura Sustentável",
    "Lato Sensu em Análise e Gestão Ambiental",
    "Lato Sensu em Conectividade e Tecnologias da Informação",
    "Lato Sensu em Desenvolvimento de Aplicações Inteligentes",
    "Lato Sensu em Educação Ambiental e Sustentabilidade",
    "Lato Sensu em Educação Profissional e Tecnologia",
    "Lato Sensu em Eficiência Energética Industrial",
    "Lato Sensu em Engenharia de Produção com ênfase em Ciência de Dados",
    "Lato Sensu em Engenharia de Produção com ênfase em Tecnologias da Decisão",
    "Lato Sensu em Ensino de Ciências da Natureza",
    "Lato Sensu em Gestão Ambiental",
    "Lato Sensu em Gestão Empresarial",
    "Lato Sensu em Geoprocessamento",
    "Lato Sensu em Mineração de Dados Educacionais",
    "Lato Sensu em Pedagogia da Alternância",
    "Lato Sensu em Práticas Educacionais",
    "Lato Sensu em Práticas Pedagógicas",
    "Lato Sensu em Tecnologias de Produção de Rochas Ornamentais",
    "Mestrado em Agroecologia",
    "Mestrado em Computação Aplicada",
    "Mestrado em Educação em Ciências e Matemática",
    "Mestrado em Engenharia Ambiental",
    "Mestrado em Engenharia de Controle e Automação",
    "Mestrado em Engenharia Elétrica",
    "Mestrado em Engenharia Metalúrgica e de Materiais",
    "Mestrado Nacional Profissional em Ensino de Física",
    "Mestrado Profissional em Educação Profissional e Tecnológica (ProfEPT)",
    "Mestrado Profissional em Ensino de Humanidades",
    "Mestrado Profissional em Letras em Rede Nacional",
    "Mestrado Profissional em Propriedade Intelectual e Transferência de Tecnologia para Inovação",
    "Mestrado Profissional em Química",
    "Mestrado Profissional em Tecnologias Sustentáveis",
)

# LISTA_19 não ganha nenhum curso: a nota interna da Seção 7 não é executada (E-05, DP-310).

# --- Seções e Perguntas (Matriz de Migração Q1–Q54) --------------------------------------

EU = TipoPergunta.ESCOLHA_UNICA
EM = TipoPergunta.ESCOLHA_MULTIPLA
TC = TipoPergunta.TEXTO_CURTO
ESC = TipoPergunta.ESCALA

SIM_NAO = ("Sim", "Não")
OUTRO = "Outro:"  # texto transcrito; o complemento textual é a caixa de texto (E-15)

# E-09: o rótulo inicial aparece truncado ("Disc…") na fonte e não é inventado (DP-301).
CONCORDANCIA = Escala(1, 5, None, "Concordo totalmente")
# E-10: Q48 tem o rótulo em minúsculas no original; preservado.
CONCORDANCIA_MINUSCULA = Escala(1, 5, None, "concordo totalmente")
# E-08: o original grafa "Corcordo totalmente" em Q52–Q54; correção editorial aprovada
# (FR-021). É a única correção de texto da migração.
CONCORDANCIA_CORRIGIDA = Escala(1, 5, None, "Concordo totalmente")


def _afirmacao(afirmacao: str) -> str:
    return f'Indique o seu grau de concordância com a afirmação "{afirmacao}"'


S1 = SecaoDeclarada("S1", "Termos e condições", TEXTO_TERMOS, perguntas=(
    # Q1 representa o termo vigente; não é consentimento rastreável (002/DP-007).
    PerguntaDeclarada(
        "Q1", EU, "Você concorda com os termos acima?", True, opcoes=SIM_NAO,
        regras=(("Sim", "S2"), ("Não", FINALIZAR)),
    ),
))

S2 = SecaoDeclarada("S2", "Informações Pessoais", None, perguntas=(
    PerguntaDeclarada("Q2", EU, "Qual é o seu sexo/identidade de gênero?", True, opcoes=(
        "Masculino",
        "Feminino",
        "Mulher trans/travesti",
        "Homem trans",
        "Pessoa não binária",
        "Prefiro não responder",
    )),
    # Q3 permanece texto curto, sem tipo numérico (002, FR-037); candidata a dado derivado.
    PerguntaDeclarada("Q3", TC, "Quantos anos você tem?", True),
    PerguntaDeclarada("Q4", EU, "Como você se autodeclara?", True, opcoes=(
        "Branco(a)",
        "Preto(a)",
        "Pardo(a)",
        "Amarelo(a)",
        "Indígena",
    )),
    PerguntaDeclarada("Q5", EU, "Você é PcD (Pessoa com deficiência)?", True, opcoes=SIM_NAO),
    # Q6: opcional e sem condição técnica, como no original (DP-303).
    PerguntaDeclarada("Q6", EU, "Se sim, qual a deficiência?", False, opcoes=(
        "Deficiência física",
        "Deficiência visual",
        "Deficiência intelectual",
        "Deficiência auditiva",
    )),
    PerguntaDeclarada("Q7", EU, "Qual o seu estado civil?", True, opcoes=(
        "Solteiro(a)",
        "Casado(a)",
        "Divorciado(a)",
        "Separado(a)",
        "Viúvo(a)",
    )),
    PerguntaDeclarada(
        "Q8", EU, "Qual é o nível de escolaridade do seu pai?", True, opcoes=LISTA_E
    ),
    PerguntaDeclarada(
        "Q9", EU, "Qual é o nível de escolaridade da sua mãe?", True, opcoes=LISTA_E
    ),
))

S3 = SecaoDeclarada("S3", "Informações do curso", None, perguntas=(
    PerguntaDeclarada(
        "Q10", TC, "Em que ano você concluiu o seu curso no Ifes?", True,
        texto_explicativo="Exemplo: 2020, 2021, 2022, etc.",
    ),
    PerguntaDeclarada("Q11", EU, "Em qual campus você concluiu seu curso?", True, opcoes=LISTA_C),
    PerguntaDeclarada("Q12", EU, "Você é egresso(a) de qual modalidade?", True, opcoes=(
        "Presencial",
        "À distância",
    )),
    PerguntaDeclarada("Q13", EU, "Você foi admitido(a) ao curso do Ifes como estudante:", True,
                      opcoes=(
        "Cotista (vagas de cotas, ações afirmativas)",
        "Não cotista (vagas de ampla concorrência)",
        "Outros: transferência, remoção, reopção, reingresso, novo curso, etc.",
    )),
    PerguntaDeclarada(
        "Q14", EU, "Indique o questionário que pretende preencher", True,
        opcoes=(
            "Ensino Médio/Técnico Integrado",
            "Técnico Concomitante/Subsequente/EJA-PROEJA",
            "Graduação",
            "Pós-Graduação",
        ),
        regras=(
            ("Ensino Médio/Técnico Integrado", "S4"),
            ("Técnico Concomitante/Subsequente/EJA-PROEJA", "S5"),
            ("Graduação", "S6"),
            ("Pós-Graduação", "S7"),
        ),
    ),
))

CURSO = "Você é egresso(a) de qual Curso?"

# Toda Seção que encerra um ramo tem encaminhamento explícito para a convergência (FR-025).
S4 = SecaoDeclarada("S4", "Ensino Médio/Técnico Integrado", None, encaminhamento="S8", perguntas=(
    PerguntaDeclarada("Q15", EU, CURSO, True, opcoes=LISTA_15),
))

S5 = SecaoDeclarada(
    "S5", "Técnico Concomitante / Subsequente /EJA - PROEJA", None, encaminhamento="S8",
    perguntas=(
        PerguntaDeclarada("Q16", EU, "Você é egresso(a) de qual forma de oferta?", True, opcoes=(
            "Concomitante",
            "Subsequente",
            "EJA-PROEJA",
        )),
        PerguntaDeclarada("Q17", EU, CURSO, True, opcoes=LISTA_17),
    ),
)

S6 = SecaoDeclarada("S6", "Graduação", None, encaminhamento="S8", perguntas=(
    PerguntaDeclarada("Q18", EU, CURSO, True, opcoes=LISTA_18),
))

# E-05: a descrição da Seção 7 ("Tem que atualizar a lista de cursos, adicionando
# doutorado") é nota interna de edição e não é migrada.
S7 = SecaoDeclarada("S7", "Pós-Graduação", None, encaminhamento="S8", perguntas=(
    PerguntaDeclarada("Q19", EU, CURSO, True, opcoes=LISTA_19),
))

S8 = SecaoDeclarada("S8", "Avaliação", None, perguntas=(
    PerguntaDeclarada(
        "Q20", ESC,
        _afirmacao("Após o curso no Ifes, meu gosto por cultura, em geral, aumentou."), True,
        escala=CONCORDANCIA,
    ),
    PerguntaDeclarada(
        "Q21", ESC,
        _afirmacao("Após o curso no Ifes, meu acesso à cultura, em geral, aumentou."), True,
        escala=CONCORDANCIA,
    ),
    PerguntaDeclarada(
        "Q22", EU, "Você participou de ações de extensão durante o curso?", True, opcoes=SIM_NAO
    ),
    PerguntaDeclarada(
        "Q23", EU, "Você foi monitor(a) de disciplinas durante o curso?", True, opcoes=SIM_NAO
    ),
    PerguntaDeclarada(
        "Q24", EU, "Você fez algum tipo de estágio durante o curso?", True, opcoes=SIM_NAO
    ),
    PerguntaDeclarada(
        "Q25", EU,
        "Você participou de atividades acadêmicas (seminários, feiras, jornadas, etc) durante "
        "o curso?",
        True, opcoes=SIM_NAO,
    ),
    PerguntaDeclarada(
        "Q26", EM, "Que tipo de publicação você realizou durante o curso?", True,
        opcoes=(
            "Artigos técnico científicos",
            "Anais de Congresso",
            "Livro",
            "Capítulos de livro",
            "Não houve",
            OUTRO,
        ),
        complemento=OUTRO,
    ),
    PerguntaDeclarada(
        "Q27", EU, "Você fez intercâmbio no exterior durante o curso?", True, opcoes=SIM_NAO
    ),
    PerguntaDeclarada(
        "Q28", EU,
        "Durante o curso, você participou das atividades de grupos de pesquisas e de estudos?",
        True, opcoes=SIM_NAO,
    ),
    PerguntaDeclarada(
        "Q29", EU,
        "Você mantém algum vínculo com o curso, como participação em grupos de pesquisa ou de "
        "estudos?",
        True, opcoes=SIM_NAO,
    ),
    PerguntaDeclarada(
        "Q30", EU, "Você foi membro de empresa júnior durante o curso no Ifes?", True,
        opcoes=SIM_NAO,
    ),
    PerguntaDeclarada("Q31", EU, "Você participou de iniciação científica?", True, opcoes=SIM_NAO),
    PerguntaDeclarada(
        "Q32", EM, "Você recebeu algum tipo de bolsa?", True,
        # "auxilio" sem acento, como no original (E-19).
        texto_explicativo="Obs: Não considerar auxilio estudantil como bolsa.",
        opcoes=("Ensino", "Pesquisa", "Extensão", "Não recebi", OUTRO),
        complemento=OUTRO,
    ),
    PerguntaDeclarada(
        "Q33", EU, "Atualmente você trabalha?", True, opcoes=SIM_NAO,
        regras=(("Sim", "S9"), ("Não", "S10")),
    ),
))

S9 = SecaoDeclarada("S9", "Egresso que trabalha", None, encaminhamento="S11", perguntas=(
    PerguntaDeclarada("Q34", EU, "Você trabalha no setor:", True, opcoes=(
        "Misto",
        "Público",
        "Privado",
        "Terceiro setor (cooperativas/sindicatos)",
        "Trabalho em mais de um setor",
    )),
    PerguntaDeclarada(
        "Q35", EU,
        "O seu cargo/emprego exige como requisito o seguinte nível de escolaridade:", True,
        opcoes=(
            "Nenhum nível de instrução",
            "Ensino fundamental",
            "Ensino médio/técnico",
            "Graduação",
            "Pós-graduação",
            "Não sei dizer",
        ),
    ),
    PerguntaDeclarada(
        "Q36", ESC,
        _afirmacao("O meu trabalho atual é na minha área de formação do curso do Ifes."), True,
        escala=CONCORDANCIA,
    ),
    PerguntaDeclarada(
        "Q37", EU, "Você exerce cargo de chefia ou de direção atualmente?", True, opcoes=SIM_NAO
    ),
    # Faixas com limites sobrepostos, preservadas (O-18, DP-305).
    PerguntaDeclarada("Q38", EU, "Qual é a remuneração bruta mensal do seu trabalho?", True,
                      opcoes=(
        "Até 1 salário mínimo",
        "De 1 até 2,5 salários mínimos",
        "De 2,5 até 5,5 salários mínimos",
        "De 5,5 até 10 salários mínimos",
        "Acima de 10 salários mínimos",
    )),
    # O valor 500 fica sem faixa, como no original (O-18, DP-305).
    PerguntaDeclarada("Q39", EU, "A organização na qual você trabalha é:", True, opcoes=(
        "Micro empresa/organização (até 19 colaboradores)",
        "Pequena empresa/organização (de 20 a 99 colaboradores)",
        "Média empresa/organização (de 100 a 499 colaboradores)",
        "Grande empresa/organização (acima de 500 colaboradores)",
        "Não sei dizer",
    )),
    # Referência ao "campus" ambígua para EaD/Cefor, preservada (O-20, DP-306).
    PerguntaDeclarada("Q40", EU, "Você trabalha atualmente:", True, opcoes=(
        "Na mesma cidade do campus do Ifes onde fiz o curso",
        "Em outra cidade, mas na mesma região do campus do Ifes onde fiz o curso",
        "Em outra cidade e em outra região do campus do Ifes onde fiz o curso, mas ainda no "
        "estado do Espírito Santo",
        "Em outro estado brasileiro",
        "Em outro país",
    )),
    # E-06: a descrição "Verificar lugar dessa pergunta" é nota interna e não é migrada;
    # a posição é mantida (DP-310).
    PerguntaDeclarada(
        "Q41", EU,
        "Como você avalia a oferta de vagas aos profissionais da sua área de formação no Ifes?",
        True,
        opcoes=(
            "Não existem vagas de trabalho",
            "Existem poucas vagas de trabalho",
            "Existem muitas vagas de trabalho",
            "Não sei dizer",
        ),
    ),
    # Q42 e Q44 opcionais e Q43 obrigatória, como no original (O-10, DP-304).
    PerguntaDeclarada(
        "Q42", ESC,
        _afirmacao(
            "A realização de curso no Ifes foi indispensável para que eu conseguisse o meu "
            "trabalho atual. Sem ele, eu não teria o emprego que tenho hoje."
        ),
        False, escala=CONCORDANCIA,
    ),
    PerguntaDeclarada(
        "Q43", ESC,
        _afirmacao(
            "A minha experiência profissional anterior foi indispensável para que eu "
            "conseguisse o meu trabalho atual."
        ),
        True, escala=CONCORDANCIA,
    ),
    PerguntaDeclarada(
        "Q44", ESC,
        _afirmacao(
            "Eu usei as minhas redes de contato do Ifes para conseguir o meu trabalho atual."
        ),
        False, escala=CONCORDANCIA,
    ),
))

S10 = SecaoDeclarada("S10", "Egresso que não trabalha", None, encaminhamento="S11", perguntas=(
    PerguntaDeclarada(
        "Q45", EU, "Você não está trabalhando por qual motivo:", True,
        opcoes=(
            "Não encontrei vaga de trabalho, mas estou à procura",
            "Não estou à procura de vaga de trabalho no momento",
            OUTRO,
        ),
        complemento=OUTRO,
    ),
))

# Q46 é a única pergunta com regras seguida de outras na mesma Seção. A ordem é a do
# original; o momento de aplicação das regras não é registrado (FR-026, DP-302).
S11 = SecaoDeclarada("S11", "Estudo", None, perguntas=(
    PerguntaDeclarada(
        "Q46", EU, "Atualmente você estuda?", True, opcoes=SIM_NAO,
        regras=(("Sim", "S12"), ("Não", "S13")),
    ),
    PerguntaDeclarada("Q47", EM, "Após o curso, você:", True, opcoes=(
        "Não estudei mais",
        "Fiz cursos livres",
        "Fiz curso técnico",
        "Fiz curso de graduação",
        "Fiz especialização lato sensu",
        "Fiz mestrado",
        "Fiz doutorado",
        "Fiz pós-doutorado",
    )),
    PerguntaDeclarada(
        "Q48", ESC,
        _afirmacao(
            "O curso que realizei, citado acima, estava totalmente relacionado à área do meu "
            "curso do Ifes."
        ),
        False,
        texto_explicativo="Caso não tenha estudado mais deixe essa resposta em branco.",
        escala=CONCORDANCIA_MINUSCULA,
    ),
))

S12 = SecaoDeclarada("S12", "Egresso que estuda", None, encaminhamento="S13", perguntas=(
    PerguntaDeclarada(
        "Q49", EU, "Em qual categoria de estudante você se enquadra atualmente?", True,
        opcoes=(
            "Sou estudante de curso técnico",
            "Sou estudante de curso de graduação",
            "Sou estudante de curso de especialização lato sensu",
            "Sou estudante de mestrado",
            "Sou estudante de doutorado",
            "Sou estudante de pós-doutorado",
        ),
    ),
    PerguntaDeclarada(
        "Q50", ESC,
        _afirmacao(
            "O curso que estou realizando está totalmente relacionado à área do meu curso do "
            "Ifes."
        ),
        True, escala=CONCORDANCIA,
    ),
    # E-07: a regra "Instituição Privada" → Q52 não é reproduzida: nenhuma resposta a Q51
    # muda o percurso (FR-024).
    PerguntaDeclarada("Q51", EU, "A instituição na qual você está cursando é:", True, opcoes=(
        "Ifes",
        "Outra Instituição Pública",
        "Instituição Privada",
    )),
))

# Seção sem título visível no original (E-11).
S13 = SecaoDeclarada("S13", None, None, perguntas=(
    PerguntaDeclarada(
        "Q52", ESC,
        _afirmacao(
            "O meu curso no Ifes mudou a minha vida para melhor. Hoje, eu me considero uma "
            "pessoa diferente de quem eu era antes do Ifes."
        ),
        True, escala=CONCORDANCIA_CORRIGIDA,
    ),
    PerguntaDeclarada(
        "Q53", ESC,
        _afirmacao(
            "A situação econômica da minha família melhorou após eu ter concluído o curso no "
            "Ifes."
        ),
        True, escala=CONCORDANCIA_CORRIGIDA,
    ),
    PerguntaDeclarada(
        "Q54", ESC,
        _afirmacao(
            "Eu acredito que sou exemplo e inspiração para outras pessoas (amigos, colegas, "
            "familiares) se espelharem e ampliarem seus horizontes de estudos e profissionais."
        ),
        True, escala=CONCORDANCIA_CORRIGIDA,
    ),
))

SECOES: tuple[SecaoDeclarada, ...] = (S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13)

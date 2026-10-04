"""Constantes do contrato de dados analíticos, versão 2 (contracts/pacote-de-dados.md).

Só constantes, sem função de negócio. Os textos (descrições das colunas base e notas fixas)
são **literais do contrato**: mudá-los de forma incompatível exige nova `VERSAO_CONTRATO`
(spec FR-065). Nenhum nome aqui depende de ferramenta a jusante (spec FR-122).
"""

from dataclasses import dataclass

from trajetoria.instrumento.models import TipoPergunta

VERSAO_CONTRATO = 2
ESQUEMA_PSEUDONIMIZACAO = "hmac-sha256-v1"  # HMAC-SHA-256 de "<domínio>:<uuid>", hexadecimal

# Primeiro caractere de texto que recebe o apóstrofo de escape no CSV (spec FR-075). O
# próprio apóstrofo está na lista para que a reversão universal seja exata.
GATILHOS_DE_ESCAPE = ("=", "+", "-", "@", "\t", "\r", "'")


@dataclass(frozen=True)
class ColunaBase:
    nome: str
    tipo_valor: str  # booleano | texto | inteiro | data
    proveniencia: str  # institucional | derivado | coleta | declarado
    descricao: str


# As 15 colunas base de Dados, nesta ordem (data-model §1.1).
COLUNAS_BASE = (
    ColunaBase(
        "conclusao_analitica_id",
        "texto",
        "derivado",
        (
            "Pseudônimo analítico da Conclusão Acadêmica (formação concluída). Estável entre "
            "exportações feitas com a mesma chave; não reversível pelo consumidor."
        ),
    ),
    ColunaBase(
        "pessoa_analitica_id",
        "texto",
        "derivado",
        (
            "Pseudônimo analítico do registro de Pessoa a que a Conclusão pertence. Liga "
            "Conclusões da mesma Pessoa entre exportações feitas com a mesma chave; não "
            "reversível pelo consumidor; não reconcilia registros de fontes diferentes."
        ),
    ),
    ColunaBase(
        "elegivel_no_snapshot",
        "booleano",
        "derivado",
        (
            "Se a Conclusão pertencia à população elegível da Campanha no momento da captura do "
            "snapshot. Não é a elegibilidade atual. É o denominador das taxas."
        ),
    ),
    ColunaBase(
        "unidade",
        "texto",
        "institucional",
        (
            "Unidade (campus, campus avançado ou Cefor) da Conclusão, segundo a fonte "
            "institucional no momento da captura. Dado institucional, não declarado pelo "
            "egresso. Vazio = não informado."
        ),
    ),
    ColunaBase(
        "curso",
        "texto",
        "institucional",
        (
            "Curso da Conclusão, segundo a fonte institucional no momento da captura. "
            "Interpretar junto com a unidade: cursos homônimos de unidades diferentes são "
            "distintos. Vazio = não informado."
        ),
    ),
    ColunaBase(
        "nivel",
        "texto",
        "institucional",
        (
            "Nível da Conclusão, segundo a fonte institucional no momento da captura. Vazio = "
            "não informado."
        ),
    ),
    ColunaBase(
        "modalidade",
        "texto",
        "institucional",
        (
            "Modalidade da Conclusão, segundo a fonte institucional no momento da captura. Vazio "
            "= não informado."
        ),
    ),
    ColunaBase(
        "forma_oferta",
        "texto",
        "institucional",
        (
            "Forma de oferta da Conclusão, segundo a fonte institucional no momento da captura. "
            "Vazio = não informado."
        ),
    ),
    ColunaBase(
        "ano_conclusao",
        "inteiro",
        "institucional",
        (
            "Ano de conclusão, segundo a fonte institucional no momento da captura. Independente "
            "de data_conclusao: a fonte pode informar só o ano. Vazio = não informado."
        ),
    ),
    ColunaBase(
        "data_conclusao",
        "data",
        "institucional",
        (
            "Data de conclusão, segundo a fonte institucional no momento da captura, quando a "
            "fonte a informa. Vazio = não informada."
        ),
    ),
    ColunaBase(
        "possui_participacao",
        "booleano",
        "coleta",
        "Se existe Participação desta Conclusão na Campanha.",
    ),
    ColunaBase(
        "participacao_concluida",
        "booleano",
        "coleta",
        (
            "Se a Participação teve conclusão registrada (inclusive por recusa em Q1). Falso = "
            "iniciada e não concluída até o encerramento. Vazio = sem Participação."
        ),
    ),
    ColunaBase(
        "participacao_iniciada_em",
        "data",
        "coleta",
        (
            "Data de início da Participação, na timezone institucional (America/Sao_Paulo). "
            "Vazio = sem Participação."
        ),
    ),
    ColunaBase(
        "participacao_concluida_em",
        "data",
        "coleta",
        (
            "Data da conclusão registrada da Participação, na timezone institucional. Vazio = "
            "sem Participação ou não concluída."
        ),
    ),
    ColunaBase(
        "origem_formacao", "texto", "derivado",
        "Como a Participação chegou à Conclusão Acadêmica: âncora institucional ou "
        "declaração do egresso validada depois pela fonte digital ou pelo acervo histórico. "
        "O contexto acadêmico desta linha é sempre o da Conclusão, dado institucional.",
    ),
)

# Dicionário: nome e tipo de cada uma das 24 colunas, nesta ordem (data-model §2).
COLUNAS_DICIONARIO = (
    ("elemento", "texto"),
    ("coluna", "texto"),
    ("ordem", "inteiro"),
    ("tipo_valor", "texto"),
    ("proveniencia", "texto"),
    ("descricao", "texto"),
    ("versao", "texto"),
    ("secao_posicao", "inteiro"),
    ("secao_titulo", "texto"),
    ("secao_encaminhamento_destino", "inteiro"),
    ("pergunta_posicao", "inteiro"),
    ("pergunta_tipo", "texto"),
    ("pergunta_texto", "texto"),
    ("pergunta_texto_explicativo", "texto"),
    ("pergunta_obrigatoria", "booleano"),
    ("opcao_posicao", "inteiro"),
    ("opcao_texto", "texto"),
    ("opcao_admite_complemento", "booleano"),
    ("opcao_regra_finaliza", "booleano"),
    ("opcao_regra_destino_secao", "inteiro"),
    ("escala_inicio", "inteiro"),
    ("escala_fim", "inteiro"),
    ("escala_rotulo_inicio", "texto"),
    ("escala_rotulo_fim", "texto"),
)
CABECALHO_DICIONARIO = tuple(nome for nome, _ in COLUNAS_DICIONARIO)
CABECALHO_METADADOS = ("chave", "valor", "tipo")

# Descrições das colunas de Pergunta, por papel (data-model §2).
DESCRICAO_APLICABILIDADE = (
    "Indica se a Pergunta pertence ao percurso calculado da Participação: verdadeiro = "
    "pertence; falso = fora do percurso; vazio = sem Participação ou percurso não determinável."
)
DESCRICAO_VALOR = "Resposta declarada à Pergunta (ver pergunta_texto)."
DESCRICAO_OPCAO = (
    "Indica se a Opção foi escolhida: verdadeiro = escolhida; falso = não escolhida; "
    "vazio = sem Resposta válida."
)
DESCRICAO_COMPLEMENTO = "Complemento textual declarado com a Opção que o admite."
DESCRICAO_VALOR_POSSIVEL = "Valor possível da coluna: o texto da Opção."

TIPOS_DE_PERGUNTA = {
    TipoPergunta.ESCOLHA_UNICA: "escolha_unica",
    TipoPergunta.ESCOLHA_MULTIPLA: "escolha_multipla",
    TipoPergunta.TEXTO_CURTO: "texto_curto",
    TipoPergunta.ESCALA: "escala",
}

# Finalidade e notas fixas dos Metadados, nesta ordem relativa (data-model §3).
NOTAS = {
    "finalidade": (
        "Análise institucional dos resultados do acompanhamento de egressos (PAEG, Art. 10, "
        "III). Não é lista de contatos nem base de comunicação."
    ),
    "nota_snapshot": (
        "Este pacote contém exatamente um snapshot analítico, escolhido por quem exportou. "
        "Nenhum snapshot é oficial ou de referência; essa designação é decisão institucional "
        "pendente."
    ),
    "nota_privacidade": (
        "Dados individualizados e pseudonimizados, não anônimos. Linhas podem ser "
        "reidentificáveis pela combinação de atributos e pela ligação entre exportações. Não "
        "compartilhar fora da finalidade autorizada."
    ),
    "nota_representacao": (
        "Célula vazia = ausência de valor (não informado, não se aplica ou sem Resposta). "
        "Booleanos como true/false; datas como AAAA-MM-DD; momentos em ISO 8601 com "
        "deslocamento; datas da Participação na timezone institucional."
    ),
    "nota_proveniencia": (
        "Coluna proveniencia do Dicionário: institucional = contexto da Conclusão na fonte "
        "acadêmica, congelado no snapshot; derivado = calculado por regra (elegibilidade no "
        "snapshot, pseudônimos, aplicabilidade); coleta = fato registrado pelo sistema durante a "
        "coleta (existência, início e conclusão da Participação); declarado = Resposta do "
        "egresso."
    ),
    "nota_aplicabilidade": (
        "Para cada Pergunta, a coluna __aplicavel indica se ela pertence ao percurso calculado "
        "da Participação (verdadeiro), está fora dele (falso) ou não tem percurso (vazio: sem "
        "Participação ou percurso não determinável). Valor preenchido só ocorre com "
        "aplicabilidade verdadeira."
    ),
    "nota_escape_csv": (
        "No CSV, todo campo de texto que começa por =, +, -, @, tabulação, retorno de carro ou "
        "apóstrofo recebe um apóstrofo inicial, para não ser interpretado como fórmula. Para "
        "reverter, remova o apóstrofo inicial de qualquer campo que comece por apóstrofo. No "
        "XLSX não há escape: o texto é gravado como texto."
    ),
}

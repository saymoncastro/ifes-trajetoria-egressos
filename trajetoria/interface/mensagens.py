"""Textos fixos ao egresso (008 R12; data-model §4). Linguagem simples, sem motivo interno,
identificador ou valor declarado (FR-067, FR-068). A linguagem definitiva é DP-801: estes
textos podem ser revistos sem mudar comportamento. Nenhum texto do instrumento está aqui —
Perguntas, Opções e textos de abertura/encerramento vêm sempre da Versão."""

from trajetoria.participacao.entrada import SituacaoDaFormacao
from trajetoria.participacao.regras import Motivo

# Situação de cada formação (007) — nunca nomeia nem conta Campanhas (FR-023, FR-024).
# "Sem pesquisa" não se repete por formação: a situação geral da tela já o diz uma vez (014
# FR-036). A ambiguidade continua comunicada: tratamento provisório do 007/DP-701 (FR-037).
SITUACAO_DA_FORMACAO = {
    SituacaoDaFormacao.SEM_PESQUISA: None,
    SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR: "Pesquisa disponível para responder.",
    SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR: "Pesquisa em andamento.",
    SituacaoDaFormacao.JA_CONCLUIDA: "Pesquisa já respondida.",
    SituacaoDaFormacao.AMBIGUIDADE_OPERACIONAL: (
        "A pesquisa referente a esta formação não está disponível neste momento."
    ),
}

# Tela "Sua trajetória no Ifes" (014 FR-030 a FR-033). A frase de entrada usa só a linha da
# formação (curso · unidade · ano informados): nenhuma qualificação fixa da unidade.
TITULO_TRAJETORIA = "Sua trajetória no Ifes"
ENTRADA_FATO = "Você concluiu {linha}."
ENTRADA_SEM_ATRIBUTOS = "Encontramos uma formação sua no Ifes."
ENTRADA_CONTINUACAO = "O Ifes quer saber como sua trajetória seguiu depois disso."
SELECAO = (
    "Cada formação tem sua própria pesquisa. Escolha por qual começar ou continuar; as outras "
    "continuam disponíveis aqui."
)

AVISOS = {
    "situacao": "A situação da pesquisa mudou. Veja abaixo a situação atual.",
    "percurso": (
        "As respostas anteriores mudaram o caminho da pesquisa. Esta é a seção a responder agora."
    ),
    # Chegada à trajetória por "Salvar e sair" (014 FR-012): "salvo" só com Resposta gravada
    # na Seção; senão, "saida", neutro e verdadeiro (FR-008).
    "salvo": (
        "O que você respondeu nesta seção está salvo. Você pode continuar a pesquisa quando quiser."
    ),
    "saida": "Você pode continuar a pesquisa quando quiser.",
}
# Variante visual fixa de cada aviso (015 FR-026): sucesso só quando algo foi salvo.
VARIANTE_DO_AVISO = {
    "situacao": "informacao",
    "percurso": "informacao",
    "salvo": "sucesso",
    "saida": "informacao",
}
# Nota de "Sair sem salvar esta seção" (014 FR-013).
SAIR_SEM_SALVAR_NOTA = "O que já foi salvo antes continua guardado."

# Entrada: a Seção pode ser salva incompleta (014 FR-002).
ENTRADA_OPERACIONAL = (
    "Você responde uma seção de cada vez. Pode salvar a qualquer momento, mesmo sem terminar a "
    "seção, e continuar depois."
)

# Resumo no topo da Seção (014 FR-004 a FR-008). Erro de forma recusa o envio sem gravar nada;
# pendência é o que falta depois de um envio aceito e gravado — nunca apresentada como erro.
RESUMO = {
    "erros": {
        "titulo": "Há problemas nesta seção",
        "prefixo_titulo": "Erro: ",
        "prefixo_item": "Erro:",
    },
    "pendencias": {
        "titulo": "Ainda faltam estas perguntas:",
        "prefixo_titulo": "Faltam respostas: ",
        "prefixo_item": "Falta responder:",
    },
}
# Só quando a Seção tem Resposta gravada (014 FR-008).
SECAO_SALVA = "O que você respondeu nesta seção está salvo."

# Erros de preenchimento por Pergunta (FR-070).
ESCOLHA_INVALIDA = "Selecione uma das opções apresentadas."
ESCALA_INVALIDA = "Selecione um valor da escala."
OBRIGATORIA = "Esta pergunta é obrigatória."
COMPLEMENTO_SEM_OPCAO = "Para descrever, marque a opção «{opcao}»."
POR_MOTIVO = {
    Motivo.OPCAO_DE_OUTRA_PERGUNTA: ESCOLHA_INVALIDA,
    Motivo.VALOR_INCOMPATIVEL: ESCOLHA_INVALIDA,
    Motivo.ESCALA_FORA_DOS_LIMITES: ESCALA_INVALIDA,
    Motivo.VALOR_VAZIO: "Preencha a resposta ou deixe o campo em branco.",
    Motivo.COMPLEMENTO_NAO_ADMITIDO: "Para descrever, marque a opção a que a descrição se refere.",
    Motivo.PERGUNTA_DE_OUTRA_VERSAO: "Não foi possível salvar esta resposta.",
}
NAO_SALVA = "Não foi possível salvar esta resposta."

# Confirmação (014 FR-038 a FR-040): o que foi registrado, sem finalidade nem promessa. O
# agradecimento fixo só aparece quando a Versão não tem texto de encerramento.
REGISTRADAS_CURSO = "Suas respostas sobre {curso} foram registradas."
REGISTRADAS = "Suas respostas foram registradas."
AGRADECIMENTO = "Obrigado pela sua participação."

# Telas de estado (aviso.html): título e parágrafos.
JA_RESPONDIDA = ("Esta pesquisa já foi respondida.", ())
PERIODO_ENCERRADO = (
    "O período de resposta desta pesquisa foi encerrado.",
    ("As respostas salvas anteriormente foram preservadas.",),
)
PESQUISA_INDISPONIVEL = ("Esta pesquisa não está disponível no momento.", ())
FORMACAO_INDISPONIVEL = ("Formação não disponível.", ())

REGISTRADA_DECLARADA = ("Obrigado. Sua resposta foi registrada. "
                       "A formação informada passará por verificação institucional.")

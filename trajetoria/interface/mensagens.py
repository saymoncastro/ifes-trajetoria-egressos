"""Textos fixos ao egresso (008 R12; data-model §4). Linguagem simples, sem motivo interno,
identificador ou valor declarado (FR-067, FR-068). A linguagem definitiva é DP-801: estes
textos podem ser revistos sem mudar comportamento. Nenhum texto do instrumento está aqui —
Perguntas, Opções e textos de abertura/encerramento vêm sempre da Versão."""

from trajetoria.participacao.entrada import SituacaoDaFormacao
from trajetoria.participacao.regras import Motivo

# Situação de cada formação (007) — nunca nomeia nem conta Campanhas (FR-023, FR-024).
SITUACAO_DA_FORMACAO = {
    SituacaoDaFormacao.SEM_PESQUISA: "Sem pesquisa disponível no momento.",
    SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR: "Pesquisa disponível para responder.",
    SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR: "Pesquisa em andamento.",
    SituacaoDaFormacao.JA_CONCLUIDA: "Pesquisa já respondida.",
    SituacaoDaFormacao.AMBIGUIDADE_OPERACIONAL: (
        "A pesquisa referente a esta formação não está disponível neste momento."
    ),
}

AVISOS = {
    "situacao": "A situação da pesquisa mudou. Veja abaixo a situação atual.",
    "percurso": (
        "As respostas anteriores mudaram o caminho da pesquisa. Esta é a seção a responder agora."
    ),
}

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

# Telas de estado (aviso.html): título e parágrafos.
JA_RESPONDIDA = ("Esta pesquisa já foi respondida.", ())
PERIODO_ENCERRADO = (
    "O período de resposta desta pesquisa foi encerrado.",
    ("As respostas salvas anteriormente foram preservadas.",),
)
PESQUISA_INDISPONIVEL = ("Esta pesquisa não está disponível no momento.", ())
FORMACAO_INDISPONIVEL = ("Formação não disponível.", ())

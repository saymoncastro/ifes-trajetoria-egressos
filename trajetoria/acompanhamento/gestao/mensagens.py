"""Vocabulário fechado da gestão; detalhes técnicos nunca são apresentados."""

from trajetoria.campanha.regras import Motivo

ERROS = {
    Motivo.NOME_VAZIO: ("nome", "Informe o nome da Campanha."),
    Motivo.PERIODO_INCOMPLETO: (
        None,
        "Informe as duas datas do período, ou deixe ambas em branco para definir depois.",
    ),
    Motivo.PERIODO_INVERTIDO: ("inicio", "O início deve ser igual ou anterior ao fim."),
}
AVISOS = {
    "campanha-criada": "Campanha criada.",
    "configuracao-salva": "Configuração salva.",
    "coleta-aberta": "Coleta aberta. A Campanha já aceita respostas.",
    "coleta-encerrada": "Coleta encerrada.",
    "ja-em-coleta": "Esta Campanha já está em coleta. Nada foi alterado.",
    "ja-encerrada": "Esta Campanha já está encerrada. Nada foi alterado.",
}
SEM_PUBLICADA = "Ainda não há Versão publicada disponível. A publicação não é feita aqui."
JA_ABERTA = (
    "Esta Campanha já foi aberta e não pode mais ser alterada. Mudanças exigem nova Campanha."
)
NUNCA_ABERTA = "Esta Campanha nunca foi aberta; não há coleta para encerrar."
PERIODO_REMOVIDO = "O período pode ser corrigido, mas não removido."
SOBREPOSICAO = (
    "Já existem outras Campanhas em coleta. Isso pode fazer com que alguns egressos "
    "tenham mais de uma pesquisa disponível."
)
ABRANGENCIA = (
    "Esta Campanha tem abrangência restrita definida fora desta interface. "
    "Os critérios expressam a abrangência do instrumento, são somente para leitura "
    "e não podem ser alterados aqui."
)

CONFIRMAR_ABERTURA = (
    "A Campanha passa a aceitar respostas imediatamente. Depois de aberta, a configuração "
    "não pode ser alterada, e não há reabertura nem prorrogação."
)
CONFIRMAR_ENCERRAMENTO = (
    "Novas respostas deixarão de ser aceitas. As Participações existentes são preservadas. "
    "Não há reabertura."
)

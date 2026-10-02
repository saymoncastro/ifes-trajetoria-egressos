"""Textos do editor ao operador (research R10; FR-003, FR-034, FR-056, FR-071, FR-094 a
FR-096). Só textos: os mapeamentos de rejeição são locais, nas views e no diagnóstico.
Nenhum texto do instrumento está aqui — Pesquisas, Versões, Seções, Perguntas e Opções vêm
sempre do banco. Linguagem revisável sem mudar comportamento (008/DP-801)."""

BANNER = (
    "Ambiente não produtivo: não há autenticação, e ter acesso a este editor não confere "
    "competência institucional para elaborar ou publicar o instrumento."
)

SEMANTICA_NAVEGACAO = (
    "Como a jornada atual aplica a navegação: o desvio é aplicado quando o respondente "
    "conclui a Seção; as demais Perguntas da mesma Seção continuam sendo apresentadas. "
    "Prevalece o desvio da Opção escolhida; sem ele, o encaminhamento da Seção; sem ele, a "
    "ordem. Pergunta opcional sem resposta não aciona desvio. Esta é a semântica atual da "
    "jornada, não uma regra permanente."
)

SO_ESCOLHA_UNICA = "Somente Perguntas de escolha única podem ter desvio de navegação."

TIPO_FIXO = (
    "O tipo não pode ser trocado depois da criação. Para usar outro tipo, crie uma nova "
    "Pergunta e remova esta."
)

SEM_IMPEDIMENTOS = (
    "Isso significa apenas que nenhuma verificação técnica existente aponta impedimento. "
    "Não é aprovação, homologação, autorização nem publicação. A publicação não está "
    "disponível neste editor: depende da definição institucional de quem pode publicar."
)

TRABALHE_EM_COPIA = (
    "Para experimentar mudanças sem alterar esta Versão, crie uma nova Versão a partir dela "
    "e trabalhe na cópia."
)

PUBLICADA_409 = (
    "Esta Versão está publicada e não pode ser alterada. Para mudar o instrumento, crie "
    "uma nova Versão a partir dela."
)

CONFLITO = (
    "O conteúdo mudou desde que esta página foi aberta. Confira o estado atual e tente de novo."
)

INCOMPATIVEL_COM_A_JORNADA = (
    "A jornada atual não consegue aplicar mais de uma Pergunta com desvio na mesma Seção. "
    "Deixe desvio em apenas uma Pergunta desta Seção, ou distribua as Perguntas com desvio "
    "em Seções diferentes."
)

NOME_REPETIDO = (
    "Já existe uma Pesquisa com este nome. Duas Pesquisas com o mesmo nome ficam difíceis "
    "de distinguir. Marque a confirmação abaixo para criar mesmo assim."
)

# Avisos depois de redirecionar (lista fechada, como na 008).
AVISOS = {
    "pesquisa-criada": "Pesquisa criada.",
    "versao-criada": "Versão criada em rascunho.",
    "dados-salvos": "Alterações salvas.",
    "secao-criada": "Seção adicionada ao final.",
    "secao-removida": "Seção removida.",
    "pergunta-criada": "Pergunta adicionada ao final da Seção.",
    "adicione-opcoes": "Pergunta criada. Adicione agora as Opções (pelo menos duas).",
    "pergunta-movida": "Pergunta movida para o final da Seção escolhida.",
    "pergunta-removida": "Pergunta removida.",
    "opcao-criada": "Opção adicionada ao final.",
    "opcao-removida": "Opção removida.",
    "sem-movimento": "Nada foi movido: o elemento já está na ponta.",
    "publicada": "Esta Versão está publicada e só pode ser consultada.",
}

# Erros de formulário vindos de rejeições da 002 (associados ao campo).
DESIGNACAO_REPETIDA = "Já existe uma Versão com esta designação nesta Pesquisa."
TEXTO_VAZIO = "Informe o texto."
OPCAO_REPETIDA = "Já existe uma Opção com este texto nesta Pergunta."
COMPLEMENTO_REPETIDO = (
    "Só uma Opção por Pergunta pode aceitar complemento escrito. Desmarque a Opção atual "
    "antes de marcar outra."
)
ESCALA_INVALIDA = "O limite inicial precisa ser um número inteiro menor que o limite final."
OBRIGATORIEDADE = "Indique se a Pergunta é obrigatória ou opcional."
NUMERO_INTEIRO = "Informe um número inteiro."
SECAO_COM_PERGUNTAS = "Esta Seção tem Perguntas. Remova ou mova as Perguntas antes de removê-la."
SECAO_REFERENCIADA = (
    "Esta Seção é destino de: {referencias}. Altere esses desvios ou encaminhamentos antes "
    "de removê-la."
)

# O que corrigir, por condição de completude da 002 (diagnóstico A).
CORRIGIR_SEM_SECOES = "A Versão não tem Seções. Adicione pelo menos uma Seção."
CORRIGIR_SECAO_SEM_PERGUNTAS = "{onde} não tem Perguntas. Adicione Perguntas ou remova a Seção."
CORRIGIR_OPCOES_INSUFICIENTES = "{onde} precisa ter pelo menos duas Opções."
CORRIGIR_DESTINO_NAO_POSTERIOR = (
    "{onde}: o destino precisa ser uma Seção posterior. Escolha uma Seção que venha depois "
    "ou reordene as Seções."
)
CORRIGIR_REFERENCIA_OUTRA_VERSAO = "{onde}: o destino não pertence a esta Versão. Escolha outro."

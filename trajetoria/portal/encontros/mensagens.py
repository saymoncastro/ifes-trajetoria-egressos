"""Textos dos encontros (031, incremento 1). Provisórios (DP-801), os mesmos do protótipo.

Vocabulário: a confirmação nunca é chamada de inscrição, nem afirma presença; nada de
"turma", "geração", "conectad" (ADR 0009, decisão 7). Termo e ciência têm versão: ela vai para
o Encontro e para a Confirmação (XVII). Eles registram ciência; não definem base legal (D9).
"""

VERSAO_DO_TERMO = "2026-10-11.1 (provisória)"
VERSAO_DA_CIENCIA = "2026-10-11.1 (provisória)"

TITULO_ENCONTROS = "Encontros"
INTRODUCAO = (
    "Encontros com outros egressos do Ifes. Alguns são propostos por egressos; outros são "
    "eventos divulgados pelo Ifes."
)
PROPOR = "Propor um encontro"
SEUS = "Seus encontros"
GRUPO_F = "Propostos por egressos"
GRUPO_F_NOTA = "Cada um foi analisado pelo Ifes antes de aparecer aqui. Quem propõe é quem conduz."
GRUPO_A = "Eventos do Ifes"
GRUPO_A_NOTA = "Divulgados pelas unidades. Data, local e inscrição estão na página oficial."
SELO_F = "Proposto por egresso"
SELO_F_PAGINA = "Encontro proposto por egresso"
SELO_A = "Evento do Ifes"
VAZIO_F = "Nenhum encontro proposto para a sua formação agora."
VAZIO_F_CONVITE = (
    "Você pode propor o primeiro: um tema da sua área, uma conversa sobre carreira ou sobre "
    "voltar a estudar."
)
VAZIO_A = "Nenhum evento divulgado pelo Ifes para a sua formação agora."
ABERTO_A_TODOS = "Aberto a todos os egressos do Ifes."
PROPOSTO_POR = "Proposto por {nome} · {origem}"
VIRTUAL = "virtual"

# Página do encontro
ONDE = "Virtual · o link aparece para quem confirmar"
FUSO = "(horário de Brasília)"
SOBRE = "Sobre o encontro"
QUEM_PROPOE = "Quem propõe"
NOME_ESCOLHIDO = "Nome escolhido por quem propõe"
REGISTRO_DO_IFES = "Registro do Ifes"
MODERADO_POR = (
    "Publicado depois da análise da {quem}. O Ifes revisou a proposta, mas não organiza este "
    "encontro: quem conduz é a pessoa que propôs."
)
PARA_QUEM = "Para quem foi proposto"
QUEM_RECEBE_O_ENDERECO = "Quem receber o endereço também pode participar."
VOCE_RECEBEU = (
    "O encontro não aparece na sua lista porque foi pensado para essas formações, mas você "
    "também pode participar."
)
VOU_PARTICIPAR_TITULO = "Vou participar?"
VOU_PARTICIPAR = "Vou participar"
CIENCIA = (
    "Quem propôs vê só quantas pessoas confirmaram. Ninguém vê o seu nome.",
    "O link da reunião aparece aqui depois que você confirmar.",
    "Confirmar não é inscrição e não registra presença.",
    "Você pode cancelar até o início do encontro.",
    "Você não recebe e-mail nem notificação. As mudanças aparecem nesta página.",
    "O encontro acontece fora do Portal, na plataforma do link.",
)
CIENCIA_VERSAO = "Ciência da participação, versão {versao}."
VOCE_VAI = "Você vai participar"
CONFIRMADO_EM = "Confirmado em {data}. Quem propôs vê só que há mais uma pessoa, sem o seu nome."
LINK_DA_REUNIAO = "Link da reunião"
LINK_NOTA = "{origem}: {dominio} · sala criada por quem propôs, fora do Portal"
CANCELAR_PARTICIPACAO = "Cancelar minha participação"
INDICAR = (
    "Para indicar o encontro a alguém, envie o endereço desta página. A pessoa precisa "
    "confirmar os dados no Portal para ver."
)
VER_TODOS = "Ver todos os encontros"
PARTICIPACAO_ENCERRADA = "As confirmações se encerram no início do encontro."

# Situações
EM_ANALISE = "Em análise pela {quem} desde {data}"
NAO_ANALISADO = "Não analisado a tempo"
NAO_ANALISADO_TEXTO = "Não foi publicado."
PUBLICADO = "Publicado em {data}, depois da análise da {quem}"
ENCERRADO = "Encontro encerrado"
ENCERRADO_TEXTO = "Terminou em {data}, às {hora}. O link da reunião não aparece mais."
RECUSADO = "Recusado pela {quem} em {data}"
RETIRADO = "Retirado pela moderação"
RETIRADO_TEXTO = "Este encontro foi retirado pela moderação do Ifes e não está mais disponível."
CANCELADO = "Cancelado por quem propôs"
CANCELADO_TEXTO = (
    "Cancelado em {data}. O encontro não vai acontecer, e o link não está mais disponível."
)
CANCELADO_TEXTO_CURTO = "O encontro não vai acontecer, e o link não está mais disponível."
ENCERRADO_TEXTO_CURTO = "O encontro já aconteceu. O link da reunião não aparece mais."
INDISPONIVEL_TITULO = "Este encontro não está disponível"
INDISPONIVEL_TEXTO = "Ele não foi publicado ou não está mais disponível."
CONFIRMACOES = {0: "Nenhuma pessoa confirmou", 1: "1 pessoa confirmou"}
CONFIRMACOES_VARIAS = "{n} pessoas confirmaram"
SO_O_NUMERO = "Você vê só o número. Ninguém, nem você, vê quem confirmou."

# Sem sessão e sem Conclusão (FR-022)
NEUTRA_TITULO = "Encontro no Portal do Egresso"
NEUTRA_TEXTO = (
    "Este endereço leva a um encontro entre egressos do Ifes. Para ver a data, a descrição e "
    "quem propõe, confirme seus dados."
)
NEUTRA_ACAO = "Confirme seus dados para ver"
NEUTRA_NOTA = "São pedidos o CPF e a data de nascimento registrados no Ifes."
SO_PARA_EGRESSOS = "Os encontros são para quem tem formação concluída registrada no Ifes."

# Organizador
PROPOR_LEAD = (
    "Um encontro virtual entre egressos, conduzido por você. O Ifes analisa antes de publicar."
)
ROTULO_TITULO = "Título"
DICA_TITULO = "Até 90 caracteres."
ROTULO_DESCRICAO = "Do que vocês vão conversar"
DICA_DESCRICAO = "Até 400 caracteres. Não inclua telefone, e-mail ou outros contatos."
ROTULO_DATA = "Data"
DICA_DATA = "Entre {de} e {ate}."
ROTULO_INICIO = "Início"
DICA_INICIO = "Horário de Brasília."
ROTULO_TERMINO = "Término"
DICA_TERMINO = "Até 3 horas depois do início."
LEGENDA_PUBLICO = "Para quem o encontro aparece?"
NOTA_PUBLICO = (
    "Ele aparece na lista de quem tem essas formações. Quem receber o endereço também pode "
    "participar. Não precisa incluir a sua formação: um tema pode reunir egressos de cursos e "
    "unidades diferentes."
)
PUBLICO_TODOS = "Todos os egressos do Ifes"
PUBLICO_FORMACOES = "Egressos de certas unidades, níveis ou cursos"
RESUMO_UNIDADES = "Unidades"
RESUMO_NIVEIS = "Níveis"
RESUMO_CURSOS = "Cursos"
QUEM_ANALISA = (
    "Quem analisa na demonstração: a CSAEG da unidade, se você escolher uma só unidade; a "
    "CPAEG, nos demais casos."
)
ROTULO_LINK = "Link da reunião"
DICA_LINK = (
    "Crie a sala na plataforma que preferir e cole o endereço, começando com https://. Ele só "
    "aparece para quem confirmar."
)
ROTULO_NOME = "Como você quer se apresentar"
DICA_NOME = "Aparece na página do encontro. Pode ser só o primeiro nome."
LEGENDA_ORIGEM = "Sua formação de origem"
NOTA_ORIGEM = "Aparece como registro do Ifes. Não limita quem pode participar."
CONTINUAR = "Continuar"
VOLTAR_AOS_ENCONTROS = "Voltar aos encontros"
CONFIRA = "Confira e envie"
ANTES_DE_ENVIAR = "Antes de enviar"
TERMO = (
    "Você propõe e conduz o encontro. O Ifes analisa antes de publicar, mas não organiza.",
    "Na página aparecem o título, a descrição, a data, o público, o nome que você escolheu e a "
    "sua formação de origem. Só egressos que entraram no Portal veem a página.",
    "O link da reunião aparece só para quem confirmar. Quem confirmou pode repassá-lo; o "
    "Portal não impede.",
    "Você vê quantas pessoas confirmaram, nunca quem são.",
    "A análise não tem prazo garantido. Se não for analisado até a data, o encontro não é "
    "publicado.",
    "O Ifes pode recusar ou retirar o encontro, sempre com o motivo. Você pode cancelar até o "
    "início.",
    "Ninguém recebe e-mail nem notificação: as mudanças aparecem só na página do encontro.",
)
TERMO_VERSAO = "Termo do organizador, versão {versao}."
ENVIAR = "Enviar para análise"
VOLTAR_E_ALTERAR = "Voltar e alterar"
RESUMO = {
    "descricao": "Descrição", "quando": "Quando", "onde_aparece": "Onde aparece",
    "quem_analisa": "Quem analisa", "link": "Link da reunião", "como_aparece": "Como você aparece",
}
QUEM_ANALISA_UNIDADE = "CSAEG {unidade}, porque o público é só dessa unidade."
QUEM_ANALISA_CPAEG = "CPAEG, porque o público inclui mais de uma unidade ou não é de uma unidade."
ENVIADO = "Encontro enviado para análise."
EM_ANALISE_ITENS = (
    "Ainda não aparece para ninguém.",
    "Quando a moderação decidir, a situação muda aqui e em Seus encontros. Você não recebe "
    "e-mail.",
    "Se não for analisado até o início, o encontro não é publicado.",
)
SEUS_LEAD = "Os encontros que você propôs. Você vê quantas pessoas confirmaram, nunca quem são."
SEUS_VAZIO = "Você ainda não propôs nenhum encontro."
SEUS_VAZIO_CONVITE = (
    "Um encontro pode ser uma conversa sobre a sua área, sobre carreira ou sobre voltar a "
    "estudar, com egressos de qualquer curso ou unidade."
)
MOTIVO = "Motivo"
CANCELAR_ENCONTRO = "Cancelar este encontro"
CANCELAR_ITENS = (
    'O encontro sai das listas, e a página passa a dizer "Cancelado por quem propôs".',
    "O link deixa de aparecer.",
    "Quem confirmou não é avisado automaticamente: verá o cancelamento na página.",
    "O cancelamento não pode ser desfeito.",
)
CANCELAR_O_ENCONTRO = "Cancelar o encontro"
VOLTAR_SEM_CANCELAR = "Voltar sem cancelar"
CANCELAR_PARTICIPACAO_TITULO = "Cancelar sua participação"
CANCELAR_PARTICIPACAO_ITENS = (
    "O link da reunião deixa de aparecer para você.",
    "Quem propôs passa a ver uma confirmação a menos, sem saber quem cancelou.",
    "Você pode confirmar de novo até o início do encontro.",
)
CANCELAR_PARTICIPACAO_ACAO = "Cancelar participação"
VOCE_PROPOS = "Você propôs este encontro"
PARA_COMPARTILHAR = "Para compartilhar"
COMPARTILHAR_TEXTO = (
    "Envie o endereço desta página. Quem receber precisa confirmar os dados no Portal para ver."
)
CONFLITO_TITULO = "Não foi possível concluir"
CONFLITO = "A situação deste encontro mudou enquanto você estava nesta tela. Nada foi registrado."

AVISOS = {
    "enviado": ENVIADO,
    "confirmado": "Participação confirmada.",
    "participacao_cancelada": "Participação cancelada.",
    "cancelado": "Encontro cancelado.",
}

ERROS = {
    "titulo": "Informe um título de até 90 caracteres.",
    "descricao": "Descreva o encontro em até 400 caracteres.",
    "nome": "Informe como você quer se apresentar, em até 40 caracteres.",
    "data": "Escolha uma data entre {de} e {ate}.",
    "inicio": "Informe o horário de início.",
    "termino": "O término precisa ser depois do início, no mesmo dia, com até 3 horas.",
    "termino_vazio": "Informe o horário de término.",
    "publico": "Escolha ao menos uma unidade, um nível ou um curso, ou marque todos os egressos.",
    "link": "O link precisa começar com https://, sem espaços, com até 500 caracteres.",
    "origem": "Escolha uma das suas formações.",
    "termo": "O termo mudou desde que você abriu a tela. Leia de novo e envie.",
    "limite": (
        "Você já tem 3 encontros em análise ou publicados. Para propor outro, espere um deles "
        "terminar ou cancele um em Seus encontros."
    ),
    "resumo": "Corrija para continuar",
}

# Moderação
MODERACAO_TITULO = "Encontros propostos por egressos"
MODERACAO_INTRODUCAO = (
    "Encontros no escopo da sua atuação. Nenhum aparece aos egressos sem a sua publicação. "
    "Você não vê CPF, data de nascimento nem contato de quem propõe, nem quem confirmou."
)
PARA_ANALISE = "Para análise"
PUBLICADOS = "Publicados"
FILA_VAZIA = "Nenhum encontro para análise no escopo da sua atuação."
PUBLICADOS_VAZIO = "Nenhum encontro publicado no escopo da sua atuação."
ANALISAR = "Analisar"
ANALISAR_TITULO = "Analisar encontro"
COMO_VERAO = "Como os egressos verão"
SITE_EXTERNO_AVISO = (
    "{origem}: {dominio}. O Portal não abre nem verifica o link. Confira o domínio antes de "
    "publicar."
)
PUBLICAR = "Publicar"
PUBLICAR_NOTA = (
    "Publicar faz o encontro aparecer aos egressos com formação no público. Você e a data "
    "ficam registrados."
)
RECUSAR = "Recusar"
RECUSAR_TITULO = "Recusar encontro"
RETIRAR = "Retirar"
RETIRAR_TITULO = "Retirar encontro publicado"
LEGENDA_MOTIVO = "Motivo"
NOTA_MOTIVO = "Lista provisória; os critérios para uso real dependem de decisão institucional."
ROTULO_COMPLEMENTO = "Complemento"
DICA_COMPLEMENTO = (
    'Até 300 caracteres; obrigatório em "Outro motivo". Quem propôs vê o motivo e o '
    "complemento."
)
RECUSA_NOTA = "A recusa é definitiva; a pessoa pode propor outro encontro."
RETIRADA_NOTA = (
    'O encontro sai das listas na hora, a página passa a dizer "Retirado pela moderação" e o '
    "link some. A retirada é definitiva."
)
VOLTAR = "Voltar"
MODERACAO_RECUSA = "Sua atuação não inclui a moderação de encontros propostos por egressos."
ERRO_MOTIVO = "Escolha um motivo."
ERRO_COMPLEMENTO = 'Escreva o complemento (até 300 caracteres), obrigatório em "Outro motivo".'
DECISAO_AVISOS = {
    "publicado": "Encontro publicado.",
    "recusado": "Encontro recusado.",
    "retirado": "Encontro retirado.",
}

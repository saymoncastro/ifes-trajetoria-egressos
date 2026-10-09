"""Textos de Oportunidades (025; contracts/oportunidades-egresso.md, contracts/curadoria.md,
contracts/pertinencia.md). Provisórios: a linguagem definitiva é 008/DP-801.

Vocabulário vetado nos textos do sistema (FR-022; research R14): "recomendado", "não perca",
"últimas vagas", "selecionado para você", contagem de outros egressos e estimativa de tempo.
O conteúdo escrito pelo operador é orientado, não bloqueado (FR-022, esclarecido).
"""

# --- Egresso --------------------------------------------------------------------------------

TITULO = "Oportunidades"
INTRODUCAO = (
    "Oportunidades divulgadas pelo Ifes, com links para as páginas oficiais. Aparecem pelas "
    "formações que o Ifes registra ou porque estão abertas a todos os egressos."
)
GRUPO_FORMACAO = "Pela sua formação"
GRUPO_TODOS = "Para todos os egressos"
VAZIO = (
    "No momento, não há oportunidades divulgadas para as suas formações. Novas oportunidades "
    "aparecem aqui quando o Ifes as divulga."
)
VOLTAR_AO_INICIO = "Voltar ao Início"
VER_TODAS = "Ver as {n} oportunidades"
VER_PAGINA = "Ver a página de Oportunidades"

ABERTA_A_TODOS = "Aberta a todos os egressos do Ifes."
APARECE_PORQUE = "Aparece porque você concluiu {formacoes}."
UMA_FORMACAO = "uma formação"
FORMACAO_DE_NIVEL = ", formação de {nivel}"
NA_UNIDADE = " na unidade {unidade}"
OFERECIDA_PELA_UNIDADE = "Oferecida pela unidade {unidade}"
OFERECIDA_PELO_IFES = "Oferecida pelo Ifes"
SITE_DO_IFES = "site do Ifes"
SITE_EXTERNO = "site externo"

# --- Curadoria ------------------------------------------------------------------------------

CURADORIA_TITULO = "Oportunidades"
CURADORIA_TRILHA = "Curadoria de oportunidades"
NOVA = "Nova oportunidade"
LISTA_VAZIA = "Nenhuma oportunidade no escopo da sua atuação."
IFES_INSTITUCIONAL = "Ifes (institucional)"
RECUSA = "A curadoria de oportunidades não está disponível para esta atuação."

AJUDA_CONTEUDO = (
    "Evite urgência e promessas, como 'últimas vagas' ou 'não perca'. Os prazos ficam na "
    "página oficial."
)
AJUDA_PUBLICO = (
    "Sem nenhuma marcação, a oportunidade aparece para todos os egressos do Ifes. Com "
    "marcações, aparece para quem tem uma formação que atende a todas elas."
)

ERROS = {
    "titulo": "Informe um título de até 120 caracteres.",
    "resumo": "Informe um resumo de até 300 caracteres.",
    "categoria": "Escolha uma categoria.",
    "unidade_responsavel": "Escolha uma unidade da sua atuação.",
    "endereco": (
        "Informe um endereço completo que comece com https://, sem usuário, senha nem número IP."
    ),
    "periodo_invertido": "O fim da divulgação não pode ser anterior ao início.",
    "fim_antes_de_hoje": "Para encerrar antes do prazo, retire a oportunidade.",
    "publicacao_vencida": "O fim da divulgação já passou. Ajuste o período antes de publicar.",
    "data": "Informe a data no formato dd/mm/aaaa.",
    "publico": "Escolha só valores da lista.",
}

CONFLITO_TITULO = "Ação não disponível"
CONFLITO = "Esta oportunidade mudou desde que você abriu a página."

PUBLICAR_TITULO = "Publicar oportunidade"
PUBLICAR_ACAO = "Publicar"
PUBLICO_TODOS = "Público: todos os egressos do Ifes"
PUBLICO_ALGUNS = "Público: quem concluiu {criterios}"
PERIODO = "Divulgação de {inicio} a {fim}"
ENDERECO_CONFIRMACAO = "Endereço: {dominio}"
AVISO_EXTERNO = (
    "Este endereço não é de um site do Ifes. Confira se é a página oficial da oportunidade."
)
RETIRAR_TITULO = "Retirar oportunidade"
RETIRAR_ACAO = "Retirar"
RETIRAR_TEXTO = (
    "A oportunidade sai da vista dos egressos imediatamente. A retirada não pode ser desfeita."
)
CANCELAR = "Cancelar"
EDITAR = "Editar"
EDITAR_TITULO = "Editar oportunidade"
PREVIA_EXPLICACAO = (
    "Aqui aparece a explicação de por que a oportunidade aparece, gerada pela formação de "
    "cada egresso."
)

AVISOS = {
    "cadastrada": "Oportunidade salva como rascunho.",
    "editada": "Alterações salvas.",
    "publicada": "Oportunidade publicada.",
    "retirada": "Oportunidade retirada da divulgação.",
}

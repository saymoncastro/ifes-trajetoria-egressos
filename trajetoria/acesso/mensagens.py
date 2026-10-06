"""Vocabulário fechado da entrada (018 contracts/rotas)."""

NAO_CONFIRMADA = "Não foi possível confirmar os dados informados."
ESPERA = "Aguarde alguns instantes antes de tentar novamente."
INDISPONIVEL = "Não foi possível verificar agora. Tente novamente em instantes."
BASE_INDEVIDA = "A entrada de demonstração não pode ser usada com este banco de dados."
ERROS = {
    "cpf": "Confira o CPF informado.",
    "data_nascimento": "Confira a data de nascimento informada.",
}

# 023 (FR-001, FR-003, FR-030): avisos de chegada à entrada, por código de lista fechada.
SESSAO_ENCERRADA = (
    "Por segurança, confirme seus dados de novo para continuar. O que você já tinha salvo "
    "continua guardado."
)
ENVIO_GUARDADO = "O que você marcou nesta parte foi guardado e volta assim que você confirmar."
SELO_VENCIDO = "Por segurança, confirme seus dados de novo para continuar."
# 023 (FR-021): os dois passos de NAO_CONFIRMADA, iguais para toda causa (018 FR-032).
PASSO_CONFERIR = "Confira se o CPF e a data de nascimento estão certos."
PASSO_INFORMAR = (
    "Se estiverem certos, sua formação pode ainda não estar na nossa base. Você pode "
    "informá-la, e ela passará por verificação institucional."
)

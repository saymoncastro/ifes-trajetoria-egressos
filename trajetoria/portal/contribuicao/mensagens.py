"""Textos da contribuição (026; spec FR-007, FR-014; plan R4). Provisórios: a redação final é
DP-801 (CPAEG e ACS).

Nenhum texto promete resposta, prazo, vaga, remuneração ou certificado (FR-014), e valem as
vedações da ADR 0009 (decisão 7) e da 025. Mudar o texto de ciência exige subir
`VERSAO_DA_CIENCIA`: a versão confirmada é gravada em cada manifestação (XVII).
"""

from trajetoria.portal.models import Forma

VERSAO_DA_CIENCIA = "2026-10-09.1"

DESCRICOES = {
    Forma.MENTORIA: "Acompanhar estudantes ou recém-formados da sua área.",
    Forma.EXPERIENCIA: "Conversa, palestra ou roda com estudantes.",
    Forma.OPORTUNIDADE: "Vaga, estágio, curso ou programa da organização em que você atua.",
    Forma.PESQUISA_EXTENSAO: "Participar de projetos com professores e estudantes.",
    Forma.PARCERIA: "Aproximar o Ifes da organização em que você atua.",
    Forma.HISTORIA: "Dizer à unidade que você topa contar sua trajetória.",
}


def destino(unidade: str, *, inicio: bool = False) -> str:
    """Quem recebe, em texto: a unidade copiada da formação, ou o Ifes quando a formação não
    tem unidade registrada."""
    texto = f"a unidade {unidade}" if unidade else "o Ifes"
    return texto[0].upper() + texto[1:] if inicio else texto


def quem_recebe(unidade: str) -> str:
    """Rótulo curto, para linhas de lista: "Unidade Vila Velha" ou "Ifes"."""
    return f"Unidade {unidade}" if unidade else "Ifes"


def da_unidade(unidade: str) -> str:
    return f"da unidade {unidade}" if unidade else "do Ifes"


# --- Egresso: escolha -----------------------------------------------------------------------

TITULO = "Contribuir com o Ifes"
INTRODUCAO = (
    "Escolha como você quer contribuir. A unidade da formação que você escolher recebe e pode "
    "entrar em contato com você."
)
LEGENDA_FORMA = "Como você quer contribuir?"
LEGENDA_FORMACAO = "Por qual formação?"
NOTA_FORMACAO = "A unidade dessa formação recebe."
ROTULO_MENSAGEM = "Mensagem"
OPCIONAL = "(opcional)"
DICA_MENSAGEM = "Até 500 caracteres. Não inclua CPF, endereço ou outros dados pessoais."
CONTINUAR = "Continuar"
VOLTAR_AO_INICIO = "Voltar ao Início"
SEM_UNIDADE = "sem unidade registrada"

# --- Egresso: confirmação -------------------------------------------------------------------

CONFIRMAR_TITULO = "Confira e envie"
RESUMO_FORMA = "Como"
RESUMO_FORMACAO = "Formação"
RESUMO_DESTINO = "Quem recebe"
RESUMO_MENSAGEM = "Mensagem"
CIENCIA_TITULO = "O que acontece depois"


def ciencia(unidade: str) -> list[str]:
    """O texto de ciência da versão `VERSAO_DA_CIENCIA` (FR-007)."""
    return [
        f"{destino(unidade, inicio=True)} recebe sua contribuição.",
        "Se houver interesse, o Ifes entra em contato pelo e-mail que você informar. Não há "
        "prazo garantido.",
        "Quando o contato for registrado, isso aparece em Suas contribuições.",
        "Este e-mail é usado só para responder sobre esta contribuição. Ele não inclui você em "
        "convites de pesquisa.",
        "Você pode retirar a contribuição quando quiser.",
    ]


VERSAO_TEXTO = "Texto de ciência, versão {versao} (provisório)."
ROTULO_EMAIL = "E-mail para a resposta"
DICA_EMAIL = "Pode ser o mesmo que você usa em outros contatos com o Ifes."
ENVIAR = "Enviar contribuição"
VOLTAR_E_ALTERAR = "Voltar e alterar"

RESUMO_DE_ERROS = "Confira o que falta"
ERROS = {
    "forma": "Escolha como você quer contribuir.",
    "formacao": "Escolha uma das suas formações.",
    "mensagem": "Escreva no máximo 500 caracteres.",
    "email": "Informe um e-mail válido, por exemplo nome@provedor.com.br.",
    "duplicada": (
        "Você já enviou essa contribuição por esta formação, e ela continua ativa. Veja em "
        "Suas contribuições."
    ),
    "ciencia": (
        "O texto sobre o que acontece depois foi atualizado. Confira de novo antes de enviar."
    ),
}

# --- Egresso: detalhe, lista e retirada -----------------------------------------------------

DETALHE_TITULO = "Sua contribuição"
LISTA_TITULO = "Suas contribuições"
LISTA_VAZIA = "Você ainda não enviou contribuições."
SITUACAO_ENVIADA = "Enviada em {data}. O contato ainda não foi registrado."
SITUACAO_ENVIADA_NA_LISTA = "O contato ainda não foi registrado."
SITUACAO_CONTATO = "{destino} registrou contato em {data}."
SITUACAO_RETIRADA = "Retirada em {data}."
LINHA_DA_LISTA = "{formacao} · {quem_recebe} · enviada em {data}"
VER_DETALHES = "Ver detalhes"
CONTRIBUIR_DE_NOVO = "Contribuir de novo"
RETIRAR = "Retirar"
RETIRAR_ESTA = "Retirar esta contribuição"
RETIRAR_TITULO = "Retirar contribuição"
RETIRAR_TEXTO = (
    "Depois de retirada, ela sai da lista {da_unidade}. A retirada não pode ser desfeita; para "
    "contribuir de novo, envie uma nova."
)
CANCELAR = "Cancelar"
FORMACAO_NAO_ENCONTRADA = "Formação não encontrada nos registros"
AVISOS = {
    "enviada": "Contribuição enviada.",
    "retirada": "Contribuição retirada.",
}

# --- Início ---------------------------------------------------------------------------------

INICIO_TITULO = "Contribuir com o Ifes"
INICIO_TEXTO = (
    "Você pode se oferecer para conversar com estudantes, ser mentor, divulgar uma vaga da sua "
    "área ou propor uma parceria. A unidade da sua formação recebe."
)
INICIO_ACAO = "Quero contribuir"
INICIO_SUAS = "Suas contribuições"

# --- Unidade --------------------------------------------------------------------------------

UNIDADE_TITULO = "Contribuições recebidas"
UNIDADE_INTRODUCAO = (
    "Contribuições ativas das unidades da sua atuação. O contato com o egresso é feito fora do "
    "sistema, pelo e-mail informado para a contribuição."
)
UNIDADE_TABELA = "Contribuições recebidas no escopo da sua atuação"
UNIDADE_VAZIA = "Nenhuma contribuição ativa no escopo da sua atuação."
UNIDADE_RECUSA = "As contribuições recebidas não estão disponíveis para esta atuação."
EXPORTAR = "Exportar CSV"
VER_OPORTUNIDADES = "Curadoria de oportunidades"
SEM_CONTATO = "Sem contato registrado"
CONTATO_EM = "Contato registrado em {data}"
REGISTRAR_CONTATO = "Registrar contato feito"
CONTATO_TEXTO = (
    "Registre só depois de entrar em contato com o egresso. Ele verá em Suas contribuições que "
    "{destino} registrou contato, com a data. O registro não pode ser desfeito."
)
CONTATO_AVISO = "Contato registrado."
CONFLITO_TITULO = "Ação não disponível"
CONFLITO = (
    "Esta contribuição mudou desde que você abriu a página: foi retirada pelo egresso ou o "
    "contato já foi registrado."
)
VOLTAR_A_LISTA = "Voltar às contribuições recebidas"
SEM_NOME = "Egresso sem nome informado"

CSV_CABECALHO = (
    "recebida_em", "egresso", "formacao", "unidade", "forma", "mensagem", "email", "situacao",
)

from tests.editor.construcao_editor import texto_visivel


def formulario(cliente, url):
    return cliente.get(url)


def enviar(cliente, url, dados):
    return cliente.post(url, dados)


def erros(resposta):
    return resposta.context["formulario"].errors


def acoes(resposta):
    texto = texto_visivel(resposta)
    return tuple(
        a for a in ("Editar configuração", "Abrir coleta", "Encerrar coleta") if a in texto
    )

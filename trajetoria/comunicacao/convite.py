"""Modelo institucional não editável; um renderer para prévia e transporte."""

from dataclasses import dataclass

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from trajetoria.comunicacao.seguranca import (
    NOME_REMETENTE,
    REMETENTE,
    validar_conteudo,
    validar_mensagem,
    validar_url,
)


@dataclass(frozen=True)
class Convite:
    assunto: str
    texto: str
    html: str
    url: str
    remetente: str = REMETENTE

    def mensagem(self, destinatario, *, connection=None):
        msg = EmailMultiAlternatives(
            self.assunto, self.texto, self.remetente, [destinatario], connection=connection
        )
        msg.attach_alternative(self.html, "text/html")
        validar_mensagem(msg)
        return msg


def renderizar_convite(nome_pessoa, nome_campanha, url_entrada):
    if any(c in nome_campanha for c in "\r\n"):
        raise ValueError("cabecalho_invalido")
    validar_url(url_entrada)
    dados = {
        "saudacao": f"Olá, {nome_pessoa}!" if nome_pessoa else "Olá!",
        "campanha": nome_campanha,
        "url": url_entrada,
        "assinatura": NOME_REMETENTE,
    }
    texto = render_to_string("comunicacao/convite.txt", dados)
    html = render_to_string("comunicacao/convite.html", dados)
    validar_conteudo(texto, html)
    return Convite(f"Convite para a pesquisa — {nome_campanha}", texto, html, url_entrada)

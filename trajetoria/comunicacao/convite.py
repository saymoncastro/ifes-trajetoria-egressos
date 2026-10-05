"""Modelo institucional não editável; um renderer para prévia e transporte (016 FR-015 a
FR-020; 020 FR-027, FR-035).

Dois pares de templates fixos: o de demonstração da 016 (teste e demonstração) e o
provisório do modo real, identificado como pendente de aprovação (DP-2003; 008/DP-801).
Personalização só pela saudação com o nome e pelo nome da Campanha. Link neutro igual para
todos, sem identificador de Pessoa, Conclusão, Lote, membro ou token.
"""

from dataclasses import dataclass

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from trajetoria.comunicacao.seguranca import (
    DEMONSTRACAO,
    NOME_REMETENTE,
    REAL,
    REMETENTE,
    validar_conteudo,
    validar_mensagem,
    validar_remetente,
    validar_url,
)

ASSINATURA_REAL = "Instituto Federal do Espírito Santo — acompanhamento de egressos"


@dataclass(frozen=True)
class Convite:
    assunto: str
    texto: str
    html: str
    url: str
    remetente: str = REMETENTE
    modo: str = DEMONSTRACAO

    def mensagem(self, destinatario, *, connection=None):
        msg = EmailMultiAlternatives(
            self.assunto, self.texto, self.remetente, [destinatario], connection=connection
        )
        msg.attach_alternative(self.html, "text/html")
        validar_mensagem(msg, modo=self.modo, remetente=self.remetente, url_permitida=self.url)
        return msg


def renderizar_convite(nome_pessoa, nome_campanha, url_entrada, *, modo=DEMONSTRACAO,
                       remetente=REMETENTE):
    if any(c in nome_campanha for c in "\r\n"):
        raise ValueError("cabecalho_invalido")
    validar_url(url_entrada, modo)
    validar_remetente(remetente, modo)
    real = modo == REAL
    dados = {
        "saudacao": f"Olá, {nome_pessoa}!" if nome_pessoa else "Olá!",
        "campanha": nome_campanha,
        "url": url_entrada,
        "assinatura": ASSINATURA_REAL if real else NOME_REMETENTE,
    }
    base = "comunicacao/convite_real" if real else "comunicacao/convite"
    texto = render_to_string(f"{base}.txt", dados)
    html = render_to_string(f"{base}.html", dados)
    validar_conteudo(texto, html, url_entrada, modo)
    return Convite(
        f"Convite para a pesquisa — {nome_campanha}", texto, html, url_entrada, remetente, modo
    )

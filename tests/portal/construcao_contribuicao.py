"""Auxiliares dos testes da Feature 026 (não são testes). As manifestações são criadas só pelas
operações, como as fictícias da demonstração."""

from tests.participacao import construcao as c
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.portal.contribuicao import operacoes
from trajetoria.portal.contribuicao.mensagens import VERSAO_DA_CIENCIA

OPERADOR_A = "demonstracao:operador-a"  # CPAEG
OPERADOR_B = "demonstracao:operador-b"  # CSAEG de Vitória
OPERADOR_C = "demonstracao:operador-c"  # sem vínculo
ESCOPO_A = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
ESCOPO_VITORIA = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vitória"}))
ESCOPO_VILA_VELHA = EscopoDeAcompanhamento(
    institucional=False, unidades=frozenset({"Vila Velha"})
)
EMAIL = "egresso.contribuicao@example.invalid"
MENSAGEM = "Posso conversar com as turmas sobre a carreira."


def conclusao(pessoa, curso: str):
    return pessoa.conclusoes.get(curso=curso)


def registrar(pessoa, conclusao=None, *, forma="experiencia", mensagem=MENSAGEM, email=EMAIL,
              agora=None):
    conclusao = conclusao or pessoa.conclusoes.first()
    return operacoes.registrar(
        pessoa, conclusao_id=conclusao.pk, forma=forma, mensagem=mensagem, email=email,
        versao_da_ciencia=VERSAO_DA_CIENCIA, agora=agora or c.NO_PERIODO,
    )


def escolha(conclusao, *, forma="experiencia", mensagem=MENSAGEM) -> dict:
    return {"forma": forma, "formacao": str(conclusao.pk), "mensagem": mensagem}


def confirmacao(conclusao, *, email=EMAIL, versao=VERSAO_DA_CIENCIA, **extra) -> dict:
    return {**escolha(conclusao, **extra), "email": email, "versao": versao}

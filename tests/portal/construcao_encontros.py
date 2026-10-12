"""Auxiliares dos testes da Feature 031 (não são testes). Os encontros são criados só pelas
operações, como os fictícios da demonstração. O relógio dos testes do Portal é
`c.NO_PERIODO` (tests/portal/conftest.py)."""

from datetime import timedelta

from tests.participacao import construcao as c
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.portal.encontros import operacoes
from trajetoria.portal.encontros.mensagens import VERSAO_DA_CIENCIA, VERSAO_DO_TERMO
from trajetoria.portal.encontros.operacoes import Proposta

OPERADOR_A = "demonstracao:operador-a"  # CPAEG
OPERADOR_B = "demonstracao:operador-b"  # CSAEG de Vitória
OPERADOR_C = "demonstracao:operador-c"  # sem vínculo
CPAEG = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
VITORIA = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vitória"}))
VILA_VELHA = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vila Velha"}))
LINK = "https://meet.exemplo.org/sala-de-teste"
INICIO = c.NO_PERIODO + timedelta(days=10, hours=7)  # 11/05/2027, 19h
TITULO = "Tecnologia na sala de aula"


def proposta(conclusao, **campos) -> Proposta:
    dados = {
        "titulo": TITULO, "descricao": "Conversa entre egressos que dão aula.",
        "nome_apresentacao": "Maria E.", "inicio": INICIO,
        "termino": INICIO + timedelta(minutes=90), "publico_unidades": None,
        "publico_niveis": None, "publico_cursos": None, "link": LINK,
        "conclusao_origem_id": conclusao.pk if conclusao else None,
    }
    dados.update(campos)
    return Proposta(**dados)


def propor(pessoa, conclusao=None, *, agora=None, **campos):
    conclusao = conclusao or pessoa.conclusoes.first()
    return operacoes.propor(pessoa, proposta(conclusao, **campos),
                            versao_do_termo=VERSAO_DO_TERMO, agora=agora or c.NO_PERIODO)


def publicado(pessoa, conclusao=None, *, escopo=CPAEG, **campos):
    encontro = propor(pessoa, conclusao, **campos)
    return operacoes.publicar(encontro.pk, operador=OPERADOR_A, escopo=escopo,
                              agora=c.NO_PERIODO)


def confirmar(pessoa, encontro, agora=None):
    return operacoes.confirmar(pessoa, encontro.pk, versao_da_ciencia=VERSAO_DA_CIENCIA,
                               agora=agora or c.NO_PERIODO)


def formulario(conclusao, **campos) -> dict:
    """Os campos do POST de `/encontros/propor/` e de `/encontros/propor/enviar/`."""
    local = INICIO.astimezone(c.NO_PERIODO.tzinfo)
    dados = {
        "titulo": TITULO, "descricao": "Conversa entre egressos que dão aula.",
        "nome": "Maria E.", "data": local.date().isoformat(), "inicio": "19:00",
        "termino": "20:30", "publico": "todos", "link": LINK, "origem": str(conclusao.pk),
    }
    dados.update(campos)
    return {k: v for k, v in dados.items() if v is not None}

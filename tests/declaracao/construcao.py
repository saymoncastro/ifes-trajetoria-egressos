from datetime import date
from uuid import uuid4

from tests.participacao.construcao import NO_PERIODO

CPF = "00000000949"
DATA = date(1998, 4, 12)
DADOS = dict(
    nome="Pessoa Fictícia",
    unidade="Serra",
    nivel="Técnico",
    curso="Informática",
    ano_conclusao=2004,
)


def declaracao_concluida(campanha, **campos):
    from trajetoria.acesso.chaves import chaves_de_acesso, identificador_cpf, verificador
    from trajetoria.declaracao.models import DadosConsultaAcervo, FormacaoDeclarada
    from trajetoria.declaracao.selo import selar_consulta
    from trajetoria.participacao.models import Participacao

    chaves = chaves_de_acesso()
    dados = DADOS | campos
    formacao = FormacaoDeclarada.objects.create(
        **dados,
        identificador_cpf=identificador_cpf(CPF, chaves),
        verificador=verificador(CPF, DATA, chaves),
        chave_de_criacao=uuid4(),
        declarada_em=NO_PERIODO,
    )
    DadosConsultaAcervo.objects.create(
        formacao=formacao, selado=selar_consulta(formacao.pk, CPF, DATA)
    )
    Participacao.objects.create(
        campanha=campanha,
        formacao_declarada=formacao,
        iniciada_em=NO_PERIODO,
        concluida_em=NO_PERIODO,
    )
    return formacao


def validar(formacao, conclusao=None, resultado="CONFIRMADA", fora=False, conflito=False):
    from trajetoria.declaracao.models import ValidacaoDaFormacao

    return ValidacaoDaFormacao.objects.create(
        formacao=formacao,
        conclusao=conclusao,
        resultado=resultado,
        fora_da_abrangencia_na_validacao=fora,
        conflito_detectado_na_validacao=conflito,
        operador="A",
        registrada_em=NO_PERIODO,
    )

from uuid import uuid4

import pytest

from tests.declaracao.construcao import CPF, DADOS, DATA
from tests.participacao import construcao as c
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.declaracao.models import DadosConsultaAcervo, FormacaoDeclarada
from trajetoria.declaracao.operacoes import Ambiguidade, SemCampanha, iniciar_participacao_declarada
from trajetoria.declaracao.selo import ChaveIndisponivel, SeloInvalido, abrir_consulta
from trajetoria.participacao.models import Participacao

pytestmark = pytest.mark.django_db


def test_atomico_idempotente():
    c.campanha_aberta(c.instrumento().versao)
    antes = (
        Pessoa.objects.count(),
        ConclusaoAcademica.objects.count(),
        MaterialDeVerificacao.objects.count(),
    )
    chave = uuid4()
    p, criada = iniciar_participacao_declarada(
        DADOS, CPF, DATA, chave, origem="local", agora=c.NO_PERIODO
    )
    assert criada and p.conclusao_id is None
    assert abrir_consulta(DadosConsultaAcervo.objects.get(formacao=p.formacao_declarada)) == (
        CPF,
        DATA,
    )
    assert iniciar_participacao_declarada(
        DADOS, CPF, DATA, chave, origem="local", agora=c.NO_PERIODO
    ) == (p, False)
    with pytest.raises(SeloInvalido):
        iniciar_participacao_declarada(
            DADOS, "00000000191", DATA, chave, origem="local", agora=c.NO_PERIODO
        )
    assert FormacaoDeclarada.objects.count() == Participacao.objects.count() == 1
    assert antes == (
        Pessoa.objects.count(),
        ConclusaoAcademica.objects.count(),
        MaterialDeVerificacao.objects.count(),
    )


def test_sem_campanha_e_ambiguidade():
    with pytest.raises(SemCampanha):
        iniciar_participacao_declarada(
            DADOS, CPF, DATA, uuid4(), origem="local", agora=c.NO_PERIODO
        )
    for _ in range(2):
        c.campanha_aberta(c.instrumento().versao)
    with pytest.raises(Ambiguidade):
        iniciar_participacao_declarada(
            DADOS, CPF, DATA, uuid4(), origem="local", agora=c.NO_PERIODO
        )
    assert not FormacaoDeclarada.objects.exists()


def test_chave_falha_sem_escrita(settings):
    c.campanha_aberta(c.instrumento().versao)
    settings.TRAJETORIA_CHAVE_CONSULTA_ACERVO = ""
    with pytest.raises(ChaveIndisponivel):
        iniciar_participacao_declarada(
            DADOS, CPF, DATA, uuid4(), origem="local", agora=c.NO_PERIODO
        )
    assert not FormacaoDeclarada.objects.exists()


def test_limitacao_da_origem_reusada_e_idempotencia_preservada():
    from trajetoria.acesso import limitacao
    from trajetoria.acesso.chaves import chave_de_origem, chaves_de_acesso
    from trajetoria.declaracao.operacoes import EmEspera

    c.campanha_aberta(c.instrumento().versao)
    chave = uuid4()
    p, _ = iniciar_participacao_declarada(
        DADOS, CPF, DATA, chave, origem="local", agora=c.NO_PERIODO,
    )
    origem = "acesso:origem:" + chave_de_origem("local", chaves_de_acesso())
    for _ in range(100):
        limitacao.registrar(limitacao.ORIGEM, origem, c.NO_PERIODO)
    with pytest.raises(EmEspera):
        iniciar_participacao_declarada(
            DADOS, CPF, DATA, uuid4(), origem="local", agora=c.NO_PERIODO,
        )
    assert iniciar_participacao_declarada(
        DADOS, CPF, DATA, chave, origem="local", agora=c.NO_PERIODO,
    ) == (p, False)
    assert FormacaoDeclarada.objects.count() == 1

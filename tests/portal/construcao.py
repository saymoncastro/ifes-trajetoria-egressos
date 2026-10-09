"""Auxiliares dos testes da Feature 024 (não são testes). Pessoas da fonte simulada, como em
toda a demonstração; reutiliza as construções da 008, da 018 e da 021 sem alterá-las."""

from django.db.models import Model

from tests.acesso.construcao import DIEGO, MARIA, preparar_material
from tests.interface import construcao_interface as ci
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.contato.models import ContatoDaPessoa
from trajetoria.declaracao.models import FormacaoDeclarada
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.participacao.models import Participacao, Resposta
from trajetoria.portal.models import Oportunidade
from trajetoria.video.models import GeracaoDeVideo

DADOS = {"SIM-P-0003": MARIA, "SIM-P-0004": DIEGO}
CONTADOS: tuple[type[Model], ...] = (
    Pessoa, ConclusaoAcademica, Participacao, Resposta, ContatoDaPessoa, FormacaoDeclarada,
    GeracaoDeVideo, Oportunidade,
)


def contagens() -> dict[str, int]:
    return {m._meta.label: m.objects.count() for m in CONTADOS}


def pessoa_sem_conclusao() -> Pessoa:
    """Pessoa da fonte simulada sem nenhuma Conclusão Acadêmica. A demonstração não tem uma
    (a incorporação ignora quem não concluiu; research R13): só existe em teste."""
    return Pessoa.objects.create(
        fonte=FonteSimulada.codigo, id_externo="SIM-P-9024", nome="Pessoa Sem Conclusão"
    )


def com_material(id_externo: str) -> Pessoa:
    preparar_material(id_externo)
    return Pessoa.objects.get(fonte=FonteSimulada.codigo, id_externo=id_externo)


def post_de_identificacao(client, endereco: str, id_externo: str):
    dados = DADOS[id_externo]
    return client.post(endereco, {"cpf": dados.cpf, "data_nascimento": dados.nascimento})


def entrar_pelo_portal(client, id_externo: str):
    return post_de_identificacao(client, "/entrar/", id_externo)


def entrar_pelo_convite(client, id_externo: str):
    return post_de_identificacao(client, "/acesso/", id_externo)


def entrar(client, pessoa) -> None:
    """Sessão de Pessoa já estabelecida, sem passar pela identificação."""
    ci.entrar_como(client, pessoa)


def sessao_de_declarante(client, formacao) -> None:
    from django.conf import settings

    from tests.participacao import construcao as c

    sessao = client.session
    sessao.update({
        "declaracao.formacoes": [str(formacao.pk)],
        "declaracao.confirmada_em": c.NO_PERIODO.isoformat(),
        "declaracao.ultimo_uso": c.NO_PERIODO.isoformat(),
    })
    sessao.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key


def envio_guardado(client, settings, relogio, pessoa):
    """Participação em rascunho com um envio guardado pela sessão expirada (023 FR-001 a
    FR-006). Devolve o `id` da Participação."""
    from datetime import timedelta

    from trajetoria.acesso import pendente

    participacao = ci.participacao_de(ci.iniciar(client, pessoa))
    settings.TRAJETORIA_SESSAO_INATIVIDADE = timedelta(minutes=1)
    relogio.agora += timedelta(seconds=61)
    resposta = client.post(f"/participacoes/{participacao}/secoes/1/", {"p1": "1"})
    assert resposta["Location"] == "/acesso/?aviso=sessao"
    assert pendente.CHAVE in client.session
    return participacao

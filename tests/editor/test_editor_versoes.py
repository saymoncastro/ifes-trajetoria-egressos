"""Versões no editor (US1, US3, US4; FR-013 a FR-017)."""

import uuid

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.instrumento import operacoes as op

pytestmark = pytest.mark.django_db


# --- US1: listar ---------------------------------------------------------------------------


def test_lista_versoes_com_estado_escrito_e_origem(client, baseline, publicada):
    resposta = client.get(f"/editor/pesquisas/{baseline.pesquisa_id}/")
    assert resposta.status_code == 200
    texto = ce.texto_visivel(resposta)
    assert "Rascunho" in texto
    assert f"Publicada em {publicada.publicada_em.astimezone().strftime('%d/%m/%Y')}" in texto
    assert f"criada a partir de «{baseline.designacao}»" in texto
    html = resposta.content.decode()
    assert f'href="/editor/versoes/{baseline.pk}/"' in html
    assert f'href="/editor/versoes/{publicada.pk}/nova-a-partir/"' in html
    assert ce.padroes_tecnicos(resposta) == []


def test_pesquisa_sem_versoes(client, pesquisa):
    resposta = client.get(f"/editor/pesquisas/{pesquisa.pk}/")
    assert "Ainda não há Versões" in ce.texto_visivel(resposta)
    assert f'href="/editor/pesquisas/{pesquisa.pk}/versoes/nova/"' in resposta.content.decode()


def test_pesquisa_inexistente(client, db):
    assert client.get(f"/editor/pesquisas/{uuid.uuid4()}/").status_code == 404


def test_versao_vazia_criada_por_operacao_aparece(client, pesquisa):
    op.criar_versao(pesquisa, "2026 — teste")
    assert "2026 — teste" in ce.texto_visivel(client.get(f"/editor/pesquisas/{pesquisa.pk}/"))


# --- US3: criar Versão em rascunho ---------------------------------------------------------


def test_cria_versao_vazia_em_rascunho(client, pesquisa):
    resposta = client.post(
        f"/editor/pesquisas/{pesquisa.pk}/versoes/nova/", {"designacao": "2026 — teste"}
    )
    versao = pesquisa.versoes.get(designacao="2026 — teste")
    assert resposta["Location"] == f"/editor/versoes/{versao.pk}/?aviso=versao-criada"
    assert not versao.publicada and versao.origem_id is None and versao.secoes.count() == 0


def test_designacao_repetida_recusada_no_campo(client, pesquisa):
    op.criar_versao(pesquisa, "2026 — teste")
    antes = ce.contagens()
    resposta = client.post(
        f"/editor/pesquisas/{pesquisa.pk}/versoes/nova/", {"designacao": "2026 — teste"}
    )
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Já existe uma Versão com esta designação nesta Pesquisa." in html
    assert 'id="id_designacao-erro"' in html and 'value="2026 — teste"' in html
    assert ce.contagens() == antes


def test_designacao_vazia_recusada(client, pesquisa):
    resposta = client.post(f"/editor/pesquisas/{pesquisa.pk}/versoes/nova/", {"designacao": ""})
    assert resposta.status_code == 200 and "Informe o texto." in resposta.content.decode()
    assert pesquisa.versoes.count() == 0


# --- US4: nova Versão a partir de outra ------------------------------------------------------


def _criar_a_partir(client, origem, designacao):
    return client.post(f"/editor/versoes/{origem.pk}/nova-a-partir/", {"designacao": designacao})


def test_copia_da_baseline_equivalente_e_independente(client, baseline):
    from tests.instrumento.construcao import sem_identidades
    from trajetoria.instrumento.conteudo import conteudo_da_versao

    antes = ce.retrato(baseline)
    resposta = _criar_a_partir(client, baseline, "Cópia de trabalho")
    copia = baseline.pesquisa.versoes.get(designacao="Cópia de trabalho")
    assert resposta["Location"] == f"/editor/versoes/{copia.pk}/?aviso=versao-criada"
    assert not copia.publicada and copia.origem_id == baseline.pk
    assert sem_identidades(conteudo_da_versao(copia)) == sem_identidades(
        conteudo_da_versao(baseline)
    )
    lista = ce.texto_visivel(client.get(f"/editor/pesquisas/{baseline.pesquisa_id}/"))
    assert f"criada a partir de «{baseline.designacao}»" in lista
    # Editar a cópia pelo editor não toca a origem.
    pergunta = ce.pergunta(copia, 2, 1)
    client.post(
        f"/editor/perguntas/{pergunta.pk}/editar/",
        {"texto": "Texto alterado na cópia", "obrigatoria": "sim"},
    )
    assert ce.retrato(baseline) == antes


def test_copia_de_publicada(client, publicada):
    antes = ce.retrato(publicada)
    resposta = _criar_a_partir(client, publicada, "Nova a partir da publicada")
    nova = publicada.pesquisa.versoes.get(designacao="Nova a partir da publicada")
    assert resposta.status_code == 302 and not nova.publicada and nova.origem_id == publicada.pk
    assert ce.retrato(publicada) == antes


def test_copia_com_designacao_repetida_nao_cria_nada(client, baseline):
    antes = ce.contagens()
    resposta = _criar_a_partir(client, baseline, baseline.designacao)
    assert resposta.status_code == 200
    assert "Já existe uma Versão com esta designação" in resposta.content.decode()
    assert ce.contagens() == antes


def test_formulario_da_copia_explica_independencia(client, baseline):
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{baseline.pk}/nova-a-partir/"))
    assert "independente" in texto and "rascunho" in texto

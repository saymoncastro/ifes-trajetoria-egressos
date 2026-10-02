"""Diagnóstico técnico (US11; FR-066 a FR-075; contracts/diagnostico.md §2).

O diagnóstico é comparado com as capacidades **reais** da 002 (`verificar_completude`) e
da 006 (`secoes_nao_suportadas`) — nunca com uma lista de regras escrita no teste.
"""

import pytest

from tests.editor import construcao_editor as ce
from tests.participacao.construcao import FIM, pergunta_mem, secao_mem
from trajetoria.editor.diagnostico import diagnosticar
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.instrumento.regras import Motivo, verificar_completude
from trajetoria.participacao import regras as regras_006
from trajetoria.participacao.percurso import secoes_nao_suportadas

pytestmark = pytest.mark.django_db
TEXTO = TipoPergunta.TEXTO_CURTO
COM_PROBLEMAS = "Com problemas de estrutura"
INCOMPATIVEL = "Estrutura válida, mas incompatível com a jornada atual"
SEM_IMPEDIMENTOS = "Sem impedimentos técnicos conhecidos"


@pytest.fixture
def problematica(pesquisa):
    """Um problema de cada: Opções insuficientes, Seção sem Perguntas, encaminhamento e
    desvio não posteriores (A) e duas Perguntas com desvio numa Seção (B)."""
    return ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(opcoes=("Só",)), titulo="S1"),
        secao_mem(titulo="S2"),
        secao_mem(pergunta_mem(tipo=TEXTO), encaminhamento=1, titulo="S3"),
        secao_mem(pergunta_mem(regras={"Sim": 4}), titulo="S4"),
        secao_mem(pergunta_mem(regras={"Sim": 6}), pergunta_mem(regras={"Não": FIM}), titulo="S5"),
        secao_mem(pergunta_mem(tipo=TEXTO), titulo="S6"),
    )


def _diagnostico(client, versao):
    return client.get(f"/editor/versoes/{versao.pk}/diagnostico/")


# --- diagnosticar: preserva os problemas concretos das duas fontes ----------------------


def test_um_problema_por_violacao_da_002_e_por_secao_da_006(problematica):
    diagnostico = diagnosticar(problematica)
    violacoes = verificar_completude(problematica)
    assert [p.causa for p in diagnostico.estrutura] == [v.motivo for v in violacoes]
    assert [p.elemento_id for p in diagnostico.estrutura] == [v.elemento for v in violacoes]
    assert {p.origem for p in diagnostico.estrutura} == {"estrutura"}
    nao_suportadas = secoes_nao_suportadas(conteudo_da_versao(problematica))
    assert [p.elemento_id for p in diagnostico.jornada] == [s.id for s in nao_suportadas]
    assert all(p.causa is regras_006.Motivo.ESTRUTURA_NAO_SUPORTADA for p in diagnostico.jornada)
    assert {p.origem for p in diagnostico.jornada} == {"jornada"}
    assert diagnostico.estrutura_valida is (not diagnostico.estrutura) is False
    assert diagnostico.compativel_com_jornada is False
    assert diagnostico.sem_impedimentos_conhecidos is False


def test_versao_sem_secoes(client, versao):
    diagnostico = diagnosticar(versao)
    assert [p.causa for p in diagnostico.estrutura] == [Motivo.SEM_SECOES]
    texto = ce.texto_visivel(_diagnostico(client, versao))
    assert COM_PROBLEMAS in texto and "A Versão não tem Seções" in texto


def test_todos_os_problemas_numa_unica_consulta(client, problematica):
    resposta = _diagnostico(client, problematica)
    assert resposta.status_code == 200
    texto = ce.texto_visivel(resposta)
    assert COM_PROBLEMAS in texto
    s1 = ce.secao(problematica, 1)
    pergunta = ce.pergunta(problematica, 1, 1)
    esperados = [
        f"A Pergunta «{pergunta.texto}» (Pergunta 1 da Seção 1) precisa ter pelo menos duas "
        "Opções.",
        "A Seção 2 — S2 não tem Perguntas.",
        "O encaminhamento da Seção 3 — S3: o destino precisa ser uma Seção posterior.",
        "O desvio da Opção «Sim» da Pergunta 1 da Seção 4: o destino precisa ser uma Seção "
        "posterior.",
        "A jornada atual não consegue aplicar mais de uma Pergunta com desvio na mesma Seção.",
    ]
    posicoes = [texto.index(e) for e in esperados]
    assert posicoes == sorted(posicoes)  # A antes de B, cada um na ordem da fonte
    html = resposta.content.decode()
    assert f'href="/editor/perguntas/{pergunta.pk}/"' in html
    assert f'href="/editor/secoes/{ce.secao(problematica, 5).pk}/"' in html
    assert s1.titulo == "S1"
    assert 'role="alert"' not in html
    assert ce.padroes_tecnicos(resposta) == []


def test_estrutura_valida_mas_incompativel(client, pesquisa):
    versao = ce.versao_de(
        pesquisa,
        secao_mem(pergunta_mem(regras={"Sim": 2}), pergunta_mem(regras={"Não": FIM})),
        secao_mem(pergunta_mem(tipo=TEXTO)),
    )
    diagnostico = diagnosticar(versao)
    assert diagnostico.estrutura_valida and not diagnostico.compativel_com_jornada
    texto = ce.texto_visivel(_diagnostico(client, versao))
    assert INCOMPATIVEL in texto and "nenhum problema de estrutura" in texto


def test_correcao_e_recalculo_ate_sem_impedimentos(client, problematica):
    v = problematica
    pergunta_s1 = ce.pergunta(v, 1, 1)
    client.post(
        f"/editor/perguntas/{pergunta_s1.pk}/opcoes/nova/", {"texto": "Outra", "desvio": ""}
    )
    assert Motivo.OPCOES_INSUFICIENTES not in [p.causa for p in diagnosticar(v).estrutura]
    client.post(
        f"/editor/secoes/{ce.secao(v, 2).pk}/perguntas/nova/?tipo=TEXTO_CURTO",
        {"texto": "Nova", "texto_explicativo": "", "obrigatoria": "sim"},
    )
    client.post(
        f"/editor/secoes/{ce.secao(v, 3).pk}/editar/",
        {"titulo": "S3", "texto": "", "encaminhamento": ""},
    )
    sim_s4 = ce.opcao(ce.pergunta(v, 4, 1), "Sim")
    client.post(f"/editor/opcoes/{sim_s4.pk}/", {"texto": "Sim", "desvio": ""})
    intermediario = ce.texto_visivel(_diagnostico(client, v))
    assert INCOMPATIVEL in intermediario
    nao_s5 = ce.opcao(ce.pergunta(v, 5, 2), "Não")
    client.post(f"/editor/opcoes/{nao_s5.pk}/", {"texto": "Não", "desvio": ""})
    texto = ce.texto_visivel(_diagnostico(client, v))
    assert SEM_IMPEDIMENTOS in texto
    assert "Não é aprovação, homologação, autorização nem publicação." in texto
    # Coerência: a publicação da 002 (só no teste) e a jornada da 006 aceitam a Versão.
    assert secoes_nao_suportadas(conteudo_da_versao(v)) == ()
    op.publicar(v)


def test_diagnostico_nao_grava(client, problematica):
    antes = ce.retrato(problematica), ce.contagens()
    _diagnostico(client, problematica)
    client.get(f"/editor/versoes/{problematica.pk}/")
    assert (ce.retrato(problematica), ce.contagens()) == antes


def test_sem_linguagem_de_aprovacao(client, pesquisa):
    versao = ce.versao_de(pesquisa, secao_mem(pergunta_mem(tipo=TEXTO)))
    texto = ce.texto_visivel(_diagnostico(client, versao))
    assert SEM_IMPEDIMENTOS in texto
    sem_negacao = texto.replace("Não é aprovação, homologação, autorização nem publicação.", "")
    for proibido in ("pronta para publicação", "aprovada", "homologada", "autorizada"):
        assert proibido not in sem_negacao.lower()


def test_marcas_por_elemento_na_estrutura(client, problematica):
    texto = ce.texto_visivel(client.get(f"/editor/versoes/{problematica.pk}/"))
    assert COM_PROBLEMAS in texto and "Problema:" in texto
    secao = ce.texto_visivel(client.get(f"/editor/secoes/{ce.secao(problematica, 2).pk}/"))
    assert "Problema: A Seção 2 — S2 não tem Perguntas." in secao


def test_publicada_nao_tem_diagnostico(client, publicada):
    resposta = _diagnostico(client, publicada)
    assert resposta["Location"] == f"/editor/versoes/{publicada.pk}/?aviso=publicada"
    assert "Diagnóstico técnico" not in ce.texto_visivel(
        client.get(f"/editor/versoes/{publicada.pk}/")
    )


def test_marcas_de_problema_da_opcao(client, problematica):
    # Desvio da Opção «Sim» (S4) para a própria Seção: o problema é da Opção.
    alvo = "O desvio da Opção «Sim» da Pergunta 1 da Seção 4"
    pergunta = ce.pergunta(problematica, 4, 1)
    pagina = ce.texto_visivel(client.get(f"/editor/perguntas/{pergunta.pk}/"))
    assert f"Problema: {alvo}" in pagina
    secao = ce.texto_visivel(client.get(f"/editor/secoes/{ce.secao(problematica, 4).pk}/"))
    assert f"Problema: {alvo}" in secao
    estrutura = ce.texto_visivel(client.get(f"/editor/versoes/{problematica.pk}/"))
    assert f"Problema: {alvo}" in estrutura

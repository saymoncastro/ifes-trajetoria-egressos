"""Cenários ponta a ponta da spec, só por HTTP (SC-001, SC-002, SC-011).

Tudo pela interface: nenhuma operação da 002 é chamada pelo teste depois do arranjo. A
baseline é só lida e copiada; a Versão publicada vem do arranjo (como o preparo da 008).
"""

import re

import pytest

from tests.editor import construcao_editor as ce
from trajetoria.campanha.models import Campanha
from trajetoria.formulario_2024 import materializar
from trajetoria.instrumento.models import EstadoVersao, Versao

pytestmark = pytest.mark.django_db
SEM_IMPEDIMENTOS = "Sem impedimentos técnicos conhecidos"


def _local(resposta):
    return resposta["Location"].split("?")[0].split("#")[0]


def test_cenario_principal(client, baseline, publicada):
    campanhas, publicadas = (
        Campanha.objects.count(),
        Versao.objects.filter(estado=EstadoVersao.PUBLICADA).count(),
    )
    # 1–3. Pesquisas → Pesquisa → baseline (só leitura).
    assert baseline.pesquisa.nome in ce.texto_visivel(client.get("/editor/"))
    assert baseline.designacao in ce.texto_visivel(
        client.get(f"/editor/pesquisas/{baseline.pesquisa_id}/")
    )
    assert "13 Seções" in ce.texto_visivel(client.get(f"/editor/versoes/{baseline.pk}/"))
    # 4. Nova Versão a partir da baseline.
    r = client.post(
        f"/editor/versoes/{baseline.pk}/nova-a-partir/", {"designacao": "Cópia de trabalho"}
    )
    copia_url = _local(r)
    copia = Versao.objects.get(designacao="Cópia de trabalho")
    # 5. Alterar o texto de uma Pergunta.
    secao = ce.secao(copia, 2)
    pergunta = ce.pergunta(copia, 2, 1)
    r = client.post(
        f"/editor/perguntas/{pergunta.pk}/editar/",
        {"texto": "Texto revisado na cópia", "texto_explicativo": "", "obrigatoria": "sim"},
    )
    assert r.status_code == 302
    # 6–7. Nova Pergunta de escolha única com duas Opções.
    r = client.post(
        f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=ESCOLHA_UNICA",
        {"texto": "Pergunta nova", "texto_explicativo": "", "obrigatoria": "nao"},
    )
    nova_url = _local(r)
    for texto in ("Primeira", "Segunda"):
        client.post(f"{nova_url}opcoes/nova/", {"texto": texto, "desvio": ""})
    nova = secao.perguntas.get(texto="Pergunta nova")
    # 8. Subir a Pergunta e inverter as Opções.
    client.post(f"{nova_url}mover/", {"direcao": "cima"})
    segunda = nova.opcoes.get(texto="Segunda")
    client.post(f"/editor/opcoes/{segunda.pk}/mover/", {"direcao": "cima"})
    assert ce.ordem(nova.opcoes) == ["Segunda", "Primeira"]
    textos = [p.texto for p in secao.perguntas.order_by("posicao")]
    assert textos.index("Pergunta nova") == len(textos) - 2
    # 9. Obrigatória.
    client.post(
        f"{nova_url}editar/",
        {"texto": "Pergunta nova", "texto_explicativo": "", "obrigatoria": "sim"},
    )
    nova.refresh_from_db()
    assert nova.obrigatoria
    # 10. Estrutura e pré-visualização.
    assert "Pergunta nova" in ce.texto_visivel(client.get(copia_url))
    assert client.get(f"{copia_url}previa/secoes/2/").status_code == 200
    # 11–12. Diagnóstico, problema provocado e corrigido.
    r = client.post(
        f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=ESCOLHA_MULTIPLA",
        {"texto": "Sem Opções", "texto_explicativo": "", "obrigatoria": "nao"},
    )
    sem_opcoes_url = _local(r)
    texto = ce.texto_visivel(client.get(f"{copia_url}diagnostico/"))
    assert "Com problemas de estrutura" in texto and "precisa ter pelo menos duas Opções" in texto
    client.post(f"{sem_opcoes_url}remover/")
    # 13. Sem impedimentos técnicos conhecidos.
    assert SEM_IMPEDIMENTOS in ce.texto_visivel(client.get(f"{copia_url}diagnostico/"))
    # 14. Publicada: nada pode ser editado.
    p = ce.pergunta(publicada, 1, 1)
    assert (
        client.post(
            f"/editor/perguntas/{p.pk}/editar/", {"texto": "X", "obrigatoria": "sim"}
        ).status_code
        == 409
    )
    # Ao final: baseline intacta, nada publicado pelo editor, nenhuma Campanha.
    assert materializar().criada is False
    assert Campanha.objects.count() == campanhas
    assert Versao.objects.filter(estado=EstadoVersao.PUBLICADA).count() == publicadas


def test_cenario_navegacao(client, pesquisa):
    r = client.post(f"/editor/pesquisas/{pesquisa.pk}/versoes/nova/", {"designacao": "Navegação"})
    v_url = _local(r)
    versao = Versao.objects.get(designacao="Navegação")
    for titulo in ("A", "B", "C"):
        client.post(f"{v_url}secoes/nova/", {"titulo": titulo, "texto": "", "encaminhamento": ""})
    a, b, c = (ce.secao(versao, n) for n in (1, 2, 3))
    r = client.post(
        f"/editor/secoes/{a.pk}/perguntas/nova/?tipo=ESCOLHA_UNICA",
        {"texto": "Continua?", "texto_explicativo": "", "obrigatoria": "sim"},
    )
    q_url = _local(r)
    client.post(f"{q_url}opcoes/nova/", {"texto": "Sim", "desvio": ""})
    client.post(f"{q_url}opcoes/nova/", {"texto": "Não", "desvio": str(c.pk)})
    for secao in (b, c):
        client.post(
            f"/editor/secoes/{secao.pk}/perguntas/nova/?tipo=TEXTO_CURTO",
            {"texto": f"Em {secao.titulo}", "texto_explicativo": "", "obrigatoria": "nao"},
        )
    estrutura = ce.texto_visivel(client.get(f"/editor/secoes/{a.pk}/"))
    assert "«Não» → segue para a Seção 3 — C" in estrutura
    assert "finaliza o instrumento" in ce.texto_visivel(client.get(v_url))
    assert SEM_IMPEDIMENTOS in ce.texto_visivel(client.get(f"{v_url}diagnostico/"))
    # (a) segunda Pergunta com desvio na Seção A → diagnóstico B.
    r = client.post(
        f"/editor/secoes/{a.pk}/perguntas/nova/?tipo=ESCOLHA_UNICA",
        {"texto": "Outra?", "texto_explicativo": "", "obrigatoria": "sim"},
    )
    outra_url = _local(r)
    client.post(f"{outra_url}opcoes/nova/", {"texto": "Sim", "desvio": str(b.pk)})
    client.post(f"{outra_url}opcoes/nova/", {"texto": "Não", "desvio": ""})
    texto = ce.texto_visivel(client.get(f"{v_url}diagnostico/"))
    assert "Estrutura válida, mas incompatível com a jornada atual" in texto
    # (b) C sobe para antes de A → destino não posterior (diagnóstico A).
    client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "cima"})
    client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "cima"})
    texto = ce.texto_visivel(client.get(f"{v_url}diagnostico/"))
    assert (
        "Com problemas de estrutura" in texto
        and "o destino precisa ser uma Seção posterior" in texto
    )
    # Desfazer (a) e (b).
    client.post(f"{outra_url}remover/")
    client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "baixo"})
    client.post(f"/editor/secoes/{c.pk}/mover/", {"direcao": "baixo"})
    assert SEM_IMPEDIMENTOS in ce.texto_visivel(client.get(f"{v_url}diagnostico/"))
    # Troca de destino numa única gravação.
    nao = ce.opcao(ce.pergunta(versao, 1, 1), "Não")
    client.post(f"/editor/opcoes/{nao.pk}/", {"texto": "Não", "desvio": "finalizar"})
    nao.refresh_from_db()
    assert nao.regra_finaliza and nao.regra_destino_id is None


def test_duas_acoes_ate_qualquer_pergunta(client, copia):
    estrutura = client.get(f"/editor/versoes/{copia.pk}/").content.decode()
    secoes = re.findall(r'href="(/editor/secoes/[0-9a-f-]+/)"', estrutura)
    alcancaveis = set()
    for url in dict.fromkeys(secoes):
        html = client.get(url).content.decode()
        alcancaveis |= set(re.findall(r'href="/editor/perguntas/([0-9a-f-]+)/"', html))
    todas = {str(p.pk) for s in copia.secoes.all() for p in s.perguntas.all()}
    assert len(todas) == 54 and todas <= alcancaveis

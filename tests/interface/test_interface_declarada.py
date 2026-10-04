import pytest
from django.test import Client

from tests.declaracao.construcao import CPF, DATA, declaracao_concluida
from tests.participacao import construcao as c
from trajetoria.declaracao.selo import selar_transito

pytestmark = pytest.mark.django_db


def test_declarada_contexto_posse_conclusao(client, settings, monkeypatch):
    from django.utils import timezone

    settings.TRAJETORIA_DEMONSTRACAO = True
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO)
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    client.post("/declaracao/", {"selo": selar_transito(CPF, DATA)})
    url = f"/participacoes/{f.participacao.pk}/"
    r = client.get(url + "concluida/")
    html = r.content.decode()
    assert r.status_code == 200 and "Formação informada por você" in html
    assert "A formação informada passará por verificação institucional." in html
    outro = declaracao_concluida(campanha)
    assert client.get(f"/participacoes/{outro.participacao.pk}/").status_code == 404
    assert Client().get(url).status_code == 302
    p = f.participacao
    p.concluida_em = None
    p.save()
    r = client.get(url, follow=True)
    assert r.status_code == 200 and "Formação informada por você" in r.content.decode()
    assert "Você concluiu" not in r.content.decode()


def test_pessoa_nao_herda_posse_da_declaracao_validada(client, settings, monkeypatch):
    from django.utils import timezone

    from tests.acesso.construcao import preparar_material
    from tests.declaracao.construcao import validar
    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import dados_de_sessao

    settings.TRAJETORIA_DEMONSTRACAO = True
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO)
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha)
    incorporacao = preparar_material("SIM-P-0001")[0]
    x = incorporacao.pessoa.conclusoes.get()
    validar(f, x)
    sessao = client.session
    sessao.update(dados_de_sessao(incorporacao.pessoa,
        MaterialDeVerificacao.objects.get(pessoa=incorporacao.pessoa).atualizado_em, c.NO_PERIODO))
    sessao.save()
    # A confirmação da identidade institucional não permite abrir respostas declaradas.
    assert client.get(f"/participacoes/{f.participacao.pk}/").status_code == 404


def test_pessoa_ve_a_sua_conclusao_na_tela_de_ja_respondida(client, settings, monkeypatch):
    # Regressão (code review da 019): a resposta veio de uma declaração validada (FR-092), mas
    # a Pessoa vê a sua Conclusão institucional, nunca os valores declarados nem o caminho
    # do declarante.
    from django.utils import timezone

    from tests.acesso.construcao import preparar_material
    from tests.declaracao.construcao import validar
    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import dados_de_sessao

    settings.TRAJETORIA_DEMONSTRACAO = True
    monkeypatch.setattr(timezone, "now", lambda: c.NO_PERIODO)
    campanha = c.campanha_aberta(c.instrumento().versao)
    f = declaracao_concluida(campanha, curso="Curso declarado diferente")
    incorporacao = preparar_material("SIM-P-0001")[0]
    x = incorporacao.pessoa.conclusoes.get()
    validar(f, x)
    sessao = client.session
    sessao.update(dados_de_sessao(incorporacao.pessoa,
        MaterialDeVerificacao.objects.get(pessoa=incorporacao.pessoa).atualizado_em, c.NO_PERIODO))
    sessao.save()
    html = client.post("/formacoes/entrar/", {"formacao": str(x.pk)}).content.decode()
    assert x.curso in html
    assert "Curso declarado diferente" not in html
    assert "Formação informada por você" not in html
    assert 'href="/declaracao/"' not in html and 'href="/formacoes/"' in html

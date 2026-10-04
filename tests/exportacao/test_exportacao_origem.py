import pytest

from trajetoria.exportacao.contrato import COLUNAS_BASE, VERSAO_CONTRATO


def test_contrato_origem():
    assert VERSAO_CONTRATO == 2
    coluna = next(c for c in COLUNAS_BASE if c.nome == "origem_formacao")
    assert coluna.proveniencia == "derivado" and coluna.tipo_valor == "texto"
    assert "sempre o da Conclusão" in coluna.descricao


@pytest.mark.django_db
def test_tres_origens_contexto_confirmado_e_quarentena(monkeypatch, settings):
    from tests.declaracao.construcao import DADOS, declaracao_concluida, validar
    from tests.governanca.test_governanca_regras import CPAEG
    from tests.participacao import construcao as c
    from trajetoria.analitico.operacoes import capturar_snapshot
    from trajetoria.campanha.operacoes import encerrar
    from trajetoria.declaracao.operacoes import registrar_validacao
    from trajetoria.exportacao.dataset import dataset_exportado
    from trajetoria.participacao.models import Participacao

    def conclusao(curso):
        x = c.conclusao()
        x.curso = curso
        x.save()
        return x

    campanha = c.campanha_aberta(c.instrumento().versao)
    x = conclusao(curso="Curso institucional")
    Participacao.objects.create(campanha=campanha, conclusao=x, iniciada_em=c.NO_PERIODO)
    digital = declaracao_concluida(campanha, curso="Curso declarado que não será exportado")
    validar(digital, conclusao(curso="Curso confirmado digital"))
    acervo = declaracao_concluida(campanha)
    registrar_validacao(
        acervo,
        vinculos=[CPAEG],
        operador="A",
        agora=c.NO_PERIODO,
        resultado="CONFIRMADA",
        acervo={k: v for k, v in DADOS.items() if k != "nome"}
        | {"referencia": "Livro exportação", "curso": "Curso confirmado acervo"},
    )
    pendente = declaracao_concluida(campanha, curso="Não oficial pendente")
    nao = declaracao_concluida(campanha, curso="Não oficial recusada")
    validar(nao, resultado="NAO_CONFIRMADA")
    fora = declaracao_concluida(campanha, curso="Não oficial fora")
    validar(fora, c.conclusao(), fora=True)
    conflito = declaracao_concluida(campanha, curso="Não oficial conflito")
    validar(conflito, x, conflito=True)
    conclusao(curso="Elegível sem participação")
    encerrar(campanha, agora=c.NO_PERIODO)
    monkeypatch.setattr(
        "trajetoria.analitico.operacoes.momento_de_referencia", lambda _: c.NO_PERIODO
    )
    settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO = "p" * 64
    snapshot = capturar_snapshot(campanha)
    pacote = dataset_exportado(snapshot)
    linhas = [
        dict(zip(pacote.dados.cabecalho, linha, strict=True)) for linha in pacote.dados.linhas
    ]
    origens = {linha["curso"]: linha["origem_formacao"] for linha in linhas}
    assert origens["Curso institucional"] == "institucional"
    assert origens["Curso confirmado digital"] == "declarada_validada_fonte_digital"
    assert origens["Curso confirmado acervo"] == "declarada_validada_acervo"
    assert origens["Elegível sem participação"] is None
    assert all("Não oficial" not in (linha["curso"] or "") for linha in linhas)
    antes = pacote
    validar(pendente, c.conclusao())
    assert dataset_exportado(snapshot) == antes

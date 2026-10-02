"""Colunas de Pergunta e aplicabilidade (US5; spec FR-030 a FR-047; data-model §1.2, §1.3;
casos E a O, L, M).

Instrumento de teste (`tests/participacao/construcao.instrumento`): Seção 1 — `unica` (regra
"Não" → finaliza), `unica_outro` (A, B, "Outro:"), `multipla` (A, B, C, "Outro:"; opcional),
`texto`, `escala` 1–5, `campus`; Seção 2 — `posterior` (texto opcional). "Sim" em `unica` não
tem regra: o percurso segue para a Seção 2.
"""

import dataclasses

import pytest

from tests.analitico import construcao as c
from tests.exportacao import apoio
from tests.participacao.construcao import (
    FIM,
    instrumento_derivado,
    opcao_de,
    pergunta_de,
    pergunta_mem,
    preencher_instrumento,
    secao_mem,
    versao_publicada_de,
)
from trajetoria.analitico.operacoes import capturar_snapshot
from trajetoria.exportacao import dataset as modulo_dataset
from trajetoria.exportacao.contrato import COLUNAS_BASE
from trajetoria.exportacao.dataset import dataset_exportado
from trajetoria.exportacao.regras import ExportacaoInconsistente
from trajetoria.instrumento.models import EstadoVersao, Versao
from trajetoria.participacao.models import Resposta
from trajetoria.participacao.operacoes import (
    concluir,
    responder_escolha_multipla,
    responder_escolha_unica,
    responder_texto,
)

pytestmark = pytest.mark.django_db

TEXTO_DIFICIL = '  ação 😀 "x", y; z\nnova linha  '


def _p(pergunta) -> str:
    return f"pergunta_{pergunta.pk.hex}"


def _o(pergunta, texto) -> str:
    return f"{_p(pergunta)}__opcao_{opcao_de(pergunta, texto).pk.hex}"


def _colunas_esperadas(inst) -> list[str]:
    colunas = [b.nome for b in COLUNAS_BASE]
    colunas += [f"{_p(inst.unica)}__aplicavel", _p(inst.unica)]
    colunas += [
        f"{_p(inst.unica_outro)}__aplicavel",
        _p(inst.unica_outro),
        f"{_p(inst.unica_outro)}__complemento",
    ]
    colunas += [f"{_p(inst.multipla)}__aplicavel"]
    colunas += [_o(inst.multipla, t) for t in ("A", "B", "C", "Outro:")]
    colunas += [f"{_p(inst.multipla)}__complemento"]
    for pergunta in (inst.texto, inst.escala, inst.campus, inst.posterior):
        colunas += [f"{_p(pergunta)}__aplicavel", _p(pergunta)]
    return colunas


def _concluida_com(campanha, inst, *, multipla=None, complemento_multipla=None, **extras):
    """Concluída com a Seção 1 preenchida e, opcionalmente, a múltipla e outras Respostas."""
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    preencher_instrumento(participacao, inst, agora=c.na_coleta())
    if multipla:
        opcoes = [opcao_de(inst.multipla, t) for t in multipla]
        responder_escolha_multipla(
            participacao,
            inst.multipla,
            opcoes,
            complemento=complemento_multipla,
            agora=c.na_coleta(),
        )
    if "unica_outro" in extras:
        texto, complemento = extras["unica_outro"]
        responder_escolha_unica(
            participacao,
            inst.unica_outro,
            opcao_de(inst.unica_outro, texto),
            complemento=complemento,
            agora=c.na_coleta(),
        )
    if "texto" in extras:
        responder_texto(participacao, inst.texto, extras["texto"], agora=c.na_coleta())
    concluir(participacao, agora=c.na_coleta())
    return conclusao


# --- Colunas -----------------------------------------------------------------------------------


def test_cabecalho_exato(snapshot, inst):
    assert list(dataset_exportado(snapshot).dados.cabecalho) == _colunas_esperadas(inst)


# --- Os quatro tipos -----------------------------------------------------------------------------


def test_escolha_unica_texto_e_escala(snapshot, cenario, chave_ficticia):  # casos E e K
    inst = cenario.inst
    linha = apoio.linha_de(snapshot, cenario.serra_info, chave_ficticia)
    assert linha[_p(inst.unica)] == "Sim"
    assert linha[_p(inst.unica_outro)] == "A"
    assert linha[f"{_p(inst.unica_outro)}__complemento"] is None
    assert linha[_p(inst.texto)] == "27"
    assert linha[_p(inst.escala)] == 3 and type(linha[_p(inst.escala)]) is int
    assert linha[_p(inst.campus)] == "Campus Serra"


def test_escolha_multipla_por_indicador(cenario, chave_ficticia):  # casos F, G, H
    inst = cenario.inst
    uma = _concluida_com(cenario.campanha, inst, multipla=["A"])
    varias = _concluida_com(
        cenario.campanha, inst, multipla=["A", "C", "Outro:"], complemento_multipla="robótica"
    )
    snapshot = capturar_snapshot(cenario.campanha)
    a = apoio.linha_de(snapshot, uma, chave_ficticia)
    b = apoio.linha_de(snapshot, varias, chave_ficticia)
    opcoes = [_o(inst.multipla, t) for t in ("A", "B", "C", "Outro:")]
    assert [a[o] for o in opcoes] == [True, False, False, False]
    assert [b[o] for o in opcoes] == [True, False, True, True]
    assert a[f"{_p(inst.multipla)}__complemento"] is None
    assert b[f"{_p(inst.multipla)}__complemento"] == "robótica"


def test_escolha_unica_com_complemento(cenario, chave_ficticia):
    inst = cenario.inst
    conclusao = _concluida_com(cenario.campanha, inst, unica_outro=("Outro:", "estágio"))
    linha = apoio.linha_de(capturar_snapshot(cenario.campanha), conclusao, chave_ficticia)
    assert linha[_p(inst.unica_outro)] == "Outro:"
    assert linha[f"{_p(inst.unica_outro)}__complemento"] == "estágio"


def test_texto_preservado_exatamente(cenario, chave_ficticia):  # caso I
    inst = cenario.inst
    conclusao = _concluida_com(cenario.campanha, inst, texto=TEXTO_DIFICIL)
    linha = apoio.linha_de(capturar_snapshot(cenario.campanha), conclusao, chave_ficticia)
    assert linha[_p(inst.texto)] == TEXTO_DIFICIL


# --- Aplicabilidade ------------------------------------------------------------------------------


def test_aplicavel_nao_respondida(snapshot, cenario, chave_ficticia):  # caso M
    inst = cenario.inst
    linha = apoio.linha_de(snapshot, cenario.serra_info, chave_ficticia)
    assert linha[f"{_p(inst.multipla)}__aplicavel"] is True
    assert all(linha[_o(inst.multipla, t)] is None for t in ("A", "B", "C", "Outro:"))
    # "Sim" leva à Seção 2 (opcional): aplicável, não respondida.
    assert linha[f"{_p(inst.posterior)}__aplicavel"] is True
    assert linha[_p(inst.posterior)] is None


def test_fora_do_percurso_em_rascunho(snapshot, cenario, chave_ficticia):  # caso L
    inst = cenario.inst
    linha = apoio.linha_de(snapshot, cenario.serra_eng, chave_ficticia)
    assert Resposta.objects.filter(participacao=cenario.rascunho, pergunta=inst.posterior).exists()
    assert linha[f"{_p(inst.posterior)}__aplicavel"] is False
    assert linha[_p(inst.posterior)] is None  # preservada, mas não é valor analítico
    assert linha[_p(inst.unica)] == "Não"


def test_recusa(snapshot, cenario, chave_ficticia):
    inst = cenario.inst
    linha = apoio.linha_de(snapshot, cenario.vitoria_info, chave_ficticia)
    assert linha["participacao_concluida"] is True
    assert linha[_p(inst.unica)] == "Não"
    for pergunta in (inst.unica, inst.unica_outro, inst.multipla, inst.texto, inst.escala):
        assert linha[f"{_p(pergunta)}__aplicavel"] is True
    assert linha[f"{_p(inst.posterior)}__aplicavel"] is False


def test_percurso_nao_determinavel(inst, chave_ficticia):
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(regras={"Sim": FIM}), pergunta_mem(regras={"Não": FIM}))
    )
    campanha = c.campanha_aberta_no_passado(versao)
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    pergunta = pergunta_de(versao, 1, 1)
    responder_escolha_unica(participacao, pergunta, opcao_de(pergunta, "Sim"), agora=c.na_coleta())
    snapshot = capturar_snapshot(campanha)
    linha = apoio.linha_de(snapshot, conclusao, chave_ficticia)
    perguntas = [n for n in linha if n.startswith("pergunta_")]
    assert perguntas and all(linha[n] is None for n in perguntas)
    assert apoio.metadados(snapshot)["participacoes_com_percurso_nao_determinavel"] == 1


def test_invariantes_de_preenchimento(cenario):
    inst = cenario.inst
    _concluida_com(cenario.campanha, inst, multipla=["B"], unica_outro=("Outro:", "x"))
    for linha in apoio.linhas(capturar_snapshot(cenario.campanha)):
        grupos: dict[str, list[str]] = {}
        for nome in linha:
            if nome.startswith("pergunta_") and not nome.endswith("__aplicavel"):
                grupos.setdefault(nome.split("__")[0], []).append(nome)
        for base, colunas in grupos.items():
            aplicavel = linha[f"{base}__aplicavel"]
            if not linha["possui_participacao"]:
                assert aplicavel is None
            if aplicavel is not True:
                assert all(linha[col] is None for col in colunas), base
            assert all(v != "" for v in linha.values())


# --- Identidade local à Versão --------------------------------------------------------------------


def test_perguntas_de_mesmo_texto_tem_chaves_distintas(inst):  # caso N
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(tipo="TEXTO_CURTO", obrigatoria=False)),
        secao_mem(pergunta_mem(tipo="TEXTO_CURTO", obrigatoria=False)),
    )
    um, dois = pergunta_de(versao, 1, 1), pergunta_de(versao, 2, 1)
    assert um.texto == dois.texto
    campanha = c.campanha_aberta_no_passado(versao)
    cabecalho = dataset_exportado(capturar_snapshot(campanha)).dados.cabecalho
    assert _p(um) in cabecalho and _p(dois) in cabecalho and _p(um) != _p(dois)


def test_opcoes_de_rotulos_parecidos(inst, chave_ficticia):  # caso O
    versao = versao_publicada_de(
        secao_mem(pergunta_mem(opcoes=("Sim", "Sim, parcialmente"))),
        secao_mem(
            pergunta_mem(
                tipo="ESCOLHA_MULTIPLA", opcoes=("Sim", "Sim, parcialmente"), obrigatoria=False
            )
        ),
    )
    unica, multipla = pergunta_de(versao, 1, 1), pergunta_de(versao, 2, 1)
    campanha = c.campanha_aberta_no_passado(versao)
    conclusao = c.conclusao(unidade="Serra")
    participacao = c.iniciada(campanha, conclusao)
    responder_escolha_unica(
        participacao, unica, opcao_de(unica, "Sim, parcialmente"), agora=c.na_coleta()
    )
    responder_escolha_multipla(
        participacao, multipla, [opcao_de(multipla, "Sim")], agora=c.na_coleta()
    )
    linha = apoio.linha_de(capturar_snapshot(campanha), conclusao, chave_ficticia)
    assert linha[_p(unica)] == "Sim, parcialmente"
    assert linha[_o(multipla, "Sim")] is True
    assert linha[_o(multipla, "Sim, parcialmente")] is False


def test_versao_derivada_nao_compartilha_chaves(inst):
    derivada = instrumento_derivado(inst)
    origem = dataset_exportado(capturar_snapshot(c.campanha_aberta_no_passado(inst.versao)))
    nova = dataset_exportado(capturar_snapshot(c.campanha_aberta_no_passado(derivada.versao)))

    def perguntas(dataset):
        return {n for n in dataset.dados.cabecalho if n.startswith("pergunta_")}

    assert perguntas(origem) and not perguntas(origem) & perguntas(nova)


# --- Inconsistências (forçadas por escrita direta, só no teste) -----------------------------------


def _sem_valores(erro, *valores):
    for valor in valores:
        assert str(valor) not in str(erro.value)


def test_resposta_de_forma_incompativel(snapshot, cenario):
    # escala com texto: só por escrita fora das operações (ADR 0002)
    Resposta.objects.filter(participacao=cenario.concluida, pergunta=cenario.inst.escala).update(
        escala=None, texto="valor-que-nao-pode-vazar"
    )
    with pytest.raises(ExportacaoInconsistente) as erro:
        dataset_exportado(snapshot)
    _sem_valores(erro, "valor-que-nao-pode-vazar")


def test_opcao_de_outra_pergunta(snapshot, cenario):
    inst = cenario.inst
    Resposta.objects.filter(participacao=cenario.concluida, pergunta=inst.unica_outro).update(
        opcao=opcao_de(inst.campus, "Campus Serra")
    )
    with pytest.raises(ExportacaoInconsistente) as erro:
        dataset_exportado(snapshot)
    _sem_valores(erro, "Campus Serra")


def test_concluida_com_resposta_fora_do_percurso(snapshot, cenario):
    Resposta.objects.create(
        participacao=cenario.recusa, pergunta=cenario.inst.posterior, texto="segredo"
    )
    with pytest.raises(ExportacaoInconsistente) as erro:
        dataset_exportado(snapshot)
    _sem_valores(erro, "segredo")


def test_complemento_sem_opcao_que_o_admita(snapshot, cenario):
    Resposta.objects.filter(
        participacao=cenario.concluida, pergunta=cenario.inst.unica_outro
    ).update(complemento="segredo")
    with pytest.raises(ExportacaoInconsistente) as erro:
        dataset_exportado(snapshot)
    _sem_valores(erro, "segredo")


def test_versao_nao_publicada(snapshot, cenario):
    Versao.objects.filter(pk=cenario.inst.versao.pk).update(
        estado=EstadoVersao.RASCUNHO, publicada_em=None
    )
    with pytest.raises(ExportacaoInconsistente):
        dataset_exportado(snapshot)


def test_tipo_de_pergunta_desconhecido(snapshot, monkeypatch):
    # O CHECK da 002 impede o tipo inválido no banco; o conteúdo lido é adulterado no teste.
    original = modulo_dataset.conteudo_da_versao

    def adulterado(versao):
        conteudo = original(versao)
        secao = conteudo.secoes[0]
        pergunta = dataclasses.replace(secao.perguntas[0], tipo="MATRIZ")
        secao = dataclasses.replace(secao, perguntas=(pergunta, *secao.perguntas[1:]))
        return dataclasses.replace(conteudo, secoes=(secao, *conteudo.secoes[1:]))

    monkeypatch.setattr(modulo_dataset, "conteudo_da_versao", adulterado)
    with pytest.raises(ExportacaoInconsistente):
        dataset_exportado(snapshot)

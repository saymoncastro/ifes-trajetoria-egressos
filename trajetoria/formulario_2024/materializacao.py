"""Materialização da baseline do Formulário Egresso Ifes 2024 (contracts/materializacao.md).

`materializar()` garante que exista a Versão da baseline, em RASCUNHO, com o conteúdo da
declaração. Escreve só pelas operações da 002 (research R4), numa única transação (R7).
Baseline existente equivalente → nada é escrito; divergente → `BaselineDivergente`, sem
nenhuma escrita (R6). Nunca publica (002/DP-001).
"""

from dataclasses import dataclass

from django.db import transaction

from trajetoria.formulario_2024 import declaracao as d
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import Pesquisa, Versao


@dataclass(frozen=True)
class Resultado:
    versao: Versao
    criada: bool


class MaterializacaoRecusada(Exception):
    """A materialização não foi feita; nada foi gravado."""


class BaselineDivergente(MaterializacaoRecusada):
    """A baseline existente difere da declaração. Exige análise humana (FR-033)."""

    def __init__(self, divergencia: str):
        self.divergencia = divergencia
        super().__init__(f"baseline divergente da declaração — {divergencia}")


class PesquisaAmbigua(MaterializacaoRecusada):
    """Há mais de uma Pesquisa com o nome da baseline (FR-031)."""


# --- Forma por valor ------------------------------------------------------------------
#
# Versão:   (titulo, texto_abertura, texto_encerramento, secoes)
# Seção:    (titulo, texto, posição do encaminhamento | None, perguntas)
# Pergunta: (tipo, texto, texto_explicativo, obrigatoria, escala | None, opcoes)
# Opção:    (texto, complemento_textual, regra), regra = None | "FINALIZAR" | posição
#
# Sem identidades, estado, publicação, origem, designação ou nome da Pesquisa.

_FINALIZAR = "FINALIZAR"
# Destino que não é Seção desta Versão (só por escrita fora das operações da 002). Valor
# próprio, para não se confundir com "sem regra"/"sem encaminhamento" (None).
_FORA_DA_VERSAO = "FORA_DA_VERSAO"


def forma_esperada() -> tuple:
    posicao = {s.chave: n for n, s in enumerate(d.SECOES, 1)}

    def destino(chave):
        return _FINALIZAR if chave is d.FINALIZAR else posicao[chave]

    def pergunta(p: d.PerguntaDeclarada) -> tuple:
        regras = dict(p.regras)
        escala = p.escala and (
            p.escala.inicio, p.escala.fim, p.escala.rotulo_inicio, p.escala.rotulo_fim
        )
        opcoes = tuple(
            (texto, texto == p.complemento, destino(regras[texto]) if texto in regras else None)
            for texto in p.opcoes
        )
        return (p.tipo, p.texto, p.texto_explicativo, p.obrigatoria, escala, opcoes)

    secoes = tuple(
        (
            s.titulo,
            s.texto,
            s.encaminhamento and posicao[s.encaminhamento],
            tuple(pergunta(p) for p in s.perguntas),
        )
        for s in d.SECOES
    )
    return (d.TITULO, d.TEXTO_ABERTURA, d.TEXTO_ENCERRAMENTO, secoes)


def forma_da_versao(versao: Versao) -> tuple:
    conteudo = conteudo_da_versao(versao)
    posicao = {s.id: n for n, s in enumerate(conteudo.secoes, 1)}

    def regra(r):
        if r is None:
            return None
        return _FINALIZAR if r.finaliza else posicao.get(r.destino_secao_id, _FORA_DA_VERSAO)

    def pergunta(p) -> tuple:
        escala = p.escala and (
            p.escala.inicio, p.escala.fim, p.escala.rotulo_inicio, p.escala.rotulo_fim
        )
        opcoes = tuple((o.texto, o.complemento_textual, regra(o.regra)) for o in p.opcoes)
        return (p.tipo, p.texto, p.texto_explicativo, p.obrigatoria, escala, opcoes)

    secoes = tuple(
        (
            s.titulo,
            s.texto,
            s.encaminhamento_id and posicao.get(s.encaminhamento_id, _FORA_DA_VERSAO),
            tuple(pergunta(p) for p in s.perguntas),
        )
        for s in conteudo.secoes
    )
    return (conteudo.titulo, conteudo.texto_abertura, conteudo.texto_encerramento, secoes)


_CAMPOS_VERSAO = ("título", "texto de abertura", "texto de encerramento")
_CAMPOS_SECAO = ("título", "texto", "encaminhamento")
_CAMPOS_PERGUNTA = ("tipo", "texto", "texto explicativo", "obrigatoriedade", "escala")
_CAMPOS_OPCAO = ("texto", "complemento textual", "regra")


def _primeira_divergencia(esperada: tuple, existente: tuple) -> str:
    """Local e natureza da primeira diferença entre duas formas. Não é diff completo."""

    def campos(local, nomes, a, b):
        for nome, x, y in zip(nomes, a, b, strict=False):
            if x != y:
                return f"{local}: {nome} difere"
        return None

    def quantidade(local, itens, a, b):
        if len(a) != len(b):
            return f"{local}: {len(b)} {itens}, esperadas {len(a)}"
        return None

    # Em cada nível, os itens em comum vêm antes da contagem: a diferença de quantidade só
    # é a primeira quando todos os itens comparáveis são iguais.
    def opcoes(local, a, b):
        for o, (oa, ob) in enumerate(zip(a, b, strict=False), 1):
            if achado := campos(f"{local}·{o}", _CAMPOS_OPCAO, oa, ob):
                return achado
        return quantidade(local, "Opções", a, b)

    def perguntas(local, a, b):
        for p, (pa, pb) in enumerate(zip(a, b, strict=False), 1):
            sub = f"{local}·{p}"
            if achado := campos(sub, _CAMPOS_PERGUNTA, pa, pb) or opcoes(sub, pa[5], pb[5]):
                return achado
        return quantidade(local, "Perguntas", a, b)

    def secoes(a, b):
        for s, (sa, sb) in enumerate(zip(a, b, strict=False), 1):
            local = f"S{s}"
            if achado := campos(local, _CAMPOS_SECAO, sa, sb) or perguntas(local, sa[3], sb[3]):
                return achado
        return quantidade("Versão", "Seções", a, b)

    return (
        campos("Versão", _CAMPOS_VERSAO, esperada, existente)
        or secoes(esperada[3], existente[3])
        or "formas diferentes"
    )


# --- Operação -------------------------------------------------------------------------


def materializar() -> Resultado:
    """Cria a baseline se não existir; não faz nada se existir equivalente; recusa se
    existir divergente ou se o nome da Pesquisa for ambíguo. Tudo ou nada."""
    with transaction.atomic():
        pesquisas = list(Pesquisa.objects.filter(nome=d.NOME_PESQUISA))
        if len(pesquisas) > 1:
            raise PesquisaAmbigua(f"{len(pesquisas)} Pesquisas com o nome {d.NOME_PESQUISA!r}")
        pesquisa = pesquisas[0] if pesquisas else op.criar_pesquisa(d.NOME_PESQUISA)

        existente = Versao.objects.filter(pesquisa=pesquisa, designacao=d.DESIGNACAO).first()
        if existente is not None:
            # Equivalente → nada a fazer; divergente → recusa, sem merge nem reparo.
            _exigir_equivalente(existente)
            return Resultado(existente, criada=False)

        versao = _construir(pesquisa)
        _exigir_equivalente(versao)  # pós-condição: construção fiel à declaração
        return Resultado(versao, criada=True)


def _exigir_equivalente(versao: Versao) -> None:
    esperada, existente = forma_esperada(), forma_da_versao(versao)
    if existente != esperada:
        raise BaselineDivergente(_primeira_divergencia(esperada, existente))


def _construir(pesquisa: Pesquisa) -> Versao:
    versao = op.criar_versao(pesquisa, d.DESIGNACAO)
    op.alterar_versao(
        versao,
        titulo=d.TITULO,
        texto_abertura=d.TEXTO_ABERTURA,
        texto_encerramento=d.TEXTO_ENCERRAMENTO,
    )

    secoes, perguntas = {}, []
    for n, declarada in enumerate(d.SECOES, 1):
        secao = op.adicionar_secao(versao, n, titulo=declarada.titulo, texto=declarada.texto)
        secoes[declarada.chave] = secao
        for m, p in enumerate(declarada.perguntas, 1):
            pergunta = op.adicionar_pergunta(
                secao,
                m,
                p.tipo,
                p.texto,
                obrigatoria=p.obrigatoria,
                texto_explicativo=p.texto_explicativo,
                escala=p.escala,
            )
            opcoes = {
                texto: op.adicionar_opcao(
                    pergunta, k, texto, complemento_textual=(texto == p.complemento)
                )
                for k, texto in enumerate(p.opcoes, 1)
            }
            perguntas.append((p, pergunta, opcoes))

    # Regras e encaminhamentos apontam para Seções posteriores, que agora existem.
    for declarada in d.SECOES:
        if declarada.encaminhamento:
            op.definir_encaminhamento(secoes[declarada.chave], secoes[declarada.encaminhamento])
    for p, pergunta, opcoes in perguntas:
        for texto, destino in p.regras:
            alvo = op.FINALIZAR if destino is d.FINALIZAR else secoes[destino]
            op.definir_regra(pergunta, opcoes[texto], alvo)
    return versao

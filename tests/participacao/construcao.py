"""Auxiliares dos testes de Participação e Resposta (não são testes).

Todo teste temporal passa `agora` explícito, construído por `momento`: nenhum teste depende
do relógio real (research R13). Instrumentos são montados e publicados pelas operações da
002; a baseline da 003 nunca é publicada. Somente dados fictícios (DP-504).

Imports de `trajetoria.participacao.models` ficam dentro das funções, para que este módulo
importe antes de os modelos existirem (tasks, F1).
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from itertools import count
from uuid import UUID, uuid4

import pytest
from django.utils import timezone

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.models import Campanha
from trajetoria.formulario_2024 import materializar
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import (
    ConteudoOpcao,
    ConteudoPergunta,
    ConteudoSecao,
    ConteudoVersao,
    Escala,
    RegraNavegacao,
)
from trajetoria.instrumento.models import EstadoVersao, Opcao, Pergunta, Secao, TipoPergunta, Versao
from trajetoria.participacao.regras import ParticipacaoRejeitada

_sequencia = count(1)


def momento(ano: int, mes: int, dia: int, hora: int = 12) -> datetime:
    """Data e hora na timezone configurada do projeto, sem fuso nominal."""
    return timezone.make_aware(datetime(ano, mes, dia, hora))


INICIO, FIM = date(2027, 4, 1), date(2027, 6, 30)
NO_PERIODO = momento(2027, 5, 1)
ULTIMO_DIA = momento(2027, 6, 30, 23)
DEPOIS_DO_FIM = momento(2027, 7, 1)


# --- Instrumento de teste ------------------------------------------------------------------


@dataclass
class Instrumento:
    versao: Versao
    unica: Pergunta
    unica_outro: Pergunta
    multipla: Pergunta
    texto: Pergunta
    escala: Pergunta
    campus: Pergunta
    posterior: Pergunta

    def opcao(self, pergunta: Pergunta, texto: str) -> Opcao:
        return Opcao.objects.get(pergunta=pergunta, texto=texto)


def _escolha(secao, posicao, tipo, texto, opcoes, *, obrigatoria=True, outro=False):
    pergunta = op.adicionar_pergunta(secao, posicao, tipo, texto, obrigatoria=obrigatoria)
    for i, texto_opcao in enumerate(opcoes, start=1):
        op.adicionar_opcao(pergunta, i, texto_opcao)
    if outro:
        op.adicionar_opcao(pergunta, len(opcoes) + 1, "Outro:", complemento_textual=True)
    return pergunta


def _carregar(versao: Versao) -> Instrumento:
    """As Perguntas da Versão, pela posição (Seção 1: 1–6; Seção 2: 1)."""

    def pergunta(secao: int, posicao: int) -> Pergunta:
        return Pergunta.objects.get(secao__versao=versao, secao__posicao=secao, posicao=posicao)

    return Instrumento(
        versao=versao,
        unica=pergunta(1, 1),
        unica_outro=pergunta(1, 2),
        multipla=pergunta(1, 3),
        texto=pergunta(1, 4),
        escala=pergunta(1, 5),
        campus=pergunta(1, 6),
        posterior=pergunta(2, 1),
    )


def instrumento(designacao: str = "2027") -> Instrumento:
    """Versão publicada com uma pergunta de cada tipo, "Outro:" com complemento, uma regra
    de finalização e uma Seção posterior."""
    pesquisa = op.criar_pesquisa(f"Pesquisa de teste {next(_sequencia)}")
    versao = op.criar_versao(pesquisa, designacao)
    s1 = op.adicionar_secao(versao, 1)
    s2 = op.adicionar_secao(versao, 2)
    unica = _escolha(s1, 1, "ESCOLHA_UNICA", "Atualmente você trabalha?", ["Sim", "Não"])
    op.definir_regra(unica, Opcao.objects.get(pergunta=unica, texto="Não"), op.FINALIZAR)
    _escolha(s1, 2, "ESCOLHA_UNICA", "Motivo", ["A", "B"], outro=True)
    _escolha(
        s1, 3, "ESCOLHA_MULTIPLA", "Atividades", ["A", "B", "C"], obrigatoria=False, outro=True
    )
    op.adicionar_pergunta(s1, 4, "TEXTO_CURTO", "Quantos anos você tem?", obrigatoria=True)
    op.adicionar_pergunta(
        s1,
        5,
        "ESCALA",
        "Grau de concordância",
        obrigatoria=True,
        escala=Escala(inicio=1, fim=5, rotulo_fim="Concordo totalmente"),
    )
    _escolha(
        s1,
        6,
        "ESCOLHA_UNICA",
        "Em qual campus você concluiu seu curso?",
        ["Campus Serra", "Campus Vitória"],
    )
    op.adicionar_pergunta(s2, 1, "TEXTO_CURTO", "Comentário", obrigatoria=False)
    op.publicar(versao)
    versao.refresh_from_db()
    return _carregar(versao)


def instrumento_derivado(origem: Instrumento, designacao: str = "2028") -> Instrumento:
    """Nova Versão da mesma Pesquisa, criada da origem: textos idênticos, elementos novos."""
    versao = op.criar_versao_a_partir_de(origem.versao, designacao)
    op.publicar(versao)
    versao.refresh_from_db()
    return _carregar(versao)


# --- Conclusões e Campanhas ----------------------------------------------------------------


def conclusao(*, ano=2022, unidade="Serra", pessoa: Pessoa | None = None) -> ConclusaoAcademica:
    """Conclusão fictícia por ORM, fora dos cenários da 001."""
    n = next(_sequencia)
    if pessoa is None:
        pessoa = Pessoa.objects.create(fonte="teste-participacao", id_externo=f"TP-P-{n}")
    return ConclusaoAcademica.objects.create(
        pessoa=pessoa,
        fonte="teste-participacao",
        id_externo=f"TP-C-{n}",
        unidade=unidade,
        ano_conclusao=ano,
    )


def campanha_em_preparacao(versao: Versao, *, inicio=INICIO, fim=FIM, **criterios) -> Campanha:
    campanha = op_campanha.criar_campanha(f"Campanha {next(_sequencia)}", versao)
    op_campanha.definir_periodo(campanha, inicio, fim)
    if criterios:
        op_campanha.definir_criterios(campanha, **criterios)
    return campanha


def campanha_aberta(
    versao: Versao, *, inicio=INICIO, fim=FIM, abrir_em=None, **criterios
) -> Campanha:
    """Campanha aberta pelas operações da 004; por padrão, no primeiro dia do período."""
    campanha = campanha_em_preparacao(versao, inicio=inicio, fim=fim, **criterios)
    if abrir_em is None:
        abrir_em = momento(inicio.year, inicio.month, inicio.day)
    op_campanha.abrir(campanha, agora=abrir_em)
    return campanha


# --- Verificação ---------------------------------------------------------------------------


def rejeita(motivos, operacao, *args, **kwargs):
    """Executa a operação, exige rejeição com exatamente `motivos` e devolve as violações."""
    with pytest.raises(ParticipacaoRejeitada) as erro:
        operacao(*args, **kwargs)
    assert erro.value.motivos == tuple(motivos)
    return erro.value.violacoes


def retrato(participacao) -> dict:
    """Linhas gravadas da Participação, das suas Respostas e das suas seleções, para comparar
    antes e depois."""
    from trajetoria.participacao.models import Participacao, Resposta, RespostaOpcao

    respostas = Resposta.objects.filter(participacao_id=participacao.pk)
    return {
        "participacao": list(Participacao.objects.filter(pk=participacao.pk).values()),
        "respostas": list(respostas.order_by("id").values()),
        "selecoes": list(
            RespostaOpcao.objects.filter(resposta__in=respostas).order_by("id").values()
        ),
    }


# --- Feature 006: Versões descritas uma vez, em memória ou publicadas ----------------------
# A mesma descrição (`pergunta_mem`, `secao_mem`) monta um `ConteudoVersao` em memória, para
# testar `percurso.py` sem banco, ou uma Versão publicada pelas operações da 002, para os
# testes de ponta a ponta. Índices de Seção e de Pergunta são 1-based.

FIM = "FIM"


@dataclass(frozen=True)
class PerguntaMem:
    obrigatoria: bool
    tipo: TipoPergunta
    opcoes: tuple[str, ...]
    regras: dict  # texto da Opção → índice da Seção de destino ou FIM
    outro: bool


@dataclass(frozen=True)
class SecaoMem:
    perguntas: tuple[PerguntaMem, ...]
    encaminhamento: int | None
    titulo: str | None


def pergunta_mem(
    *,
    obrigatoria=True,
    tipo=TipoPergunta.ESCOLHA_UNICA,
    opcoes=("Sim", "Não"),
    regras=None,
    outro=False,
) -> PerguntaMem:
    if tipo in (TipoPergunta.TEXTO_CURTO, TipoPergunta.ESCALA):
        opcoes = ()
    return PerguntaMem(obrigatoria, tipo, tuple(opcoes), dict(regras or {}), outro)


def secao_mem(*perguntas, encaminhamento=None, titulo=None) -> SecaoMem:
    return SecaoMem(tuple(perguntas), encaminhamento, titulo)


def _textos_das_opcoes(p: PerguntaMem) -> tuple[str, ...]:
    return p.opcoes + (("Outro:",) if p.outro else ())


def versao_mem(*secoes: SecaoMem) -> ConteudoVersao:
    """`ConteudoVersao` construído em memória, sem banco, com identidades novas."""
    ids = [uuid4() for _ in secoes]

    def destino(alvo):
        return RegraNavegacao(None, True) if alvo == FIM else RegraNavegacao(ids[alvo - 1], False)

    def opcao(p: PerguntaMem, posicao: int, texto: str) -> ConteudoOpcao:
        regra = destino(p.regras[texto]) if texto in p.regras else None
        return ConteudoOpcao(uuid4(), posicao, texto, texto == "Outro:", regra)

    def pergunta(p: PerguntaMem, posicao: int) -> ConteudoPergunta:
        escala = Escala(1, 5) if p.tipo == TipoPergunta.ESCALA else None
        return ConteudoPergunta(
            id=uuid4(),
            posicao=posicao,
            tipo=p.tipo,
            texto=f"Pergunta {posicao}",
            texto_explicativo=None,
            obrigatoria=p.obrigatoria,
            escala=escala,
            opcoes=tuple(opcao(p, i, t) for i, t in enumerate(_textos_das_opcoes(p), 1)),
        )

    return ConteudoVersao(
        id=uuid4(),
        pesquisa_id=uuid4(),
        designacao="em memória",
        estado=EstadoVersao.PUBLICADA,
        publicada_em=None,
        origem_id=None,
        titulo=None,
        texto_abertura=None,
        texto_encerramento=None,
        secoes=tuple(
            ConteudoSecao(
                id=ids[i],
                posicao=i + 1,
                titulo=s.titulo,
                texto=None,
                encaminhamento_id=ids[s.encaminhamento - 1] if s.encaminhamento else None,
                perguntas=tuple(pergunta(p, j) for j, p in enumerate(s.perguntas, 1)),
            )
            for i, s in enumerate(secoes)
        ),
    )


def pergunta_id(conteudo: ConteudoVersao, s: int, p: int) -> UUID:
    return conteudo.secoes[s - 1].perguntas[p - 1].id


def opcao_id(conteudo: ConteudoVersao, s: int, p: int, texto: str) -> UUID:
    pergunta = conteudo.secoes[s - 1].perguntas[p - 1]
    return next(o.id for o in pergunta.opcoes if o.texto == texto)


def respondidas(conteudo: ConteudoVersao, escolhas: dict) -> dict[UUID, UUID | None]:
    """`(seção, pergunta)` → texto da Opção escolhida (escolha única) ou `None`."""
    return {
        pergunta_id(conteudo, s, p): None if texto is None else opcao_id(conteudo, s, p, texto)
        for (s, p), texto in escolhas.items()
    }


def rotulos(passagens) -> tuple[str, ...]:
    """Seções das passagens no formato do oráculo `PERCURSOS` da 003 (título ou "#posição"),
    terminadas em "FIM" quando a jornada está finalizada."""
    from trajetoria.participacao.percurso import finalizada

    nomes = tuple(p.secao.titulo or f"#{p.secao.posicao}" for p in passagens)
    return nomes + ((FIM,) if finalizada(passagens) else ())


def versao_publicada_de(*secoes: SecaoMem) -> Versao:
    """A mesma descrição de `versao_mem`, montada e publicada pelas operações da 002."""
    versao = op.criar_versao(op.criar_pesquisa(f"Pesquisa 006 {next(_sequencia)}"), "2027")
    criadas = [op.adicionar_secao(versao, i, titulo=s.titulo) for i, s in enumerate(secoes, 1)]
    for secao, s in zip(criadas, secoes, strict=True):
        if s.encaminhamento:
            op.definir_encaminhamento(secao, criadas[s.encaminhamento - 1])
        for j, p in enumerate(s.perguntas, 1):
            escala = Escala(inicio=1, fim=5) if p.tipo == TipoPergunta.ESCALA else None
            pergunta = op.adicionar_pergunta(
                secao, j, p.tipo, f"Pergunta {j}", obrigatoria=p.obrigatoria, escala=escala
            )
            for k, texto in enumerate(_textos_das_opcoes(p), 1):
                opcao = op.adicionar_opcao(
                    pergunta, k, texto, complemento_textual=texto == "Outro:"
                )
                if texto in p.regras:
                    alvo = p.regras[texto]
                    op.definir_regra(
                        pergunta, opcao, op.FINALIZAR if alvo == FIM else criadas[alvo - 1]
                    )
    op.publicar(versao)
    versao.refresh_from_db()
    return versao


def pergunta_de(versao: Versao, s: int, p: int) -> Pergunta:
    return Pergunta.objects.get(secao__versao=versao, secao__posicao=s, posicao=p)


def opcao_de(pergunta: Pergunta, texto: str) -> Opcao:
    return Opcao.objects.get(pergunta=pergunta, texto=texto)


# --- Feature 006: baseline da 003 (cópia publicada só no banco de teste) ------------------

Q14 = {
    "medio": "Ensino Médio/Técnico Integrado",
    "tecnico": "Técnico Concomitante/Subsequente/EJA-PROEJA",
    "graduacao": "Graduação",
    "pos": "Pós-Graduação",
}
_SECAO_DE_Q14 = {texto: 4 + i for i, texto in enumerate(Q14.values())}


@dataclass
class Baseline:
    """Cópia publicada da baseline. Qn e Sn seguem a ordem (Seção, posição), como
    `perguntas_por_chave` da 003."""

    versao: Versao
    perguntas: dict[str, Pergunta] = field(default_factory=dict)
    secoes: dict[str, Secao] = field(default_factory=dict)

    def q(self, n: int) -> Pergunta:
        return self.perguntas[f"Q{n}"]

    def s(self, n: int) -> Secao:
        return self.secoes[f"S{n}"]

    def opcao(self, n: int, texto: str) -> Opcao:
        return opcao_de(self.q(n), texto)

    def chave(self, pergunta: Pergunta) -> str:
        return next(k for k, p in self.perguntas.items() if p.id == pergunta.id)


def baseline_publicada() -> Baseline:
    """`materializar()` → `criar_versao_a_partir_de` → `publicar` a cópia. A baseline da 003
    continua RASCUNHO; publicar a cópia no banco de teste não é publicação institucional
    (002/DP-001; research R15)."""
    original = materializar().versao
    copia = op.criar_versao_a_partir_de(original, f"Cópia de teste 006 {next(_sequencia)}")
    op.publicar(copia)
    copia.refresh_from_db()
    base = Baseline(copia)
    perguntas = Pergunta.objects.filter(secao__versao=copia).order_by(
        "secao__posicao", "posicao"
    )
    for n, pergunta in enumerate(perguntas, 1):
        base.perguntas[f"Q{n}"] = pergunta
    for secao in Secao.objects.filter(versao=copia).order_by("posicao"):
        base.secoes[f"S{secao.posicao}"] = secao
    return base


def escolhas_baseline(q1, q14=None, q33=None, q46=None) -> dict[str, str]:
    """Textos das Opções das quatro Perguntas com regra da baseline."""
    escolhas = {"Q1": q1, "Q14": q14, "Q33": q33, "Q46": q46}
    return {k: v for k, v in escolhas.items() if v is not None}


def secoes_esperadas(q1, q14=None, q33=None, q46=None) -> list[int]:
    """Oráculo de teste escrito à mão a partir de "Percursos esperados" da 003."""
    if q1 == "Não":
        return [1]
    return [
        1,
        2,
        3,
        _SECAO_DE_Q14[q14],
        8,
        9 if q33 == "Sim" else 10,
        11,
        *([12] if q46 == "Sim" else []),
        13,
    ]


def combinacoes_baseline():
    """As 17 combinações de Q1 × Q14 × Q33 × Q46 da tabela "Percursos esperados"."""
    yield ("Não", None, None, None)
    for q14 in Q14.values():
        for q33 in ("Sim", "Não"):
            for q46 in ("Sim", "Não"):
                yield ("Sim", q14, q33, q46)


def _chaves(conteudo: ConteudoVersao):
    perguntas = [p for s in conteudo.secoes for p in s.perguntas]
    return {f"Q{n}": p for n, p in enumerate(perguntas, 1)}


def respondidas_baseline(conteudo: ConteudoVersao, escolhas: dict, *, exceto=()) -> dict:
    """`respondidas` em memória para **todas** as Perguntas da baseline (fora as de `exceto`):
    escolha única → Opção de `escolhas` ou a primeira; demais tipos → `None`. Responder
    tudo prova que respostas fora do percurso não interferem."""
    resultado = {}
    for chave, pergunta in _chaves(conteudo).items():
        if chave in exceto:
            continue
        if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
            texto = escolhas.get(chave, pergunta.opcoes[0].texto)
            resultado[pergunta.id] = next(o.id for o in pergunta.opcoes if o.texto == texto)
        else:
            resultado[pergunta.id] = None
    return resultado


def chaves_baseline(conteudo: ConteudoVersao) -> dict[str, UUID]:
    """Qn → `id` da Pergunta no conteúdo."""
    return {k: p.id for k, p in _chaves(conteudo).items()}


def preencher(participacao, base: Baseline, secoes, escolhas: dict, *, agora=NO_PERIODO, exceto=()):
    """Responde, pelas operações da 005, as Perguntas **obrigatórias** das Seções `secoes`
    da baseline (escolha única → Opção de `escolhas` ou a primeira; múltipla → a primeira;
    texto → "resposta fictícia"; escala → início). Dados fictícios."""
    from trajetoria.participacao import operacoes as op_participacao

    for n in secoes:
        for pergunta in base.s(n).perguntas.order_by("posicao"):
            chave = base.chave(pergunta)
            if not pergunta.obrigatoria or chave in exceto:
                continue
            responder(op_participacao, participacao, pergunta, escolhas.get(chave), agora)


def responder(op_participacao, participacao, pergunta, texto, agora):
    """Uma resposta válida qualquer à Pergunta, ou a Opção de texto `texto`."""
    primeira = pergunta.opcoes.order_by("posicao").first()
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        opcao = opcao_de(pergunta, texto) if texto else primeira
        return op_participacao.responder_escolha_unica(participacao, pergunta, opcao, agora=agora)
    if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
        return op_participacao.responder_escolha_multipla(
            participacao, pergunta, [primeira], agora=agora
        )
    if pergunta.tipo == TipoPergunta.TEXTO_CURTO:
        return op_participacao.responder_texto(
            participacao, pergunta, "resposta fictícia", agora=agora
        )
    return op_participacao.responder_escala(
        participacao, pergunta, pergunta.escala_inicio, agora=agora
    )


def preencher_instrumento(participacao, inst: Instrumento, agora=NO_PERIODO):
    """Responde as obrigatórias da Seção 1 do instrumento de teste da 005 ("Sim" na escolha
    única com regra): a Seção 2 é opcional, então a jornada fica finalizada (006)."""
    from trajetoria.participacao.operacoes import (
        responder_escala,
        responder_escolha_unica,
        responder_texto,
    )

    def unica(pergunta, texto):
        responder_escolha_unica(participacao, pergunta, inst.opcao(pergunta, texto), agora=agora)

    unica(inst.unica, "Sim")
    unica(inst.unica_outro, "A")
    responder_texto(participacao, inst.texto, "27", agora=agora)
    responder_escala(participacao, inst.escala, 3, agora=agora)
    unica(inst.campus, "Campus Serra")

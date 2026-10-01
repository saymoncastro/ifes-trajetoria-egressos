"""Telas da jornada do egresso (Feature 008; contracts/rotas.md).

**Camada fina.** Nenhuma regra de domínio vive aqui: formações e entrada vêm da 007,
jornada e conclusão da 006, gravação de Respostas da 005 (por `gravacao.py`). As views
apenas traduzem resultados em telas e ações em chamadas às operações existentes. A
Pessoa vem do adaptador de demonstração (`pessoa_em_uso`), substituível pela futura
fronteira de identidade (FR-005).
"""

from functools import wraps

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.demonstracao.entrada import pessoa_em_uso
from trajetoria.interface import mensagens
from trajetoria.interface.apresentacao import contexto_da_formacao, resumo_da_formacao
from trajetoria.interface.formularios import FormularioDaSecao
from trajetoria.interface.gravacao import salvar_secao
from trajetoria.participacao.consultas import situacao_da_jornada
from trajetoria.participacao.entrada import (
    FormacaoDeOutraPessoa,
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    entrar,
    situacao_de_entrada,
)
from trajetoria.participacao.models import Participacao
from trajetoria.participacao.operacoes import concluir
from trajetoria.participacao.percurso import Saida
from trajetoria.participacao.regras import Motivo, ParticipacaoRejeitada


class _Resposta(Exception):
    """Interrompe a view com uma resposta pronta (redirecionamento ou tela de estado)."""

    def __init__(self, resposta):
        self.resposta = resposta


def _respondendo(view):
    """Devolve a resposta carregada por `_Resposta`, para que os auxiliares de posse e de
    jornada possam encerrar a view sem repetir verificações em cada uma."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except _Resposta as interrompida:
            return interrompida.resposta

    return envolvida


def _tela(request, texto, *, conclusao=None, status=200):
    """Tela de estado (`aviso.html`): já respondida, período encerrado, indisponível."""
    titulo, paragrafos = texto
    contexto = {"titulo": titulo, "mensagem": paragrafos}
    if conclusao is not None:
        contexto["contexto_formacao"] = contexto_da_formacao(conclusao)
        contexto["mostrar_contexto"] = True
    return render(request, "interface/aviso.html", contexto, status=status)


def _pessoa(request):
    """A Pessoa resolvida (hoje, pela demonstração) ou o redirecionamento à entrada."""
    pessoa = pessoa_em_uso(request)
    if pessoa is None:
        raise _Resposta(redirect("/demonstracao/"))
    return pessoa


def _participacao_da_pessoa(request, pk) -> Participacao:
    """A Participação, só se pertencer a uma formação da Pessoa em uso. Alheia ou
    inexistente: o mesmo 404, sem revelar nada (FR-089, FR-090)."""
    pessoa = _pessoa(request)
    participacao = (
        Participacao.objects.select_related("campanha__versao", "conclusao")
        .filter(pk=pk, conclusao__pessoa=pessoa)
        .first()
    )
    if participacao is None:
        raise Http404
    return participacao


def _jornada(request, participacao):
    """A jornada da 006. Estrutura fora da capacidade da 006 vira "pesquisa indisponível",
    sem detalhe técnico (006 FR-016)."""
    try:
        return situacao_da_jornada(participacao)
    except ParticipacaoRejeitada as erro:
        if Motivo.ESTRUTURA_NAO_SUPORTADA in erro.motivos:
            raise _Resposta(_tela(request, mensagens.PESQUISA_INDISPONIVEL)) from None
        raise


def _base(participacao) -> str:
    return f"/participacoes/{participacao.pk}/"


@require_GET
def inicio(request):
    return redirect("/formacoes/" if pessoa_em_uso(request) else "/demonstracao/")


# --- Formações (007) ---------------------------------------------------------------------------

_ACAO = {
    SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR: "Iniciar a pesquisa",
    SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR: "Continuar a pesquisa",
}
_TELA_DE_FORMACOES = {
    ResolucaoDaEntrada.SEM_FORMACAO: (
        "Suas formações",
        "Não encontramos formações concluídas no Ifes associadas a você.",
    ),
    ResolucaoDaEntrada.SEM_PESQUISA: (
        "Suas formações",
        "No momento, não há pesquisa disponível para as suas formações.",
    ),
    ResolucaoDaEntrada.SEM_ENTRADA_PENDENTE: (
        "Suas formações",
        "Não há pesquisa pendente para você neste momento.",
    ),
    ResolucaoDaEntrada.ENTRADA_RESOLVIDA: ("Sua pesquisa", None),
    ResolucaoDaEntrada.SELECAO_NECESSARIA: (
        "Sobre qual formação do Ifes você responderá esta pesquisa?",
        None,
    ),
}


_COM_ACAO = (ResolucaoDaEntrada.ENTRADA_RESOLVIDA, ResolucaoDaEntrada.SELECAO_NECESSARIA)


def _aviso(request, permitido: str) -> str | None:
    """Faixa de aviso por código de lista fechada; qualquer outro valor é ignorado."""
    return mensagens.AVISOS[permitido] if request.GET.get("aviso") == permitido else None


def _formacao_apresentada(formacao) -> dict:
    return {
        "pk": formacao.conclusao.pk,
        "contexto": contexto_da_formacao(formacao.conclusao),
        "situacao": mensagens.SITUACAO_DA_FORMACAO[formacao.situacao],
        "acao": _ACAO.get(formacao.situacao),
    }


@require_GET
@never_cache
@_respondendo
def formacoes(request):
    pessoa = _pessoa(request)
    situacao = situacao_de_entrada(pessoa)
    destaque = situacao.pendentes if situacao.resolucao in _COM_ACAO else ()
    chaves = {f.conclusao.pk for f in destaque}
    titulo, mensagem = _TELA_DE_FORMACOES[situacao.resolucao]
    pendentes = [_formacao_apresentada(f) for f in destaque]
    return render(
        request,
        "interface/formacoes.html",
        {
            "titulo": titulo,
            "mensagem": mensagem,
            "resolucao": situacao.resolucao.value,
            "principal": pendentes[0] if pendentes else None,
            "pendentes": pendentes,
            "outras": [
                _formacao_apresentada(f)
                for f in situacao.formacoes
                if f.conclusao.pk not in chaves
            ],
            "aviso": _aviso(request, "situacao"),
        },
    )



# --- Entrada na Participação (007 → 005) -------------------------------------------------------


def _formacao_informada(request) -> ConclusaoAcademica | None:
    """A Conclusão informada no POST, ou `None` sem o campo. Valor malformado ou inexistente
    recebe a mesma resposta de formação alheia (007 FR-044)."""
    pk = request.POST.get("formacao")
    if not pk:
        return None
    try:
        conclusao = ConclusaoAcademica.objects.filter(pk=pk).first()
    except ValidationError:
        conclusao = None
    if conclusao is None:
        raise _Resposta(_tela(request, mensagens.FORMACAO_INDISPONIVEL, status=404))
    return conclusao


@require_POST
@never_cache
@_respondendo
def entrar_view(request):
    pessoa = _pessoa(request)
    try:
        resultado = entrar(pessoa, _formacao_informada(request))
    except FormacaoDeOutraPessoa:
        return _tela(request, mensagens.FORMACAO_INDISPONIVEL, status=404)
    except ParticipacaoRejeitada:
        return _tela(request, mensagens.PERIODO_ENCERRADO)
    participacao = resultado.participacao
    if participacao is None:
        return redirect("/formacoes/?aviso=situacao")
    if participacao.concluida_em is not None:
        return _tela(request, mensagens.JA_RESPONDIDA, conclusao=participacao.conclusao)
    return redirect(_base(participacao))


@require_GET
@never_cache
@_respondendo
def participacao(request, participacao):
    participacao = _participacao_da_pessoa(request, participacao)
    jornada = _jornada(request, participacao)
    if jornada.concluida_em is not None:
        return redirect(_base(participacao) + "concluida/")
    if not jornada.admite_escrita:
        return _tela(request, mensagens.PERIODO_ENCERRADO, conclusao=participacao.conclusao)
    if jornada.finalizada:
        return redirect(_base(participacao) + "concluir/")
    return redirect(_base(participacao) + f"secoes/{jornada.secao_atual.posicao}/")


# --- Seção (006 jornada, 005 gravação) --------------------------------------------------------


def _endereco_atual(participacao, jornada) -> str:
    """Onde a jornada está agora, segundo a 006: a Seção atual ou a tela de conclusão."""
    if jornada.finalizada:
        return _base(participacao) + "concluir/"
    return _base(participacao) + f"secoes/{jornada.secao_atual.posicao}/"


def _exigir_rascunho_aberto(request, participacao, jornada) -> None:
    """Concluída → "já respondida"; coleta não admitida → "período encerrado". A interface
    não avalia período nem estado de Campanha: lê `admite_escrita` da 006 (FR-065)."""
    if jornada.concluida_em is not None:
        raise _Resposta(
            _tela(request, mensagens.JA_RESPONDIDA, conclusao=participacao.conclusao)
        )
    if not jornada.admite_escrita:
        raise _Resposta(
            _tela(request, mensagens.PERIODO_ENCERRADO, conclusao=participacao.conclusao)
        )


def _passagem(participacao, jornada, posicao):
    """A Passagem da Seção pedida no percurso determinado (006). Fora dele — ramo não
    escolhido, Seção ainda não alcançada ou posição inexistente — leva à Seção atual (FR-055)."""
    for passagem in jornada.passagens:
        if passagem.secao.posicao == posicao:
            return passagem
    raise _Resposta(redirect(_endereco_atual(participacao, jornada) + "?aviso=percurso"))


def _tela_da_secao(request, participacao, jornada, passagem, formulario, erros=None, *,
                   salvo=False):  # fmt: skip
    # Título e abertura vêm da Versão já carregada com a Participação (sem reler o conteúdo);
    # a primeira passagem do percurso é sempre a primeira Seção da Versão (006 FR-014).
    versao = participacao.campanha.versao
    itens = formulario.itens(erros)
    # Anterior **no percurso determinado** (006), nunca na ordem da Versão (FR-054).
    indice = jornada.passagens.index(passagem)
    anterior = jornada.passagens[indice - 1].secao.posicao if indice else None
    resumo = [
        {"ancora": item.nome, "texto": f"{item.pergunta.texto} — {erro}"}
        for item in itens
        for erro in item.erros
    ]
    return render(
        request,
        "interface/secao.html",
        {
            "titulo_pesquisa": versao.titulo or "Pesquisa",
            "texto_abertura": versao.texto_abertura,
            "primeira": indice == 0,
            "acao": _base(participacao) + f"secoes/{passagem.secao.posicao}/",
            "resumo_formacao": resumo_da_formacao(participacao.conclusao),
            "passagem": passagem,
            "itens": itens,
            "resumo_erros": resumo,
            "ha_erros": bool(resumo),
            "salvo": salvo,
            "aviso": _aviso(request, "percurso"),
            "anterior": anterior and _base(participacao) + f"secoes/{anterior}/",
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def secao(request, participacao, posicao):
    participacao = _participacao_da_pessoa(request, participacao)
    jornada = _jornada(request, participacao)
    _exigir_rascunho_aberto(request, participacao, jornada)
    passagem = _passagem(participacao, jornada, posicao)
    if request.method == "POST":
        return _salvar(request, participacao, jornada, passagem)
    formulario = FormularioDaSecao(passagem.secao, jornada.respostas)
    pendencias = None
    if request.GET.get("pendencias") == "1" and passagem is jornada.passagens[-1]:
        pendencias = _pendencias(passagem)
    salvo = bool(pendencias) and request.GET.get("salvo") == "1"
    return _tela_da_secao(
        request, participacao, jornada, passagem, formulario, pendencias, salvo=salvo
    )


def _pendencias(passagem) -> dict[int, list[str]]:
    """As Perguntas obrigatórias sem Resposta da Seção, exatamente as da 006 (FR-053)."""
    pendentes = set(passagem.pendentes)
    return {
        p.posicao: [mensagens.OBRIGATORIA] for p in passagem.secao.perguntas if p.id in pendentes
    }


def _salvar(request, participacao, jornada, passagem):
    """Envio da Seção (contracts/rotas.md, "POST secoes"): forma → 005 → 006."""
    formulario = FormularioDaSecao(passagem.secao, jornada.respostas, data=request.POST)
    if not formulario.is_valid():
        return _tela_da_secao(request, participacao, jornada, passagem, formulario)
    resultado = salvar_secao(participacao, passagem.secao, formulario.limpos, jornada.respostas)
    if resultado.motivo_global is Motivo.PARTICIPACAO_CONCLUIDA:
        return _tela(request, mensagens.JA_RESPONDIDA, conclusao=participacao.conclusao)
    if resultado.motivo_global is Motivo.COLETA_NAO_ADMITIDA:
        return _tela(request, mensagens.PERIODO_ENCERRADO, conclusao=participacao.conclusao)
    if resultado.motivo_global is not None:
        raise Http404
    if resultado.erros_por_pergunta:
        return _tela_da_secao(
            request, participacao, jornada, passagem, formulario, resultado.erros_por_pergunta
        )
    # O próximo passo é sempre o que a 006 calcula agora, com as Respostas gravadas.
    jornada = _jornada(request, participacao)
    passagem = _passagem(participacao, jornada, passagem.secao.posicao)
    secao = _base(participacao) + f"secoes/{passagem.secao.posicao}/"
    if not passagem.satisfeita:
        return redirect(secao + "?pendencias=1&salvo=1")
    if passagem.destino is Saida.FINALIZACAO:
        return redirect(_base(participacao) + "concluir/")
    # Seção satisfeita com destino determinado: o percurso da 006 segue para ele, que é,
    # portanto, a passagem seguinte (006 FR-014).
    seguinte = jornada.passagens[jornada.passagens.index(passagem) + 1]
    return redirect(_base(participacao) + f"secoes/{seguinte.secao.posicao}/")


# --- Conclusão (006) -----------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def concluir_view(request, participacao):
    participacao = _participacao_da_pessoa(request, participacao)
    jornada = _jornada(request, participacao)
    if jornada.concluida_em is not None:
        return redirect(_base(participacao) + "concluida/")
    _exigir_rascunho_aberto(request, participacao, jornada)
    if not jornada.finalizada:
        # Num POST, a jornada deixou de estar finalizada depois da tela: mostrar o porquê.
        pendencias = "?pendencias=1" if request.method == "POST" else ""
        return redirect(_endereco_atual(participacao, jornada) + pendencias)
    if request.method == "POST":
        return _concluir(request, participacao)
    secoes = [
        {
            "nome": p.secao.titulo or f"Seção {p.secao.posicao}",
            "endereco": _base(participacao) + f"secoes/{p.secao.posicao}/",
        }
        for p in jornada.passagens
    ]
    return render(
        request,
        "interface/conclusao.html",
        {
            "titulo_pesquisa": participacao.campanha.versao.titulo or "Pesquisa",
            "contexto_formacao": contexto_da_formacao(participacao.conclusao),
            "secoes": secoes,
            "acao": _base(participacao) + "concluir/",
        },
    )


def _concluir(request, participacao):
    """Só a operação da 006 (FR-057). Precedência das rejeições: coleta → somente pendências
    → qualquer outro motivo (estrutura, incoerência de Respostas, motivo futuro) como
    "pesquisa indisponível", sem detalhe (contracts/rotas.md; 006 FR-045)."""
    try:
        concluir(participacao)
    except ParticipacaoRejeitada as erro:
        if Motivo.COLETA_NAO_ADMITIDA in erro.motivos:
            return _tela(request, mensagens.PERIODO_ENCERRADO, conclusao=participacao.conclusao)
        if set(erro.motivos) != {Motivo.OBRIGATORIA_PENDENTE}:
            return _tela(request, mensagens.PESQUISA_INDISPONIVEL)
        jornada = _jornada(request, participacao)
        return redirect(_endereco_atual(participacao, jornada) + "?pendencias=1")
    return redirect(_base(participacao) + "concluida/")


@require_GET
@never_cache
@_respondendo
def concluida(request, participacao):
    """Confirmação simples: sem respostas, data, comprovante ou ação de editar (FR-062,
    FR-063). A Participação concluída é lida, nunca reaberta."""
    participacao = _participacao_da_pessoa(request, participacao)
    if participacao.concluida_em is None:
        return redirect(_base(participacao))
    return render(
        request,
        "interface/concluida.html",
        {
            "contexto_formacao": contexto_da_formacao(participacao.conclusao),
            "texto_encerramento": participacao.campanha.versao.texto_encerramento,
        },
    )

"""Telas da jornada do egresso (Feature 008; contracts/rotas.md).

**Camada fina.** Nenhuma regra de domínio vive aqui: formações e entrada vêm da 007,
jornada e conclusão da 006, gravação de Respostas da 005 (por `gravacao.py`). As views
apenas traduzem resultados em telas e ações em chamadas às operações existentes. A
Pessoa vem da sessão da confirmação de acesso (`pessoa_em_uso`), substituível pela futura
fronteira de identidade (FR-005).
"""

import re
from functools import wraps
from math import ceil

from django.core.exceptions import ValidationError
from django.http import Http404, QueryDict
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.acesso import pendente
from trajetoria.acesso.sessao import destino_da_entrada, pessoa_em_uso
from trajetoria.declaracao.sessao import declaracoes_em_uso
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import Versao
from trajetoria.interface import mensagens
from trajetoria.interface.apresentacao import (
    complemento_da_formacao,
    conclusao_efetiva,
    contexto_da_formacao,
    formacao_exibida,
    linha_da_parte,
    onde_parou_da_participacao,
    resumo_da_formacao,
    rotulo_da_formacao,
    rotulo_da_formacao_declarada,
    rotulo_da_secao,
)
from trajetoria.interface.formularios import FormularioDaSecao
from trajetoria.interface.gravacao import salvar_secao
from trajetoria.narrativa.consultas import elegivel as narrativa_elegivel
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
from trajetoria.participacao.percurso import Saida, maximo_restante
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


def _tela(request, texto, *, conclusao=None, declarada=False, status=200):
    """Tela de estado (`aviso.html`): já respondida, período encerrado, indisponível.
    `declarada` vem sempre da Participação (019), nunca deduzido do tipo do objeto."""
    titulo, paragrafos = texto
    contexto = {"titulo": titulo, "mensagem": paragrafos, "declarada": declarada}
    if conclusao is not None:
        contexto["contexto_formacao"] = contexto_da_formacao(conclusao)
        contexto["mostrar_contexto"] = True
        if declarada:
            contexto["rotulo_formacao"] = rotulo_da_formacao_declarada()
    return render(request, "interface/aviso.html", contexto, status=status)


def _da_participacao(participacao) -> dict:
    """Formação exibida nas telas de estado da jornada: a âncora original, com o rótulo de
    declarada tirado da própria Participação (019)."""
    return {
        "conclusao": formacao_exibida(participacao),
        "declarada": participacao.formacao_declarada_id is not None,
    }


def _pessoa(request, *, aceita_declarante=False):
    """A Pessoa resolvida (pela confirmação de acesso) ou o redirecionamento à entrada."""
    pessoa = pessoa_em_uso(request)
    if pessoa is None and not (aceita_declarante and declaracoes_em_uso(request) is not None):
        raise _Resposta(redirect(destino_da_entrada(request)))
    return pessoa


def _participacao_do_sujeito(request, pk) -> Participacao:
    pessoa = _pessoa(request, aceita_declarante=True)
    qs = Participacao.objects.select_related("campanha__versao", "conclusao", "formacao_declarada")
    if pessoa is not None:
        qs = qs.filter(conclusao__pessoa=pessoa)
    else:
        qs = qs.filter(formacao_declarada_id__in=declaracoes_em_uso(request))
    participacao = qs.filter(pk=pk).first()
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
            raise _Resposta(
                _tela(
                    request,
                    mensagens.PESQUISA_INDISPONIVEL,
                    declarada=participacao.formacao_declarada_id is not None,
                )
            ) from None
        raise


def _base(participacao) -> str:
    return f"/participacoes/{participacao.pk}/"


@require_GET
def inicio(request):
    if pessoa_em_uso(request):
        return redirect("/formacoes/")
    if declaracoes_em_uso(request) is not None:
        return redirect("/declaracao/")
    return redirect(destino_da_entrada(request))


# --- Formações (007) ---------------------------------------------------------------------------

_ACAO = {
    SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR: "Iniciar a pesquisa",
    SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR: "Continuar a pesquisa",
}
# Mensagem de estado por situação, informada uma vez (014 FR-036); o título é sempre o da
# trajetória (FR-030).
_TELA_DE_FORMACOES = {
    ResolucaoDaEntrada.SEM_FORMACAO: mensagens.SEM_FORMACAO,
    ResolucaoDaEntrada.SEM_PESQUISA: mensagens.SEM_PESQUISA,
    ResolucaoDaEntrada.SEM_ENTRADA_PENDENTE: mensagens.SEM_ENTRADA_PENDENTE,
    ResolucaoDaEntrada.ENTRADA_RESOLVIDA: None,
    ResolucaoDaEntrada.SELECAO_NECESSARIA: None,
}


_COM_ACAO = (ResolucaoDaEntrada.ENTRADA_RESOLVIDA, ResolucaoDaEntrada.SELECAO_NECESSARIA)


def _aviso(request, *permitidos: str) -> dict | None:
    """Faixa de aviso por código de lista fechada; qualquer outro valor é ignorado. A variante
    visual é derivada do código (015 FR-026)."""
    codigo = request.GET.get("aviso")
    if codigo not in permitidos:
        return None
    return {"texto": mensagens.AVISOS[codigo], "variante": mensagens.VARIANTE_DO_AVISO[codigo]}


def _tamanho(formacao, conteudos: dict) -> str | None:
    """024 FR-014: "no máximo N partes" para a formação disponível para iniciar, com N = a
    Seção de entrada mais o caminho mais longo depois dela (`maximo_restante`, 023). O
    conteúdo é lido uma vez por Versão na requisição."""
    if formacao.situacao is not SituacaoDaFormacao.DISPONIVEL_PARA_INICIAR:
        return None
    versao_id = formacao.campanha.versao_id
    if versao_id not in conteudos:
        conteudos[versao_id] = conteudo_da_versao(Versao(pk=versao_id))
    conteudo = conteudos[versao_id]
    if not conteudo.secoes:
        return None
    n = 1 + maximo_restante(conteudo, conteudo.secoes[0].id)
    if n == 1:
        return mensagens.TAMANHO_DA_PESQUISA_UMA
    return mensagens.TAMANHO_DA_PESQUISA.format(n=n)


def _formacao_apresentada(formacao, conteudos: dict | None = None) -> dict:
    """Forma compacta (014 FR-034): linha principal e complementar, só com o informado. Em
    andamento, também onde a pessoa parou (023 FR-017). Para iniciar, o tamanho máximo da
    pesquisa (024 FR-014), quando `conteudos` é passado."""
    return {
        "tamanho": None if conteudos is None else _tamanho(formacao, conteudos),
        "pk": formacao.conclusao.pk,
        "linha": resumo_da_formacao(formacao.conclusao),
        "complemento": complemento_da_formacao(formacao.conclusao),
        "situacao": mensagens.SITUACAO_DA_FORMACAO[formacao.situacao],
        "acao": _ACAO.get(formacao.situacao),
        "onde_parou": (
            onde_parou_da_participacao(formacao.participacao)
            if formacao.situacao is SituacaoDaFormacao.DISPONIVEL_PARA_RETOMAR
            else None
        ),
    }


# --- Envio pendente (023 FR-002 a FR-009) -----------------------------------------------------

_CAMPO_DA_SECAO = re.compile(r"p\d{1,4}(?:-complemento|-remover)?")


def _guardar_envio(request, participacao, posicao) -> None:
    """Envio de Seção sem sujeito válido: guarda só os campos de Pergunta, sem gravar nada
    (FR-002). A posse é verificada só ao restaurar, pelo sujeito que confirmar (FR-006)."""
    dados = {
        campo: request.POST.getlist(campo)
        for campo in request.POST
        if _CAMPO_DA_SECAO.fullmatch(campo)
    }
    pendente.guardar(request, participacao, posicao, dados)  # limites em `pendente`


def _envio_da_participacao(request, participacao):
    """O envio pendente válido desta Participação, ou `None`."""
    envio = pendente.ler(request)
    return envio if envio is not None and envio.participacao == participacao.pk else None


def _sem_sujeito(request) -> bool:
    return pessoa_em_uso(request) is None and declaracoes_em_uso(request) is None


@require_GET
@never_cache
@_respondendo
def formacoes(request):
    pessoa = _pessoa(request)
    # 023 FR-006: depois da nova confirmação, o envio pendente da própria Pessoa leva de volta
    # à Seção (uma vez); o de outro sujeito é descartado sem ser exibido.
    envio = pendente.ler(request)
    if envio is not None:
        dona = Participacao.objects.filter(
            pk=envio.participacao, conclusao__pessoa=pessoa, concluida_em__isnull=True
        ).exists()
        if not dona:
            pendente.descartar(request)
        elif not envio.apresentado:
            return redirect(f"/participacoes/{envio.participacao}/")
    situacao = situacao_de_entrada(pessoa)
    destaque = situacao.pendentes if situacao.resolucao in _COM_ACAO else ()
    chaves = {f.conclusao.pk for f in destaque}
    mensagem = _TELA_DE_FORMACOES[situacao.resolucao]
    # Na ordem devolvida pela 007, sem reordenar (014 FR-035).
    conteudos: dict = {}
    pendentes = [_formacao_apresentada(f, conteudos) for f in destaque]
    linha = pendentes[0]["linha"] if pendentes else ""
    # A linha da formação vai destacada na frase, sem mudar o texto (015 FR-032).
    antes_da_linha, depois_da_linha = mensagens.ENTRADA_FATO.split("{linha}")
    return render(
        request,
        "interface/formacoes.html",
        {
            "titulo": mensagens.TITULO_TRAJETORIA,
            "mensagem": mensagem,
            "entrada_fato": None if linha else mensagens.ENTRADA_SEM_ATRIBUTOS,
            "entrada_destaque": (
                {"antes": antes_da_linha, "linha": linha, "depois": depois_da_linha}
                if linha
                else None
            ),
            "entrada_continuacao": mensagens.ENTRADA_CONTINUACAO,
            "selecao": mensagens.SELECAO,
            "resolucao": situacao.resolucao.value,
            "principal": pendentes[0] if pendentes else None,
            "pendentes": pendentes,
            "outras": [
                _formacao_apresentada(f) for f in situacao.formacoes if f.conclusao.pk not in chaves
            ],
            "aviso": _aviso(request, "situacao", "salvo", "saida"),
            "entrada_operacional": mensagens.ENTRADA_OPERACIONAL,
            # 021 FR-005 e 024 FR-009: ligação para a trajetória de quem tem Conclusão.
            "narrativa_disponivel": narrativa_elegivel(pessoa),
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
        # A Pessoa vê a sua Conclusão, mesmo quando a resposta veio de uma declaração validada
        # (019 FR-092): nunca os valores declarados nem o caminho do declarante.
        return _tela(request, mensagens.JA_RESPONDIDA, conclusao=conclusao_efetiva(participacao))
    return redirect(_base(participacao))


@require_GET
@never_cache
@_respondendo
def participacao(request, participacao):
    participacao = _participacao_do_sujeito(request, participacao)
    jornada = _jornada(request, participacao)
    envio = _envio_da_participacao(request, participacao)
    if envio is not None and (jornada.concluida_em is not None or not jornada.admite_escrita):
        pendente.descartar(request)
        envio = None
    if jornada.concluida_em is not None:
        return redirect(_base(participacao) + "concluida/")
    if not jornada.admite_escrita:
        return _tela(request, mensagens.PERIODO_ENCERRADO, **_da_participacao(participacao))
    if envio is not None and not envio.apresentado:
        return redirect(_base(participacao) + f"secoes/{envio.posicao}/")
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
            _tela(request, mensagens.JA_RESPONDIDA, **_da_participacao(participacao))
        )
    if not jornada.admite_escrita:
        raise _Resposta(
            _tela(request, mensagens.PERIODO_ENCERRADO, **_da_participacao(participacao))
        )


def _passagem(participacao, jornada, posicao):
    """A Passagem da Seção pedida no percurso determinado (006). Fora dele — ramo não
    escolhido, Seção ainda não alcançada ou posição inexistente — leva à Seção atual (FR-055)."""
    for passagem in jornada.passagens:
        if passagem.secao.posicao == posicao:
            return passagem
    raise _Resposta(redirect(_endereco_atual(participacao, jornada) + "?aviso=percurso"))


def _tela_da_secao(request, participacao, jornada, passagem, formulario, erros=None, *,
                   pendencias=False, recuperado=False):  # fmt: skip
    # Título e abertura vêm da Versão já carregada com a Participação (sem reler o conteúdo);
    # a primeira passagem do percurso é sempre a primeira Seção da Versão (006 FR-014).
    versao = participacao.campanha.versao
    # Restauração de envio pendente (023 FR-007): os valores enviados, sem erros.
    itens = formulario.itens(erros, com_erros=not recuperado)
    # Anterior **no percurso determinado** (006), nunca na ordem da Versão (FR-054).
    indice = jornada.passagens.index(passagem)
    parte = indice + 1
    # Ponto seguro de salvamento no meio das Seções longas (023 FR-010).
    meio = (
        ceil(len(itens) / 2) if len(itens) > mensagens.LIMITE_PONTO_DO_MEIO else None
    )
    anterior = jornada.passagens[indice - 1].secao.posicao if indice else None
    resumo = [
        {"ancora": item.nome, "texto": f"{item.pergunta.texto} — {erro}"}
        for item in itens
        for erro in item.erros
    ]
    # Pendência (envio aceito, falta resposta) e erro de forma (envio recusado, nada gravado)
    # nunca coexistem numa reapresentação; só muda a apresentação (014 FR-003 a FR-008).
    tipo = ("pendencias" if pendencias else "erros") if resumo else None
    textos = mensagens.RESUMO.get(tipo, {})
    return render(
        request,
        "interface/secao.html",
        {
            "titulo_pesquisa": versao.titulo or "Pesquisa",
            "texto_abertura": versao.texto_abertura,
            "primeira": indice == 0,
            "acao": _base(participacao) + f"secoes/{passagem.secao.posicao}/",
            "rotulo_formacao": rotulo_da_formacao(participacao),
            "declarada": participacao.formacao_declarada_id is not None,
            "resumo_formacao": resumo_da_formacao(formacao_exibida(participacao)),
            "passagem": passagem,
            "itens": itens,
            "resumo_erros": resumo,
            "tipo_resumo": tipo,
            "titulo_resumo": textos.get("titulo"),
            "prefixo_titulo": textos.get("prefixo_titulo", ""),
            "prefixo_item": textos.get("prefixo_item"),
            "frase_salvo": (
                mensagens.SECAO_SALVA
                if tipo == "pendencias" and _ha_resposta_na_secao(jornada, passagem.secao)
                else None
            ),
            "aviso": (
                {"texto": mensagens.RECUPERADO, "variante": "informacao"}
                if recuperado
                else _aviso(request, "percurso")
            ),
            # 023 FR-016: discreto, junto da parte, e só se a Seção anterior do percurso tem
            # Resposta gravada (014 FR-008) — nunca pela simples presença do código no endereço.
            "anterior_salva": (
                mensagens.AVISOS["anterior"]
                if request.GET.get("aviso") == "anterior"
                and not recuperado
                and indice
                and _ha_resposta_na_secao(jornada, jornada.passagens[indice - 1].secao)
                else None
            ),
            "anterior": anterior and _base(participacao) + f"secoes/{anterior}/",
            "sair_sem_salvar_nota": mensagens.SAIR_SEM_SALVAR_NOTA,
            # 023 FR-013, FR-015: parte no percurso e máximo restante; "Parte X" sem título.
            "rotulo_secao": rotulo_da_secao(passagem.secao, parte),
            "linha_da_parte": linha_da_parte(
                parte, maximo_restante(jornada.conteudo, passagem.secao.id)
            ),
            "meio": meio,
            "precisa_parar": mensagens.PRECISA_PARAR,
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def secao(request, participacao, posicao):
    if request.method == "POST" and _sem_sujeito(request):
        # 023 FR-002: sessão expirada ou ausente; guarda o envio e vai à entrada com aviso.
        _guardar_envio(request, participacao, posicao)
    participacao = _participacao_do_sujeito(request, participacao)
    jornada = _jornada(request, participacao)
    envio = _envio_da_participacao(request, participacao)
    try:
        _exigir_rascunho_aberto(request, participacao, jornada)
        passagem = _passagem(participacao, jornada, posicao)
    except _Resposta:
        # Participação concluída, coleta encerrada ou Seção fora do percurso (FR-008).
        if envio is not None and envio.posicao == posicao:
            pendente.descartar(request)
        raise
    if request.method == "POST":
        return _salvar(request, participacao, jornada, passagem)
    if envio is not None and envio.posicao == posicao:
        dados = QueryDict(mutable=True)
        for campo, valores in envio.dados.items():
            dados.setlist(campo, valores)
        pendente.marcar_apresentado(request)
        formulario = FormularioDaSecao(passagem.secao, jornada.respostas, data=dados)
        return _tela_da_secao(
            request, participacao, jornada, passagem, formulario, recuperado=True
        )
    formulario = FormularioDaSecao(passagem.secao, jornada.respostas)
    pendencias = None
    if request.GET.get("pendencias") == "1" and passagem is jornada.passagens[-1]:
        pendencias = _pendencias(passagem)
    return _tela_da_secao(
        request, participacao, jornada, passagem, formulario, pendencias,
        pendencias=bool(pendencias),
    )  # fmt: skip


def _ha_resposta_na_secao(jornada, secao) -> bool:
    """Se alguma Pergunta da Seção tem Resposta gravada (005), segundo a jornada já lida.
    Única base para dizer ao egresso que algo "está salvo" (014 FR-008): nunca um
    indicador do endereço."""
    return any(p.id in jornada.respostas for p in secao.perguntas)


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
        return _tela(request, mensagens.JA_RESPONDIDA, **_da_participacao(participacao))
    if resultado.motivo_global is Motivo.COLETA_NAO_ADMITIDA:
        return _tela(request, mensagens.PERIODO_ENCERRADO, **_da_participacao(participacao))
    if resultado.motivo_global is not None:
        raise Http404
    if resultado.erros_por_pergunta:
        return _tela_da_secao(
            request, participacao, jornada, passagem, formulario, resultado.erros_por_pergunta
        )
    # Envio aceito: o envio pendente desta Seção já cumpriu seu papel (023 FR-008).
    envio = _envio_da_participacao(request, participacao)
    if envio is not None and envio.posicao == passagem.secao.posicao:
        pendente.descartar(request)
    # O próximo passo é sempre o que a 006 calcula agora, com as Respostas gravadas.
    jornada = _jornada(request, participacao)
    passagem = _passagem(participacao, jornada, passagem.secao.posicao)
    if request.POST.get("depois") == "sair":
        # "Salvar e sair" (014 FR-011, FR-012): mesma validação e gravação; só o destino
        # muda. O aviso só diz que algo está salvo se há Resposta gravada na Seção (FR-008).
        salvo = _ha_resposta_na_secao(jornada, passagem.secao)
        destino = "/formacoes/" if participacao.conclusao_id else "/declaracao/"
        return redirect(destino + "?aviso=" + ("salvo" if salvo else "saida"))
    secao = _base(participacao) + f"secoes/{passagem.secao.posicao}/"
    if not passagem.satisfeita:
        return redirect(secao + "?pendencias=1")
    if passagem.destino is Saida.FINALIZACAO:
        return redirect(_base(participacao) + "concluir/")
    # Seção satisfeita com destino determinado: o percurso da 006 segue para ele, que é,
    # portanto, a passagem seguinte (006 FR-014).
    seguinte = jornada.passagens[jornada.passagens.index(passagem) + 1]
    # "Parte anterior salva." só com Resposta gravada na Seção enviada (023 FR-016; 014 FR-008).
    aviso = "?aviso=anterior" if _ha_resposta_na_secao(jornada, passagem.secao) else ""
    return redirect(_base(participacao) + f"secoes/{seguinte.secao.posicao}/" + aviso)


# --- Conclusão (006) -----------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def concluir_view(request, participacao):
    participacao = _participacao_do_sujeito(request, participacao)
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
            "nome": rotulo_da_secao(p.secao, parte),
            "endereco": _base(participacao) + f"secoes/{p.secao.posicao}/",
        }
        for parte, p in enumerate(jornada.passagens, start=1)
    ]
    return render(
        request,
        "interface/conclusao.html",
        {
            "titulo_pesquisa": participacao.campanha.versao.titulo or "Pesquisa",
            "contexto_formacao": contexto_da_formacao(formacao_exibida(participacao)),
            "rotulo_formacao": rotulo_da_formacao(participacao),
            "declarada": participacao.formacao_declarada_id is not None,
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
            return _tela(request, mensagens.PERIODO_ENCERRADO, **_da_participacao(participacao))
        if set(erro.motivos) != {Motivo.OBRIGATORIA_PENDENTE}:
            return _tela(
                request,
                mensagens.PESQUISA_INDISPONIVEL,
                declarada=participacao.formacao_declarada_id is not None,
            )
        jornada = _jornada(request, participacao)
        return redirect(_endereco_atual(participacao, jornada) + "?pendencias=1")
    return redirect(_base(participacao) + "concluida/")


@require_GET
@never_cache
@_respondendo
def concluida(request, participacao):
    """Confirmação simples: sem respostas, data, comprovante ou ação de editar (FR-062,
    FR-063). A Participação concluída é lida, nunca reaberta. A ação principal leva à Minha
    trajetória (021 FR-003, revista pela 020); abaixo, o convite secundário e opcional de
    e-mail (020 FR-009, E7). A declarada continua como na 019 (021 FR-007). Antes delas, a
    próxima formação pendente da Pessoa, quando houver (023 FR-011, FR-012)."""
    participacao = _participacao_do_sujeito(request, participacao)
    if participacao.concluida_em is None:
        return redirect(_base(participacao))
    proximas = _proximas_formacoes(request, participacao)
    proxima = (
        {**_formacao_apresentada(proximas[0]), "acao": mensagens.ACAO_PROXIMA[proximas[0].situacao]}
        if proximas
        else None
    )
    curso = formacao_exibida(participacao).curso
    encerramento = participacao.campanha.versao.texto_encerramento
    return render(
        request,
        "interface/concluida.html",
        {
            "registro": (
                mensagens.REGISTRADA_DECLARADA
                if participacao.formacao_declarada_id
                else (
                    mensagens.REGISTRADAS_CURSO.format(curso=curso)
                    if curso
                    else mensagens.REGISTRADAS
                )
            ),
            # O texto de encerramento da Versão já agradece: um agradecimento só (014 FR-040).
            "agradecimento": None
            if encerramento or participacao.formacao_declarada_id
            else mensagens.AGRADECIMENTO,
            "declarada": bool(participacao.formacao_declarada_id),
            "contexto_formacao": contexto_da_formacao(formacao_exibida(participacao)),
            "rotulo_formacao": rotulo_da_formacao(participacao),
            "texto_encerramento": encerramento,
            "proxima": proxima,
            "outras_proximas": len(proximas) > 1,
            "proxima_titulo": mensagens.PROXIMA_FORMACAO,
        },
    )


def _proximas_formacoes(request, participacao) -> list:
    """As formações a iniciar ou retomar da Pessoa, na ordem da 007, sem a recém-concluída
    (023 FR-011). Nunca para a declarada, nem com ambiguidade ou sem pesquisa (FR-012)."""
    pessoa = pessoa_em_uso(request)
    if participacao.formacao_declarada_id or pessoa is None:
        return []
    return [
        f
        for f in situacao_de_entrada(pessoa).pendentes
        if f.conclusao.pk != participacao.conclusao_id
    ]

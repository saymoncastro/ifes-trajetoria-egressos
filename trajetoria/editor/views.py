"""Telas do editor institucional do instrumento (Feature 009; contracts/rotas.md).

**Camada fina sobre a Feature 002.** Toda escrita chama uma operação de
`trajetoria.instrumento.operacoes`; as leituras usam `conteudo_da_versao` e consultas
simples. Nenhuma regra do domínio vive aqui: as recusas vêm da 002 e são traduzidas por
mapas **locais**, só com os motivos que a operação chamada pode devolver — motivo não
mapeado continua sendo erro (research R10). Nada aqui publica (002/DP-001), autentica ou
autoriza (DP-901): o editor só existe no modo de demonstração local.
"""

from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from trajetoria.editor import acoes, apresentacao, mensagens
from trajetoria.editor import formularios as f
from trajetoria.editor.diagnostico import diagnosticar
from trajetoria.instrumento import operacoes as op
from trajetoria.instrumento.conteudo import Escala, conteudo_da_versao
from trajetoria.instrumento.models import Opcao, Pergunta, Pesquisa, Secao, TipoPergunta, Versao
from trajetoria.instrumento.regras import Motivo, OperacaoRejeitada
from trajetoria.interface.formularios import FormularioDaSecao


class _Resposta(Exception):
    """Interrompe a view com uma resposta pronta (redirecionamento ou tela 409/404)."""

    def __init__(self, resposta):
        self.resposta = resposta


def _respondendo(view):
    @wraps(view)
    def envolvida(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except _Resposta as interrompida:
            return interrompida.resposta

    return envolvida


def _render(request, template, contexto, status=200):
    formulario = contexto.get("formulario")
    contexto = {
        "banner": mensagens.BANNER,
        "ha_erros": bool(formulario is not None and formulario.errors),
        "aviso": _aviso(request),
        **contexto,
    }
    return render(request, template, contexto, status=status)


def _dados(request):
    """Dados do formulário: num POST, sempre ligados (mesmo vazios, para serem validados);
    num GET, nenhum."""
    return request.POST if request.method == "POST" else None


def _aviso(request) -> str | None:
    """Aviso por código de lista fechada; qualquer outro valor é ignorado."""
    return mensagens.AVISOS.get(request.GET.get("aviso", ""))


def _tela(request, titulo, paragrafos, ligacoes, status):
    return _render(
        request,
        "editor/aviso.html",
        {"titulo": titulo, "mensagem": paragrafos, "ligacoes": ligacoes},
        status=status,
    )


def _publicada(request, versao):
    return _tela(
        request,
        "Versão publicada",
        (mensagens.PUBLICADA_409,),
        (
            ("Criar nova Versão a partir desta", f"/editor/versoes/{versao.pk}/nova-a-partir/"),
            ("Ver a Versão", f"/editor/versoes/{versao.pk}/"),
        ),
        status=409,
    )


def _conflito(request, endereco):
    return _tela(
        request,
        "O conteúdo mudou",
        (mensagens.CONFLITO,),
        (("Ver o estado atual", endereco),),
        status=409,
    )


def _exigir_rascunho(request, versao, consulta: str) -> None:
    """Versão publicada: formulário (GET) volta à consulta; escrita (POST) é recusada com
    409 **antes** de qualquer operação. A recusa definitiva continua sendo a da 002."""
    if not versao.publicada:
        return
    if request.method == "POST":
        raise _Resposta(_publicada(request, versao))
    raise _Resposta(redirect(consulta + "?aviso=publicada"))


def _objeto(request, modelo, pk, *relacionados):
    """O elemento pedido. Inexistente: GET → 404 padrão; POST → 404 explicando que o
    conteúdo mudou (formulário antigo)."""
    objeto = modelo.objects.select_related(*relacionados).filter(pk=pk).first()
    if objeto is not None:
        return objeto
    if request.method == "POST":
        raise _Resposta(
            _tela(
                request,
                "O conteúdo mudou",
                (mensagens.CONFLITO,),
                (("Ir ao editor", "/editor/"),),
                404,
            )
        )
    raise Http404


_CONFLITOS = (Motivo.POSICAO_OCUPADA, Motivo.ORDEM_INCOMPLETA)


def _aplicar_rejeicao(request, erro: OperacaoRejeitada, formulario, mapa: dict, versao, endereco):
    """Traduz a recusa da 002: `VERSAO_PUBLICADA` → 409; conflito de posição/ordem → 409;
    motivos do `mapa` local → erro no campo (`None` = resumo). Qualquer outro motivo é
    relançado: é erro de programa, não validação."""
    motivos = set(erro.motivos)
    if Motivo.VERSAO_PUBLICADA in motivos:
        raise _Resposta(_publicada(request, versao))
    if motivos & set(_CONFLITOS):
        raise _Resposta(_conflito(request, endereco))
    if not motivos <= set(mapa):
        raise erro
    for motivo in erro.motivos:
        campo, texto = mapa[motivo]
        formulario.add_error(campo, texto)


def _mover_e_voltar(request, em_ordem, elemento, reordenar, dono, versao, destino, prefixo):
    """Subir/descer (FR-061 a FR-064): lê a ordem atual, troca com o vizinho e chama a
    reordenação completa da 002. Na ponta nada é gravado. Volta à âncora do elemento
    (`#<prefixo>-<ordinal novo>`)."""
    _exigir_rascunho(request, versao, destino)
    nova = acoes.mover(em_ordem, elemento, request.POST.get("direcao", ""))
    if nova is None:
        return redirect(destino + "?aviso=sem-movimento")
    try:
        reordenar(dono, nova)
    except OperacaoRejeitada as erro:
        _aplicar_rejeicao(request, erro, None, {}, versao, destino)
    return redirect(f"{destino}#{prefixo}-{nova.index(elemento) + 1}")


def _trilha_pesquisa(pesquisa):
    return [("Pesquisas", "/editor/"), (pesquisa.nome, f"/editor/pesquisas/{pesquisa.pk}/")]


# --- Pesquisas e Versões (US1–US4) ------------------------------------------------------------


@require_GET
@never_cache
def pesquisas(request):
    lista = Pesquisa.objects.annotate(versoes_n=Count("versoes")).order_by("nome", "pk")
    return _render(
        request,
        "editor/pesquisas.html",
        {
            "pesquisas": [
                (p, apresentacao.plural(p.versoes_n, "Versão", "Versões", "nenhuma Versão"))
                for p in lista
            ],
            "trilha": [("Pesquisas", None)],
        },
    )


@require_GET
@never_cache
@_respondendo
def pesquisa(request, pesquisa):
    pesquisa = _objeto(request, Pesquisa, pesquisa)
    return _render(
        request,
        "editor/pesquisa.html",
        {
            "pesquisa": pesquisa,
            "versoes": pesquisa.versoes.select_related("origem").order_by("designacao"),
            "trilha": [("Pesquisas", "/editor/"), (pesquisa.nome, None)],
        },
    )


def _formulario(request, formulario, *, titulo, trilha, cancelar, envio, campos=None, **extra):
    """Página de formulário simples (`formulario.html`): um `<form>`, um envio."""
    return _render(
        request,
        "editor/formulario.html",
        {
            "formulario": formulario,
            "campos": campos if campos is not None else list(formulario),
            "titulo": titulo,
            "trilha": [*trilha, (titulo, None)],
            "cancelar": cancelar,
            "rotulo_envio": envio,
            "acao": request.get_full_path(),
            **extra,
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def pesquisa_nova(request):
    formulario = f.PesquisaForm(_dados(request))
    repetido = False
    if request.method == "POST" and formulario.is_valid():
        nome = formulario.cleaned_data["nome"]
        confirmado = formulario.cleaned_data["confirmar_nome_repetido"]
        # Aviso operacional, não regra: a 002 permite nomes repetidos (FR-012).
        repetido = not confirmado and Pesquisa.objects.filter(nome=nome).exists()
        if not repetido:
            try:
                pesquisa = op.criar_pesquisa(nome)
            except OperacaoRejeitada as erro:
                mapa = {Motivo.TEXTO_VAZIO: ("nome", mensagens.TEXTO_VAZIO)}
                _aplicar_rejeicao(request, erro, formulario, mapa, None, "/editor/")
            else:
                return redirect(f"/editor/pesquisas/{pesquisa.pk}/?aviso=pesquisa-criada")
    campos = [c for c in formulario if repetido or c.name != "confirmar_nome_repetido"]
    return _formulario(
        request,
        formulario,
        titulo="Criar Pesquisa",
        trilha=[("Pesquisas", "/editor/")],
        cancelar="/editor/",
        envio="Criar Pesquisa",
        campos=campos,
        alerta=mensagens.NOME_REPETIDO if repetido else None,
    )


_MAPA_DESIGNACAO = {
    Motivo.DESIGNACAO_REPETIDA: ("designacao", mensagens.DESIGNACAO_REPETIDA),
    Motivo.TEXTO_VAZIO: ("designacao", mensagens.TEXTO_VAZIO),
}


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def versao_nova(request, pesquisa):
    pesquisa = _objeto(request, Pesquisa, pesquisa)
    formulario = f.DesignacaoForm(_dados(request))
    endereco = f"/editor/pesquisas/{pesquisa.pk}/"
    if request.method == "POST" and formulario.is_valid():
        try:
            versao = op.criar_versao(pesquisa, formulario.cleaned_data["designacao"])
        except OperacaoRejeitada as erro:
            _aplicar_rejeicao(request, erro, formulario, _MAPA_DESIGNACAO, None, endereco)
        else:
            return redirect(f"/editor/versoes/{versao.pk}/?aviso=versao-criada")
    return _formulario(
        request,
        formulario,
        titulo="Criar Versão em rascunho",
        trilha=_trilha_pesquisa(pesquisa),
        cancelar=endereco,
        envio="Criar Versão",
        introducao=("A Versão nasce vazia, em rascunho.",),
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def versao_a_partir(request, versao):
    origem = _objeto(request, Versao, versao, "pesquisa")
    formulario = f.DesignacaoForm(_dados(request))
    endereco = f"/editor/versoes/{origem.pk}/"
    if request.method == "POST" and formulario.is_valid():
        try:
            nova = op.criar_versao_a_partir_de(origem, formulario.cleaned_data["designacao"])
        except OperacaoRejeitada as erro:
            _aplicar_rejeicao(request, erro, formulario, _MAPA_DESIGNACAO, None, endereco)
        else:
            return redirect(f"/editor/versoes/{nova.pk}/?aviso=versao-criada")
    return _formulario(
        request,
        formulario,
        titulo=f"Criar nova Versão a partir de «{origem.designacao}»",
        trilha=[*_trilha_pesquisa(origem.pesquisa), (origem.designacao, endereco)],
        cancelar=endereco,
        envio="Criar nova Versão",
        introducao=(
            "A nova Versão começa como cópia do conteúdo desta, em rascunho, e é "
            "independente: alterá-la não muda a Versão de origem.",
        ),
    )


def _marcar(secoes, diagnostico) -> None:
    """Marcas por elemento (FR-074), sempre do mesmo diagnóstico, sem cálculo próprio."""
    if diagnostico is None:
        return
    for secao in secoes:
        secao["problemas"] = diagnostico.textos_de(secao["id"])
        for pergunta in secao["perguntas"]:
            pergunta["problemas"] = diagnostico.textos_de(pergunta["id"], *pergunta["opcoes_ids"])


def _textos_do_diagnostico() -> dict:
    return {
        "sem_impedimentos": mensagens.SEM_IMPEDIMENTOS,
        "semantica": mensagens.SEMANTICA_NAVEGACAO,
    }


def _trilha_versao(versao):
    return [
        *_trilha_pesquisa(versao.pesquisa),
        (versao.designacao, f"/editor/versoes/{versao.pk}/"),
    ]


@require_GET
@never_cache
@_respondendo
def versao(request, versao):
    versao = _objeto(request, Versao, versao, "pesquisa", "origem")
    conteudo = conteudo_da_versao(versao)
    secoes = apresentacao.estrutura(conteudo)
    total = sum(len(s["perguntas"]) for s in secoes)
    diagnostico = None if versao.publicada else diagnosticar(versao, conteudo)
    _marcar(secoes, diagnostico)
    return _render(
        request,
        "editor/versao.html",
        {
            "versao": versao,
            "editavel": not versao.publicada,
            "diagnostico": diagnostico,
            **_textos_do_diagnostico(),
            "secoes": secoes,
            "total_secoes": apresentacao.plural(len(secoes), "Seção", "Seções", "0 Seções"),
            "total_perguntas": apresentacao.plural(total, "Pergunta", "Perguntas", "0 Perguntas"),
            "trabalhe_em_copia": mensagens.TRABALHE_EM_COPIA,
            "trilha": [*_trilha_pesquisa(versao.pesquisa), (versao.designacao, None)],
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def versao_dados(request, versao):
    versao = _objeto(request, Versao, versao, "pesquisa")
    endereco = f"/editor/versoes/{versao.pk}/"
    _exigir_rascunho(request, versao, endereco)
    inicial = {
        "designacao": versao.designacao,
        "titulo": versao.titulo or "",
        "texto_abertura": versao.texto_abertura or "",
        "texto_encerramento": versao.texto_encerramento or "",
    }
    formulario = f.DadosVersaoForm(_dados(request), initial=inicial)
    if request.method == "POST" and formulario.is_valid():
        try:
            op.alterar_versao(versao, **formulario.argumentos())
        except OperacaoRejeitada as erro:
            _aplicar_rejeicao(request, erro, formulario, _MAPA_DESIGNACAO, versao, endereco)
        else:
            return redirect(endereco + "?aviso=dados-salvos")
    return _formulario(
        request,
        formulario,
        titulo="Editar dados da Versão",
        trilha=_trilha_versao(versao),
        cancelar=endereco,
        envio="Salvar",
    )


# --- Seções (US6) e navegação (US10) -------------------------------------------------------------


def _destinos(conteudo, exceto=None, prefixo="Ir para a ") -> list[tuple[str, str]]:
    """Seções da Versão como opções de destino ("Ir para a Seção N — …"), sem filtro de
    posição: destino anterior é problema do diagnóstico A (002 FR-059 d), não do formulário."""
    local = apresentacao.localizador(conteudo)
    return [
        (str(s.id), f"{prefixo}{local[s.id].rotulo}") for s in conteudo.secoes if s.id != exceto
    ]


def _destino(valor: str):
    """Valor do formulário → destino das operações da 002 (`None`, `FINALIZAR` ou Seção)."""
    if not valor:
        return None
    if valor == "finalizar":
        return op.FINALIZAR
    return Secao.objects.get(pk=valor)


def _secao(request, pk) -> Secao:
    return _objeto(request, Secao, pk, "versao__pesquisa")


def _trilha_secao(secao, conteudo):
    rotulo = apresentacao.localizador(conteudo)[secao.pk].rotulo
    return [*_trilha_versao(secao.versao), (rotulo, f"/editor/secoes/{secao.pk}/")]


def _gravar(request, versao, formulario, gravar, mapa, endereco):
    """Executa `gravar()` (uma ou mais operações da 002) num único bloco atômico. Recusa
    conhecida → erro no formulário e `None`; as demais seguem `_aplicar_rejeicao`. Um
    elemento escolhido no formulário que deixou de existir antes da gravação (por exemplo, a
    Seção de destino removida por outra pessoa) é conflito, não erro (FR-095)."""
    try:
        with transaction.atomic():
            return gravar()
    except ObjectDoesNotExist:
        raise _Resposta(_conflito(request, endereco)) from None
    except OperacaoRejeitada as erro:
        _aplicar_rejeicao(request, erro, formulario, mapa, versao, endereco)
        return None


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def secao_nova(request, versao):
    versao = _objeto(request, Versao, versao, "pesquisa")
    endereco = f"/editor/versoes/{versao.pk}/"
    _exigir_rascunho(request, versao, endereco)
    formulario = f.SecaoForm(_destinos(conteudo_da_versao(versao)), _dados(request))
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            posicao = acoes.proxima_posicao(versao.secoes.all())
            secao = op.adicionar_secao(versao, posicao, **formulario.argumentos())
            destino = _destino(formulario.cleaned_data["encaminhamento"])
            if destino is not None:
                op.definir_encaminhamento(secao, destino)
            return secao

        secao = _gravar(request, versao, formulario, gravar, {}, endereco)
        if secao is not None:
            return redirect(f"/editor/secoes/{secao.pk}/?aviso=secao-criada")
    return _formulario(
        request,
        formulario,
        titulo="Adicionar Seção",
        trilha=_trilha_versao(versao),
        cancelar=endereco,
        envio="Adicionar Seção ao final",
        introducao=(mensagens.SEMANTICA_NAVEGACAO,),
    )


@require_GET
@never_cache
@_respondendo
def secao(request, secao):
    secao = _secao(request, secao)
    versao = secao.versao
    conteudo = conteudo_da_versao(versao)
    dados = next(s for s in apresentacao.estrutura(conteudo) if s["id"] == secao.pk)
    _marcar([dados], None if versao.publicada else diagnosticar(versao, conteudo))
    return _render(
        request,
        "editor/secao.html",
        {
            "secao": secao,
            "dados": dados,
            "versao": versao,
            "editavel": not versao.publicada,
            "trilha": [*_trilha_versao(versao), (dados["rotulo"], None)],
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def secao_editar(request, secao):
    secao = _secao(request, secao)
    endereco = f"/editor/secoes/{secao.pk}/"
    _exigir_rascunho(request, secao.versao, endereco)
    conteudo = conteudo_da_versao(secao.versao)
    inicial = {
        "titulo": secao.titulo or "",
        "texto": secao.texto or "",
        "encaminhamento": str(secao.encaminhamento_id or ""),
    }
    destinos = _destinos(conteudo, exceto=secao.pk)
    formulario = f.SecaoForm(destinos, _dados(request), initial=inicial)
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            op.alterar_secao(secao, **formulario.argumentos())
            destino = _destino(formulario.cleaned_data["encaminhamento"])
            return op.definir_encaminhamento(secao, destino)

        if _gravar(request, secao.versao, formulario, gravar, {}, endereco) is not None:
            return redirect(endereco + "?aviso=dados-salvos")
    return _formulario(
        request,
        formulario,
        titulo="Editar dados da Seção",
        trilha=_trilha_secao(secao, conteudo),
        cancelar=endereco,
        envio="Salvar",
        introducao=(mensagens.SEMANTICA_NAVEGACAO,),
    )


@require_POST
@never_cache
@_respondendo
def secao_mover(request, secao):
    secao = _secao(request, secao)
    versao = secao.versao
    em_ordem = list(versao.secoes.order_by("posicao"))
    return _mover_e_voltar(
        request, em_ordem, secao, op.reordenar_secoes, versao, versao,
        f"/editor/versoes/{versao.pk}/", "secao",
    )  # fmt: skip


def _remover(request, *, versao, rotulo, consequencias, remover, voltar, sucesso, trilha,
             explicar):  # fmt: skip
    """Confirmação (GET) e remoção (POST) pela operação da 002. A interface não verifica
    antes se a remoção é possível: quem decide é a 002, e a recusa é explicada por
    `explicar(erro)` (motivos conhecidos) ou segue como erro."""
    _exigir_rascunho(request, versao, voltar)
    impedimentos = ()
    if request.method == "POST":
        try:
            remover()
        except OperacaoRejeitada as erro:
            impedimentos = explicar(erro)
            if not impedimentos:
                _aplicar_rejeicao(request, erro, None, {}, versao, voltar)
        else:
            return redirect(sucesso)
    return _render(
        request,
        "editor/confirmar_remocao.html",
        {
            "rotulo": rotulo,
            "consequencias": consequencias,
            "impedimentos": impedimentos,
            "acao": request.path,
            "voltar": voltar,
            "trilha": [*trilha, ("Remover", None)],
        },
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def secao_remover(request, secao):
    secao = _secao(request, secao)
    versao = secao.versao
    conteudo = conteudo_da_versao(versao)
    rotulo = apresentacao.localizador(conteudo)[secao.pk].rotulo

    def explicar(erro):
        if erro.motivos == (Motivo.SECAO_COM_PERGUNTAS,):
            return (mensagens.SECAO_COM_PERGUNTAS,)
        if erro.motivos == (Motivo.SECAO_REFERENCIADA,):
            referencias = "; ".join(apresentacao.referencias_a(conteudo, secao.pk))
            return (mensagens.SECAO_REFERENCIADA.format(referencias=referencias),)
        return ()

    return _remover(
        request,
        versao=versao,
        rotulo=rotulo,
        consequencias=(),
        remover=lambda: op.remover_secao(secao),
        voltar=f"/editor/secoes/{secao.pk}/",
        sucesso=f"/editor/versoes/{versao.pk}/?aviso=secao-removida",
        trilha=_trilha_secao(secao, conteudo)[:-1],
        explicar=explicar,
    )


# --- Perguntas (US7) -----------------------------------------------------------------------------

_MAPA_PERGUNTA = {
    Motivo.TEXTO_VAZIO: ("texto", mensagens.TEXTO_VAZIO),
    Motivo.ESCALA_INVALIDA: ("inicio", mensagens.ESCALA_INVALIDA),
}


def _pergunta(request, pk) -> Pergunta:
    return _objeto(request, Pergunta, pk, "secao__versao__pesquisa")


def _introducao_do_tipo(tipo) -> tuple[str, ...]:
    nome, descricao = apresentacao.TIPOS[TipoPergunta(tipo)]
    return (f"Tipo: {nome} — {descricao}.",)


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def pergunta_nova(request, secao):
    secao = _secao(request, secao)
    versao = secao.versao
    endereco = f"/editor/secoes/{secao.pk}/"
    _exigir_rascunho(request, versao, endereco)
    trilha = _trilha_secao(secao, conteudo_da_versao(versao))
    tipo = request.GET.get("tipo", "")
    if tipo not in TipoPergunta.values:
        return _render(
            request,
            "editor/pergunta_tipo.html",
            {
                "formulario": f.TipoPerguntaForm(),
                "acao": request.path,
                "cancelar": endereco,
                "trilha": [*trilha, ("Adicionar Pergunta", None)],
            },
        )
    formulario = f.PerguntaForm(tipo, _dados(request))
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            posicao = acoes.proxima_posicao(secao.perguntas.all())
            return op.adicionar_pergunta(secao, posicao, tipo, **formulario.argumentos())

        pergunta = _gravar(request, versao, formulario, gravar, _MAPA_PERGUNTA, endereco)
        if pergunta is not None:
            if formulario.tipo in apresentacao.TIPOS_DE_ESCOLHA:
                return redirect(f"/editor/perguntas/{pergunta.pk}/?aviso=adicione-opcoes")
            ordinal = secao.perguntas.filter(posicao__lte=pergunta.posicao).count()
            return redirect(f"{endereco}?aviso=pergunta-criada#pergunta-{ordinal}")
    return _formulario(
        request,
        formulario,
        titulo="Adicionar Pergunta",
        trilha=trilha,
        cancelar=endereco,
        envio="Adicionar Pergunta ao final da Seção",
        introducao=_introducao_do_tipo(tipo),
    )


@require_GET
@never_cache
@_respondendo
def pergunta(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    versao = pergunta.secao.versao
    conteudo = conteudo_da_versao(versao)
    dados = apresentacao.pergunta_apresentada(conteudo, pergunta.pk)
    if not versao.publicada:
        diagnostico = diagnosticar(versao, conteudo)
        dados["problemas"] = diagnostico.textos_de(pergunta.pk)
        for opcao in dados["opcoes"]:
            opcao["problemas"] = diagnostico.textos_de(opcao["id"])
    return _render(
        request,
        "editor/pergunta.html",
        {
            "pergunta": pergunta,
            "dados": dados,
            "versao": versao,
            "editavel": not versao.publicada,
            "tipo_fixo": mensagens.TIPO_FIXO,
            "so_escolha_unica": mensagens.SO_ESCOLHA_UNICA,
            "semantica": mensagens.SEMANTICA_NAVEGACAO,
            "trilha": [
                *_trilha_versao(versao),
                (dados["secao"]["rotulo"], dados["secao"]["endereco"]),
                (dados["rotulo"], None),
            ],
        },
    )


def _trilha_pergunta(pergunta, conteudo):
    dados = apresentacao.pergunta_apresentada(conteudo, pergunta.pk)
    return [
        *_trilha_versao(pergunta.secao.versao),
        (dados["secao"]["rotulo"], dados["secao"]["endereco"]),
        (dados["rotulo"], f"/editor/perguntas/{pergunta.pk}/"),
    ]


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def pergunta_editar(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    versao = pergunta.secao.versao
    endereco = f"/editor/perguntas/{pergunta.pk}/"
    _exigir_rascunho(request, versao, endereco)
    inicial = {
        "texto": pergunta.texto,
        "texto_explicativo": pergunta.texto_explicativo or "",
        "obrigatoria": "sim" if pergunta.obrigatoria else "nao",
        "inicio": pergunta.escala_inicio,
        "fim": pergunta.escala_fim,
        "rotulo_inicio": pergunta.escala_rotulo_inicio or "",
        "rotulo_fim": pergunta.escala_rotulo_fim or "",
    }
    formulario = f.PerguntaForm(pergunta.tipo, _dados(request), initial=inicial)
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            return op.alterar_pergunta(pergunta, **formulario.argumentos())

        if _gravar(request, versao, formulario, gravar, _MAPA_PERGUNTA, endereco) is not None:
            return redirect(endereco + "?aviso=dados-salvos")
    return _formulario(
        request,
        formulario,
        titulo="Editar Pergunta",
        trilha=_trilha_pergunta(pergunta, conteudo_da_versao(versao)),
        cancelar=endereco,
        envio="Salvar",
        introducao=(
            *_introducao_do_tipo(pergunta.tipo),
            mensagens.TIPO_FIXO,
            *_escala_atual(pergunta),
        ),
    )


def _escala_atual(pergunta) -> tuple[str, ...]:
    """A escala gravada, explicada (FR-049), para a página de edição."""
    if pergunta.tipo != TipoPergunta.ESCALA:
        return ()
    escala = Escala(
        pergunta.escala_inicio, pergunta.escala_fim,
        pergunta.escala_rotulo_inicio, pergunta.escala_rotulo_fim,
    )  # fmt: skip
    return (f"Escala atual: {apresentacao.descrever_escala(escala)}",)


@require_POST
@never_cache
@_respondendo
def pergunta_mover(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    secao = pergunta.secao
    return _mover_e_voltar(
        request, list(secao.perguntas.order_by("posicao")), pergunta, op.reordenar_perguntas,
        secao, secao.versao, f"/editor/secoes/{secao.pk}/", "pergunta",
    )  # fmt: skip


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def pergunta_trocar_secao(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    versao = pergunta.secao.versao
    endereco = f"/editor/perguntas/{pergunta.pk}/"
    _exigir_rascunho(request, versao, endereco)
    conteudo = conteudo_da_versao(versao)
    destinos = _destinos(conteudo, exceto=pergunta.secao_id, prefixo="")
    formulario = f.MoverPerguntaForm(destinos, _dados(request))
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            destino = Secao.objects.get(pk=formulario.cleaned_data["secao"])
            posicao = acoes.proxima_posicao(destino.perguntas.all())
            return op.mover_pergunta(pergunta, destino, posicao)

        if _gravar(request, versao, formulario, gravar, {}, endereco) is not None:
            return redirect(endereco + "?aviso=pergunta-movida")
    return _formulario(
        request,
        formulario,
        titulo="Mover Pergunta para outra Seção",
        trilha=_trilha_pergunta(pergunta, conteudo),
        cancelar=endereco,
        envio="Mover para o final da Seção escolhida",
        introducao=(
            "A Pergunta vai para o final da Seção escolhida, com suas Opções, escala e desvios.",
        ),
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def pergunta_remover(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    secao = pergunta.secao
    conteudo = conteudo_da_versao(secao.versao)
    dados = apresentacao.pergunta_apresentada(conteudo, pergunta.pk)
    consequencias = ["Os dados da Pergunta serão removidos."]
    if dados["de_escolha"]:
        consequencias.append("As Opções desta Pergunta também serão removidas.")
    if dados["admite_desvio"]:
        consequencias.append("Os desvios de navegação das Opções também serão removidos.")
    if dados["escala"]:
        consequencias.append("A configuração da escala também será removida.")
    return _remover(
        request,
        versao=secao.versao,
        rotulo=dados["rotulo_completo"],
        consequencias=consequencias,
        remover=lambda: op.remover_pergunta(pergunta),
        voltar=f"/editor/perguntas/{pergunta.pk}/",
        sucesso=f"/editor/secoes/{secao.pk}/?aviso=pergunta-removida",
        trilha=_trilha_pergunta(pergunta, conteudo),
        explicar=lambda erro: (),
    )


# --- Opções (US8) --------------------------------------------------------------------------------

_MAPA_OPCAO = {
    Motivo.TEXTO_VAZIO: ("texto", mensagens.TEXTO_VAZIO),
    Motivo.OPCAO_REPETIDA: ("texto", mensagens.OPCAO_REPETIDA),
    Motivo.COMPLEMENTO_REPETIDO: ("complemento", mensagens.COMPLEMENTO_REPETIDO),
}


def _opcao(request, pk) -> Opcao:
    return _objeto(request, Opcao, pk, "pergunta__secao__versao__pesquisa")


def _destinos_da_opcao(pergunta, conteudo):
    """Destinos de desvio só para escolha única (002 FR-050); `None` nos demais tipos."""
    return _destinos(conteudo) if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA else None


def _gravar_desvio(pergunta, opcao, formulario) -> None:
    if "desvio" in formulario.fields:
        acoes.definir_desvio(pergunta, opcao, _destino(formulario.cleaned_data["desvio"]))


def _explicacao_de_desvio(pergunta) -> str:
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        return mensagens.SEMANTICA_NAVEGACAO
    return mensagens.SO_ESCOLHA_UNICA


def _ordinal_da_opcao(opcao) -> int:
    return opcao.pergunta.opcoes.filter(posicao__lte=opcao.posicao).count()


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def opcao_nova(request, pergunta):
    pergunta = _pergunta(request, pergunta)
    if pergunta.tipo not in apresentacao.TIPOS_DE_ESCOLHA:
        raise Http404  # texto curto e escala não têm Opções (FR-041)
    versao = pergunta.secao.versao
    endereco = f"/editor/perguntas/{pergunta.pk}/"
    _exigir_rascunho(request, versao, endereco)
    conteudo = conteudo_da_versao(versao)
    formulario = f.OpcaoForm(_destinos_da_opcao(pergunta, conteudo), _dados(request))
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            posicao = acoes.proxima_posicao(pergunta.opcoes.all())
            opcao = op.adicionar_opcao(pergunta, posicao, **formulario.argumentos())
            _gravar_desvio(pergunta, opcao, formulario)
            return opcao

        opcao = _gravar(request, versao, formulario, gravar, _MAPA_OPCAO, endereco)
        if opcao is not None:
            if request.POST.get("adicionar_outra"):
                return redirect(f"{endereco}opcoes/nova/?aviso=opcao-criada")
            return redirect(f"{endereco}#opcao-{_ordinal_da_opcao(opcao)}")
    return _formulario(
        request,
        formulario,
        titulo="Adicionar Opção",
        trilha=_trilha_pergunta(pergunta, conteudo),
        cancelar=endereco,
        envio="Adicionar",
        envio_extra=("adicionar_outra", "Adicionar e incluir outra"),
        introducao=(f"Pergunta: {pergunta.texto}", _explicacao_de_desvio(pergunta)),
    )


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def opcao_editar(request, opcao):
    opcao = _opcao(request, opcao)
    pergunta = opcao.pergunta
    versao = pergunta.secao.versao
    endereco = f"/editor/perguntas/{pergunta.pk}/"
    _exigir_rascunho(request, versao, endereco)
    conteudo = conteudo_da_versao(versao)
    desvio = "finalizar" if opcao.regra_finaliza else str(opcao.regra_destino_id or "")
    inicial = {"texto": opcao.texto, "complemento": opcao.complemento_textual, "desvio": desvio}
    destinos = _destinos_da_opcao(pergunta, conteudo)
    formulario = f.OpcaoForm(destinos, _dados(request), initial=inicial)
    if request.method == "POST" and formulario.is_valid():

        def gravar():
            op.alterar_opcao(opcao, **formulario.argumentos())
            _gravar_desvio(pergunta, opcao, formulario)
            return opcao

        if _gravar(request, versao, formulario, gravar, _MAPA_OPCAO, endereco) is not None:
            return redirect(f"{endereco}?aviso=dados-salvos#opcao-{_ordinal_da_opcao(opcao)}")
    rotulo = apresentacao.localizador(conteudo)[opcao.pk].rotulo
    return _formulario(
        request,
        formulario,
        titulo=f"Editar a {rotulo}",
        trilha=_trilha_pergunta(pergunta, conteudo),
        cancelar=endereco,
        envio="Salvar",
        introducao=(_explicacao_de_desvio(pergunta),),
    )


@require_POST
@never_cache
@_respondendo
def opcao_mover(request, opcao):
    opcao = _opcao(request, opcao)
    pergunta = opcao.pergunta
    return _mover_e_voltar(
        request, list(pergunta.opcoes.order_by("posicao")), opcao, op.reordenar_opcoes,
        pergunta, pergunta.secao.versao, f"/editor/perguntas/{pergunta.pk}/", "opcao",
    )  # fmt: skip


@require_http_methods(["GET", "POST"])
@never_cache
@_respondendo
def opcao_remover(request, opcao):
    opcao = _opcao(request, opcao)
    pergunta = opcao.pergunta
    conteudo = conteudo_da_versao(pergunta.secao.versao)
    consequencias = ["A Opção será removida da Pergunta."]
    if opcao.tem_regra:
        consequencias.append("O desvio de navegação desta Opção também será removido.")
    return _remover(
        request,
        versao=pergunta.secao.versao,
        rotulo=apresentacao.localizador(conteudo)[opcao.pk].rotulo,
        consequencias=consequencias,
        remover=lambda: op.remover_opcao(opcao),
        voltar=f"/editor/perguntas/{pergunta.pk}/",
        sucesso=f"/editor/perguntas/{pergunta.pk}/?aviso=opcao-removida",
        trilha=_trilha_pergunta(pergunta, conteudo),
        explicar=lambda erro: (),
    )


# --- Diagnóstico técnico (US11) -----------------------------------------------------------------


@require_GET
@never_cache
@_respondendo
def diagnostico(request, versao):
    versao = _objeto(request, Versao, versao, "pesquisa")
    endereco = f"/editor/versoes/{versao.pk}/"
    if versao.publicada:
        return redirect(endereco + "?aviso=publicada")
    return _render(
        request,
        "editor/diagnostico.html",
        {
            "versao": versao,
            "diagnostico": diagnosticar(versao),
            **_textos_do_diagnostico(),
            "trilha": [*_trilha_versao(versao), ("Diagnóstico técnico", None)],
        },
    )


# --- Pré-visualização (US13): leitura, não jornada ------------------------------------------------


def _trilha_previa(versao):
    return [*_trilha_versao(versao), ("Pré-visualização", f"/editor/versoes/{versao.pk}/previa/")]


@require_GET
@never_cache
@_respondendo
def previa(request, versao):
    versao = _objeto(request, Versao, versao, "pesquisa")
    conteudo = conteudo_da_versao(versao)
    local = apresentacao.localizador(conteudo)
    return _render(
        request,
        "editor/previa.html",
        {
            "versao": versao,
            "conteudo": conteudo,
            "secoes": [(n, local[s.id].rotulo) for n, s in enumerate(conteudo.secoes, 1)],
            "trilha": [*_trilha_versao(versao), ("Pré-visualização", None)],
        },
    )


@require_GET
@never_cache
@_respondendo
def previa_secao(request, versao, ordinal):
    """Uma Seção por página (ids `p<n>` da 008 únicos). Anterior e seguinte seguem a
    **ordem** da Versão; desvios são anotações estruturais. Nada da 006 é chamado, nada é
    gravado, nenhum estado é guardado entre requisições (FR-088 a FR-091)."""
    versao = _objeto(request, Versao, versao, "pesquisa")
    conteudo = conteudo_da_versao(versao)
    if not 1 <= ordinal <= len(conteudo.secoes):
        raise Http404
    secao = conteudo.secoes[ordinal - 1]
    itens = FormularioDaSecao(secao, {}).itens()
    anotacoes = [
        [a for o in item.pergunta.opcoes if (a := apresentacao.anotacao_previa(conteudo, o))]
        for item in itens
    ]
    encaminhamento = None
    if secao.encaminhamento_id is not None:
        destino = apresentacao.nome_da_secao(conteudo, secao.encaminhamento_id)
        encaminhamento = f"Na aplicação real, depois desta seção vem: {destino}."
    base = f"/editor/versoes/{versao.pk}/previa/secoes/"
    rotulo = apresentacao.rotulo_secao(ordinal, secao)
    return _render(
        request,
        "editor/previa_secao.html",
        {
            "versao": versao,
            "secao": secao,
            "rotulo": rotulo,
            "ordinal": ordinal,
            "total": len(conteudo.secoes),
            "itens_anotados": list(zip(itens, anotacoes, strict=True)),
            "encaminhamento": encaminhamento,
            "anterior": f"{base}{ordinal - 1}/" if ordinal > 1 else None,
            "seguinte": f"{base}{ordinal + 1}/" if ordinal < len(conteudo.secoes) else None,
            "trilha": [*_trilha_previa(versao), (rotulo, None)],
        },
    )

"""Curadoria de oportunidades (025 FR-025 a FR-035; contracts/curadoria.md; T032, T034, T037).

Padrão da gestão de Campanha (017): barreira externa relida a cada pedido, formulário que só
converte, escrita só pelas operações, recusa de campo vira erro no campo (422), estado que
mudou vira conflito (409), registro fora do escopo é 404 (não revela que existe). Sem Django
admin.
"""

from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import Atuacao, recusa
from trajetoria.demonstracao.operador import operador_em_uso, vinculos_do_operador_em_uso
from trajetoria.portal.models import Categoria, Oportunidade
from trajetoria.portal.oportunidades import mensagens as m
from trajetoria.portal.oportunidades import operacoes
from trajetoria.portal.oportunidades.consultas import da_curadoria
from trajetoria.portal.oportunidades.formularios import OportunidadeForm
from trajetoria.portal.oportunidades.governanca import (
    administra,
    escopo_de_curadoria,
    pode_curar_oportunidades,
)
from trajetoria.portal.oportunidades.pertinencia import Item, oferecida
from trajetoria.portal.oportunidades.regras import (
    EDITAVEIS,
    RETIRAVEIS,
    Estado,
    Motivo,
    OportunidadeRejeitada,
    estado,
    origem_do_site,
)

LISTA = "/curadoria/oportunidades/"
ESCOLHA_DE_OPERADOR = "/demonstracao/operador/?destino=curadoria"

_ERROS = {
    Motivo.TITULO: ("titulo", m.ERROS["titulo"]),
    Motivo.RESUMO: ("resumo", m.ERROS["resumo"]),
    Motivo.CATEGORIA: ("categoria", m.ERROS["categoria"]),
    Motivo.UNIDADE_FORA_DO_ESCOPO: ("unidade_responsavel", m.ERROS["unidade_responsavel"]),
    Motivo.ENDERECO: ("endereco", m.ERROS["endereco"]),
    Motivo.PERIODO_INVERTIDO: ("fim", m.ERROS["periodo_invertido"]),
    Motivo.FIM_ANTES_DE_HOJE: ("fim", m.ERROS["fim_antes_de_hoje"]),
    Motivo.PUBLICO: (None, m.ERROS["publico"]),
}


def curadoria(view):
    """Barreira externa (contracts/curadoria.md, "Acesso"): demonstração, operador e
    competência, relidos a cada pedido. O identificador do operador nunca vai ao template."""

    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not settings.TRAJETORIA_DEMONSTRACAO:
            raise Http404
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect(ESCOLHA_DE_OPERADOR)
        if not pode_curar_oportunidades(vinculos):
            return recusa(request, m.RECUSA)
        request.escopo = escopo_de_curadoria(vinculos)
        request.atuacao = Atuacao(tuple(v.rotulo_de_atuacao for v in vinculos), False)
        return view(request, *args, **kwargs)

    return envolvida


def _pagina(request, template, *, titulo, status=200, **contexto):
    formulario = contexto.get("formulario")
    if formulario is not None and formulario.errors:
        for nome, campo in formulario.fields.items():
            if nome in formulario.errors:
                campo.widget.attrs["autofocus"] = True
                break
    trilha = [(m.CURADORIA_TRILHA, LISTA)]
    if template != "lista":
        trilha.append((titulo, None))
    else:
        trilha = [(m.CURADORIA_TRILHA, None)]
    return render(
        request,
        f"portal/curadoria/{template}.html",
        {"banner": ap.BANNER, "atuacao": request.atuacao, "trilha": trilha, "titulo": titulo,
         **contexto},
        status=status,
    )


def _da_curadoria_ou_404(request, pk) -> Oportunidade:
    oportunidade = Oportunidade.objects.filter(pk=pk).first()
    if oportunidade is None or not administra(request.escopo, oportunidade.unidade_responsavel):
        raise Http404
    return oportunidade


def _conflito(request):
    return _pagina(request, "conflito", titulo=m.CONFLITO_TITULO, texto=m.CONFLITO, status=409)


def _hoje():
    return timezone.localdate()


def _periodo(o) -> str:
    return m.PERIODO.format(inicio=o.inicio.strftime("%d/%m/%Y"), fim=o.fim.strftime("%d/%m/%Y"))


def _publico(o) -> str:
    partes = []
    for valores, rotulo in ((o.publico_cursos, "curso"), (o.publico_niveis, "nível"),
                            (o.publico_unidades, "unidade")):
        if valores is not None:
            partes.append(f"{rotulo} {' ou '.join(valores)}")
    if not partes:
        return m.PUBLICO_TODOS
    return m.PUBLICO_ALGUNS.format(criterios="; ".join(partes))


def _previa(o) -> Item:
    """O item como o egresso o verá; a explicação real depende da formação de cada egresso."""
    do_ifes, dominio = origem_do_site(o.endereco)
    return Item(
        oportunidade=o, grupo="", formacoes=(),
        explicacao=m.ABERTA_A_TODOS if not o.tem_publico else m.PREVIA_EXPLICACAO,
        categoria=Categoria(o.categoria).label, oferecida=oferecida(o), do_ifes=do_ifes,
        dominio=dominio,
    )


def _erros(formulario, erro: OportunidadeRejeitada) -> None:
    for violacao in erro.violacoes:
        if violacao.motivo not in _ERROS:
            raise erro
        campo, texto = _ERROS[violacao.motivo]
        formulario.add_error(campo or violacao.campo, texto)


@curadoria
@require_http_methods(["GET"])
@never_cache
def lista(request):
    hoje = _hoje()
    linhas = []
    for o in da_curadoria(request.escopo):
        situacao = estado(o, hoje)
        acoes = []
        if situacao in EDITAVEIS:
            acoes.append(("editar", m.EDITAR))
        if situacao is Estado.RASCUNHO:
            acoes.append(("publicar", m.PUBLICAR_ACAO))
        if situacao in RETIRAVEIS:
            acoes.append(("retirar", m.RETIRAR_ACAO))
        linhas.append({
            "oportunidade": o,
            "unidade": o.unidade_responsavel or m.IFES_INSTITUCIONAL,
            "categoria": Categoria(o.categoria).label,
            "periodo": f"{o.inicio:%d/%m/%Y} a {o.fim:%d/%m/%Y}",
            "estado": situacao.value,
            "acoes": acoes,
        })
    return _pagina(
        request, "lista", titulo=m.CURADORIA_TITULO, linhas=linhas, nova=m.NOVA,
        lista_vazia=m.LISTA_VAZIA, aviso=m.AVISOS.get(request.GET.get("aviso")),
    )


def _formulario(request, *, titulo, instancia=None):
    escopo = request.escopo
    if request.method == "GET":
        inicial = None
        if instancia is not None:
            inicial = {campo: getattr(instancia, campo) for campo in operacoes.CAMPOS_DE_CONTEUDO}
        formulario = OportunidadeForm(escopo, initial=inicial)
        return _pagina(request, "formulario", titulo=titulo, formulario=formulario,
                       ajuda_conteudo=m.AJUDA_CONTEUDO, ajuda_publico=m.AJUDA_PUBLICO,
                       voltar=LISTA)
    formulario = OportunidadeForm(escopo, request.POST)
    if formulario.is_valid():
        operador = operador_em_uso(request)
        try:
            if instancia is None:
                operacoes.cadastrar(formulario.dados(), operador=operador, escopo=escopo,
                                    hoje=_hoje())
                return redirect(f"{LISTA}?aviso=cadastrada")
            operacoes.editar(instancia.pk, formulario.dados(), operador=operador, escopo=escopo,
                             hoje=_hoje())
            return redirect(f"{LISTA}?aviso=editada")
        except OportunidadeRejeitada as erro:
            if Motivo.ESTADO in erro.motivos:
                return _conflito(request)
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            _erros(formulario, erro)
    return _pagina(request, "formulario", titulo=titulo, formulario=formulario, status=422,
                   ajuda_conteudo=m.AJUDA_CONTEUDO, ajuda_publico=m.AJUDA_PUBLICO, voltar=LISTA)


@curadoria
@require_http_methods(["GET", "POST"])
@never_cache
def nova(request):
    return _formulario(request, titulo=m.NOVA)


@curadoria
@require_http_methods(["GET", "POST"])
@never_cache
def editar(request, pk):
    oportunidade = _da_curadoria_ou_404(request, pk)
    if estado(oportunidade, _hoje()) not in EDITAVEIS:
        return _conflito(request)
    return _formulario(request, titulo=m.EDITAR_TITULO, instancia=oportunidade)


@curadoria
@require_http_methods(["GET", "POST"])
@never_cache
def publicar(request, pk):
    oportunidade = _da_curadoria_ou_404(request, pk)
    if estado(oportunidade, _hoje()) is not Estado.RASCUNHO:
        return _conflito(request)
    erro_de_prazo = None
    if request.method == "POST":
        try:
            operacoes.publicar(pk, operador=operador_em_uso(request), escopo=request.escopo,
                               agora=timezone.now())
            return redirect(f"{LISTA}?aviso=publicada")
        except OportunidadeRejeitada as erro:
            if Motivo.ESTADO in erro.motivos:
                return _conflito(request)
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            erro_de_prazo = m.ERROS["publicacao_vencida"]
    previa = _previa(oportunidade)
    return _pagina(
        request, "publicar", titulo=m.PUBLICAR_TITULO, status=422 if erro_de_prazo else 200,
        item=previa, publico=_publico(oportunidade), periodo=_periodo(oportunidade),
        endereco=m.ENDERECO_CONFIRMACAO.format(dominio=previa.dominio),
        aviso_externo=None if previa.do_ifes else m.AVISO_EXTERNO, erro=erro_de_prazo,
        acao=m.PUBLICAR_ACAO, cancelar=m.CANCELAR, voltar=LISTA,
    )


@curadoria
@require_http_methods(["GET", "POST"])
@never_cache
def retirar(request, pk):
    oportunidade = _da_curadoria_ou_404(request, pk)
    if estado(oportunidade, _hoje()) not in RETIRAVEIS:
        return _conflito(request)
    if request.method == "POST":
        try:
            operacoes.retirar(pk, operador=operador_em_uso(request), escopo=request.escopo,
                              agora=timezone.now())
        except OportunidadeRejeitada as erro:
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            return _conflito(request)
        return redirect(f"{LISTA}?aviso=retirada")
    return _pagina(
        request, "retirar", titulo=m.RETIRAR_TITULO, oportunidade=oportunidade,
        texto=m.RETIRAR_TEXTO, acao=m.RETIRAR_ACAO, cancelar=m.CANCELAR, voltar=LISTA,
    )

"""Orquestração da 017: autorização externa e escrita somente pela 004."""

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.acompanhamento.acesso import gestao
from trajetoria.acompanhamento.gestao import mensagens as m
from trajetoria.acompanhamento.gestao.formularios import CampanhaForm
from trajetoria.acompanhamento.gestao.painel import abrangencia_restrita, painel, versoes_oferecidas
from trajetoria.campanha import operacoes as op
from trajetoria.campanha.consultas import (
    EstadoCampanha,
    campanhas_em_coleta,
    data_de_referencia,
    estado,
)
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.regras import CampanhaRejeitada, Motivo
from trajetoria.instrumento.models import Versao

_IMPEDIMENTOS = {Motivo.VERSAO_NAO_PUBLICADA, Motivo.PERIODO_NAO_DEFINIDO, Motivo.FORA_DO_PERIODO}


def _pagina(request, template, *, status=200, **contexto):
    formulario = contexto.get("formulario")
    if formulario is not None and formulario.is_bound:
        formulario.focar_primeiro_erro()
    titulo = contexto.get(
        "titulo",
        {
            "confirmar_abertura": "Confirmar abertura da coleta",
            "confirmar_encerramento": "Confirmar encerramento da coleta",
            "conflito": "Ação não disponível",
        }.get(template),
    )
    trilha = [("Acompanhamento da coleta", "/acompanhamento/")]
    campanha = contexto.get("campanha")
    if campanha is not None:
        trilha.append((campanha.nome, f"/acompanhamento/campanhas/{campanha.pk}/"))
    trilha.append((titulo, None))
    return render(
        request,
        f"acompanhamento/gestao/{template}.html",
        {
            "banner": ap.BANNER,
            "atuacao": request.atuacao,
            "trilha": trilha,
            **contexto,
        },
        status=status,
    )


def _destino(campanha, aviso):
    return redirect(f"/acompanhamento/campanhas/{campanha.pk}/?aviso={aviso}")


def _erros(formulario, violacoes):
    for violacao in violacoes:
        if violacao.motivo not in m.ERROS:
            raise CampanhaRejeitada(violacoes)
        campo, texto = m.ERROS[violacao.motivo]
        formulario.add_error(campo or violacao.campo, texto)


def _tentar(formulario, operacao, *args, **kwargs):
    """Executa uma operação da 004 num savepoint; rejeição de campo vira erro no formulário.
    Devolve o resultado, ou `None` se rejeitada. `CAMPANHA_JA_ABERTA` segue como exceção."""
    try:
        with transaction.atomic():
            return operacao(*args, **kwargs)
    except CampanhaRejeitada as erro:
        if Motivo.CAMPANHA_JA_ABERTA in erro.motivos:
            raise
        _erros(formulario, erro.violacoes)
        return None


def _tem_data(dados):
    return dados["inicio"] is not None or dados["fim"] is not None


def _carregar(campanha):
    return get_object_or_404(Campanha.objects.select_related("versao__pesquisa"), pk=campanha)


def _conflito(request, campanha, texto):
    return _pagina(request, "conflito", campanha=campanha, texto=texto, status=409)


@gestao
@require_http_methods(["GET", "POST"])
@never_cache
def nova(request):
    versoes = versoes_oferecidas()
    if not versoes:
        return _pagina(request, "formulario", titulo="Nova Campanha", sem_publicada=m.SEM_PUBLICADA)
    formulario = CampanhaForm(versoes, request.POST if request.method == "POST" else None)
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        with transaction.atomic():
            campanha = _tentar(
                formulario,
                op.criar_campanha,
                dados["nome"],
                Versao.objects.get(pk=dados["versao"]),
            )
            if _tem_data(dados):
                if campanha is not None:
                    _tentar(formulario, op.definir_periodo, campanha, dados["inicio"], dados["fim"])
                else:
                    # Sem Campanha criada, o período é verificado pela mesma regra da 004, para
                    # que todos os problemas apareçam na mesma submissão (FR-014).
                    _erros(formulario, op.violacoes_de_periodo(dados["inicio"], dados["fim"]))
            if formulario.errors:
                transaction.set_rollback(True)
        if not formulario.errors:
            return _destino(campanha, "campanha-criada")
    return _pagina(
        request,
        "formulario",
        formulario=formulario,
        titulo="Nova Campanha",
        voltar="/acompanhamento/",
        status=422 if formulario.errors else 200,
    )


@gestao
@require_http_methods(["GET", "POST"])
@never_cache
def editar(request, campanha):
    campanha = _carregar(campanha)
    if campanha.aberta_em is not None:
        return _conflito(request, campanha, m.JA_ABERTA)
    formulario = CampanhaForm(
        versoes_oferecidas(atual=campanha.versao),
        request.POST if request.method == "POST" else None,
        initial={
            "nome": campanha.nome,
            "versao": str(campanha.versao_id),
            "inicio": campanha.inicio,
            "fim": campanha.fim,
        },
    )
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        try:
            with transaction.atomic():
                if campanha.inicio is not None and not _tem_data(dados):
                    formulario.add_error("inicio", m.PERIODO_REMOVIDO)
                else:
                    # A 004 bloqueia a linha e recusa Campanha já aberta em cada operação.
                    versao = Versao.objects.get(pk=dados["versao"])
                    _tentar(
                        formulario, op.alterar_campanha, campanha, nome=dados["nome"], versao=versao
                    )
                    if _tem_data(dados):
                        _tentar(
                            formulario, op.definir_periodo, campanha, dados["inicio"], dados["fim"]
                        )
                if formulario.errors:
                    transaction.set_rollback(True)
        except CampanhaRejeitada as erro:
            if Motivo.CAMPANHA_JA_ABERTA not in erro.motivos:
                raise
            return _conflito(request, _carregar(campanha.pk), m.JA_ABERTA)
        if not formulario.errors:
            return _destino(campanha, "configuracao-salva")
        # As operações sincronizam a instância; desfeita a transação, relê o que está gravado.
        campanha = _carregar(campanha.pk)
    return _pagina(
        request,
        "formulario",
        formulario=formulario,
        titulo="Editar configuração",
        campanha=campanha,
        voltar=f"/acompanhamento/campanhas/{campanha.pk}/",
        abrangencia=abrangencia_restrita(campanha),
        texto_abrangencia=m.ABRANGENCIA,
        status=422 if formulario.errors else 200,
    )


@gestao
@require_http_methods(["GET", "POST"])
@never_cache
def abrir(request, campanha):
    campanha = _carregar(campanha)
    agora = timezone.now()
    status = 200
    if request.method == "POST":
        try:
            resultado = op.abrir(campanha, agora=agora)
        except CampanhaRejeitada as erro:
            if not set(erro.motivos) <= _IMPEDIMENTOS:
                raise
            campanha = _carregar(campanha.pk)
            status = 409
        else:
            aviso = {
                op.SituacaoAbertura.ABERTA: "coleta-aberta",
                op.SituacaoAbertura.JA_EM_COLETA: "ja-em-coleta",
                op.SituacaoAbertura.JA_ENCERRADA: "ja-encerrada",
            }[resultado]
            return _destino(campanha, aviso)
    painel_ = painel(campanha, agora)
    confirmar = campanha.aberta_em is None and not painel_["impedimentos"]
    outras = ()
    if confirmar:
        outras = tuple(
            campanhas_em_coleta(agora=agora)
            .exclude(pk=campanha.pk)
            .order_by("nome", "id")
            .values_list("nome", flat=True)
        )
    ja_aberta = None
    if campanha.aberta_em is not None:
        encerrada = estado(campanha, agora=agora) is EstadoCampanha.ENCERRADA
        ja_aberta = m.AVISOS["ja-encerrada" if encerrada else "ja-em-coleta"]
    return _pagina(
        request,
        "confirmar_abertura",
        campanha=campanha,
        painel=painel_,
        confirmar=confirmar,
        ja_aberta=ja_aberta,
        outras=outras,
        sobreposicao=m.SOBREPOSICAO,
        confirmacao=m.CONFIRMAR_ABERTURA,
        ultimo_dia=campanha.fim == data_de_referencia(agora),
        status=status,
    )


@gestao
@require_http_methods(["GET", "POST"])
@never_cache
def encerrar(request, campanha):
    campanha = _carregar(campanha)
    agora = timezone.now()
    if request.method == "POST":
        try:
            resultado = op.encerrar(campanha, agora=agora)
        except CampanhaRejeitada as erro:
            if erro.motivos != (Motivo.CAMPANHA_NUNCA_ABERTA,):
                raise
            return _conflito(request, campanha, m.NUNCA_ABERTA)
        aviso = (
            "ja-encerrada"
            if resultado is op.SituacaoEncerramento.JA_ENCERRADA
            else "coleta-encerrada"
        )
        return _destino(campanha, aviso)
    if estado(campanha, agora=agora) is not EstadoCampanha.EM_COLETA:
        texto = m.NUNCA_ABERTA if campanha.aberta_em is None else m.AVISOS["ja-encerrada"]
        return _conflito(request, campanha, texto)
    return _pagina(
        request, "confirmar_encerramento", campanha=campanha, confirmacao=m.CONFIRMAR_ENCERRAMENTO
    )

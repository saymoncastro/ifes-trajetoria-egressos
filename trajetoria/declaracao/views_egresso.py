from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST

from trajetoria.acesso import pendente
from trajetoria.acesso.sessao import destino_da_entrada
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.declaracao import mensagens
from trajetoria.declaracao.formularios import FormacaoForm
from trajetoria.declaracao.models import FormacaoDeclarada
from trajetoria.declaracao.operacoes import (
    Ambiguidade,
    EmEspera,
    SemCampanha,
    campanhas_compativeis,
    declaracoes_do_par,
    iniciar_participacao_declarada,
)
from trajetoria.declaracao.selo import (
    ChaveIndisponivel,
    SeloInvalido,
    abrir_inicio,
    abrir_transito,
    selar_inicio,
)
from trajetoria.declaracao.sessao import (
    acrescentar_declaracao,
    declaracoes_em_uso,
    estabelecer_declarante,
)
from trajetoria.interface.apresentacao import onde_parou_da_participacao
from trajetoria.interface.mensagens import AVISOS
from trajetoria.participacao.models import Participacao

# 023 FR-030: selo vencido ou inválido volta à entrada com aviso.
_ENTRADA_SELO = "/acesso/?aviso=selo"


def _tela(request, **dados):
    return render(request, "declaracao/egresso.html", dados)


def _indisponivel(request):
    return render(request, "declaracao/egresso.html", {"aviso": mensagens.INDISPONIVEL}, status=503)


def _lista(uuids):
    itens = []
    for f in FormacaoDeclarada.objects.filter(pk__in=uuids).select_related(
        "participacao__campanha"
    ):
        p = f.participacao
        rotulo = (
            "Resposta registrada"
            if p.concluida_em
            else "Continuar"
            if estado(p.campanha) == EstadoCampanha.EM_COLETA
            else "Período encerrado"
        )
        itens.append(
            dict(
                formacao=f,
                rotulo=rotulo,
                continuar=rotulo == "Continuar",
                participacao=p,
                onde_parou=onde_parou_da_participacao(p) if rotulo == "Continuar" else None,
            )
        )
    return itens



@never_cache
@sensitive_post_parameters("selo")
@require_http_methods(["GET", "POST"])
def entrada(request):
    if request.method == "GET":
        uuids = declaracoes_em_uso(request)
        if uuids is None:
            return redirect(destino_da_entrada(request))
        return _tela(
            request,
            lista=_lista(uuids),
            mostrar_lista=True,
            # Os mesmos avisos de "Salvar e sair" da 014 (FR-008, FR-012): "salvo" só com
            # Resposta gravada; "saida", neutro.
            aviso_salvo=AVISOS.get(request.GET.get("aviso"))
            if request.GET.get("aviso") in ("salvo", "saida")
            else None,
        )
    token = request.POST.get("selo", "")
    try:
        cpf, data = abrir_transito(token, timezone.now())
        uuids = declaracoes_do_par(cpf, data)
        estabelecer_declarante(request, uuids, timezone.now())
    except ChaveIndisponivel:
        return _indisponivel(request)
    except SeloInvalido:
        return redirect(_ENTRADA_SELO)
    # 023 FR-006, FR-008: envio pendente de Participação fora das declarações do par é
    # descartado sem ser exibido; o do próprio par volta pela lista ("Continuar").
    envio = pendente.ler(request)
    if envio is not None and not Participacao.objects.filter(
        pk=envio.participacao, formacao_declarada_id__in=uuids
    ).exists():
        pendente.descartar(request)
    if uuids:
        return _tela(request, lista=_lista(uuids), mostrar_lista=True, selo=token)
    return _tela(request, form=FormacaoForm(), selo=token)


@never_cache
@sensitive_post_parameters("selo")
@require_POST
def nova(request):
    token = request.POST.get("selo", "")
    agora = timezone.now()
    try:
        cpf, data = abrir_transito(token, agora)
        if "nome" not in request.POST:
            return _tela(request, form=FormacaoForm(), selo=token)
        if request.POST.get("corrigir") == "1":
            # 023 FR-032: "Corrigir" volta ao formulário preenchido, sem nova confirmação.
            return _tela(request, form=FormacaoForm(request.POST), selo=token)
        form = FormacaoForm(request.POST)
        if not form.is_valid():
            return _tela(request, form=form, selo=token, prefixo_titulo="Erro: ")
        campanhas = campanhas_compativeis(form.cleaned_data, agora=agora)
        if not campanhas:
            return _tela(request, aviso=mensagens.SEM_PESQUISA)
        if len(campanhas) > 1:
            return _tela(request, aviso=mensagens.AMBIGUIDADE)
        return _tela(
            request,
            confirmacao=form.cleaned_data,
            selo=selar_inicio(cpf, data, form.cleaned_data),
            selo_transito=token,
        )
    except ChaveIndisponivel:
        return _indisponivel(request)
    except SeloInvalido:
        return redirect(_ENTRADA_SELO)


@never_cache
@sensitive_post_parameters("selo")
@require_POST
def comecar(request):
    try:
        cpf, data, dados, chave = abrir_inicio(request.POST.get("selo", ""), timezone.now())
        p, _ = iniciar_participacao_declarada(
            dados,
            cpf,
            data,
            chave,
            origem=request.META.get("REMOTE_ADDR", ""),
            agora=timezone.now(),
        )
        # O selo identifica o par; um envio em outra sessão substitui o sujeito anterior.
        estabelecer_declarante(request, declaracoes_do_par(cpf, data), timezone.now())
        acrescentar_declaracao(request, p.formacao_declarada_id)
        return HttpResponse(status=303, headers={"Location": f"/participacoes/{p.pk}/"})
    except ChaveIndisponivel:
        return _indisponivel(request)
    except (SeloInvalido, ValueError):
        return redirect(_ENTRADA_SELO)
    except SemCampanha:
        return _tela(request, aviso=mensagens.SEM_PESQUISA)
    except Ambiguidade:
        return _tela(request, aviso=mensagens.AMBIGUIDADE)
    except EmEspera:
        return render(
            request,
            "declaracao/egresso.html",
            {"aviso": "Aguarde alguns instantes antes de tentar novamente."},
            status=429,
        )

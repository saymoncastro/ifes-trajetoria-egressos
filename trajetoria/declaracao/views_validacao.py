"""Fila administrativa fictícia, sem respostas e com revelação explícita registrada."""

from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from trajetoria.acompanhamento.acesso import Atuacao, recusa
from trajetoria.acompanhamento.apresentacao import BANNER
from trajetoria.declaracao import consultas, operacoes
from trajetoria.declaracao.acervo import ReferenciaDivergente
from trajetoria.declaracao.formularios import AcervoForm
from trajetoria.declaracao.selo import ChaveIndisponivel, SeloInvalido
from trajetoria.demonstracao.operador import operador_em_uso, vinculos_do_operador_em_uso
from trajetoria.governanca.regras import pode_consultar_rascunho, pode_validar_formacao


def validacao(view):
    @wraps(view)
    def envolvida(request, *args, **kwargs):
        vinculos = vinculos_do_operador_em_uso(request)
        if vinculos is None:
            return redirect("/demonstracao/operador/?destino=acompanhamento")
        if not pode_validar_formacao(vinculos):
            return recusa(request, "A validação de formação não está disponível para esta atuação.")
        request.vinculos_validacao = vinculos
        request.atuacao = Atuacao(
            tuple(v.rotulo_de_atuacao for v in vinculos), pode_consultar_rascunho(vinculos)
        )
        return view(request, *args, **kwargs)

    return envolvida


def _formacao(request, id):
    return get_object_or_404(
        consultas.no_escopo(request.vinculos_validacao).select_related(
            "participacao__campanha", "validacao__conclusao"
        ),
        pk=id,
    )


def _detalhe(request, f, **dados):
    candidatas = consultas.candidatas(f)
    escopo = operacoes.escopo_de_acompanhamento(request.vinculos_validacao)
    if not escopo.institucional:
        candidatas = candidatas.filter(unidade__in=escopo.unidades)
    candidatas = [
        dict(conclusao=x, conflito=consultas.conflito_potencial(f, x)) for x in candidatas
    ]
    outras = consultas.outras_do_mesmo_cpf(f).filter(
        pk__in=consultas.no_escopo(request.vinculos_validacao)
    )
    decisao = getattr(f, "validacao", None)
    diferencas = (
        consultas.divergencia(f, decisao.conclusao) if decisao and decisao.conclusao_id else ()
    )
    return render(
        request,
        "declaracao/validacao/detalhe.html",
        dict(
            banner=BANNER,
            atuacao=request.atuacao,
            formacao=f,
            candidatas=candidatas,
            cpf_na_fonte_digital=consultas.cpf_encontrado_na_fonte_digital(f),
            outras=outras,
            decisao=decisao,
            diferencas=diferencas,
            acervo_form=dados.pop("acervo_form", AcervoForm(prefix="acervo")),
            **dados,
        ),
    )


@validacao
@never_cache
@require_GET
def fila(request):
    return render(
        request,
        "declaracao/validacao/fila.html",
        {
            "banner": BANNER,
            "atuacao": request.atuacao,
            "itens": consultas.fila(request.vinculos_validacao),
            "aviso": "Resultado registrado." if request.GET.get("registrada") == "1" else None,
        },
    )


@validacao
@never_cache
@require_GET
def detalhe(request, id):
    return _detalhe(request, _formacao(request, id))


@validacao
@never_cache
@require_POST
def revelar(request, id):
    f = _formacao(request, id)
    try:
        dados = operacoes.revelar_dados(
            f,
            vinculos=request.vinculos_validacao,
            operador=operador_em_uso(request),
            agora=timezone.now(),
        )
        return _detalhe(
            request,
            f,
            revelados=dados,
            aviso=None if dados else "Os dados não estão mais disponíveis.",
        )
    except (ChaveIndisponivel, SeloInvalido):
        return _detalhe(request, f, aviso="A consulta está indisponível no momento.")


@validacao
@never_cache
@require_POST
def registrar(request, id):
    f = _formacao(request, id)
    if request.POST.get("confirmar") != "1":
        return _detalhe(request, f, erro="Confirme explicitamente o registro do resultado.")
    resultado = {"confirmada": "CONFIRMADA", "nao_confirmada": "NAO_CONFIRMADA"}.get(
        request.POST.get("resultado")
    )
    origem = request.POST.get("origem")
    kwargs = {}
    acervo_form = AcervoForm(prefix="acervo")
    try:
        if resultado == "CONFIRMADA":
            if origem == "candidata":
                candidata = request.POST.get("candidata")
                from django.core.exceptions import ValidationError

                try:
                    x = consultas.candidatas(f).filter(pk=candidata).first()
                except (ValidationError, ValueError):
                    x = None
                if x is None:
                    raise operacoes.ForaDoEscopo
                kwargs["candidata"] = x
            elif origem == "referencia_fonte":
                kwargs["referencia_fonte"] = request.POST.get("referencia_fonte", "").strip()
            elif origem == "acervo":
                acervo_form = AcervoForm(request.POST, prefix="acervo")
                if not acervo_form.is_valid():
                    return _detalhe(
                        request, f, erro="Confira os dados do acervo.", acervo_form=acervo_form
                    )
                kwargs["acervo"] = acervo_form.cleaned_data
            else:
                raise ValueError
        operacoes.registrar_validacao(
            f,
            vinculos=request.vinculos_validacao,
            operador=operador_em_uso(request),
            agora=timezone.now(),
            resultado=resultado,
            **kwargs,
        )
        return HttpResponse(status=303, headers={"Location": "/validacoes-formacao/?registrada=1"})
    except operacoes.ForaDoEscopo:
        raise Http404 from None
    except operacoes.JaDecidida:
        return _detalhe(request, f, erro="Esta formação já foi decidida.")
    except (
        operacoes.ForaDaFila,
        operacoes.ReferenciaInexistente,
        operacoes.FonteIndisponivel,
        ReferenciaDivergente,
        ChaveIndisponivel,
        ValueError,
    ):
        return _detalhe(
            request,
            f,
            erro="Não foi possível registrar. Confira a origem e os dados encontrados.",
            acervo_form=acervo_form,
        )

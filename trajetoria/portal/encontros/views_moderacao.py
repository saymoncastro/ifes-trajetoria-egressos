"""Moderação de encontros (031 US2; FR-015 a FR-019; protótipos m1 a m5).

Padrão da curadoria da 025 e da lista da 026: barreira relida a cada pedido, escrita só pelas
operações, confirmação explícita, situação que mudou vira conflito (409) e encontro fora do
escopo é 404 (não revela que existe). A moderação não vê CPF, data de nascimento, contato
nem quem confirmou (FR-018). Sem Django admin.
"""


from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from trajetoria.acompanhamento import apresentacao as ap
from trajetoria.demonstracao.operador import operador_em_uso
from trajetoria.portal.barreiras import operador
from trajetoria.portal.encontros import consultas, operacoes, regras
from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.apresentacao import apresentar, confirmacoes, data, quem_analisa
from trajetoria.portal.encontros.governanca import (
    escopo_de_moderacao,
    modera,
    pode_moderar_encontros,
)
from trajetoria.portal.encontros.regras import EncontroRejeitado, Motivo, Situacao
from trajetoria.portal.models import Encontro, MotivoDeModeracao
from trajetoria.portal.oportunidades import mensagens as m_oportunidades
from trajetoria.portal.oportunidades.regras import origem_do_site

LISTA = "/curadoria/encontros/"
DESTINO = "encontros"  # destino registrado da escolha de operador (portal/apps.py)
ESCOLHA_DE_OPERADOR = f"/demonstracao/operador/?destino={DESTINO}"


# Barreira das telas de operação, comum à curadoria da 025 e à lista da unidade da 026.
moderacao = operador(pode=pode_moderar_encontros, escopo_de=escopo_de_moderacao,
                     mensagem_de_recusa=m.MODERACAO_RECUSA, destino=DESTINO)


def _pagina(request, template, *, titulo, status=200, **contexto):
    trilha = [(m.MODERACAO_TITULO, None)] if template == "lista" else [
        (m.MODERACAO_TITULO, LISTA), (titulo, None)
    ]
    return render(
        request, f"portal/encontros/moderacao/{template}.html",
        {"banner": ap.BANNER, "atuacao": request.atuacao, "trilha": trilha, "titulo": titulo,
         "destino_operador": DESTINO, "m": m, **contexto},
        status=status,
    )


def _no_escopo_ou_404(request, pk) -> Encontro:
    encontro = Encontro.objects.filter(pk=pk).first()
    if encontro is None or not modera(request.escopo, encontro):
        raise Http404
    return encontro


def _conflito(request):
    return _pagina(request, "conflito", titulo=m.CONFLITO_TITULO, status=409)


@moderacao
@require_GET
@never_cache
def lista(request):
    agora = timezone.now()
    analise, publicados = [], []
    for encontro in consultas.do_escopo(request.escopo, agora):
        atual = regras.situacao(encontro, agora)
        linha = {"e": apresentar(encontro), "responsavel": quem_analisa(encontro),
                 "enviado_em": data(encontro.enviado_em)}
        if atual is Situacao.EM_ANALISE:
            analise.append(linha)
        elif atual is Situacao.PUBLICADO:
            linha["contagem"] = confirmacoes(encontro.n_confirmacoes)
            publicados.append(linha)
    aviso = m.DECISAO_AVISOS.get(request.GET.get("aviso"))
    return _pagina(request, "lista", titulo=m.MODERACAO_TITULO, analise=analise,
                   publicados=publicados, aviso=aviso)


def _analise(encontro) -> dict:
    do_ifes, dominio = origem_do_site(encontro.link)
    origem = m_oportunidades.SITE_DO_IFES if do_ifes else m_oportunidades.SITE_EXTERNO
    return {
        "e": apresentar(encontro), "link": encontro.link,
        "aviso_link": m.SITE_EXTERNO_AVISO.format(origem=origem.capitalize(), dominio=dominio),
        "termo": f"{encontro.versao_do_termo}, aceito em {data(encontro.enviado_em)}",
        "contagem": (confirmacoes(consultas.quantas_confirmaram(encontro))
                     if encontro.publicado_em else None),
    }


@moderacao
@require_http_methods(["GET", "POST"])
@never_cache
def analisar(request, pk):
    """A análise; o POST publica (FR-015, FR-018). Só "Em análise"."""
    encontro = _no_escopo_ou_404(request, pk)
    agora = timezone.now()
    if regras.situacao(encontro, agora) is not Situacao.EM_ANALISE:
        return _conflito(request)
    if request.method == "POST":
        try:
            operacoes.publicar(pk, operador=operador_em_uso(request), escopo=request.escopo,
                               agora=agora)
        except EncontroRejeitado as erro:
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            return _conflito(request)
        return redirect(f"{LISTA}?aviso=publicado")
    return _pagina(request, "analisar", titulo=m.ANALISAR_TITULO, **_analise(encontro))


def _decidir(request, pk, *, situacao_exigida, operacao, template, titulo, aviso):
    encontro = _no_escopo_ou_404(request, pk)
    agora = timezone.now()
    if regras.situacao(encontro, agora) is not situacao_exigida:
        return _conflito(request)
    erros, motivo, complemento = {}, "", ""
    if request.method == "POST":
        motivo = request.POST.get("motivo", "")
        complemento = request.POST.get("complemento", "")
        try:
            operacao(pk, operador=operador_em_uso(request), escopo=request.escopo,
                     motivo=motivo, complemento=complemento, agora=agora)
        except EncontroRejeitado as erro:
            if Motivo.FORA_DO_ESCOPO in erro.motivos:
                raise Http404 from None
            if Motivo.ESTADO in erro.motivos:
                return _conflito(request)
            if Motivo.MOTIVO in erro.motivos:
                erros["motivo"] = m.ERRO_MOTIVO
            if Motivo.COMPLEMENTO in erro.motivos:
                erros["complemento"] = m.ERRO_COMPLEMENTO
        else:
            return redirect(f"{LISTA}?aviso={aviso}")
    motivos = [{"valor": v, "rotulo": r, "marcado": v == motivo}
               for v, r in MotivoDeModeracao.choices]
    return _pagina(request, template, titulo=titulo, status=422 if erros else 200,
                   erros=erros, motivos=motivos, complemento=complemento, **_analise(encontro))


@moderacao
@require_http_methods(["GET", "POST"])
@never_cache
def recusar(request, pk):
    """Recusa com motivo (FR-017). Definitiva."""
    return _decidir(request, pk, situacao_exigida=Situacao.EM_ANALISE,
                    operacao=operacoes.recusar, template="recusar",
                    titulo=m.RECUSAR_TITULO, aviso="recusado")


@moderacao
@require_http_methods(["GET", "POST"])
@never_cache
def retirar(request, pk):
    """Retirada de um publicado, com motivo (FR-017). O link some na hora."""
    return _decidir(request, pk, situacao_exigida=Situacao.PUBLICADO,
                    operacao=operacoes.retirar, template="retirar",
                    titulo=m.RETIRAR_TITULO, aviso="retirado")

"""Escritas atômicas da declaração; a validação nunca altera a âncora ou respostas."""

from types import SimpleNamespace

from django.db import IntegrityError, transaction
from django.utils import timezone

from trajetoria.academico.incorporacao import incorporar_encontrada
from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.acesso import limitacao
from trajetoria.acesso.chaves import (
    ChavesInvalidas,
    chave_de_origem,
    chaves_de_acesso,
    identificador_cpf,
    verificador,
)
from trajetoria.acesso.material import incorporar_com_material
from trajetoria.campanha.consultas import Criterio, EstadoCampanha, avaliar, estado
from trajetoria.campanha.models import Campanha
from trajetoria.declaracao.consultas import candidatas, conflito_potencial, no_escopo
from trajetoria.declaracao.models import (
    AcessoAosDadosDeConsulta,
    DadosConsultaAcervo,
    FormacaoDeclarada,
    ValidacaoDaFormacao,
)
from trajetoria.declaracao.selo import (
    ChaveIndisponivel,
    SeloInvalido,
    abrir_consulta,
    selar_consulta,
    validar_chaves,
)
from trajetoria.fonte_academica.contrato import ConclusaoEncontrada, FonteAcademicaIndisponivel
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.governanca.regras import escopo_de_acompanhamento
from trajetoria.participacao.models import Participacao


class SemCampanha(Exception):
    pass


class Ambiguidade(Exception):
    pass


class EmEspera(Exception):
    pass


class JaDecidida(Exception):
    pass


class ForaDaFila(Exception):
    pass


class ForaDoEscopo(Exception):
    pass


class ReferenciaInexistente(Exception):
    pass


class FonteIndisponivel(Exception):
    pass


def _chaves():
    try:
        return chaves_de_acesso()
    except ChavesInvalidas:
        raise ChaveIndisponivel("Dados temporariamente indisponíveis.") from None


def campanhas_compativeis(dados, *, agora):
    declarada = SimpleNamespace(**dados, modalidade=None, forma_oferta=None)
    ignorados = {Criterio.MODALIDADE, Criterio.FORMA_OFERTA}
    return tuple(
        c
        for c in Campanha.objects.select_related("versao").all()
        if estado(c, agora=agora) == EstadoCampanha.EM_COLETA
        and not any(p.criterio not in ignorados for p in avaliar(c, declarada).pendencias)
    )


def _existente(chave, par):
    f = FormacaoDeclarada.objects.filter(chave_de_criacao=chave).first()
    if f is None:
        return None
    if f.verificador != par:
        raise SeloInvalido("Confirme os dados novamente.")
    return f.participacao


def iniciar_participacao_declarada(dados, cpf11, data, chave_de_criacao, *, origem, agora):
    chaves = _chaves()
    par = verificador(cpf11, data, chaves)
    if p := _existente(chave_de_criacao, par):
        return p, False
    origem_derivada = "acesso:origem:" + chave_de_origem(origem, chaves)
    if limitacao.em_espera(origem_derivada, agora):
        raise EmEspera
    limitacao.registrar(limitacao.ORIGEM, origem_derivada, agora)
    validar_chaves()
    campos = ("nome", "unidade", "nivel", "curso", "ano_conclusao")
    if set(dados) != set(campos) or any(
        not isinstance(dados[c], str) or not dados[c].strip() for c in campos[:-1]
    ):
        raise ValueError("Confira os campos da formação.")
    ano = dados["ano_conclusao"]
    if type(ano) is not int or not 1000 <= ano <= timezone.localtime(agora).year:
        raise ValueError("Confira o ano de conclusão.")
    campanhas = campanhas_compativeis(dados, agora=agora)
    if not campanhas:
        raise SemCampanha
    if len(campanhas) != 1:
        raise Ambiguidade
    try:
        with transaction.atomic():
            f = FormacaoDeclarada.objects.create(
                **dados,
                chave_de_criacao=chave_de_criacao,
                identificador_cpf=identificador_cpf(cpf11, chaves),
                verificador=par,
                declarada_em=agora,
            )
            DadosConsultaAcervo.objects.create(formacao=f, selado=selar_consulta(f.pk, cpf11, data))
            p = Participacao.objects.create(
                campanha=campanhas[0], formacao_declarada=f, iniciada_em=agora
            )
            return p, True
    except IntegrityError:
        if p := _existente(chave_de_criacao, par):
            return p, False
        raise


def declaracoes_do_par(cpf11, data):
    par = verificador(cpf11, data, _chaves())
    return tuple(FormacaoDeclarada.objects.filter(verificador=par).values_list("pk", flat=True))


_SEM_UNIDADE = object()


def _exigir_escopo(formacao, vinculos, unidade=_SEM_UNIDADE):
    if not no_escopo(vinculos).filter(pk=formacao.pk).exists():
        raise ForaDoEscopo
    escopo = escopo_de_acompanhamento(vinculos)
    if unidade is not _SEM_UNIDADE and not escopo.institucional and unidade not in escopo.unidades:
        raise ForaDoEscopo
    return escopo


@transaction.atomic
def registrar_validacao(
    formacao,
    *,
    vinculos,
    operador,
    agora,
    resultado,
    candidata=None,
    referencia_fonte=None,
    acervo=None,
):
    formacao = FormacaoDeclarada.objects.select_for_update().get(pk=formacao.pk)
    _exigir_escopo(formacao, vinculos)
    if ValidacaoDaFormacao.objects.filter(formacao=formacao).exists():
        raise JaDecidida
    if formacao.participacao.concluida_em is None:
        raise ForaDaFila
    if resultado not in ValidacaoDaFormacao.Resultado.values:
        raise ValueError("Resultado inválido.")
    conclusao = None
    fora = conflito = False
    if resultado == "CONFIRMADA":
        if sum(v is not None for v in (candidata, referencia_fonte, acervo)) != 1:
            raise ValueError("Informe uma única origem da formação confirmada.")
        if candidata is not None:
            conclusao = candidatas(formacao).filter(pk=candidata.pk).first()
            if conclusao is None:
                raise ForaDoEscopo
        elif referencia_fonte is not None:
            fonte = FonteSimulada()
            try:
                resposta = fonte.obter_conclusao(referencia_fonte)
                if not isinstance(resposta, ConclusaoEncontrada):
                    raise ReferenciaInexistente
                _exigir_escopo(formacao, vinculos, resposta.conclusao.unidade)
                incorporado = incorporar_com_material(fonte, resposta.id_externo_pessoa)
            except FonteAcademicaIndisponivel:
                raise FonteIndisponivel from None
            conclusao = ConclusaoAcademica.objects.filter(
                fonte=fonte.codigo,
                id_externo=resposta.conclusao.id_externo,
                pessoa=incorporado.pessoa,
            ).first()
            if conclusao is None:
                raise ReferenciaInexistente
        else:
            from trajetoria.declaracao.acervo import FonteAcervoHistorico, registrar_referencia

            _exigir_escopo(formacao, vinculos, acervo.get("unidade"))
            referencia = registrar_referencia(acervo, operador=operador, agora=agora)
            fonte = FonteAcervoHistorico()
            incorporado = incorporar_encontrada(
                fonte.codigo, fonte.obter_pessoa(f"acervo:{referencia.pk}")
            )
            conclusao = ConclusaoAcademica.objects.get(
                fonte=fonte.codigo, id_externo=str(referencia.pk), pessoa=incorporado.pessoa
            )
        _exigir_escopo(formacao, vinculos, conclusao.unidade)
        conclusao = ConclusaoAcademica.objects.select_for_update().get(pk=conclusao.pk)
        fora = not avaliar(formacao.participacao.campanha, conclusao).elegivel
        conflito = not fora and conflito_potencial(formacao, conclusao)
    elif any(v is not None for v in (candidata, referencia_fonte, acervo)):
        raise ValueError("A não confirmação não recebe uma origem.")
    return ValidacaoDaFormacao.objects.create(
        formacao=formacao,
        resultado=resultado,
        conclusao=conclusao,
        fora_da_abrangencia_na_validacao=fora,
        conflito_detectado_na_validacao=conflito,
        operador=operador,
        registrada_em=agora,
    )


@transaction.atomic
def revelar_dados(formacao, *, vinculos, operador, agora):
    _exigir_escopo(formacao, vinculos)
    validar_chaves()
    dados = DadosConsultaAcervo.objects.filter(formacao=formacao).first()
    if dados is None:
        return None
    AcessoAosDadosDeConsulta.objects.create(formacao=formacao, operador=operador, acessado_em=agora)
    cpf, data = abrir_consulta(dados)
    return formacao.nome, cpf, data

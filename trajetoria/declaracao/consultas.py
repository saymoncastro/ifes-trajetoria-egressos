"""Consultas da declaração e fila no escopo; nenhuma resposta é lida."""

from django.db.models import Q

from trajetoria.academico.models import ConclusaoAcademica
from trajetoria.acesso.models import MaterialDeVerificacao
from trajetoria.campanha.models import Campanha
from trajetoria.declaracao.models import FormacaoDeclarada
from trajetoria.governanca.regras import escopo_de_acompanhamento, pode_validar_formacao
from trajetoria.participacao.consultas import participacoes_oficiais


def _opcoes(campo, criterio):
    valores = set(
        ConclusaoAcademica.objects.exclude(**{f"{campo}__isnull": True}).values_list(
            campo, flat=True
        )
    )
    for conjunto in Campanha.objects.values_list(criterio, flat=True):
        valores.update(conjunto or ())
    return tuple(sorted(valores))


def opcoes_de_unidade():
    return _opcoes("unidade", "unidades")


def opcoes_de_nivel():
    return _opcoes("nivel", "niveis")


def no_escopo(vinculos):
    escopo = escopo_de_acompanhamento(vinculos)
    qs = FormacaoDeclarada.objects.all()
    if not pode_validar_formacao(vinculos) or escopo is None:
        return qs.none()
    return qs if escopo.institucional else qs.filter(unidade__in=escopo.unidades)


def fila(vinculos):
    return (
        no_escopo(vinculos)
        .filter(participacao__concluida_em__isnull=False)
        .filter(Q(validacao__isnull=True) | Q(validacao__conflito_detectado_na_validacao=True))
        .select_related("participacao__campanha", "validacao")
    )


def candidatas(formacao):
    pessoas = MaterialDeVerificacao.objects.filter(
        identificador_cpf=formacao.identificador_cpf
    ).values("pessoa_id")
    return ConclusaoAcademica.objects.filter(pessoa_id__in=pessoas)


def outras_do_mesmo_cpf(formacao):
    return FormacaoDeclarada.objects.filter(identificador_cpf=formacao.identificador_cpf).exclude(
        pk=formacao.pk
    )


def divergencia(formacao, conclusao):
    return tuple(
        c
        for c in ("unidade", "nivel", "curso", "ano_conclusao")
        if getattr(formacao, c) != getattr(conclusao, c)
    )


def conflito_potencial(formacao, conclusao):
    return (
        participacoes_oficiais()
        .filter(campanha_id=formacao.participacao.campanha_id, conclusao_efetiva_id=conclusao.pk)
        .exclude(formacao_declarada=formacao)
        .exists()
    )


def cpf_encontrado_na_fonte_digital(formacao):
    return MaterialDeVerificacao.objects.filter(
        identificador_cpf=formacao.identificador_cpf
    ).exists()

"""Apresentação derivada; a regra de abertura pertence exclusivamente à 004."""

from trajetoria.acompanhamento.gestao import mensagens as m
from trajetoria.campanha.consultas import (
    EstadoCampanha,
    data_de_referencia,
    estado,
    impedimentos_de_abertura,
)
from trajetoria.campanha.regras import Motivo
from trajetoria.instrumento.models import EstadoVersao, Versao


def versoes_oferecidas(atual=None):
    versoes = (
        Versao.objects.filter(estado=EstadoVersao.PUBLICADA)
        .select_related("pesquisa")
        .order_by("pesquisa__nome", "designacao", "id")
    )
    opcoes = [(str(v.pk), f"{v.pesquisa.nome} — {v.designacao}") for v in versoes]
    if atual is not None and atual.estado != EstadoVersao.PUBLICADA:
        opcoes.insert(
            0,
            (
                str(atual.pk),
                f"{atual.pesquisa.nome} — {atual.designacao} (não publicada — impede a abertura)",
            ),
        )
    return opcoes


def abrangencia_restrita(campanha):
    criterios = []
    for campo, rotulo in (
        ("ano_minimo", "Ano mínimo de conclusão"),
        ("ano_maximo", "Ano máximo de conclusão"),
        ("unidades", "Unidades"),
        ("niveis", "Níveis"),
        ("modalidades", "Modalidades"),
        ("formas_oferta", "Formas de oferta"),
    ):
        valor = getattr(campanha, campo)
        if valor is not None:
            texto = ", ".join(valor) if isinstance(valor, list) else str(valor)
            criterios.append(f"{rotulo}: {texto}")
    return tuple(criterios)


def painel(campanha, agora):
    situacao = estado(campanha, agora=agora)
    impedimentos = []
    acoes = []
    if campanha.aberta_em is None:
        for violacao in impedimentos_de_abertura(campanha, agora=agora):
            if violacao.motivo is Motivo.VERSAO_NAO_PUBLICADA:
                correcao = (
                    "Escolha uma Versão publicada em Editar configuração. "
                    "A publicação não é feita aqui."
                    if Versao.objects.filter(estado=EstadoVersao.PUBLICADA).exists()
                    else m.SEM_PUBLICADA
                )
                impedimentos.append(f"A Versão escolhida ainda não foi publicada. {correcao}")
            elif violacao.motivo is Motivo.PERIODO_NAO_DEFINIDO:
                impedimentos.append(
                    "O período de coleta não foi definido. "
                    "Defina início e fim em Editar configuração."
                )
            elif violacao.motivo is Motivo.FORA_DO_PERIODO:
                if data_de_referencia(agora) < campanha.inicio:
                    impedimentos.append(
                        f"A coleta poderá ser aberta a partir de {campanha.inicio:%d/%m/%Y}."
                    )
                else:
                    impedimentos.append(
                        "O período terminou sem que a coleta fosse aberta. "
                        "Para usar esta Campanha, corrija o período em Editar configuração."
                    )
            else:
                raise ValueError("Impedimento de abertura sem mensagem")
        acoes.append(("editar", "Editar configuração"))
        if not impedimentos:
            acoes.append(("abrir", "Abrir coleta"))
        situacao_gestao = (
            "periodo_encerrado_nunca_aberta"
            if situacao is EstadoCampanha.ENCERRADA
            else "nunca_aberta_impedida"
            if impedimentos
            else "nunca_aberta_pronta"
        )
    elif situacao is EstadoCampanha.EM_COLETA:
        acoes.append(("encerrar", "Encerrar coleta"))
        situacao_gestao = "em_coleta"
    else:
        situacao_gestao = "encerrada_apos_coleta"
    return {
        "situacao_gestao": situacao_gestao,
        "acoes": tuple(acoes),
        "impedimentos": tuple(impedimentos),
        "encerramento_previsto": campanha.fim if situacao is EstadoCampanha.EM_COLETA else None,
        "abrangencia_restrita": abrangencia_restrita(campanha),
        "texto_abrangencia": m.ABRANGENCIA,
    }

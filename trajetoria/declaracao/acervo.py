"""Fonte acadêmica de referências atestadas; nunca usa a declaração como fonte."""

from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from trajetoria.declaracao.models import ReferenciaDeAcervo
from trajetoria.fonte_academica.acervo_historico import CODIGO
from trajetoria.fonte_academica.contrato import (
    ConclusaoEncontrada,
    ConclusaoInexistente,
    ConclusaoNaFonte,
    PessoaEncontrada,
    PessoaInexistente,
)


class ReferenciaDivergente(Exception):
    pass


@transaction.atomic
def registrar_referencia(dados, *, operador, agora):
    campos = (
        "unidade",
        "referencia",
        "nivel",
        "curso",
        "ano_conclusao",
        "modalidade",
        "forma_oferta",
        "data_conclusao",
    )
    valores = {c: dados.get(c) for c in campos}
    for campo in ("unidade", "referencia"):
        valor = valores[campo]
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("Confira a referência.")
        valores[campo] = " ".join(valor.split())
    for campo in ("nivel", "curso", "modalidade", "forma_oferta"):
        valor = valores[campo]
        if valor is None and campo in ("modalidade", "forma_oferta"):
            continue
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("Confira os dados encontrados no acervo.")
    nova = ReferenciaDeAcervo(**valores, operador=operador, registrada_em=agora)
    try:
        nova.full_clean(
            exclude=[c for c in campos if valores[c] is None],
            validate_unique=False,
            validate_constraints=False,
        )
        if not 1000 <= nova.ano_conclusao <= 9999:
            raise ValueError
        if nova.data_conclusao and nova.data_conclusao.year != nova.ano_conclusao:
            raise ValueError
    except (ValidationError, ValueError, TypeError):
        raise ValueError("Confira os dados encontrados no acervo.") from None
    normalizados = {c: getattr(nova, c) for c in campos}
    chave = {c: normalizados[c] for c in ("unidade", "referencia")}
    referencia, _ = ReferenciaDeAcervo.objects.get_or_create(
        **chave,
        defaults={
            c: v
            for c, v in (normalizados | {"operador": operador, "registrada_em": agora}).items()
            if c not in chave
        },
    )
    if any(getattr(referencia, c) != v for c, v in normalizados.items()):
        raise ReferenciaDivergente("A referência já existe com dados diferentes.")
    return referencia


class FonteAcervoHistorico:
    codigo = CODIGO

    def _referencia(self, id_externo):
        try:
            return ReferenciaDeAcervo.objects.filter(pk=UUID(id_externo)).first()
        except (ValueError, TypeError, AttributeError):
            return None

    def _conclusao(self, r):
        return ConclusaoNaFonte(
            id_externo=str(r.pk),
            unidade=r.unidade,
            nivel=r.nivel,
            curso=r.curso,
            ano_conclusao=r.ano_conclusao,
            modalidade=r.modalidade,
            forma_oferta=r.forma_oferta,
            data_conclusao=r.data_conclusao,
        )

    def obter_pessoa(self, id_externo):
        if not isinstance(id_externo, str) or not id_externo.startswith("acervo:"):
            return PessoaInexistente(id_externo)
        r = self._referencia(id_externo[7:])
        if r is None:
            return PessoaInexistente(id_externo)
        return PessoaEncontrada(
            id_externo=f"acervo:{r.pk}", nome=None, conclusoes=(self._conclusao(r),)
        )

    def obter_conclusao(self, id_externo):
        r = self._referencia(id_externo)
        if r is None:
            return ConclusaoInexistente(id_externo)
        return ConclusaoEncontrada(self._conclusao(r), f"acervo:{r.pk}")

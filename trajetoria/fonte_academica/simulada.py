"""Fonte simulada (conceitualmente, `MockAcademicDataProvider`).

Implementa o contrato sobre registros fictícios declarados. Como fará um adaptador real,
é aqui, e não no núcleo, que a situação acadêmica da fonte vira "conclusão reconhecida".
"""

from collections.abc import Iterable

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.cenarios import PessoaSimulada, RegistroSimulado
from trajetoria.fonte_academica.contrato import (
    CAMPOS_DE_CONTEXTO,
    ConclusaoEncontrada,
    ConclusaoInexistente,
    ConclusaoNaFonte,
    FonteAcademicaIndisponivel,
    PessoaEncontrada,
    PessoaInexistente,
    RegistroNaoReconhecidoComoConclusao,
)


class FonteSimulada:
    codigo = "simulada"

    def __init__(
        self,
        pessoas: Iterable[PessoaSimulada] = cenarios.PESSOAS,
        registros: Iterable[RegistroSimulado] = cenarios.REGISTROS,
        indisponivel: bool = False,
    ) -> None:
        self._pessoas = {p.id_externo: p for p in pessoas}
        self._registros = {r.id_externo: r for r in registros}
        self._indisponivel = indisponivel

    def obter_pessoa(self, id_externo: str) -> PessoaEncontrada | PessoaInexistente:
        self._verificar_disponibilidade()
        pessoa = self._pessoas.get(id_externo)
        if pessoa is None:
            return PessoaInexistente(id_externo)
        conclusoes = tuple(
            _para_contrato(r)
            for r in sorted(self._registros.values(), key=lambda r: r.id_externo)
            if r.id_pessoa == id_externo and _reconhecida(r)
        )
        return PessoaEncontrada(id_externo, pessoa.nome, conclusoes)

    def obter_conclusao(
        self, id_externo: str
    ) -> ConclusaoEncontrada | RegistroNaoReconhecidoComoConclusao | ConclusaoInexistente:
        self._verificar_disponibilidade()
        registro = self._registros.get(id_externo)
        if registro is None:
            return ConclusaoInexistente(id_externo)
        if not _reconhecida(registro):
            return RegistroNaoReconhecidoComoConclusao(id_externo)
        return ConclusaoEncontrada(_para_contrato(registro), registro.id_pessoa)

    def _verificar_disponibilidade(self) -> None:
        if self._indisponivel:
            raise FonteAcademicaIndisponivel("fonte simulada configurada como indisponível")


def _reconhecida(registro: RegistroSimulado) -> bool:
    # Matrícula ativa, evasão, transferência, situação desconhecida ou ausente: não.
    return registro.situacao == cenarios.CONCLUIDA


def _para_contrato(registro: RegistroSimulado) -> ConclusaoNaFonte:
    return ConclusaoNaFonte(
        id_externo=registro.id_externo,
        **{campo: getattr(registro, campo) for campo in CAMPOS_DE_CONTEXTO},
    )

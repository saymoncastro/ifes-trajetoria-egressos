"""Fonte simulada de contexto da trajetória (Feature 021, P2; research R18).

Implementa só `FonteDeContextoDaTrajetoria`; a `FonteSimulada` (001) não muda. Os valores
são fictícios e não afirmam que a fonte acadêmica real os fornece (FR-064).
"""

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contexto_da_trajetoria import (
    AgregadoNaFonte,
    ComplementoNaFonte,
    ContextoDaTrajetoriaNaFonte,
    ContextoIndisponivel,
    MetricaAgregada,
)


class ContextoSimulado:
    codigo = "simulada"

    def __init__(self, complementos=None, agregados=None, indisponivel: bool = False) -> None:
        self._complementos = cenarios.COMPLEMENTOS if complementos is None else complementos
        self._agregados = cenarios.AGREGADOS if agregados is None else agregados
        self._indisponivel = indisponivel

    def obter_contexto(self, ids_externos_conclusoes) -> ContextoDaTrajetoriaNaFonte:
        if self._indisponivel:
            raise ContextoIndisponivel("fonte de contexto simulada configurada como indisponível")
        pedidas = [
            r for r in sorted(cenarios.REGISTROS, key=lambda r: r.id_externo)
            if r.id_externo in set(ids_externos_conclusoes) and r.situacao == cenarios.CONCLUIDA
        ]
        complementos = tuple(
            ComplementoNaFonte(r.id_externo, *self._complementos[r.id_externo])
            for r in pedidas
            if r.id_externo in self._complementos
        )
        recortes = {(r.curso, r.unidade, r.ano_conclusao) for r in pedidas}
        unidades = {(u, a) for _, u, a in recortes}
        agregados = []
        for metrica, curso, unidade, ano, valor, apurado_em in self._agregados:
            if metrica == MetricaAgregada.CONCLUSOES_CURSO_UNIDADE_ANO.value:
                aplica = (curso, unidade, ano) in recortes
            else:
                aplica = (unidade, ano) in unidades
            if aplica:
                agregados.append(
                    AgregadoNaFonte(
                        MetricaAgregada(metrica), unidade, ano, valor, apurado_em, curso
                    )
                )
        return ContextoDaTrajetoriaNaFonte(complementos, tuple(agregados))

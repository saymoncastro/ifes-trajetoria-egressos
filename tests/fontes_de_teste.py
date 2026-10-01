"""Fontes usadas só nos testes.

`FonteAlternativa` é uma segunda implementação do contrato, independente da simulada, para
provar a substituibilidade (FR-024, SC-006). Não existe em produção.
"""

from datetime import date

from trajetoria.fonte_academica.contrato import (
    ConclusaoEncontrada,
    ConclusaoInexistente,
    ConclusaoNaFonte,
    FonteAcademicaIndisponivel,
    PessoaEncontrada,
    PessoaInexistente,
    RegistroNaoReconhecidoComoConclusao,
)
from trajetoria.fonte_academica.simulada import FonteSimulada


class FonteAlternativa:
    """Outra estrutura interna: conclusões reconhecidas e demais registros guardados à parte."""

    codigo = "teste-alternativa"

    _NOMES = {"ALT-P-1": "Rita Exemplo", "ALT-P-2": "Otto Exemplo"}
    _RECONHECIDAS = {
        "ALT-C-1": (
            "ALT-P-1",
            ConclusaoNaFonte(
                "ALT-C-1", "Licenciatura em Física", "Cariacica", "Graduação", "Presencial",
                None, 2018, date(2018, 12, 14),
            ),
        ),
        "ALT-C-2": (
            "ALT-P-1",
            ConclusaoNaFonte(
                "ALT-C-2", "Especialização em Educação Profissional e Tecnológica", "Cefor",
                "Pós-graduação", None, None, 2021,
            ),
        ),
    }
    _NAO_RECONHECIDOS = {"ALT-C-9": "ALT-P-2"}

    def __init__(self, indisponivel: bool = False) -> None:
        self._indisponivel = indisponivel

    def obter_pessoa(self, id_externo):
        self._verificar()
        if id_externo not in self._NOMES:
            return PessoaInexistente(id_externo)
        conclusoes = tuple(
            c for dono, c in sorted(self._RECONHECIDAS.values(), key=lambda par: par[1].id_externo)
            if dono == id_externo
        )
        return PessoaEncontrada(id_externo, self._NOMES[id_externo], conclusoes)

    def obter_conclusao(self, id_externo):
        self._verificar()
        if id_externo in self._RECONHECIDAS:
            dono, conclusao = self._RECONHECIDAS[id_externo]
            return ConclusaoEncontrada(conclusao, dono)
        if id_externo in self._NAO_RECONHECIDOS:
            return RegistroNaoReconhecidoComoConclusao(id_externo)
        return ConclusaoInexistente(id_externo)

    def _verificar(self):
        if self._indisponivel:
            raise FonteAcademicaIndisponivel("fonte alternativa indisponível")


# Identificadores que cada implementação declara para a suíte de contrato.
CASOS_DE_CONTRATO = {
    FonteSimulada: {
        "pessoa_com_conclusoes": "SIM-P-0004",
        "pessoa_sem_conclusao": "SIM-P-0006",
        "pessoa_inexistente": "SIM-P-9999",
        "conclusao_reconhecida": "SIM-C-0001",
        "registro_nao_reconhecido": "SIM-C-0901",
        "conclusao_inexistente": "SIM-C-9999",
    },
    FonteAlternativa: {
        "pessoa_com_conclusoes": "ALT-P-1",
        "pessoa_sem_conclusao": "ALT-P-2",
        "pessoa_inexistente": "ALT-P-404",
        "conclusao_reconhecida": "ALT-C-1",
        "registro_nao_reconhecido": "ALT-C-9",
        "conclusao_inexistente": "ALT-C-404",
    },
}

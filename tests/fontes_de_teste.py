"""Fontes usadas só nos testes.

`FonteAlternativa` é uma segunda implementação do contrato, independente da simulada, para
provar a substituibilidade (FR-024, SC-006). Não existe em produção.
"""

from dataclasses import replace
from datetime import date

from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.cenarios import RegistroSimulado
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


def variante_canonica(variante: str) -> FonteSimulada:
    """O catálogo canônico com uma única mudança, mesmo código de fonte ("simulada").

    Simula a mesma fonte devolvendo, numa leitura posterior, conteúdo diferente do já
    incorporado (FR-033).
    """
    pessoas = list(cenarios.PESSOAS)
    registros = list(cenarios.REGISTROS)

    def trocar(id_externo, **mudancas):
        i = next(n for n, r in enumerate(registros) if r.id_externo == id_externo)
        registros[i] = replace(registros[i], **mudancas)

    match variante:
        case "i":  # curso de SIM-C-0001 alterado
            trocar("SIM-C-0001", curso="Tecnologia em Sistemas para Internet")
        case "ii":  # SIM-C-0003 ausente
            registros = [r for r in registros if r.id_externo != "SIM-C-0003"]
        case "iii":  # SIM-C-0002 atribuída a SIM-P-0001
            trocar("SIM-C-0002", id_pessoa="SIM-P-0001")
        case "iv":  # SIM-P-0009 passa a ter nome
            pessoas = [
                replace(p, nome="Nina Exemplo") if p.id_externo == "SIM-P-0009" else p
                for p in pessoas
            ]
        case "v":  # nova conclusão para SIM-P-0001
            registros.append(
                RegistroSimulado(
                    "SIM-C-0099", "SIM-P-0001", "concluida", "Especialização em Gestão Pública",
                    "Cefor", "Pós-graduação", "A distância", None, 2024,
                )
            )
        case "vi":  # SIM-P-0001 fica sem conclusão reconhecida
            trocar("SIM-C-0001", situacao="matricula_ativa")
        case "vii":  # SIM-P-0001 e SIM-C-0001 ausentes
            pessoas = [p for p in pessoas if p.id_externo != "SIM-P-0001"]
            registros = [r for r in registros if r.id_externo != "SIM-C-0001"]
        case _:
            raise ValueError(variante)
    return FonteSimulada(pessoas=pessoas, registros=registros)
